"""Cria (ou troca a senha de) um usuário da GESTÃO, direto no banco.

Como usar (com o MySQL ligado, na pasta do projeto, depois de rodar o tcc.sql):
    python criar_gestor.py

A senha é digitada no terminal (não aparece na tela) e guardada como hash.
Nada de usuário/senha dentro do código ou do tcc.sql.
"""
import getpass
import sys

from werkzeug.security import generate_password_hash
from app import conectar_banco

TAMANHO_MINIMO_SENHA = 8


def pedir_senha():
    while True:
        senha = getpass.getpass(f"Senha (mínimo {TAMANHO_MINIMO_SENHA} caracteres): ")
        if len(senha) < TAMANHO_MINIMO_SENHA:
            print(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
            continue
        if senha != getpass.getpass("Repita a senha: "):
            print("As senhas não são iguais. Tente de novo.")
            continue
        return senha


def main():
    nome = input("Nome de usuário da gestão: ").strip()
    if not nome or len(nome) > 50:
        sys.exit("O nome é obrigatório e pode ter no máximo 50 caracteres.")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT id_gestor FROM `gestão` WHERE nome = %s", (nome,))
        existente = cursor.fetchone()

        if existente:
            resposta = input(f"Já existe a gestão '{nome}'. Trocar a senha dela? [s/N] ")
            if resposta.strip().lower() not in ("s", "sim"):
                sys.exit("Nada foi alterado.")
            cursor.execute(
                "UPDATE `gestão` SET senha = %s WHERE id_gestor = %s",
                (generate_password_hash(pedir_senha()), existente[0])
            )
            print(f"Senha de '{nome}' atualizada.")
        else:
            cursor.execute(
                "INSERT INTO `gestão` (nome, senha) VALUES (%s, %s)",
                (nome, generate_password_hash(pedir_senha()))
            )
            print(f"Gestão '{nome}' criada.")

        conexao.commit()

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    main()
