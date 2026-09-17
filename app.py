from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mysql.connector
import os
import uuid

app = Flask(__name__)
CORS(app)

PASTA_UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(PASTA_UPLOADS, exist_ok=True)

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def extensao_permitida(nome_arquivo):
    return '.' in nome_arquivo and \
        nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

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
        cursor.execute(
            "SELECT id_aluno, nome FROM aluno WHERE nome = %s AND senha = %s",
            (nome_recebido, senha_recebida)
        )
        usuario_encontrado = cursor.fetchone()
        if usuario_encontrado:
            return jsonify({
                "sucesso": True,
                "mensagem": f"Bem-vindo, {usuario_encontrado['nome']}!",
                "usuario_id": usuario_encontrado['id_aluno']
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": "Usuário ou senha incorretos."
            }), 401
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro interno no servidor."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    nome = dados.get('nome')
    senha = dados.get('senha')
    if not nome or not senha:
        return jsonify({"sucesso": False, "mensagem": "Nome e senha são obrigatórios."}), 400
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO aluno (nome, senha) VALUES (%s, %s)", (nome, senha))
        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Cadastro realizado com sucesso!"}), 201
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao cadastrar usuário."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/login_gestao', methods=['POST'])
def login_gestao():
    dados = request.get_json()
    nome_recebido = dados.get('nome')
    senha_recebida = dados.get('senha')
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_gestor, nome FROM gestão WHERE nome = %s AND senha = %s",
            (nome_recebido, senha_recebida)
        )
        gestor_encontrado = cursor.fetchone()
        if gestor_encontrado:
            return jsonify({
                "sucesso": True,
                "mensagem": f"Bem-vindo, {gestor_encontrado['nome']}!",
                "gestor_id": gestor_encontrado['id_gestor']
            }), 200
        else:
            return jsonify({"sucesso": False, "mensagem": "Usuário ou senha inválidos."}), 401
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro interno no servidor."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/api/turmas', methods=['GET'])
def listar_turmas():
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT turma FROM turmas ORDER BY turma")
        linhas = cursor.fetchall()
        turmas_lista = [linha['turma'] for linha in linhas]
        return jsonify({"sucesso": True, "turmas": turmas_lista}), 200
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao buscar turmas."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/api/turmas/<turma>/alunos', methods=['GET'])
def listar_alunos_da_turma(turma):
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_aluno, ra_aluno, nome_aluno FROM turmas WHERE turma = %s ORDER BY nome_aluno",
            (turma,)
        )
        alunos_lista = cursor.fetchall()
        return jsonify({"sucesso": True, "alunos": alunos_lista}), 200
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao buscar alunos da turma."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/uploads/<nome_arquivo>', methods=['GET'])
def servir_imagem(nome_arquivo):
    return send_from_directory(PASTA_UPLOADS, nome_arquivo)

@app.route('/api/fotos', methods=['POST'])
def publicar_foto():
    if 'imagem' not in request.files:
        return jsonify({"sucesso": False, "mensagem": "Nenhuma imagem foi enviada."}), 400
    arquivo = request.files['imagem']
    legenda = request.form.get('legenda', '').strip()
    gestor_id = request.form.get('gestor_id')

    if arquivo.filename == '':
        return jsonify({"sucesso": False, "mensagem": "Nenhuma imagem foi selecionada."}), 400

    if not extensao_permitida(arquivo.filename):
        return jsonify({"sucesso": False, "mensagem": "Formato de imagem não permitido."}), 400

    nome_seguro = secure_filename(arquivo.filename)
    extensao = nome_seguro.rsplit('.', 1)[1].lower()
    nome_no_disco = f"{uuid.uuid4().hex}.{extensao}"

    caminho_completo = os.path.join(PASTA_UPLOADS, nome_no_disco)
    arquivo.save(caminho_completo)

    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO fotos (nome_arquivo, legenda, id_gestor) VALUES (%s, %s, %s)",
            (nome_no_disco, legenda, gestor_id)
        )
        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Foto publicada com sucesso!", "id_foto": cursor.lastrowid}), 201
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)
        return jsonify({"sucesso": False, "mensagem": "Erro ao publicar a foto."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/api/fotos', methods=['GET'])
def listar_fotos():
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                f.id_foto,
                f.nome_arquivo,
                f.legenda,
                f.data_postagem,
                g.nome AS nome_gestor,
                COUNT(c.id_comentario) AS total_comentarios
            FROM fotos f
            LEFT JOIN gestão g ON g.id_gestor = f.id_gestor
            LEFT JOIN comentarios c ON c.id_foto = f.id_foto
            GROUP BY f.id_foto, f.nome_arquivo, f.legenda, f.data_postagem, g.nome
            ORDER BY f.data_postagem DESC
            """
        )
        fotos_lista = cursor.fetchall()
        for foto in fotos_lista:
            foto['url'] = f"/uploads/{foto['nome_arquivo']}"
            if foto['data_postagem']:
                foto['data_postagem'] = foto['data_postagem'].isoformat()
        return jsonify({"sucesso": True, "fotos": fotos_lista}), 200
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao buscar as fotos."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/api/fotos/<int:id_foto>', methods=['DELETE'])
def excluir_foto(id_foto):
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT nome_arquivo FROM fotos WHERE id_foto = %s", (id_foto,))
        foto = cursor.fetchone()
        if not foto:
            return jsonify({"sucesso": False, "mensagem": "Foto não encontrada."}), 404

        cursor.execute("DELETE FROM fotos WHERE id_foto = %s", (id_foto,))
        conexao.commit()

        caminho_completo = os.path.join(PASTA_UPLOADS, foto['nome_arquivo'])
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)

        return jsonify({"sucesso": True, "mensagem": "Foto excluída com sucesso!"}), 200
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao excluir a foto."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/api/fotos/<int:id_foto>/comentarios', methods=['GET'])
def listar_comentarios(id_foto):
    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT c.id_comentario, c.texto, c.data_comentario, a.nome AS nome_aluno
            FROM comentarios c
            JOIN aluno a ON a.id_aluno = c.id_aluno
            WHERE c.id_foto = %s
            ORDER BY c.data_comentario ASC
            """,
            (id_foto,)
        )
        comentarios_lista = cursor.fetchall()
        for comentario in comentarios_lista:
            if comentario['data_comentario']:
                comentario['data_comentario'] = comentario['data_comentario'].isoformat()
        return jsonify({"sucesso": True, "comentarios": comentarios_lista}), 200
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao buscar os comentários."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

@app.route('/api/fotos/<int:id_foto>/comentarios', methods=['POST'])
def comentar_foto(id_foto):
    dados = request.get_json()
    aluno_id = dados.get('aluno_id')
    texto = (dados.get('texto') or '').strip()

    if not aluno_id or not texto:
        return jsonify({"sucesso": False, "mensagem": "É preciso estar logado e escrever um comentário."}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO comentarios (id_foto, id_aluno, texto) VALUES (%s, %s, %s)",
            (id_foto, aluno_id, texto)
        )
        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Comentário publicado!", "id_comentario": cursor.lastrowid}), 201
    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao publicar o comentário."}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)