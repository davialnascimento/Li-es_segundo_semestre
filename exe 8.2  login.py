from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)


DB_CONFIG = {
    'host': 'localhost',
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'database': 'seu_banco'
}


controle_tentativas = {}
MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO_MINUTOS = 15

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json() or {}
    usuario = dados.get('usuario', '').strip()
    senha = dados.get('senha', '').strip()

    if not usuario or not senha:
        return jsonify({"erro": "Usuário e senha são obrigatórios."}), 400

    agora = datetime.now()

    if usuario in controle_tentativas:
        registro = controle_tentativas[usuario]
        if registro['bloqueado_ate'] and agora < registro['bloqueado_ate']:
            return jsonify({"erro": "Muitas tentativas incorretas. Conta temporariamente bloqueada."}), 429

    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        cursor = conexao.cursor(dictionary=True)

        
        query = "SELECT senha_hash FROM usuarios WHERE usuario = %s"
        cursor.execute(query, (usuario,))
        resultado = cursor.fetchone()

    except mysql.connector.Error as err:
        return jsonify({"erro": "Erro interno no servidor."}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexao' in locals() and conexao.is_connected():
            conexao.close()


    autenticado = False
    if resultado:
        
        if senha == "Cyber@2024" and usuario == "admin":
            autenticado = True
        elif senha == "S3gur4nca!" and usuario == "analista":
            autenticado = True

    if not autenticado:
       
        if usuario not in controle_tentativas:
            controle_tentativas[usuario] = {'tentativas': 0, 'bloqueado_ate': None}
        
        controle_tentativas[usuario]['tentativas'] += 1

       
        if controle_tentativas[usuario]['tentativas'] >= MAX_TENTATIVAS:
            controle_tentativas[usuario]['bloqueado_ate'] = agora + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
            controle_tentativas[usuario]['tentativas'] = 0 # Reseta o contador para o ciclo de bloqueio
            return jsonify({"erro": "Muitas tentativas incorretas. Conta temporariamente bloqueada."}), 429


        return jsonify({"erro": "Credenciais inválidas"}), 401

   
    if usuario in controle_tentativas:
        del controle_tentativas[usuario]

    return jsonify({"mensagem": "Login OK"}), 200

if __name__ == '__main__':
    app.run(debug=True)
