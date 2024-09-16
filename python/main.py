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

@dataclass
class Item:
    # vai servir pra passar key : value pairs
    key:str
    value:str

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
        # node inicializa tentando entrar na dht
        self.join()

    # roda numa thread separada, para consumir a fila de mensagens gRPC
    def process_message_queue(self):
        print("Fila de mensagens inicializada.")
        while True:
            try:
                # separa a tupla que foi enfileirada
                method_name, request_msg_obj, target_node_id = self.messages_queue.get()
                '''
                    node processando esse request cria um stub para processar a chamada rpc especifica.
                '''
                with grpc.insecure_channel(target_node_id) as channel:
                    stub = dht_pb2_grpc.DhtOperationsStub(channel)

                    if method_name == "FindNext":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.FindNext(request_msg_obj)
                    elif method_name == "SendJoiningPosition":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.SendJoiningPosition(request_msg_obj)
                    elif method_name == "AdjustPredJoin":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.AdjustPredJoin(request_msg_obj)
                    elif method_name == "AdjustNextLeave":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.AdjustNextLeave(request_msg_obj)
                    elif method_name == "AdjustPredLeave":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.AdjustPredLeave(request_msg_obj)
                    elif method_name == "StoreItem":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.StoreItem(request_msg_obj)
                    elif method_name == "RetrieveItem":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.RetrieveItem(request_msg_obj)
                    elif method_name == "SendItem":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.SendItem(request_msg_obj)
                    elif method_name ==  "SendNotFound":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.SendNotFound(request_msg_obj)
                    elif method_name == "TransferItems":
                        print(f"processando {method_name} para {target_node_id}.")
                        stub.TransferItems(request_msg_obj)
                    else:
                        print(f"Não existe metodo: {method_name} configurado no gRPC.")

            except grpc.RpcError as g:
                print(f"Erro na chamada gRPC: {g}")
            except Exception as e:
                print(f"Erro geral: {e}")  

    def FindNext(self, request, context) -> None:
        req:tuple
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
                        port = int(prev_port)) 
                ),
                request.joining_node.id
            )
        else:

            req = (
                "FindNext",
                dht_pb2.Join(
                    joining_node=dht_pb2.NodeInfo(
                        id = request.joining_node.id,
                        ip_addr = request.joining_node.ip_addr, 
                        port = request.joining_node.port)  
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

        print("recebi joinOK, meu proximo e anterior sao:")
        print(self.id_next)
        print(self.id_prev)


        req_adj_pred = (
            "AdjustPredJoin",
            dht_pb2.NewNode(
                joining_node=dht_pb2.NodeInfo(
                    id = self.id,
                    ip_addr = self.ip_addr,
                    port = self.port
                )
            ),
            self.id_prev
        )
        self.messages_queue.put(req_adj_pred)

        # enfileira pedido de transfer
        req_transfer = (
            "TransferItems",
            dht_pb2.Void(),
            self.id_next,
        )
        self.messages_queue.put(req_transfer)
        

    def AdjustPredJoin(self, request, context):
        new_next_ip = request.joining_node.ip_addr
        new_next_port = request.joining_node.port
        self.id_prev = f"{new_next_ip}:{str(new_next_port)}"
    
    
    def AdjustNextLeave(self, request, context):
        new_pred_ip = request.leaving_node_pred.ip_addr
        new_pred_port = request.leaving_node_pred.port 
        self.id_prev = f"{new_pred_ip}:{str(new_pred_port)}"
        # transfer

    
    def AdjustPredLeave(self, request, context):
        new_next_ip = request.leaving_node_next.ip_addr
        new_next_port = request.leaving_node_next.port 
        self.id_prev = f"{new_next_ip}:{str(new_next_port)}"
    
    def StoreItem(self, request:dht_pb2.Store, context) -> None:
        req:tuple
        if self.is_correct_place(request.key):
            print(f"Armazenando chave {request.key} no nó {self.id}")
            self.stored_items[request.key_hash] = request.value
        else:
            print(f"Enviando a chave {request.key} para o nó {self.id_next}")
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
    
    def RetrieveItem(self, request, context):
        return super().RetrieveItem(request, context)
    
    def SendItem(self, request, context):
        return super().SendItem(request, context)
    
    def SendNotFound(self, request, context):
        return super().SendNotFound(request, context)
    
    def calc_hash_id(self, id:str):
        return hashlib.sha256(id.encode(encoding="utf-8")).hexdigest()
    
    
    def is_correct_place(self, id_hash_new:str) -> bool:
        # converte para int base 16
        id_hash_new = int(id_hash_new, 16)
        self_id_hash_int = int(self.id_hash, 16)
        hash_id_prev = int(self.calc_hash_id(self.id_prev), 16)

        # hash que quer entrar eh maior do que eu? false
        if id_hash_new < self_id_hash_int:
            return True

        # hash do predecessor é maior que o meu e hash new é maior que predecessor? true
        if hash_id_prev > self_id_hash_int and id_hash_new > hash_id_prev:
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
                                    port = self.port)  
                            ),
                            host_id
                        )
                        self.messages_queue.put(req)
                        return
                    
                    except Exception as e:
                        print(f"Não foi possivel se conectar a {host_id}")
                        continue

    def leave():
        pass

    def store(self, item: Item):
        key_hash = hashlib.sha256(item.key.encode(encoding="utf-8")).hexdigest()

        if self.is_correct_place(key_hash):
            print(f"Armazenando chave {item.key} no nó {self.id}")
            self.stored_items[key_hash] = item.value
            print(f"chave {item.key} armazenada no nó {self.id}")
        else:
            try:
                print(f"Enviando a chave {item.key} para o nó {self.id_next}")
                req = (
                    "StoreItem",
                    dht_pb2.Store(
                            key = key_hash,
                            obj_size=len(item.value),
                            value=item.value
                    ),
                    self.id_next
                )
                self.messages_queue.put(req)
                print(f"chave {item.key} armazenada no nó {self.id_next}")
                return
            except:
                print("Não foi possível armazenar o item")

    
    def retrieve():
        pass

def main(port_arg:int):
    port = str(port_arg)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    manager = Node(port=port)
    dht_pb2_grpc.add_DhtOperationsServicer_to_server(manager, server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"ouvindo em {port}...")

    while True:
        operation = input("O que você deseja fazer?\n")
        if operation == "store":
            key = input("Digite a chave: ")
            valor = input("Digite o valor: ")
            mockData = Item(key, valor)
            manager.store(mockData)
        
    
        server.wait_for_termination()

    # try:
    #     server.wait_for_termination()  # Aguarda o servidor gRPC ser finalizado
    # finally:
    #     manager.queue_thread.join()  # Espera o término da thread de fila
    #     print("Servidor finalizado e fila de mensagens processada.")


if __name__ == "__main__":
    port_arg = int(sys.argv[1])
    main(port_arg)
    