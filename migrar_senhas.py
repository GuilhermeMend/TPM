"""Migração ÚNICA: converte as senhas em texto puro (aluno e gestão) em hash.

Como usar (com o MySQL ligado, na pasta do projeto):
    python migrar_senhas.py

É seguro rodar mais de uma vez: senhas que já são hash são ignoradas.
"""
from werkzeug.security import generate_password_hash
from app import conectar_banco

PREFIXOS_HASH = ("scrypt:", "pbkdf2:")


def migrar(cursor, tabela, coluna_id):
    # O hash tem ~160 caracteres; a coluna original era varchar(50)
    cursor.execute(f"ALTER TABLE `{tabela}` MODIFY `senha` VARCHAR(255)")

    cursor.execute(f"SELECT `{coluna_id}`, `senha` FROM `{tabela}`")
    linhas = cursor.fetchall()

    convertidas = 0
    for id_, senha in linhas:
        if not senha or senha.startswith(PREFIXOS_HASH):
            continue
        cursor.execute(
            f"UPDATE `{tabela}` SET `senha` = %s WHERE `{coluna_id}` = %s",
            (generate_password_hash(senha), id_)
        )
        convertidas += 1

    print(f"{tabela}: {convertidas} senha(s) convertida(s).")


conexao = conectar_banco()
cursor = conexao.cursor()
migrar(cursor, "aluno", "id_aluno")
migrar(cursor, "gestão", "id_gestor")
conexao.commit()
cursor.close()
conexao.close()
