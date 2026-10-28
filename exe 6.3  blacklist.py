import ipaddress
from flask import Flask, jsonify

app = Flask(__name__)

# Blacklist fornecida
blacklist = {"185.220.101.1", "45.33.32.156", "91.240.118.172"}


@app.route("/api/checar-ip/<ip>", methods=["GET"])
def checar_ip(ip):
  try:
    # Valida o IP (lança ValueError se o formato for inválido)
    ip_obj = ipaddress.ip_address(ip)
  except ValueError:
    return jsonify({"erro": "IP inválido"}), 400

  # Verifica se o IP está na blacklist
  na_blacklist = str(ip_obj) in blacklist

  # Classifica o tipo usando a propriedade nativa do módulo ipaddress
  tipo = "privado" if ip_obj.is_private else "publico"

  return (
      jsonify({"ip": str(ip_obj), "na_blacklist": na_blacklist, "tipo": tipo}),
      200,
  )


if __name__ == "__main__":
  app.run(debug=True)
