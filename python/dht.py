from dataclasses import dataclass
import grpc
import dht_pb2
import dht_pb2_grpc

@dataclass
class Item:
    # vai servir pra passar key : value pairs
    key:int
    value:str
    pass


class Node:
    
    def __init__(self, ip_addr:str, port:int) -> None:
        self.id:str      = f"{ip_addr}:{port}" # gera um id aleatorio e coloca em formato de string
        self.ip_addr:str = ip_addr
        self.port:int    = port
        self.id_next:str = ""
        self.id_prev:str = ""
        self.stored_items:dict = {}
    

# classe que vai gerenciar a dht e nodes
class Dht(dht_pb2_grpc.DhtOperations):
    def __init__(self) -> None:
        self.known_hosts:list = []
    
    def calcHash(id:str) -> str:
        return id
    
    def join(self, node:Node):
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
        if not self.known_hosts:
            print("nao tinha nenhum")
            node.id_next = node.id
            node.id_prev = node.id
        else:
            print("tinha algum")
            existing_node:Node = self.known_hosts[0]
            node.id_next = existing_node.id
            existing_node.id_prev = node.id
        
        self.known_hosts.append(node)
        pass

    def leave(self, node:Node):
        '''
            - Usada para sair da rede
            
            - Ao fim dessa chamada:
                * ponteiros dos vizinhos devem ter sido devidamente atualizados
                * conteudo deve ter sido repassado ao no sucessor (mensagem Transfer)
        '''
        pass

    def store(key:str ,value:str):
        '''
            - Armazena o 'value' utilziando a 'key' no dicionario stored_items do no

            - o item deve ser armazenado no no responsavel pelo intervalo que contem valor 
            calcHash(key)
        '''
        pass

    def retrieve(key:str):
        '''
            - Busca a 'key' na DHT e retorna seu valor, caso presente na DHT
        '''
        pass

    pass
        
    
    pass

# class DhtServer(dht_pb2.DhtOperations):
#     def __init__(self) -> None:
#         self.network: list[Node] = [Node]

#     def join_network(self, request: dht_pb2.JOIN) -> dht_pb2.JOIN_OK:
#         new_node = request
#         self.network.append(new_node)

#         if len(self.network) == 0:
#             response = dht_pb2.JOIN_OK(new_node, None, None)
#         elif len(self.network) == 1:
#             predecessor = self.network[1]
#             response = dht_pb2.JOIN_OK(new_node, predecessor, None)
#         else:
#             predecessor = self.network[-1]
#             response = dht_pb2.JOIN_OK(new_node, predecessor, None)


def CreateDhtNode(ip_addr:str, port:int) -> Node:
    return Node(ip_addr, port)