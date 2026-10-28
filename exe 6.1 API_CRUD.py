from flask import Flask, jsonify, request

app = Flask(__name__)

# Armazenamento em memória
usuarios = []
id_contador = 1

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    return jsonify(usuarios), 200

@app.route('/api/usuarios/<int:user_id>', methods=['GET'])
def obter_usuario(user_id):
    usuario = next((u for u in usuarios if u['id'] == user_id), None)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(usuario), 200

@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    global id_contador
    dados = request.get_json()

    if not dados or not all(k in dados for k in ('nome', 'email', 'nivel')):
        return jsonify({"erro": "Dados incompletos"}), 400

    nome = dados['nome']
    email = dados['email']
    nivel = dados['nivel']

    # Validação do nível (entre 1 e 5)
    if not isinstance(nivel, int) or not (1 <= nivel <= 5):
        return jsonify({"erro": "nível inválido"}), 400

    # Validação do email único
    if any(u['email'] == email for u in usuarios):
        return jsonify({"erro": "email já existe"}), 400

    novo_usuario = {
        "id": id_contador,
        "nome": nome,
        "email": email,
        "nivel": nivel
    }
    usuarios.append(novo_usuario)
    id_contador += 1
    return jsonify(novo_usuario), 201

@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
    usuario = next((u for u in usuarios if u['id'] == user_id), None)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados vazios"}), 400

    if 'nivel' in dados:
        nivel = dados['nivel']
        if not isinstance(nivel, int) or not (1 <= nivel <= 5):
            return jsonify({"erro": "nível inválido"}), 400
        usuario['nivel'] = nivel

    if 'email' in dados:
        email = dados['email']
        if any(u['email'] == email and u['id'] != user_id for u in usuarios):
            return jsonify({"erro": "email já existe"}), 400
        usuario['email'] = email

    if 'nome' in dados:
        usuario['nome'] = dados['nome']

    return jsonify(usuario), 200

@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
def deletar_usuario(user_id):
    global usuarios
    usuario = next((u for u in usuarios if u['id'] == user_id), None)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    usuarios = [u for u in usuarios if u['id'] != user_id]
    return jsonify({"mensagem": "Removido"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
