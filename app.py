from flask import Flask, request, jsonify, render_template_string
import mysql.connector
import os  # Importante para localizar o arquivo

app = Flask(__name__)

def db():
    return mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='lea', 
        database='agenda', 
        port=3306,
        autocommit=True
    )

@app.route('/')
def index():
    try:
        # Pega o caminho da pasta onde este app.py está localizado
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_index = os.path.join(diretorio_atual, 'index.html')
        
        with open(caminho_index, 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return f"Arquivo index.html não encontrado no caminho: {caminho_index}"

@app.route('/agendar', methods=['POST'])
def agendar():
    d = request.json
    data_formatada = d['d'].replace('T', ' ')
    try:
        con = db()
        cur = con.cursor()
        cur.execute("INSERT INTO banco de dados  (nome, senha) VALUES (%s, %s)", \
                    (d['n'], data_formatada))
        cur.close()
        con.close()
        return jsonify("OK"), 200
    except Exception as e:
        return jsonify(str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)

    