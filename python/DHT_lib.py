from dataclasses import dataclass
import grpc
import dht_pb2
import dht_pb2_grpc
import hashlib
from concurrent import futures
import time
import threading
import asyncio

@dataclass
class Item:
    # vai servir pra passar key : value pairs
    key:str
    value:str

# classe que vai gerenciar a dht e nodes
class DhtManager(dht_pb2_grpc.DhtOperationsServicer):
    def __init__(self) -> None:
        self.known_hosts:list = []
    
    class Node:
        def __init__(self, ip_addr:str, port:int) -> None:
            self.id:str      = f"{ip_addr}:{port}" # gera um id aleatorio e coloca em formato de string
            self.ip_addr:str = ip_addr
            self.port:int    = port
            #self.id_hash:str = hashlib.sha256(self.id.encode(encoding="utf-8")).hexdigest()
            self.id_hash:str = str(self.port) # so para testar mesmo
            # valor padrao de um novo node eh ser seu proprio next e prev, antes de entrar na dht
            self.id_next:str = self.id 
            self.id_prev:str = self.id
            self.stored_items:dict = {}
        
        # quero estabelecer a conexao com o primeiro node da lista de nodes conhecidos
        def init_node_stub(self, node_id:str) -> dht_pb2_grpc.DhtOperationsStub:
            # cria uma conexao com o seu next para mandar a mensagem pra ele
            with grpc.insecure_channel(node_id) as channel:
                node_stub = dht_pb2_grpc.DhtOperationsStub(channel)
                return node_stub
            
        # inicializa um listener do node, com seu proprio id que escuta por 5s
        async def init_node_listening(self):
            port = str(self.port)
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            manager = DhtManager()
            dht_pb2_grpc.add_DhtOperationsServicer_to_server(manager, server)
            server.add_insecure_port("[::]:" + port)
            server.start()
            print(f"node {self.id} ouvindo: {port}")
            server.wait_for_termination(timeout=5)

    
    '''
        func deve receber o node que quer entrar e mandar infos dele para o next na dht, essa operacao deve ser chamada toda vez ate encontrar o local correto do node.
    '''
    def FindNext(self, request, context) -> None:
        print("conexao funcionou pelo menos")
        return super().FindNext(request, context)
    
    
    async def join(self, node:Node):
        '''
            - Usada no momento que quiser entrar na DHT
            - Recebe como param uma lista de nos conhecidos pela rede (pode ler de uma lista caso
              seja primeiro)
            - caso nao consiga encontar ninguem participando, ele é o primeiro
            

            - ao fim dessa funcao, devem ter sido atualizados:
                * os campos id_next e id_prev do no ingressante
                * o campo id_prev do sucessor do no ingressante
                * o campo id_next do predecessor do ingressante
            
            - devem tambem ser transferidos do sucessor os dados que o no ingressante deverá cuidar (mensagem Transfer)
        '''
        if  self.known_hosts:
            print("tinha dht, adicionando novo node")
            
            entry_node = self.known_hosts[0]
            # funcao de server do node vai ficar ouvindo por conexao
            t = asyncio.create_task(entry_node.init_node_listening())
            
            print("thread main")
            print(entry_node.id)
            node_stub = node.init_node_stub(node_id=entry_node.id)
            node_stub.FindNext(dht_pb2.Join(joining_node=dht_pb2.NodeInfo(id=node.id_hash,
                                                                           ip_addr=node.ip_addr, port=node.port)))
            await t
            if len(self.known_hosts) == 1:
                # node ingressante escuta
                node.init_node_listening()

                # 
        
        # adiciona na lista de hosts conhecidos da dht
        self.known_hosts.append(node)

    def leave(self, node:Node):
        '''
            - Usada para sair da rede
            
            - Ao fim dessa chamada:
                * ponteiros dos vizinhos devem ter sido devidamente atualizados
                * conteudo deve ter sido repassado ao no sucessor (mensagem Transfer)
        '''
        pass

    def store(self, key:str ,value:str):
        '''
            - Armazena o 'value' utilziando a 'key' no dicionario stored_items do no

            - o item deve ser armazenado no no responsavel pelo intervalo que contem valor 
            calcHash(key)
        '''
        pass

    def retrieve(self, key:str):
        '''
            - Busca a 'key' na DHT e retorna seu valor, caso presente na DHT
        '''
        pass

    pass
        
    

def CreateDhtNode(ip_addr:str, port:int) -> DhtManager.Node:
    return DhtManager.Node(ip_addr=ip_addr, port=port)