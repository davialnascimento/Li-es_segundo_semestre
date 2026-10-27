
import mysql.connector
from mysql.connector import IntegrityError, Error


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="SUA_SENHA",
        database="seguranca"
    )


def criar_tabela(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            nivel_acesso INT NOT NULL,
            CHECK (nivel_acesso BETWEEN 1 AND 5)
        )
    """)
    conexao.commit()
    cursor.close()


def validar_nivel(nivel):
    try:
        nivel = int(nivel)
        if 1 <= nivel <= 5:
            return nivel
    except (ValueError, TypeError):
        pass

    raise ValueError("O nível de acesso deve ser de 1 a 5.")


def cadastrar(conexao):
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip()
    try:
        nivel = validar_nivel(input("Nível de acesso (1-5): "))
        if not nome or not email:
            print("Erro: nome e e-mail são obrigatórios.")
            return

        cursor = conexao.cursor()
        cursor.execute(
            """INSERT INTO usuarios (nome, email, nivel_acesso)
               VALUES (%s, %s, %s)""",
            (nome, email, nivel)
        )
        conexao.commit()
        print("Usuário cadastrado!")

    except ValueError as erro:
        print(f"Erro: {erro}")
    except IntegrityError as erro:
        conexao.rollback()
        if erro.errno == 1062:
            print("Erro: email já existe")
        else:
            print("Erro de integridade:", erro)
    except Error as erro:
        conexao.rollback()
        print("Erro no banco:", erro)
    finally:
        if "cursor" in locals():
            cursor.close()


def listar(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT nome, email, nivel_acesso
        FROM usuarios
        ORDER BY id
    """)

    usuarios = cursor.fetchall()

    if not usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        for nome, email, nivel in usuarios:
            print(f"{nome:<12} | {email:<20} | nível {nivel}")

    cursor.close()


def buscar_por_email(conexao):
    email = input("E-mail para buscar: ").strip()

    cursor = conexao.cursor()
    cursor.execute(
        """SELECT id, nome, email, nivel_acesso
           FROM usuarios WHERE email = %s""",
        (email,)
    )

    usuario = cursor.fetchone()

    if usuario:
        id_usuario, nome, email, nivel = usuario
        print(f"ID: {id_usuario} | {nome} | {email} | nível {nivel}")
    else:
        print("Usuário não encontrado.")

    cursor.close()


def atualizar_nivel(conexao):
    email = input("E-mail do usuário: ").strip()

    try:
        nivel = validar_nivel(input("Novo nível (1-5): "))

        cursor = conexao.cursor()
        cursor.execute(
            """UPDATE usuarios
               SET nivel_acesso = %s
               WHERE email = %s""",
            (nivel, email)
        )
        conexao.commit()

        if cursor.rowcount > 0:
            print("Nível atualizado!")
        else:
            print("Usuário não encontrado.")

    except ValueError as erro:
        print(f"Erro: {erro}")
    except Error as erro:
        conexao.rollback()
        print("Erro no banco:", erro)
    finally:
        if "cursor" in locals():
            cursor.close()


def remover(conexao):
    email = input("E-mail do usuário a remover: ").strip()

    confirmacao = input(
        f"Confirma a remoção de {email}? (s/n): "
    ).strip().lower()

    if confirmacao != "s":
        print("Remoção cancelada.")
        return

    cursor = conexao.cursor()
    cursor.execute(
        "DELETE FROM usuarios WHERE email = %s",
        (email,)
    )
    conexao.commit()

    if cursor.rowcount > 0:
        print("Usuário removido!")
    else:
        print("Usuário não encontrado.")

    cursor.close()


def menu():
    conexao = None

    try:
        conexao = conectar()
        criar_tabela(conexao)

        while True:
            print("""
========= GERENCIAMENTO DE USUÁRIOS =========
1 - Cadastrar usuário
2 - Listar usuários
3 - Buscar por e-mail
4 - Promover/rebaixar nível
5 - Remover usuário
0 - Sair
=============================================
""")
            opcao = input("Escolha: ").strip()

            if opcao == "1":
                cadastrar(conexao)
            elif opcao == "2":
                listar(conexao)
            elif opcao == "3":
                buscar_por_email(conexao)
            elif opcao == "4":
                atualizar_nivel(conexao)
            elif opcao == "5":
                remover(conexao)
            elif opcao == "0":
                print("Sistema encerrado.")
                break
            else:
                print("Opção inválida.")

    except Error as erro:
        print("Não foi possível conectar ao MySQL:", erro)
    finally:
        if conexao and conexao.is_connected():
            conexao.close()


if __name__ == "__main__":
    menu()
