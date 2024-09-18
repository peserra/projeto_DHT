'''
É o cliente que se comunica com a rede DHT via gRPC. Ele permite que nós se juntem ou saiam da rede,
e também que clientes armazenem ou recuperem itens. Os métodos (FindNext, StoreItem, RetrieveItem) são
chamados para realizar as operações distribuídas na DHT.
'''

import hashlib
import grpc
import dht_pb2
import dht_pb2_grpc
import sys
from dataclasses import dataclass

@dataclass
class Item:
    key: str
    value: str

'''
- Cria um canal inseguro para o endereço fornecido (para comunicação) e
- Cria um "stub" gRPC que funciona como proxy p/chamadas remotas para o servidor
'''

class DHTClient:
    def __init__(self, address: str):
        self.channel = grpc.insecure_channel(address)
        self.stub = dht_pb2_grpc.DhtOperationsStub(self.channel)
    
    '''
    Como solicitado no enunciado, o join é responsável por inserir um nó na DHT.
    No request ele cria uma mensagem do tipo Join com as informações do nó que deseja ingressar
    No findnext faz uma chamada para o método passando a requisição join, o servidor tentará
    encontrar a posição correta na DHT para este nó se conectar
    '''
    def join(self, ip_addr: str, port: int):
        request = dht_pb2.Join(
            joining_node=dht_pb2.NodeInfo(
                id=f"{ip_addr}:{port}",
                ip_addr=ip_addr,
                port=port
            )
        )
        response = self.stub.FindNext(request)
        print("Resposta do Join:", response)
    
    '''
    Método responsável para o nó sair da DHT. 
    Ele basicamente notificada o predecessor e o sucessor para que atualizem suas referências
    - O método chama AdjustPredLeave, que ajusta a referência do predecessor. Em seguida, 
    chama AdjustNextLeave, que ajusta a referência do sucessor.
    '''
    def leave(self):
        try:
            request = dht_pb2.Void()
            self.stub.AdjustPredLeave(request)
            print("Leave notificação enviada ao predecessor.")
        except grpc.RpcError as e:
            print(f"Erro ao notificar o predecessor: {e}")
        
        try:
            request = dht_pb2.Void()
            self.stub.AdjustNextLeave(request)
            print("Leave notificação enviada ao successor.")
        except grpc.RpcError as e:
            print(f"Erro ao notificar o successor: {e}")

    '''
    Método responsável por armazenar um item na DHT.
    - key_hash: Calcula o hash da chave usando o algoritmo SHA-256, 
    - request: Cria uma mensagem do tipo Store contendo a chave, o hash da chave, o tamanho do valor e o valor em si
    - response: Faz chamada para o servidor DHT para armazenar o item (StoreItem)
    '''
    def store(self, key: str, value: str):
        key_hash = hashlib.sha256(key.encode(encoding="utf-8")).hexdigest()
        request = dht_pb2.Store(
            key=key,
            key_hash=key_hash,
            obj_size=len(value),
            value=value
        )
        response = self.stub.StoreItem(request)
        print("Store resposta:", response)
    
    '''
    Método responsável por recuperar um item armazenado na DHT com base em sua chave.
    - key_hash: Calcula o hash da chave usando o algoritmo SHA-256 p/identificar qual nó é responsável pelo armazenamento do item
    - request: Cria uma mensagem do tipo Store contendo a chave e o hash da chave.
    - response: Faz uma chamada gRPC para o servidor DHT para buscar o item 
    '''
    def retrieve(self, key: str):
        key_hash = hashlib.sha256(key.encode(encoding="utf-8")).hexdigest()
        request = dht_pb2.Store(key=key, key_hash=key_hash)
        response = self.stub.RetrieveItem(request)
        print("Retrieve resposta:", response)

def main():
    #Verifica se o número correto de argumentos foi passado (ação, IP, e porta).
    if len(sys.argv) != 4:
        print("Utilize: python dht_app.py <acao> <ip> <porta>")
        sys.exit(1)

    action = sys.argv[1].lower()
    ip = sys.argv[2]
    port = int(sys.argv[3])

    #Cria um cliente DHT, conectando-se ao nó DHT no IP e porta fornecidos.
    client = DHTClient(f"{ip}:{port}")

    '''
    Dependendo da ação fornecida na linha de comando (join, store, retrieve ou leave),
    o programa chamada o método correspondente, de acordo com os seguintes parametros:
    - Join: Conecta um novo nó à DHT.
    - Store: Armazena um item (chave-valor) na DHT.
    - Retrieve: Recupera um item da DHT usando sua chave.
    - Leave: Remove o nó da DHT, notificando seus vizinhos.
    '''
    if action == "join":
        client.join(ip, port)
    elif action == "store":
        key = input("Digite a chave: ")
        value = input("Digite o valor: ")
        client.store(key, value)
    elif action == "retrieve":
        key = input("Digite a chave: ")
        client.retrieve(key)
    elif action == "leave":
        client.leave()
    else:
        print("Ação não encontrada. Use 'join', 'store', 'retrieve', ou 'leave'.")

if __name__ == "__main__":
    main()
