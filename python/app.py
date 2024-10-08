from dataclasses import dataclass
import grpc
import dht_pb2
import dht_pb2_grpc
import hashlib
from concurrent import futures
import threading
import traceback
import sys
import queue
import os

@dataclass
class Item:
    # vai servir pra passar key : value pairs
    key:str
    value:bytes

class Node(dht_pb2_grpc.DhtOperationsServicer):
    def __init__(self, port:int) -> None:
        self.ip_addr:str = "127.0.0.1"
        self.port:int    = int(port)
        self.id:str      = f"{self.ip_addr}:{port}"
        self.id_hash:str = self.calc_hash_id(self.id)
        self.id_next:str = self.id 
        self.id_prev:str = self.id
        self.stored_items:dict = {}
        self.messages_queue = queue.Queue(maxsize=10)
        # Iniciar thread para processar a fila
        self.queue_thread = threading.Thread(target=self.process_message_queue, daemon=True)
        self.queue_thread.start()

    # roda numa thread separada, para consumir a fila de mensagens gRPC
    def process_message_queue(self):
        while True:
            try:
                method_name, request_msg_obj, target_node_id = self.messages_queue.get()
                # node processando esse request cria um stub para a chamada rpc especifica.
                with grpc.insecure_channel(target_node_id) as channel:
                    stub = dht_pb2_grpc.DhtOperationsStub(channel)
                    if method_name == "FindNext":
                        stub.FindNext(request_msg_obj)
                    elif method_name == "SendJoiningPosition":
                        stub.SendJoiningPosition(request_msg_obj)
                    elif method_name == "AdjustPredJoin":
                        stub.AdjustPredJoin(request_msg_obj)
                    elif method_name == "AdjustNextLeave":
                        stub.AdjustNextLeave(request_msg_obj)
                    elif method_name == "AdjustPredLeave":
                        stub.AdjustPredLeave(request_msg_obj)
                    elif method_name == "StoreItem":
                        stub.StoreItem(request_msg_obj)
                    elif method_name == "RetrieveItem":
                        stub.RetrieveItem(request_msg_obj)
                    elif method_name == "SendItem":
                        stub.SendItem(request_msg_obj)
                    elif method_name ==  "SendNotFound":
                        stub.SendNotFound(request_msg_obj)
                    elif method_name == "TransferItems":
                        stub.TransferItems(request_msg_obj)
                    else:
                        print(f"Não existe metodo: {method_name} configurado no gRPC.")
                    
            except grpc.RpcError as g:
                print(f"Erro na chamada gRPC: {g}")
            except Exception as e:
                print(f"Erro geral: {e}")
            

            

    def FindNext(self, request, context) -> None:
        req:tuple
        # verifica se esta no lugar certo de inserir, baseado no hash
        if self.is_correct_place(request.joining_node.id):
            prev_ip, prev_port = self.id_prev.split(':')
            req = (
                "SendJoiningPosition",
                dht_pb2.JoinOk(
                    next_node=dht_pb2.NodeInfo(
                        id=self.id_hash, 
                        ip_addr=self.ip_addr, 
                        port=self.port),
                    prev_node=dht_pb2.NodeInfo(
                        id = self.calc_hash_id(self.id_prev),
                        ip_addr = prev_ip,
                        port = int(prev_port)),
                    remetente= self.id 
                ),
                f"{request.joining_node.ip_addr}:{request.joining_node.port}"
            )
        else:

            req = (
                "FindNext",
                dht_pb2.Join(
                    joining_node=dht_pb2.NodeInfo(
                        id = request.joining_node.id,
                        ip_addr = request.joining_node.ip_addr, 
                        port = request.joining_node.port),
                        remetente= self.id 
                ),
                self.id_next
            )
        # enfileira a tupla de request criada
        self.messages_queue.put(req)
        return dht_pb2.Void()

    '''
        node que recebe isso:
          * atualiza seu prev e seu next
          * manda mensagem transfer, para receber os itens que vai tomar conta
    '''
    def SendJoiningPosition(self, request, context):
        
        next_grpc = request.next_node
        prev_grpc = request.prev_node

        self.id_next = f"{next_grpc.ip_addr}:{str(next_grpc.port)}"
        self.id_prev = f"{prev_grpc.ip_addr}:{str(prev_grpc.port)}"


        req_adj_prev = (
            "AdjustPredJoin",
            dht_pb2.NewNode(
                joining_node=dht_pb2.NodeInfo(
                    id = self.id_hash,
                    ip_addr = self.ip_addr,
                    port = self.port
                ),
                remetente= self.id
            ),
            self.id_prev
        )
        self.messages_queue.put(req_adj_prev)

        # enfileira pedido de transfer,
        # node que quer receber os itens manda a mensagem para seu next 
        req_transfer = (
            "TransferItems",
            dht_pb2.NodeInfo(
                id=self.id_hash,
                ip_addr= self.ip_addr,
                port = self.port
            ),
            self.id_next,
        )
        self.messages_queue.put(req_transfer)

        # fim de uma operação Join, escreve no arquivo de nodes conhecidos
        with open("lista_nodes.txt", 'a') as hosts:
            hosts.write(f"{self.id}\n")
        
        return dht_pb2.Void()
        

    # node que recebe ajusta seu next quando um node entra na dht
    def AdjustPredJoin(self, request, context):
        new_next_ip = request.joining_node.ip_addr
        new_next_port = request.joining_node.port
        self.id_next = f"{new_next_ip}:{str(new_next_port)}"
        return dht_pb2.Void()
        
   
    # node que recebe deve ajustar seu predecessor quando um node sai da dht
    def AdjustNextLeave(self, request, context):
        new_prev_ip = request.leaving_node_pred.ip_addr
        new_prev_port = request.leaving_node_pred.port 
        self.id_prev = f"{new_prev_ip}:{str(new_prev_port)}"

        # tenho que mandar transfer para remetente me mandar os itens que ele guarda
        req_transfer = (
            "TransferItems",
            dht_pb2.NodeInfo(
                id=self.id_hash,
                ip_addr= self.ip_addr,
                port = self.port
            ),
            request.remetente
        )
        self.messages_queue.put(req_transfer)

        return dht_pb2.Void()

    # node que recebe deve ajustar seu sucessor, quando um node sai da dht
    def AdjustPredLeave(self, request, context):
        new_next_ip = request.leaving_node_next.ip_addr
        new_next_port = request.leaving_node_next.port 
        self.id_next = f"{new_next_ip}:{str(new_next_port)}"
        return dht_pb2.Void()
    
    def TransferItems(self, request, context):
        requester_id = f"{request.ip_addr}:{request.port}"
        
        if not self.stored_items.values():
            print("\nNao tenho nenhum item armazenado.")
        else:
            # supondo que k seja a string de um hash e v uma string
            for k, v in self.stored_items.values():
                if int(k, 16) >  int(request.id, 16):
                    continue
                else:
                    yield dht_pb2.Transfer(
                        key= k,
                        value = v.encode("utf-8"), # encoda a string para bytes
                        remetente= self.id
                    )
    
    def StoreItem(self, request:dht_pb2.Store, context) -> None:
        req:tuple
        if self.is_correct_place(request.key):
            print(f"Guardando o item {request.key} no nó {self.id}")
            self.stored_items[request.key_hash] = request.value
        else:
            print(f"Enviando item {request.key} para o nó {self.id_next}")
            req = (
                "StoreItem",
                dht_pb2.Store(
                        key = request.key,
                        obj_size=len(request.value),
                        value=request.value
                ),
                self.id_next
            )
            self.messages_queue.put(req)
        
        # enfileira a tupla de request criada
        return dht_pb2.Void()
    
    def RetrieveItem(self, request: dht_pb2.Retrieve, context):
        if self.is_correct_place(request.key):
            if request.key in self.stored_items.keys:
                print(f"Item {request.key} encontrado, enviando para o nó pedinte!")
                self.SendItem(
                            dht_pb2.Ok(
                                key = request.key,
                                obj_size=len(self.stored_items[request.key]),
                                value = self.stored_items[request.key],
                                remetente=self.id
                                ),
                            )
            else:
                print(f"Item {request.key} não encontrado!")
                self.SendNotFound()
        else:
            print(f"O item {request.key} não é meu, enviando solictação para o nó {self.id_next}")
            req = (
                "RetrieveItem",
                dht_pb2.Retrieve(
                        key = request.key,
                        searching_node=dht_pb2.NodeInfo(
                            id=request.searching_node.id, 
                            ip_addr=self.searching_node.ip_addr, 
                            port=self.searching_node.port),
                        remetente=self.id
                ),
                self.id_next
            )
            self.messages_queue.put(req)
        
        # enfileira a tupla de request criada
        return dht_pb2.Void()
    
    def SendItem(self, request, context):
        return super().SendItem(request, context)
    
    def SendNotFound(self, request, context):
        return super().SendNotFound(request, context)
    
    def calc_hash_id(self, id:str):
        #hash correto: hashlib.sha256(id.encode(encoding="utf-8")).hexdigest()
        ip , port = id.split(":")
        return port
    
    
    def is_correct_place(self, id_hash_new:str) -> bool:
        # converte para int base 16
        id_hash_new = int(id_hash_new, 16)
        self_id_hash_int = int(self.id_hash, 16)
        hash_id_prev = int(self.calc_hash_id(self.id_prev), 16)
        
        # hash que quer entrar eh menor do que meu hash?
        if id_hash_new < self_id_hash_int:
            return True

        # sou o primeiro do anel e hash que quer entrar maior que meu anterior? 
        if hash_id_prev >= self_id_hash_int and id_hash_new > hash_id_prev:
            return True

        return False  


    def is_responsible_for_key(self, key_hash: str) -> bool:
        '''
        Verifica se o nó é responsável por armazenar a chave com o hash fornecido.
        '''
        # O nó é responsável se o hash da chave estiver entre o ID do nó atual e o ID do seu próximo nó
        if self.id_hash < key_hash <= self.id_next:
            return True
        elif self.id_hash > self.id_next:  # Quando o ID atual é maior que o próximo (final da faixa circular)
            return key_hash > self.id_hash or key_hash <= self.id_next
        return False
    
       
    def join(self):
        known_hosts_path = "lista_nodes.txt"
        with open(known_hosts_path, 'r+') as hosts:
            known_hosts_list = hosts.readlines()
            if not known_hosts_list:
                hosts.write(f"{self.id}\n")
            else:
                # known_hosts_list = hosts.readlines()
                for host_id in known_hosts_list:
                    try:
                        req = (
                            "FindNext",
                            dht_pb2.Join(
                                joining_node=dht_pb2.NodeInfo(
                                    id = self.id_hash,
                                    ip_addr = self.ip_addr, 
                                    port = self.port
                                    ),
                                    remetente= self.id
                            ),
                            host_id
                        )
                        self.messages_queue.put(req)
                        return
                    
                    except Exception as e:
                        continue
    
    '''
    Ao final disso, os ponteiros dos vizinhos devem ter sido atualizados
    (AdjustNextLeave e AdjustPredLeave) e os itens do no que esta saindo
    devem ser transferidos para o sucessor (sucessor deve mandar Transfer
    para node que esta saindo)
    '''
    def leave(self):
        ip_addr_prev, port_prev = self.id_prev.split(":")
        ip_addr_next, port_next = self.id_next.split(":")

        # node que chamou funcao leave manda mensagem para seu next, com dados do seu prev
        req_leave_next = (
            "AdjustNextLeave",
            dht_pb2.Leave(
                leaving_node_pred= dht_pb2.NodeInfo(
                    id = self.calc_hash_id(self.id_prev),
                    ip_addr = ip_addr_prev,
                    port= int(port_prev)
                ),
                remetente=self.id
            ),
            self.id_next
        )

        self.messages_queue.put(req_leave_next)

        # node que chamou funcao leave manda mensagem para seu prev, com dados do seu next
        req_leave_prev = (
            "AdjustPredLeave",
            dht_pb2.NodeGone(
                leaving_node_next= dht_pb2.NodeInfo(
                    id = self.calc_hash_id(self.id_next),
                    ip_addr = ip_addr_next,
                    port= int(port_next)
                ),
                remetente=self.id
            ),
            self.id_prev
        )

        self.messages_queue.put(req_leave_prev)
        pass

    def store(self, item: Item):
        key_hash = self.calc_hash_id(item.key)
        # key_hash = hashlib.sha256(item.key.encode(encoding="utf-8")).hexdigest()

        if self.is_correct_place(key_hash):
        # if False: # testing
            print(f"Guardando o item {item.key} no nó {self.id}")
            self.stored_items[key_hash] = item.value
        else:
            print(f"Enviando item {item.key} para o nó {self.id_next}")
            try:
                req = (
                    "StoreItem",
                    dht_pb2.Store(
                            key = key_hash,
                            obj_size=len(item.value),
                            value=item.value,
                            remetente=self.id
                    ),
                    self.id_next
                    # "127.0.0.1:3002" #testing
                )
                self.messages_queue.put(req)
                return
            except:
                print("\n nao foi possivel armazenar o item")

    
    def retrieve(self, key: str):
        key_hash = self.calc_hash_id(key)
        # key_hash = hashlib.sha256(key.encode(encoding="utf-8")).hexdigest()

        if self.is_correct_place(key_hash):
        # if False: #testing
            print(f"Item {key} encontrado, Aqui está o conteúdo do arquivo:")
            print(self.stored_items[key_hash])
        else:
            print(f"Enviando a chave {key} para o nó {self.id_next}")
            try:
                req = (
                    "RetrieveItem",
                    dht_pb2.Retrieve(
                            key = key,
                            searching_node=dht_pb2.NodeInfo(
                                id=self.id, 
                                ip_addr=self.ip_addr, 
                                port=self.port),
                            remetente=self.id
                    ),
                    self.id_next
                    # "127.0.0.1:3002" # testing
                )
                self.messages_queue.put(req)
                return
            except:
                print("\n nao foi possivel procurar o item")

