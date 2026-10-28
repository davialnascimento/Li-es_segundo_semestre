import re
from flask import Flask, jsonify, request

app = Flask(__name__)


def verificar_senha(senha):
  """Função reaproveitada para analisar os critérios e a força da senha."""
  if not isinstance(senha, str):
    return None, None

  # Critérios de validação
  tamanho_min = len(senha) >= 8
  maiuscula = any(c.isupper() for c in senha)
  minuscula = any(c.islower() for c in senha)
  numero = any(c.isdigit() for c in senha)
  especial = bool(
      re.search(r'[^A-Za-z0-9]', senha)
  )  # Caractere especial genérico

  criterios = {
      "tamanho_min": tamanho_min,
      "maiuscula": maiuscula,
      "minuscula": minuscula,
      "numero": numero,
      "especial": especial,
  }

  # Cálculo simples da força com base nos critérios atendidos
  atendidos = sum(1 for v in criterios.values() if v)

  if atendidos == 5:
    forca = "Muito forte"
  elif atendidos == 4:
    forca = "Forte"
  elif atendidos == 3:
    forca = "Média"
  elif atendidos >= 1:
    forca = "Fraca"
  else:
    forca = "Muito fraca"

  return forca, criterios


@app.route("/api/analisar-senha", methods=["POST"])
def analisar_senha_endpoint():
  # Tenta obter o JSON da requisição com segurança
  dados = request.get_json(silent=True)

  # Validação: corpo ausente ou campo 'senha' faltando/inválido
  if not dados or "senha" not in dados or not isinstance(dados["senha"], str):
    return jsonify({"erro": "campo 'senha' obrigatório"}), 400

  senha = dados["senha"]
  forca, criterios = verificar_senha(senha)

  return jsonify({"forca": forca, "criterios": criterios}), 200


if __name__ == "__main__":
  app.run(debug=True, port=5000)
