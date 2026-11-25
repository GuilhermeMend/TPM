"""Conexão com o MySQL."""
import os
import mysql.connector


def conectar_banco():

    # Função responsável por abrir conexão com o MySQL
    return mysql.connector.connect(

        # Servidor do banco de dados
        host=os.environ.get("DB_HOST", "localhost"),

        # Usuário do MySQL
        user=os.environ.get("DB_USER", "root"),

        # Senha do MySQL (defina DB_PASSWORD no .env)
        password=os.environ.get("DB_PASSWORD", ""),

        # Nome do banco utilizado
        database=os.environ.get("DB_NAME", "banco de dados")
    )
