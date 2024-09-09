from dataclasses import dataclass
import grpc
import dht_pb2
import dht_pb2_grpc
import hashlib
from concurrent import futures
import time
import threading
import asyncio
import traceback

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
            self.id:str      = f"{ip_addr}:{port}" 
            self.ip_addr:str = ip_addr
            self.port:int    = port
            #self.id_hash:str = hashlib.sha256(self.id.encode(encoding="utf-8")).hexdigest()
            self.id_hash:str = str(self.port) # so para testar mesmo
            # valor padrao de um novo node eh ser seu proprio next e prev, antes de entrar na dht
            self.id_next:str = self.id 
            self.id_prev:str = self.id
            self.stored_items:dict = {}
            self.ready_event = asyncio.Event()
        
        # quero estabelecer a conexao com o primeiro node da lista de nodes conhecidos
        async def init_node_stub(self, node_id:str):
            # cria uma conexao com o seu next para mandar a mensagem pra ele
            channel = grpc.insecure_channel(node_id)
            node_stub = dht_pb2_grpc.DhtOperationsStub(channel)
            print(f"stub criado no canal {node_id}")
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
            self.ready_event.set()
            try:
                await server.wait_for_termination()
            except asyncio.CancelledError:
                print(f"listener de {self.id} fechado")

    
    '''
        func deve receber o node que quer entrar e mandar infos dele para o next na dht, essa operacao deve ser chamada toda vez ate encontrar o local correto do node.
    '''
    def FindNext(self, request, context) -> None:
        print("conexao funcionou pelo menos")
        return super().FindNext(request, context)
    
    
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
    async def join(self, node:Node):
        if self.known_hosts:
            print("tinha dht, adicionando novo node")
            
            entry_node = self.known_hosts[0]
            # funcao de server do node vai ficar ouvindo por conexao
            # esta ouvindo em "localhost:1234"
            t = asyncio.create_task(entry_node.init_node_listening())
            await entry_node.ready_event.wait()
            print("thread main")
            try:
                if len(self.known_hosts) == 1:
                    # proximo eh sempre o primeiro node
                    print(entry_node.id)
                    # cria um stub que esta tentando se conectar com localhost:1234
                    node_stub = await node.init_node_stub(node_id=entry_node.id)
                    print("RETORNOU O STUB")
                    node_stub.FindNext(dht_pb2.Join(joining_node=dht_pb2.NodeInfo(id=node.id_hash,
                                                                           ip_addr=node.ip_addr, port=node.port)))
                    
            except Exception as e:
                print(f"Erro ao chamar a funcao FindNext: {e}")
                traceback.print_exc()  # Mostra o stack trace completo para ajudar a identificar o problema
        
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

    def _is_responsible_for_key(self, node: Node, key_hash: str) -> bool:
        '''
        Verifica se o nó é responsável por armazenar a chave com o hash fornecido.
        '''
        # O nó é responsável se o hash da chave estiver entre o ID do nó atual e o ID do seu próximo nó
        if node.id_hash < key_hash <= node.id_next:
            return True
        elif node.id_hash > node.id_next:  # Quando o ID atual é maior que o próximo (final da faixa circular)
            return key_hash > node.id_hash or key_hash <= node.id_next
        return False

    def store(self, item: Item):
        '''
            - Armazena o 'value' utilziando a 'key' no dicionario stored_items do no

            - o item deve ser armazenado no no responsavel pelo intervalo que contem valor 
            calcHash(key)
        '''
        # Calcula o hash da chave
        # key_hash = hashlib.sha256(item.key.encode(encoding="utf-8")).hexdigest()
        key_hash = str(item.key) # so para testar mesmo

        # Obtém o nó atual
        current_node = self.known_hosts[-1]

        # Verifica se o nó atual é responsável pelo intervalo da chave
        if self._is_responsible_for_key(current_node, key_hash):
            # Armazena o item localmente
            print(f"Armazenando chave {item.key} no nó {current_node.id}")
            current_node.stored_items[item.key] = item.value
        else:
            # Caso contrário, passa a solicitação ao próximo nó
            print(f"Encaminhando chave {item.key} para o próximo nó")
            next_node_stub = current_node.init_node_stub(current_node.id_next)
            next_node_stub.StoreItem(dht_pb2.Store(key=item.key, obj_size=len(item.value), value=item.value.encode()))


    def retrieve(self, key:str):
        '''
            - Busca a 'key' na DHT e retorna seu valor, caso presente na DHT
        '''
            # Calcula o hash da chave
        key_hash = hashlib.sha256(key.encode(encoding="utf-8")).hexdigest()

        # Obtém o nó atual
        current_node = self.known_hosts[-1]

        # Verifica se o nó atual é responsável pelo intervalo da chave
        if self._is_responsible_for_key(current_node, key_hash):
            # Verifica se a chave existe no nó
            if key in current_node.stored_items:
                # Retorna o valor armazenado
                value = current_node.stored_items[key]
                print(f"Chave {key} encontrada no nó {current_node.id}. Valor: {value}")
                return value
            else:
                # Se a chave não for encontrada, envia uma mensagem de NotFound
                print(f"Chave {key} não encontrada no nó {current_node.id}")
                return None  # ou lança uma exceção, dependendo do caso
        else:
            # Encaminha a solicitação para o próximo nó
            print(f"Encaminhando solicitação da chave {key} para o próximo nó")
            next_node_stub = current_node.init_node_stub(current_node.id_next)
            response = next_node_stub.RetrieveItem(dht_pb2.Retrieve(key=key, searching_node=dht_pb2.NodeInfo(
                id=current_node.id_hash, ip_addr=current_node.ip_addr, port=current_node.port)))
            
            if response.HasField("Ok"):
                # Retorna o valor recebido da resposta
                return response.value.decode()
            else:
                print(f"Chave {key} não encontrada em toda a DHT")
                return None

            

        
    

def CreateDhtNode(ip_addr:str, port:int) -> DhtManager.Node:
    return DhtManager.Node(ip_addr=ip_addr, port=port)