def abre_server(port_arg:int):
    port = str(port_arg)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    manager = Node(port=port)
    dht_pb2_grpc.add_DhtOperationsServicer_to_server(manager, server)
    server.add_insecure_port("[::]:" + port)
    server.start()

    try:
        server.wait_for_termination()  # Aguarda o servidor gRPC ser finalizado
    finally:
        manager.queue_thread.join()  # Espera o término da thread de fila
        print("Servidor finalizado e fila de mensagens processada.")

def main():

    #vai rodar num mesmo ip sempre, so muda a porta
    if len(sys.argv) != 2:
        print(f"Utilize: python3 {os.path.basename(__file__)} <porta>")
        sys.exit(1)

    port = int(sys.argv[1])

    # server escuta numa thread separada
    server_thread = threading.Thread(target=abre_server, args=(port,), daemon=True)
    server_thread.start()
    
    print(f"APLICAÇÃO INICIADA")
    print(f"ouvindo na porta: {port}")
    node = Node(port)
    while True:
        print("Qual ação deseja fazer? (join/store/retrieve/leave):", end=" ")
        action = input().lower().strip()
        if action == "join":
            node.join()
        elif action == "store":
            key = input("Digite a chave: ")
            value = bytes(input("Digite o valor: ").encode("utf-8"))
            node.store(Item(key, value))
        elif action == "retrieve":
            key = input("Digite a chave: ")
            node.retrieve(key)
        elif action == "leave":
            node.leave()
        elif action == "exit":
            sys.exit(1)
        else:
            print("Ação não encontrada. Use 'join', 'store', 'retrieve', ou 'leave'.")


if __name__ == "__main__":
    main()
    