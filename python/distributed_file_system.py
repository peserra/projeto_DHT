import DHT_lib as DHT
import asyncio
import hashlib
import os

'''
 Classe para gerenciar o sistema de arquivos distribuído
 Ela utiliza o hash do nome do arquivo para distribuir o arquivo pelos nós da DHT
 Para este projeto, não foi implementanda a lógica de replicar arquivos em múltiplos nós da DHT, 
 e o balanceamento de carga para não sobrecarregar nenhum nó
'''

class DistributedFileSystem:
    def __init__(self, dht_instance):
        self.dht_instance = dht_instance

    def _hash_filename(self, filename):
        # Gera um hash para o nome do arquivo
        return hashlib.sha1(filename.encode()).hexdigest()

    async def store_file(self, filename, content):
        # Armazena o arquivo no DHT usando o hash do nome do arquivo
        file_hash = self._hash_filename(filename)
        print(f"Armazenando arquivo '{filename}' com hash: {file_hash}")
        
        item = DHT.Item(key=file_hash, value=content)
        await self.dht_instance.store(item)
        print(f"Arquivo '{filename}' armazenado com sucesso.")

    async def retrieve_file(self, filename):
        # Recupera o arquivo do DHT usando o hash do nome do arquivo
        file_hash = self._hash_filename(filename)
        print(f"Recuperando arquivo '{filename}' com hash: {file_hash}")
        try:
            content = await self.dht_instance.retrieve(file_hash)
            if content:
                print(f"Arquivo '{filename}' recuperado com sucesso.")
                return content
            else:
                print(f"Arquivo '{filename}' não encontrado.")
        except Exception as e:
            print(f"Erro ao recuperar arquivo '{filename}': {e}")
        return None

    async def delete_file(self, filename):
        # Remove o arquivo da DHT usando o hash do nome do arquivo
        file_hash = self._hash_filename(filename)
        print(f"Removendo arquivo '{filename}' com hash: {file_hash}")
        try:
            await self.dht_instance.delete(file_hash)  # Assumindo que existe um método de remoção
            print(f"Arquivo '{filename}' removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover arquivo '{filename}': {e}")

async def main():
    dht_instance = DHT.DhtManager()

    # Cria e adiciona nós à DHT
    print("Criando e adicionando nó de entrada...")
    node_init = DHT.CreateDhtNode(ip_addr="127.0.0.1", port=1234)
    await dht_instance.join(node=node_init)
    print(f"Nó de entrada criado: {node_init.id_hash}")

    print("Criando e adicionando segundo nó...")
    node2 = DHT.CreateDhtNode(ip_addr="127.0.0.1", port=1235)
    await dht_instance.join(node=node2)
    print(f"Segundo nó criado: {node2.id_hash}")

    # Inicializa o sistema de arquivos distribuído
    dfs = DistributedFileSystem(dht_instance)

    # Exemplo de armazenamento de arquivos
    await dfs.store_file("arquivo1.txt", "Conteúdo do arquivo 1")
    await dfs.store_file("arquivo2.txt", "Conteúdo do arquivo 2")

    # Exemplo de recuperação de arquivos
    content1 = await dfs.retrieve_file("arquivo1.txt")
    if content1:
        print(f"Conteúdo do arquivo 1: {content1}")

    content2 = await dfs.retrieve_file("arquivo2.txt")
    if content2:
        print(f"Conteúdo do arquivo 2: {content2}")

    # Exemplo de remoção de arquivos
    await dfs.delete_file("arquivo1.txt")

    # Testa a saída do nó da DHT
    print("Saindo da DHT...")
    await dht_instance.leave(node=node_init)
    print("Nó saiu da DHT.")
    print("teste")
    
if __name__ == "__main__":
    asyncio.run(main())
