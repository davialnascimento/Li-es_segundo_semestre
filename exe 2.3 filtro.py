from pymongo import MongoClient

# Exemplo de conexão e definição da coleção (ajuste conforme seu ambiente)
client = MongoClient("mongodb://localhost:27017/")
db = client["seu_banco"]
colecao = db["eventos"]

def consultar(fonte=None, tipo=None, ip=None, desde=None):
    # 1. Começa com um dicionário de filtro vazio
    filtro = {}
    
    # 2. Adiciona as chaves dinamicamente apenas se o parâmetro não for None
    if fonte is not None:
        filtro["fonte"] = fonte
        
    if tipo is not None:
        filtro["tipo"] = tipo
        
    if ip is not None:
        # Nota: Ajuste para "ip_origem" caso tenha utilizado esse nome no exercício anterior
        filtro["ip"] = ip  
        
    if desde is not None:
        filtro["timestamp"] = {"$gte": desde}
        
    # 3. Executa a consulta no MongoDB e ordena por timestamp (1 para ascendente)
    resultados = colecao.find(filtro).sort("timestamp", 1)
    
    # 4. Retorna como uma lista de documentos
    return list(resultados)
