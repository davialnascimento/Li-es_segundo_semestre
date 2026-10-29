
from openai import OpenAI, APIError, RateLimitError, APITimeoutError

client = OpenAI()

# Histórico da conversa
historico = [
    {
        "role": "system",
        "content": (
            "Você é um assistente especializado em segurança cibernética. "
            "Responda em português, de forma clara e didática. "
            "Considere o contexto das mensagens anteriores."
        )
    }
]

print("=== Chatbot de Segurança Cibernética ===")
print("Digite /sair para encerrar.\n")

while True:
    pergunta = input("Você: ").strip()

    if pergunta.lower() == "/sair":
        print("Assistente: Até logo!")
        break

    if not pergunta:
        print("Assistente: Digite uma pergunta.")
        continue

    # Adiciona a pergunta ao histórico
    historico.append({
        "role": "user",
        "content": pergunta
    })

    try:
        resposta = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=historico
        )

        texto = resposta.choices[0].message.content

        print(f"\nAssistente: {texto}\n")

        # Adiciona a resposta ao histórico
        historico.append({
            "role": "assistant",
            "content": texto
        })

    except RateLimitError:
        print("Assistente: Limite de requisições atingido. Tente novamente.\n")
        historico.pop()

    except APITimeoutError:
        print("Assistente: A API demorou para responder. Tente novamente.\n")
        historico.pop()

    except APIError as erro:
        print(f"Assistente: Erro na API: {erro.status_code or 'indisponível'}.\n")
        historico.pop()

    except Exception:
        print("Assistente: Ocorreu um erro inesperado. Tente novamente.\n")
        historico.pop()
