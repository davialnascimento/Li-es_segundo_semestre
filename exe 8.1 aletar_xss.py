from markupsafe import escape
from flask import Flask, request,redirect
app= Flask (__name__)
@app.route("/busca")



def busca():
    termo = request.args.get("q", "")
    return f"<h1>Resultados para {escape(termo)}</h1>"


if __name__ == "__main__":
    app.run(debug=True)
