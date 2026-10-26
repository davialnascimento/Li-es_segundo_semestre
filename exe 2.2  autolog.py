import re
import sys
from datetime import datetime
 
from pymongo import MongoClient
 
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "seguranca"
COLLECTION = "logs_auth"
ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else "logs.txt"
 
# 2025-02-20 08:15:01 FAIL usuario=admin ip=185.220.101.1
LINHA_RE = re.compile(
    r"^(?P<data>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<status>OK|FAIL)\s+"
    r"usuario=(?P<usuario>\S+)\s+"
    r"ip=(?P<ip>\S+)\s*$"
)
 
 
def normalizar(linha: str) -> dict | None:
    """Transforma uma linha de log em um documento. Retorna None se inválida."""
    m = LINHA_RE.match(linha.strip())
    if not m:
        return None
    return {
        "timestamp": datetime.strptime(m["data"], "%Y-%m-%d %H:%M:%S"),
        "status": m["status"],
        "sucesso": m["status"] == "OK",
        "usuario": m["usuario"],
        "ip": m["ip"],
    }
 
 
def carregar_documentos(caminho: str) -> tuple[list[dict], list[str]]:
    docs, invalidas = [], []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            doc = normalizar(linha)
            if doc:
                docs.append(doc)
            else:
                invalidas.append(linha.rstrip())
    return docs, invalidas
 
 
def main() -> None:
    docs, invalidas = carregar_documentos(ARQUIVO)
    print(f"{len(docs)} linhas válidas, {len(invalidas)} ignoradas")
    for linha in invalidas:
        print(f"  ignorada: {linha}")
 
    client = MongoClient(MONGO_URI)
    col = client[DB_NAME][COLLECTION]
 
    # Limpa a coleção para a execução ser repetível (remova se não quiser isso)
    col.delete_many({})
 
    if docs:
        resultado = col.insert_many(docs)
        print(f"{len(resultado.inserted_ids)} documentos inseridos\n")
 
    pipeline = [
        {"$match": {"status": "FAIL"}},
        {
            "$group": {
                "_id": "$ip",
                "falhas": {"$sum": 1},
                "usuarios_tentados": {"$addToSet": "$usuario"},
                "primeira_falha": {"$min": "$timestamp"},
                "ultima_falha": {"$max": "$timestamp"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "ip": "$_id",
                "falhas": 1,
                "qtd_usuarios": {"$size": "$usuarios_tentados"},
                "usuarios_tentados": 1,
                "primeira_falha": 1,
                "ultima_falha": 1,
            }
        },
        {"$sort": {"falhas": -1, "ip": 1}},
        {"$limit": 10},
    ]
 
    print(f"{'IP':<18}{'FALHAS':>7}{'USUÁRIOS':>10}  USUÁRIOS TENTADOS")
    print("-" * 70)
    for r in col.aggregate(pipeline):
        usuarios = ", ".join(sorted(r["usuarios_tentados"]))
        print(f"{r['ip']:<18}{r['falhas']:>7}{r['qtd_usuarios']:>10}  {usuarios}")
 
    client.close()
 
 
if __name__ == "__main__":
    main()
