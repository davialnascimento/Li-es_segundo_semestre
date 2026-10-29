from datetime import datetime
from bson import ObjectId, errors
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# Configuração da conexão com o MongoDB (ajuste a URI se necessário)
client = MongoClient("mongodb://localhost:27017/")
db = client["sec_incidents_db"]
collection = db["incidentes"]


def serialize_incidente(inc):
  """Converte o _id do MongoDB para string e formata a data."""
  if not inc:
    return None
  inc["id"] = str(inc["_id"])
  del inc["_id"]
  if isinstance(inc.get("criado_em"), datetime):
    inc["criado_em"] = inc["criado_em"].isoformat()
  return inc


@app.route("/api/incidentes", methods=["POST"])
def criar_incidente():
  dados = request.get_json()

  # Validação de campos obrigatórios
  campos_obrigatorios = ["titulo", "severidade", "ip_origem"]
  for campo in campos_obrigatorios:
    if not dados or campo not in dados:
      return jsonify({"erro": f"O campo '{campo}' é obrigatório."}), 400

  novo_incidente = {
      "titulo": dados["titulo"],
      "severidade": dados["severidade"],
      "status": dados.get("status", "aberto"),  # Padrão: 'aberto'
      "ip_origem": dados["ip_origem"],
      "criado_em": datetime.utcnow(),
  }

  resultado = collection.insert_one(novo_incidente)
  return jsonify({"id": str(resultado.inserted_id)}), 201


@app.route("/api/incidentes", methods=["GET"])
def listar_incidentes():
  incidentes = [serialize_incidente(inc) for inc in collection.find()]
  return jsonify(incidentes), 200


@app.route("/api/incidentes/<id>", methods=["GET"])
def obter_incidente(id):
  try:
    obj_id = ObjectId(id)
  except errors.InvalidId:
    return jsonify({"erro": "id inválido"}), 400

  inc = collection.find_one({"_id": obj_id})
  if not inc:
    return jsonify({"erro": "Incidente não encontrado"}), 404

  return jsonify(serialize_incidente(inc)), 200


@app.route("/api/incidentes/<id>", methods=["PUT"])
def atualizar_incidente(id):
  try:
    obj_id = ObjectId(id)
  except errors.InvalidId:
    return jsonify({"erro": "id inválido"}), 400

  dados = request.get_json()
  if not dados:
    return jsonify(
        {"erro": "Nenhum dado fornecido para a atualização."}
    ), 400

  campos_atualizacao = {}
  for campo in ["titulo", "severidade", "status", "ip_origem"]:
    if campo in dados:
      campos_atualizacao[campo] = dados[campo]

  if not campos_atualizacao:
    return jsonify({"erro": "Nenhum campo válido fornecido."}), 400

  resultado = collection.update_one({"_id": obj_id}, {"$set": campos_atualizacao})

  if resultado.matched_count == 0:
    return jsonify({"erro": "Incidente não encontrado"}), 404

  return jsonify({"mensagem": "Atualizado com sucesso"}), 200


@app.route("/api/incidentes/<id>", methods=["DELETE"])
def deletar_incidente(id):
  try:
    obj_id = ObjectId(id)
  except errors.InvalidId:
    return jsonify({"erro": "id inválido"}), 400

  resultado = collection.delete_one({"_id": obj_id})

  if resultado.deleted_count == 0:
    return jsonify({"erro": "Incidente não encontrado"}), 404

  return jsonify({"mensagem": "Removido"}), 200


if __name__ == "__main__":
  app.run(debug=True, port=5000)
