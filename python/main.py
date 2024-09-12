from dataclasses import dataclass
import grpc
import dht_pb2
import dht_pb2_grpc
import hashlib
from concurrent import futures
import time
import threading
import traceback
import os
import sys
import queue

class Node(dht_pb2_grpc.DhtOperationsServicer):
    def __init__(self, port:int) -> None:
        self.ip_addr:str = "127.0.0.1"
        self.porta:int   = port
        self.id:str      = f"{self.ip_addr}:{port}"
        self.id_hash:str = self.calc_hash_id(self.id)
        self.id_next:str = self.id 
        self.id_prev:str = self.id
        self.stored_items:dict = {}
        self.messages_queue = queue.Queue(maxsize=10)
        self.join()  

    def FindNext(self, request, context) -> None:
        if self.is_correct_place(request.id):
            prev_ip, prev_port = self.id_prev.split(':')
            with grpc.insecure_channel(request.joining_node.id) as channel:
                insertion_stub = dht_pb2_grpc.DhtOperationsStub(channel)
                _ = insertion_stub.SendJoiningPosition(
                    dht_pb2.JoinOk(
                        next_node=dht_pb2.NodeInfo(
                            id=self.id_hash,
                            ip_addr=self.ip_addr, 
                            port=self.port)
                        ),
                        prev_node = dht_pb2.NodeInfo(
                            id = self.calc_hash_id(self.id_prev),
                            ip_addr = prev_ip,
                            port = prev_port
                        )
                )
        else:
            with grpc.insecure_channel(self.id_next) as channel:
                joining_stub = dht_pb2_grpc.DhtOperationsStub(channel)
                _ = joining_stub.FindNext(
                    dht_pb2.Join(
                        joining_node=dht_pb2.NodeInfo(
                            id = request.joining_node.id,
                            ip_addr = request.joining_node.ip_addr, 
                            port = request.joining_node.port)
                        )
                )

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

         


    def AdjustPredJoin(self, request, context):
        return super().AdjustPredJoin(request, context)
    
    def AdjustNextLeave(self, request, context):
        return super().AdjustNextLeave(request, context)
    
    def AdjustPredLeave(self, request, context):
        return super().AdjustPredLeave(request, context)
    
    def StoreItem(self, request, context):
        return super().StoreItem(request, context)
    
    def RetrieveItem(self, request, context):
        return super().RetrieveItem(request, context)
    
    def SendItem(self, request, context):
        return super().SendItem(request, context)
    
    def SendNotFound(self, request, context):
        return super().SendNotFound(request, context)
    
    def calc_hash_id(id:str):
        return hashlib.sha256(id.encode(encoding="utf-8")).hexdigest()
    
    
    def is_correct_place(self, id_hash_inc:str) -> bool:
        # hash que quer entrar eh maior do que eu? false
        if id_hash_inc > self.id_hash:
            return False

        # sou o ultimo do anel e hash que quer entrar maior que eu? false
        if self.calc_hash_id(self.id_next) < self.id_hash and id_hash_inc > self.id_hash:
            return False

        return True


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
            if os.path.getsize(known_hosts_path) == 0:
                hosts.write(self.id)
            else:
                known_hosts_list = hosts.readlines()
                for h in known_hosts_list:
                    try:
                        with grpc.insecure_channel(h) as channel:
                            joining_stub = dht_pb2_grpc.DhtOperationsStub(channel)
                            _ = joining_stub.FindNext(dht_pb2.Join(
                                joining_node=dht_pb2.NodeInfo(
                                    id=self.id_hash,
                                    ip_addr=self.ip_addr, 
                                    port=self.port)
                                )
                            )
                            return
                    except:
                        continue
        pass

    def leave():
        pass

    def store():
        pass
    
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
    server.wait_for_termination()


if __name__ == "__main__":
    port_arg = int(sys.argv[1])
    s_thread = threading.Thread(target=main, args=(port_arg,))
    s_thread.start()
    
    s_thread.join()