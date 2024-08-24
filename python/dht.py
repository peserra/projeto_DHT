import dataclasses
import grpc

@dataclasses
class Item:
    # vai servir pra passar key : value pairs
    key:str
    value:str
    pass


class Node:
    # vai ter funcionadlidade de server e client
    def __init__(self) -> None:
        self.id:str = ""
        self.id_next:str = ""
        self.id_prev:str = ""
        self.stored_items:dict = {}

    def calcHash(id:str) -> str:
        return id
    
    def join(knowHostList:list):
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
        pass

    def leave():
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