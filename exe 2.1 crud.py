from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError 
 
# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["seguranca"]
colecao = db["ativos"]
 
# Impede IPs duplicados
colecao.create_index("ip", unique=True)
 
# Dados iniciais
ativos = [
    {"nome": "SRV-WEB01", "tipo": "servidor", "ip": "192.168.1.10", "status": "ativo"},
    {"nome": "PC-RH03", "tipo": "estacao", "ip": "192.168.1.45", "status": "ativo"},
    {"nome": "SW-CORE01", "tipo": "switch", "ip": "192.168.1.1", "status": "inativo"},
]
 
# Insere os ativos somente se a coleção estiver vazia
if colecao.count_documents({}) == 0:
    try:
        colecao.insert_many(ativos)
        print("Ativos iniciais cadastrados!")
    except DuplicateKeyError:
        print("Existem IPs duplicados.")
 
 
# [1] Cadastrar
def cadastro():
    nome = input("Digite o nome do ativo: ")
    tipo = input("Digite o tipo do ativo: ")
    ip = input("Digite o IP: ")
    status = input("Digite o status (ativo/inativo): ")
 
    novo_ativo = {
        "nome": nome,
        "tipo": tipo,
        "ip": ip,
        "status": status
    }
 
    try:
        colecao.insert_one(novo_ativo)
        print("Ativo cadastrado com sucesso!")
 
    except DuplicateKeyError:
        print("Erro: esse IP já está cadastrado!")
 
 
# [2] Listar
def listar():
    ativos = colecao.find()
 
    print("\n--- ATIVOS CADASTRADOS ---")
 
    for ativo in ativos:
        print(
            f"Nome: {ativo['nome']} | "
            f"Tipo: {ativo['tipo']} | "
            f"IP: {ativo['ip']} | "
            f"Status: {ativo['status']}"
        )
 
 
# [3] Buscar por IP
def buscar():
    ip = input("Digite o IP que deseja buscar: ")
 
    ativo = colecao.find_one({"ip": ip})
 
    if ativo:
        print("\nAtivo encontrado:")
        print(f"Nome: {ativo['nome']}")
        print(f"Tipo: {ativo['tipo']}")
        print(f"IP: {ativo['ip']}")
        print(f"Status: {ativo['status']}")
    else:
        print("Nenhum ativo encontrado com esse IP.")
 
 
# [4] Atualizar status
def atualizar():
    ip = input("Digite o IP do ativo: ")
    novo_status = input("Digite o novo status (ativo/inativo): ")
 
    resultado = colecao.update_one(
        {"ip": ip},
        {"$set": {"status": novo_status}}
    )
 
    if resultado.matched_count > 0:
        print("Status atualizado com sucesso!")
    else:
        print("Ativo não encontrado.")
 
 
# [5] Remover
def remover():
    ip = input("Digite o IP do ativo que deseja remover: ")
 
    resultado = colecao.delete_one({"ip": ip})
 
    if resultado.deleted_count > 0:
        print("Ativo removido com sucesso!")
    else:
        print("Ativo não encontrado.")
 
 
# Menu principal
while True:
 
    print("""
========================
       MENU
========================
1 - Cadastrar ativo
2 - Listar ativos
3 - Buscar por IP
4 - Atualizar status
5 - Remover ativo
6 - Sair
========================
""")
 
    desejo = input("Insira o que deseja executar: ")
 
    if desejo == "1":
        cadastro()
 
    elif desejo == "2":
        listar()
 
    elif desejo == "3":
        buscar()
 
    elif desejo == "4":
        atualizar()
 
    elif desejo == "5":
        remover()
 
    elif desejo == "6":
        print("Programa encerrado.")
        break
 
    else:
        print("Opção inválida!")
