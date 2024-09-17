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

class DHTClient:
    def __init__(self, address: str):
        self.channel = grpc.insecure_channel(address)
        self.stub = dht_pb2_grpc.DhtOperationsStub(self.channel)
    
    '''
    Envia uma solicitação para o servidor para adicionar um novo nó à rede DHT.
    Cria uma mensagem Join contendo informações do nó que deseja ingressar.
    Chama o método FindNext no servidor.
    imprime a resposta recebida.
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
        print("Join response:", response)
    
    '''
    quando o nó sair, ele precisa notificar o seu predecessor e sucessor
    para que possam atualizar suas referências e assumir a responsabilidade pelas chaves
    que o nó estava gerenciado
    - Notifica o predecessor e o sucessor que o nó está saindo.
    - Envia uma mensagem Void para ambos os métodos AdjustPredLeave e AdjustNextLeave.
    - Imprime mensagens de confirmação ou erro.

    '''
    def leave(self):
        try:
            request = dht_pb2.Void()
            self.stub.AdjustPredLeave(request)
            print("Leave notification sent to predecessor.")
        except grpc.RpcError as e:
            print(f"Error while notifying predecessor: {e}")
        
        # Notify successor to adjust its predecessor pointer
        try:
            request = dht_pb2.Void()
            self.stub.AdjustNextLeave(request)
            print("Leave notification sent to successor.")
        except grpc.RpcError as e:
            print(f"Error while notifying successor: {e}")

    '''
    Armazena um item na DHT
    Calcula o hash da chave usando SHA-256.
    Cria uma mensagem Store com a chave, o hash da chave, o tamanho do valor e o valor em si.
    Chama o método StoreItem no servidor.
    Imprime a resposta recebida.
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
        print("Store response:", response)
    
    '''
    Recupera um item da DHT
    Calcula o hash da chave.
    Cria uma mensagem Store com a chave e o hash da chave.
    Chama o método RetrieveItem no servidor.
    Imprime a resposta recebida.
    '''
    def retrieve(self, key: str):
        key_hash = hashlib.sha256(key.encode(encoding="utf-8")).hexdigest()
        request = dht_pb2.Store(key=key, key_hash=key_hash)
        response = self.stub.RetrieveItem(request)
        print("Retrieve response:", response)



def main():
    '''
    Verifica se o número correto de argumentos foi fornecido (ação, IP, e porta).
    Se não, exibe uma mensagem de uso e encerra o programa.
    '''
    if len(sys.argv) != 4:
        print("Usage: python dht_app.py <action> <ip> <port>")
        sys.exit(1)

    action = sys.argv[1].lower()
    ip = sys.argv[2]
    port = int(sys.argv[3])

    client = DHTClient(f"{ip}:{port}")

    if action == "join":
        client.join(ip, port)
    elif action == "store":
        key = input("Enter key: ")
        value = input("Enter value: ")
        client.store(key, value)
    elif action == "retrieve":
        key = input("Enter key: ")
        client.retrieve(key)
    elif action == "leave":
        client.leave()
    else:
        print("Unknown action. Use 'join', 'store', 'retrieve', or 'leave'.")

if __name__ == "__main__":
    main()
