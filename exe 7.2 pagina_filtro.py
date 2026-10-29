
from flask import Flask, request, jsonify
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# Conexão com o MongoDB
cliente = MongoClient("mongodb://localhost:27017/")
banco = cliente["seguranca"]
incidentes = banco["incidentes"]

# Popula 15 incidentes de exemplo
def popular_incidentes():
    incidentes.delete_many({})

    dados = [
        ("Tentativa de invasão", "critica", "aberto"),
        ("Ataque de força bruta", "alta", "aberto"),
        ("SQL Injection", "critica", "em_andamento"),
        ("Port scan", "media", "fechado"),
        ("Tentativa de phishing", "alta", "aberto"),
        ("Acesso suspeito", "baixa", "fechado"),
        ("Malware detectado", "critica", "aberto"),
        ("Falha de autenticação", "media", "em_andamento"),
        ("XSS detectado", "alta", "aberto"),
        ("Vazamento de dados", "critica", "em_andamento"),
        ("Acesso não autorizado", "alta", "fechado"),
        ("Tráfego suspeito", "media", "aberto"),
        ("Senha comprometida", "baixa", "aberto"),
        ("Exploração de vulnerabilidade", "critica", "aberto"),
        ("Atividade anormal", "media", "fechado")
    ]

    agora = datetime.now(timezone.utc)

    documentos = [
        {
            "titulo": titulo,
            "severidade": severidade,
            "status": status,
            "criado_em": agora - timedelta(minutes=i)
        }
        for i, (titulo, severidade, status) in enumerate(dados)
    ]

    incidentes.insert_many(documentos)


@app.route("/api/incidentes", methods=["GET"])
def listar_incidentes():
    
  try:
        pagina = int(request.args.get("pagina", 1))
        tamanho = int(request.args.get("tamanho", 10))
    except ValueError:
        return jsonify({
            "erro": "pagina e tamanho devem ser números inteiros"
        }), 400

    if pagina < 1 or tamanho < 1 or tamanho > 100:
        return jsonify({
            "erro": "pagina deve ser >= 1 e tamanho deve estar entre 1 e 100"
        }), 400

    filtro = {}

    severidade = request.args.get("severidade")
    status = request.args.get("status")

    severidades_validas = {"baixa", "media", "alta", "critica"}
    status_validos = {"aberto", "em_andamento", "fechado"}

    if severidade:
        if severidade not in severidades_validas:
            return jsonify({
                "erro": "severidade inválida",
                "valores_aceitos": sorted(severidades_validas)
            }), 400

        filtro["severidade"] = severidade

    if status:
        if status not in status_validos:
            return jsonify({
                "erro": "status inválido",
                "valores_aceitos": sorted(status_validos)
            }), 400

        filtro["status"] = status

    # Ordena pelos mais recentes e aplica paginação
    deslocamento = (pagina - 1) * tamanho

    consulta = (
        incidentes.find(filtro, {"_id": 0})
        .sort("criado_em", DESCENDING)
        .skip(deslocamento)
        .limit(tamanho)
    )

    resultados = list(consulta)

    # Converte datas para JSON
    for item in resultados:
        if isinstance(item.get("criado_em"), datetime):
            item["criado_em"] = item["criado_em"].isoformat()

    total = incidentes.count_documents(filtro)

    return jsonify({
        "pagina": pagina,
        "tamanho": tamanho,
        "total": total,
        "total_paginas": (total + tamanho - 1) // tamanho,
        "incidentes": resultados
    })


if __name__ == "__main__":
    popular_incidentes()
    app.run(debug=True)

              
