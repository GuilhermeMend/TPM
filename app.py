from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)


def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",         
        password="lea", 
        database="banco de dados"
    )

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    nome_recebido = dados.get('nome')
    senha_recebida = dados.get('senha')
    
    conexao = None
    cursor = None
    
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True) 
        
        comando_sql = "SELECT id, usuario FROM aluno WHERE nome = %s AND senha = %s"
        cursor.execute(comando_sql, (nome_recebido, senha_recebida))
        
        usuario_encontrado = cursor.fetchone()
        
        if usuario_encontrado:
            return jsonify({
                "sucesso": True,
                "mensagem": f"Bem-vindo, {usuario_recebido}! Autenticação realizada.",
                "usuario_id": usuario_encontrado['id']
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": "Usuário ou senha incorretos."
            }), 401
            
    except mysql.connector.Error as erro:
        print(f"Erro no banco de dados: {erro}")
        return jsonify({
            "sucesso": False,
            "mensagem": "Erro interno ao consultar o banco de dados."
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)