
import sqlite3

# Criando banco de dados em memória
conexao = sqlite3.connect(":memory:")
cursor = conexao.cursor()

# Criando e populando a tabela
cursor.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
)
""")

cursor.executemany(
    "INSERT INTO usuarios (nome) VALUES (?)",
    [("Davi",), ("Ana",), ("Carlos",)]
)

conexao.commit()


# FUNÇÃO INSEGURA: concatena a entrada na query
def buscar_inseguro(nome):
    query = f"SELECT * FROM usuarios WHERE nome = '{nome}'"
    cursor.execute(query)
    return cursor.fetchall()


# FUNÇÃO SEGURA: utiliza parâmetros
def buscar_seguro(nome):
    query = "SELECT * FROM usuarios WHERE nome = ?"
    cursor.execute(query, (nome,))
    return cursor.fetchall()


# Demonstração com entrada maliciosa
entrada_maliciosa = "' OR '1'='1"

resultado_inseguro = buscar_inseguro(entrada_maliciosa)
resultado_seguro = buscar_seguro(entrada_maliciosa)

print(
    f"[INSEGURO] entrada: {entrada_maliciosa} "
    f" -> {len(resultado_inseguro)} usuários retornados (VAZAMENTO!)"
)

print(
    f"[SEGURO]   entrada: {entrada_maliciosa} "
    f" -> {len(resultado_seguro)} usuários retornados (defesa OK)"
)

print(
    "Conclusão: a query parametrizada tratou a entrada como texto literal."
)

conexao.close()
