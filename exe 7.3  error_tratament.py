import os
import re
from contextlib import contextmanager
 
import mysql.connector
from flask import Flask, jsonify, request
from mysql.connector import errorcode
from werkzeug.exceptions import HTTPException
 
app = Flask(__name__)
app.json.ensure_ascii = False 
 
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "app"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "app_db"),
    "charset": "utf8mb4",
    "connection_timeout": 3,  
 
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COLUNAS = "id, nome, email, criado_em"
 
 
@contextmanager
def get_cursor(commit=False):
    """Abre conexão, entrega um cursor e garante o fechamento.
    Se ocorrer erro antes do commit, fechar a conexão descarta a transação."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(dictionary=True)
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()
 
 
def serializar(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "criado_em": row["criado_em"].isoformat(),
    }
 
 

class ErroValidacao(Exception):
    pass
 
 
def validar_corpo():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroValidacao("o corpo deve ser um objeto JSON válido")
 
    faltando = [c for c in ("nome", "email") if c not in dados]
    if faltando:
        raise ErroValidacao("campos obrigatórios ausentes: " + ", ".join(faltando))
 
    nome, email = dados["nome"], dados["email"]
    if not isinstance(nome, str) or not (1 <= len(nome.strip()) <= 100):
        raise ErroValidacao("nome deve ser um texto de 1 a 100 caracteres")
    if not isinstance(email, str):
        raise ErroValidacao("email inválido")
 
    email = email.strip().lower()
    if len(email) > 255 or not EMAIL_RE.match(email):
        raise ErroValidacao("email inválido")
 
    return nome.strip(), email
 
 
def inteiro_param(nome, padrao, minimo, maximo):
    bruto = request.args.get(nome)
    if bruto is None:
        return padrao
    try:
        valor = int(bruto)
    except ValueError:
        raise ErroValidacao(f"{nome} deve ser um inteiro")
    if not (minimo <= valor <= maximo):
        raise ErroValidacao(f"{nome} deve estar entre {minimo} e {maximo}")
    return valor
 
 

@app.post("/api/usuarios")
def criar_usuario():
    nome, email = validar_corpo()
    with get_cursor(commit=True) as cur:
        cur.execute("INSERT INTO usuarios (nome, email) VALUES (%s, %s)", (nome, email))
        novo_id = cur.lastrowid
        cur.execute(f"SELECT {COLUNAS} FROM usuarios WHERE id = %s", (novo_id,))
        row = cur.fetchone()
    resp = jsonify(serializar(row))
    resp.status_code = 201
    resp.headers["Location"] = f"/api/usuarios/{novo_id}"
    return resp
 
 
@app.get("/api/usuarios")
def listar_usuarios():
    limite = inteiro_param("limite", 50, 1, 100)
    offset = inteiro_param("offset", 0, 0, 10**9)
    with get_cursor() as cur:
        cur.execute(
            f"SELECT {COLUNAS} FROM usuarios ORDER BY id LIMIT %s OFFSET %s",
            (limite, offset),
        )
        rows = cur.fetchall()
    return jsonify([serializar(r) for r in rows])
 
 
@app.get("/api/usuarios/<int:uid>")
def obter_usuario(uid):
    with get_cursor() as cur:
        cur.execute(f"SELECT {COLUNAS} FROM usuarios WHERE id = %s", (uid,))
        row = cur.fetchone()
    if row is None:
        return jsonify(erro="usuário não encontrado"), 404
    return jsonify(serializar(row))
 
 
@app.put("/api/usuarios/<int:uid>")
def atualizar_usuario(uid):
    nome, email = validar_corpo()
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE usuarios SET nome = %s, email = %s WHERE id = %s",
            (nome, email, uid),
        )
        # rowcount vale 0 também quando os valores não mudam; por isso relemos a linha
        cur.execute(f"SELECT {COLUNAS} FROM usuarios WHERE id = %s", (uid,))
        row = cur.fetchone()
    if row is None:
        return jsonify(erro="usuário não encontrado"), 404
    return jsonify(serializar(row))
 
 
@app.delete("/api/usuarios/<int:uid>")
def remover_usuario(uid):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
        apagados = cur.rowcount
    if apagados == 0:
        return jsonify(erro="usuário não encontrado"), 404
    return "", 204
 
 

@app.errorhandler(ErroValidacao)
def erro_400(e):
    return jsonify(erro=str(e)), 400
 
 
@app.errorhandler(mysql.connector.Error)
def erro_banco(e):
    # email é a única chave única da tabela, então 1062 = email duplicado
    if getattr(e, "errno", None) == errorcode.ER_DUP_ENTRY:
        return jsonify(erro="email já cadastrado"), 409
    # Detalhes (host, usuário, query, traceback) vão só para o log do servidor.
    app.logger.error("falha no banco de dados", exc_info=e)
    return jsonify(erro="serviço indisponível"), 500
 
 
@app.errorhandler(HTTPException)
def erro_http(e):
    msgs = {404: "recurso não encontrado", 405: "método não permitido"}
    return jsonify(erro=msgs.get(e.code, "requisição inválida")), e.code
 
 
@app.errorhandler(Exception)
def erro_inesperado(e):
    app.logger.error("erro inesperado", exc_info=e)
    return jsonify(erro="erro interno"), 500
 
 
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
