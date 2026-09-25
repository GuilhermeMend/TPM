from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mysql.connector
import os
import uuid


# Criação da aplicação Flask
app = Flask(__name__)

# Permite que o JavaScript do navegador consiga acessar o Flask
CORS(app)


# ================= CONFIGURAÇÃO DE UPLOAD DE FOTOS =================

# Pasta onde as imagens enviadas pela gestão ficam salvas no disco.
# Fica na mesma pasta do app.py (cria automaticamente se não existir).
PASTA_UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(PASTA_UPLOADS, exist_ok=True)

# Extensões de imagem aceitas no upload
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Limite de tamanho do arquivo enviado (5 MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


def extensao_permitida(nome_arquivo):
    # Confere se o arquivo tem um "." e se a extensão depois do "."
    # está na lista de extensões permitidas
    return '.' in nome_arquivo and \
        nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS



# ================= CONEXÃO COM O BANCO =================

def conectar_banco():

    # Função responsável por abrir conexão com o MySQL
    return mysql.connector.connect(

        # Servidor do banco de dados
        host="localhost",

        # Usuário do MySQL
        user="root",

        # Senha do MySQL
        password="lea",

        # Nome do banco utilizado
        database="banco de dados"
    )



# ================= LOGIN DO ALUNO =================

@app.route('/login', methods=['POST'])
def login():

    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json()


    # Pega o nome enviado pelo usuário
    nome_recebido = dados.get('nome')

    # Pega a senha enviada pelo usuário
    senha_recebida = dados.get('senha')


    # Variáveis para controlar conexão e consulta
    conexao = None
    cursor = None


    try:

        # Conecta ao banco de dados
        conexao = conectar_banco()


        # Cria um cursor que retorna os dados em formato de dicionário
        cursor = conexao.cursor(dictionary=True)



        # Procura um aluno com o mesmo nome e senha
        cursor.execute(
            """
            SELECT id_aluno, nome
            FROM aluno
            WHERE nome = %s AND senha = %s
            """,
            (nome_recebido, senha_recebida)
        )


        # Guarda o resultado encontrado
        usuario_encontrado = cursor.fetchone()



        # Caso o usuário exista
        if usuario_encontrado:

            return jsonify({

                "sucesso": True,

                "mensagem": f"Bem-vindo, {usuario_encontrado['nome']}!",

                # Envia o ID do aluno para o sistema
                "usuario_id": usuario_encontrado['id_aluno']

            }), 200



        # Caso nome ou senha estejam errados
        else:

            return jsonify({

                "sucesso": False,

                "mensagem": "Usuário ou senha incorretos."

            }), 401



    # Caso aconteça algum erro no MySQL
    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({

            "sucesso": False,

            "mensagem": "Erro interno no servidor."

        }), 500



    # Sempre executa no final, fechando a conexão
    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()




# ================= CADASTRO DO ALUNO =================

@app.route('/cadastro', methods=['POST'])
def cadastro():


    # Recebe os dados enviados pelo formulário
    dados = request.get_json()


    # Separa nome e senha recebidos
    nome = dados.get('nome')
    senha = dados.get('senha')



    # Verifica se os campos foram preenchidos
    if not nome or not senha:

        return jsonify({

            "sucesso": False,

            "mensagem": "Nome e senha são obrigatórios."

        }), 400



    conexao = None
    cursor = None



    try:

        # Abre conexão com o banco
        conexao = conectar_banco()


        # Cria cursor para executar comandos SQL
        cursor = conexao.cursor()



        # Insere um novo aluno na tabela
        cursor.execute(

            """
            INSERT INTO aluno (nome, senha)
            VALUES (%s, %s)
            """,

            (nome, senha)

        )



        # Confirma a alteração no banco
        conexao.commit()



        return jsonify({

            "sucesso": True,

            "mensagem": "Cadastro realizado com sucesso!"

        }), 201



    except mysql.connector.Error as erro:


        # Mostra o erro no terminal do Flask
        print(f"Erro no banco: {erro}")


        return jsonify({

            "sucesso": False,

            "mensagem": "Erro ao cadastrar usuário."

        }), 500



    finally:


        # Fecha o cursor
        if cursor:
            cursor.close()


        # Fecha a conexão com o banco
        if conexao:
            conexao.close()




# ================= LOGIN DA GESTÃO =================

@app.route('/login_gestao', methods=['POST'])
def login_gestao():


    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json()


    nome_recebido = dados.get('nome')
    senha_recebida = dados.get('senha')



    conexao = None
    cursor = None



    try:


        conexao = conectar_banco()


        cursor = conexao.cursor(dictionary=True)



        # Procura o gestor no banco
        cursor.execute(

            """
            SELECT id_gestor, nome
            FROM gestão
            WHERE nome = %s AND senha = %s
            """,

            (nome_recebido, senha_recebida)

        )



        gestor_encontrado = cursor.fetchone()



        # Caso encontre o gestor
        if gestor_encontrado:


            return jsonify({

                "sucesso": True,

                "mensagem": f"Bem-vindo, {gestor_encontrado['nome']}!",

                "gestor_id": gestor_encontrado['id_gestor']

            }), 200



        else:


            return jsonify({

                "sucesso": False,

                "mensagem": "Usuário ou senha inválidos."

            }), 401



    except mysql.connector.Error as erro:


        print(f"Erro no banco: {erro}")


        return jsonify({

            "sucesso": False,

            "mensagem": "Erro interno no servidor."

        }), 500



    finally:


        if cursor:
            cursor.close()


        if conexao:
            conexao.close()



# ================= LISTAR TURMAS =================
#
# Rota: GET /api/turmas
# Pra que serve: devolve a lista de nomes de turma que existem de verdade
# na tabela `turmas` (ex: ["3_ano_B"]). É o que o front (home.js/gestao.js)
# usa pra criar um botão pra cada turma.
#
# DISTINCT: como cada linha da tabela `turmas` é 1 aluno, o mesmo valor de
# turma se repete várias vezes (um por aluno). DISTINCT tira as repetições
# e deixa só os nomes de turma únicos.

@app.route('/api/turmas', methods=['GET'])
def listar_turmas():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # Busca os nomes de turma distintos cadastrados na tabela turmas
        cursor.execute("SELECT DISTINCT turma FROM turmas ORDER BY turma")

        linhas = cursor.fetchall()
        # cada "linha" é um dicionário tipo {'turma': '3_ano_B'} — aqui a
        # gente pega só o valor da chave 'turma' de cada um e joga numa lista
        turmas_lista = [linha['turma'] for linha in linhas]

        return jsonify({

            "sucesso": True,

            "turmas": turmas_lista

        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({

            "sucesso": False,

            "mensagem": "Erro ao buscar turmas."

        }), 500

    finally:

        # sempre fecha cursor/conexão, mesmo se deu erro acima —
        # senão fica conexão aberta "penduradas" no banco
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= LISTAR ALUNOS DE UMA TURMA =================
#
# Rota: GET /api/turmas/<turma>/alunos
# Exemplo real: GET /api/turmas/3_ano_B/alunos
# Pra que serve: devolve todos os alunos daquela turma específica —
# id_aluno, ra_aluno e nome_aluno. Tanto a página do aluno (home.js) quanto
# a da gestão (gestao.js) chamam essa MESMA rota; a diferença de mostrar
# ou não o RA acontece só no front, na hora de montar o HTML — o back
# manda o RA sempre, e cada página decide se usa ou ignora esse dado.
#
# <turma> na URL vira o parâmetro `turma` da função automaticamente
# (é o "conversor de rota" do Flask).

@app.route('/api/turmas/<turma>/alunos', methods=['GET'])
def listar_alunos_da_turma(turma):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # %s é um placeholder — o mysql-connector troca ele pelo valor de
        # forma segura (evita SQL Injection). NUNCA monte a query colando
        # a variável direto na string (tipo f"... = '{turma}'").
        cursor.execute(
            """
            SELECT id_aluno, ra_aluno, nome_aluno
            FROM turmas
            WHERE turma = %s
            ORDER BY nome_aluno
            """,
            (turma,)
        )

        alunos_lista = cursor.fetchall()

        return jsonify({

            "sucesso": True,

            "alunos": alunos_lista

        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({

            "sucesso": False,

            "mensagem": "Erro ao buscar alunos da turma."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()




# ================= SERVIR AS IMAGENS ENVIADAS =================
#
# Rota: GET /uploads/<nome_arquivo>
# Pra que serve: o navegador usa essa URL como "src" da tag <img> pra
# mostrar a foto. O Flask lê o arquivo direto da pasta PASTA_UPLOADS.

@app.route('/uploads/<nome_arquivo>', methods=['GET'])
def servir_imagem(nome_arquivo):
    return send_from_directory(PASTA_UPLOADS, nome_arquivo)



# ================= PUBLICAR FOTO (GESTÃO) =================
#
# Rota: POST /api/fotos
# Pra que serve: a gestão envia um arquivo de imagem + uma legenda.
# O envio é multipart/form-data (não é JSON, porque tem arquivo junto),
# então os dados chegam em request.form (texto) e request.files (arquivo).

@app.route('/api/fotos', methods=['POST'])
def publicar_foto():

    # Confere se o campo "imagem" veio no formulário
    if 'imagem' not in request.files:
        return jsonify({
            "sucesso": False,
            "mensagem": "Nenhuma imagem foi enviada."
        }), 400

    arquivo = request.files['imagem']
    legenda = request.form.get('legenda', '').strip()
    gestor_id = request.form.get('gestor_id')

    # Campo de arquivo veio vazio (usuário não escolheu nada)
    if arquivo.filename == '':
        return jsonify({
            "sucesso": False,
            "mensagem": "Nenhuma imagem foi selecionada."
        }), 400

    if not extensao_permitida(arquivo.filename):
        return jsonify({
            "sucesso": False,
            "mensagem": "Formato de imagem não permitido. Use PNG, JPG, JPEG, GIF ou WEBP."
        }), 400

    # Gera um nome de arquivo único pra evitar que duas fotos com o
    # mesmo nome se sobrescrevam no disco. secure_filename() limpa
    # caracteres perigosos do nome original (espaços, acentos, "../", etc.)
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
            """
            INSERT INTO fotos (nome_arquivo, legenda, id_gestor)
            VALUES (%s, %s, %s)
            """,
            (nome_no_disco, legenda, gestor_id)
        )

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Foto publicada com sucesso!",
            "id_foto": cursor.lastrowid
        }), 201

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        # Se der erro ao salvar no banco, remove o arquivo que já foi
        # salvo no disco pra não deixar imagem "órfã" (sem registro)
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao publicar a foto."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= LISTAR FOTOS =================
#
# Rota: GET /api/fotos
# Pra que serve: devolve todas as fotos publicadas, da mais recente pra
# mais antiga. Tanto home.js (aluno) quanto gestao.js usam essa mesma
# rota pra montar a galeria. Também manda o total de comentários de
# cada foto, pra mostrar tipo "12 comentários" no card.

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

        # Monta a URL completa de cada imagem (o front só usa a URL,
        # não precisa saber o caminho no disco)
        for foto in fotos_lista:
            foto['url'] = f"/uploads/{foto['nome_arquivo']}"
            # datetime não é serializável em JSON por padrão, então
            # transforma em texto antes de mandar
            if foto['data_postagem']:
                foto['data_postagem'] = foto['data_postagem'].isoformat()

        return jsonify({
            "sucesso": True,
            "fotos": fotos_lista
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar as fotos."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= EXCLUIR FOTO (GESTÃO) =================
#
# Rota: DELETE /api/fotos/<id_foto>
# Pra que serve: a gestão remove uma foto. Apaga o registro no banco
# (os comentários somem junto, por causa do ON DELETE CASCADE lá na
# tabela `comentarios`) e também apaga o arquivo de imagem do disco.

@app.route('/api/fotos/<int:id_foto>', methods=['DELETE'])
def excluir_foto(id_foto):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # Primeiro busca o nome do arquivo, pra poder apagar do disco
        # depois de confirmar que a exclusão no banco deu certo
        cursor.execute(
            "SELECT nome_arquivo FROM fotos WHERE id_foto = %s",
            (id_foto,)
        )
        foto = cursor.fetchone()

        if not foto:
            return jsonify({
                "sucesso": False,
                "mensagem": "Foto não encontrada."
            }), 404

        cursor.execute("DELETE FROM fotos WHERE id_foto = %s", (id_foto,))
        conexao.commit()

        # Remove o arquivo físico da pasta uploads
        caminho_completo = os.path.join(PASTA_UPLOADS, foto['nome_arquivo'])
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)

        return jsonify({
            "sucesso": True,
            "mensagem": "Foto excluída com sucesso!"
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao excluir a foto."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= LISTAR COMENTÁRIOS DE UMA FOTO =================
#
# Rota: GET /api/fotos/<id_foto>/comentarios
# Pra que serve: devolve todos os comentários de uma foto específica,
# do mais antigo pro mais novo, junto com o nome de quem comentou.

@app.route('/api/fotos/<int:id_foto>/comentarios', methods=['GET'])
def listar_comentarios(id_foto):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                c.id_comentario,
                c.texto,
                c.data_comentario,
                a.nome AS nome_aluno
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

        return jsonify({
            "sucesso": True,
            "comentarios": comentarios_lista
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar os comentários."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= COMENTAR EM UMA FOTO (ALUNO) =================
#
# Rota: POST /api/fotos/<id_foto>/comentarios
# Pra que serve: o aluno logado envia um texto de comentário pra uma
# foto. Vem como JSON: { "aluno_id": ..., "texto": "..." }

@app.route('/api/fotos/<int:id_foto>/comentarios', methods=['POST'])
def comentar_foto(id_foto):

    dados = request.get_json()

    aluno_id = dados.get('aluno_id')
    texto = (dados.get('texto') or '').strip()

    if not aluno_id or not texto:
        return jsonify({
            "sucesso": False,
            "mensagem": "É preciso estar logado e escrever um comentário."
        }), 400

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            INSERT INTO comentarios (id_foto, id_aluno, texto)
            VALUES (%s, %s, %s)
            """,
            (id_foto, aluno_id, texto)
        )

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Comentário publicado!",
            "id_comentario": cursor.lastrowid
        }), 201

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao publicar o comentário."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= INICIAR SERVIDOR =================

if __name__ == "__main__":

    # Inicia o servidor Flask na porta 5000
    app.run(
        host="localhost",
        port=5000,
        debug=True
    )