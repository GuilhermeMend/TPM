from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import uuid
import requests

# Lê o arquivo .env (se existir) para as chaves e segredos
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Criação da aplicação Flask
app = Flask(__name__)

# Chave usada para assinar o cookie de sessão (login da gestão).
# Defina SECRET_KEY no .env; sem ela, é gerada uma aleatória a cada
# inicialização (o login da gestão cai sempre que o servidor reinicia).
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)

# Permite que o JavaScript do navegador (Live Server, porta 5501) acesse
# o Flask e envie o cookie de sessão junto (supports_credentials).
# IMPORTANTE: abra o site por http://localhost:5501 (não 127.0.0.1),
# senão o navegador não envia o cookie.
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5501", "http://127.0.0.1:5501"]
)

# Chaves da Sightengine (https://dashboard.sightengine.com), no .env:
#   SIGHTENGINE_USER=...
#   SIGHTENGINE_SECRET=...
SIGHTENGINE_USER = os.environ.get('SIGHTENGINE_USER')
SIGHTENGINE_SECRET = os.environ.get('SIGHTENGINE_SECRET')


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
            SELECT id_aluno, nome, senha
            FROM aluno
            WHERE nome = %s
            """,
            (nome_recebido,)
        )


        # Guarda o resultado encontrado e confere a senha com o hash
        usuario_encontrado = cursor.fetchone()

        if usuario_encontrado and not check_password_hash(
                usuario_encontrado['senha'], senha_recebida or ''):
            usuario_encontrado = None



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




# ================= CADASTRO DO ALUNO (SÓ GESTÃO) =================
#
# Rota: POST /cadastro
# JSON: { "nome": "...", "ra": "...", "senha": "...", "turma": "3_ano_B" }
# Só funciona com a gestão logada (cookie de sessão criado no
# /login_gestao). Cria o login do aluno (tabela `aluno`, senha com hash)
# e coloca o aluno na turma (tabela `turmas`), tudo na mesma transação.

@app.route('/cadastro', methods=['POST'])
def cadastro():

    if not session.get('gestor_id'):
        return jsonify({
            "sucesso": False,
            "mensagem": "Apenas a gestão pode cadastrar alunos. Faça login como gestão."
        }), 401

    dados = request.get_json() or {}

    nome = (dados.get('nome') or '').strip()
    ra = (dados.get('ra') or '').strip()
    senha = dados.get('senha') or ''
    turma = (dados.get('turma') or '').strip()

    if not nome or not ra or not senha or not turma:
        return jsonify({
            "sucesso": False,
            "mensagem": "Nome, RA, senha e turma são obrigatórios."
        }), 400

    if len(nome) > 50 or len(ra) > 50:
        return jsonify({
            "sucesso": False,
            "mensagem": "Nome e RA podem ter no máximo 50 caracteres."
        }), 400

    if len(senha) < 4:
        return jsonify({
            "sucesso": False,
            "mensagem": "A senha precisa ter pelo menos 4 caracteres."
        }), 400

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        # A turma precisa existir (criada pelo botão "+ Adicionar turma"
        # ou já com alunos)
        cursor.execute(
            """
            SELECT 1 FROM turmas_cadastradas WHERE codigo = %s
            UNION
            SELECT 1 FROM turmas WHERE turma = %s
            """,
            (turma, turma)
        )
        if not cursor.fetchone():
            return jsonify({
                "sucesso": False,
                "mensagem": "Essa turma não existe."
            }), 400

        # Nome e RA não podem se repetir
        cursor.execute("SELECT 1 FROM aluno WHERE nome = %s", (nome,))
        if cursor.fetchone():
            return jsonify({
                "sucesso": False,
                "mensagem": "Já existe um aluno com esse nome."
            }), 409

        cursor.execute("SELECT 1 FROM turmas WHERE ra_aluno = %s", (ra,))
        if cursor.fetchone():
            return jsonify({
                "sucesso": False,
                "mensagem": "Já existe um aluno com esse RA."
            }), 409

        # Login do aluno (senha guardada como hash, nunca em texto)
        cursor.execute(
            "INSERT INTO aluno (nome, senha) VALUES (%s, %s)",
            (nome, generate_password_hash(senha))
        )

        # Vínculo com a turma
        cursor.execute(
            """
            INSERT INTO turmas (ra_aluno, nome_aluno, turma)
            VALUES (%s, %s, %s)
            """,
            (ra, nome, turma)
        )

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Aluno cadastrado com sucesso!"
        }), 201

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        if conexao:
            conexao.rollback()

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao cadastrar aluno."
        }), 500

    finally:

        if cursor:
            cursor.close()

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
            SELECT id_gestor, nome, senha
            FROM gestão
            WHERE nome = %s
            """,

            (nome_recebido,)

        )



        gestor_encontrado = cursor.fetchone()

        if gestor_encontrado and not check_password_hash(
                gestor_encontrado['senha'], senha_recebida or ''):
            gestor_encontrado = None



        # Caso encontre o gestor
        if gestor_encontrado:

            # Guarda no cookie de sessão que quem fez login é gestão
            # (usado pra proteger rotas como o cadastro de alunos)
            session['gestor_id'] = gestor_encontrado['id_gestor']


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

        # Junta as turmas que já têm aluno (tabela turmas) com as criadas
        # pelo botão "+ Adicionar turma" (tabela turmas_cadastradas).
        # UNION já remove repetidos.
        cursor.execute(
            """
            SELECT turma FROM turmas
            UNION
            SELECT codigo FROM turmas_cadastradas
            ORDER BY turma
            """
        )

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



# ================= ESTATÍSTICAS DO PAINEL (GESTÃO) =================
#
# Rota: GET /api/estatisticas
# Pra que serve: números reais pros cartões do painel da gestão
# (total de turmas e total de alunos matriculados em turmas).

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT turma FROM turmas WHERE turma IS NOT NULL
                UNION
                SELECT codigo FROM turmas_cadastradas
            ) AS todas
            """
        )
        total_turmas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_alunos = cursor.fetchone()[0]

        return jsonify({
            "sucesso": True,
            "total_turmas": total_turmas,
            "total_alunos": total_alunos
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar estatísticas."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= ADICIONAR TURMA (GESTÃO) =================
#
# Rota: POST /api/turmas
# JSON: { "codigo": "3_ano_B", "nome": "3º Ano B", "professor": "...",
#         "turno": "Manhã", "cor": "linear-gradient(...)" }
# Grava na tabela `turmas_cadastradas` (veja turmas_cadastradas.sql).

@app.route('/api/turmas', methods=['POST'])
def adicionar_turma():

    dados = request.get_json() or {}

    # Espaços viram "_" pra bater com o formato da coluna turmas.turma
    codigo = (dados.get('codigo') or '').strip().replace(' ', '_')
    nome = (dados.get('nome') or '').strip()
    professor = (dados.get('professor') or '').strip()
    turno = (dados.get('turno') or '').strip()
    cor = (dados.get('cor') or '').strip()

    if not codigo or not nome or not professor:
        return jsonify({
            "sucesso": False,
            "mensagem": "Preencha código, nome e professor."
        }), 400

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        # Já existe? (na tabela de turmas criadas ou com alunos)
        cursor.execute(
            """
            SELECT 1 FROM turmas_cadastradas WHERE codigo = %s
            UNION
            SELECT 1 FROM turmas WHERE turma = %s
            """,
            (codigo, codigo)
        )
        if cursor.fetchone():
            return jsonify({
                "sucesso": False,
                "mensagem": "Já existe uma turma com esse código."
            }), 409

        cursor.execute(
            """
            INSERT INTO turmas_cadastradas (codigo, nome, professor, turno, cor)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (codigo[:50], nome[:100], professor[:100], turno[:20], cor[:100])
        )

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Turma adicionada com sucesso!",
            "codigo": codigo
        }), 201

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao adicionar a turma."
        }), 500

    finally:

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

    # Moderação: lê o arquivo, manda pra Sightengine e só segue se aprovar.
    # Nada é salvo no disco nem no banco se a imagem for bloqueada.
    conteudo = arquivo.read()
    arquivo.seek(0)

    aprovada, motivo = verificar_imagem_adequada(arquivo.filename, conteudo)
    if not aprovada:
        return jsonify({
            "sucesso": False,
            "mensagem": motivo
        }), 422

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



# ================= MENSAGENS (ALUNO <-> GESTÃO) =================
#
# Tabela `mensagens` (veja mensagens.sql). Uma mesma tabela guarda os dois
# sentidos; a coluna `direcao` diz quem mandou pra quem:
#   'aluno_para_gestao' -> o aluno escreve na home, a gestão recebe
#   'gestao_para_aluno' -> a gestão escreve no painel, o aluno recebe
#                          (id_aluno NULL = aviso pra todos os alunos)

def formatar_mensagens(linhas):
    # datetime não é serializável em JSON, então vira texto
    for linha in linhas:
        if linha.get('data_envio'):
            linha['data_envio'] = linha['data_envio'].isoformat()
    return linhas


# ---------- LISTAR ALUNOS (pra gestão escolher o destinatário) ----------
# Rota: GET /api/alunos

@app.route('/api/alunos', methods=['GET'])
def listar_alunos():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT id_aluno, nome FROM aluno ORDER BY nome")

        return jsonify({
            "sucesso": True,
            "alunos": cursor.fetchall()
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar alunos."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- ALUNO ENVIA MENSAGEM PRA GESTÃO ----------
# Rota: POST /api/mensagens/para-gestao
# JSON: { "aluno_id": ..., "assunto": "...", "texto": "..." }

@app.route('/api/mensagens/para-gestao', methods=['POST'])
def aluno_envia_mensagem():

    dados = request.get_json() or {}

    aluno_id = dados.get('aluno_id')
    assunto = (dados.get('assunto') or '').strip()
    texto = (dados.get('texto') or '').strip()

    if not aluno_id:
        return jsonify({
            "sucesso": False,
            "mensagem": "Faça login como aluno para enviar mensagens."
        }), 400

    if not assunto or not texto:
        return jsonify({
            "sucesso": False,
            "mensagem": "Preencha o assunto e a mensagem."
        }), 400

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            INSERT INTO mensagens (direcao, id_aluno, assunto, texto)
            VALUES ('aluno_para_gestao', %s, %s, %s)
            """,
            (aluno_id, assunto[:150], texto[:2000])
        )

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Mensagem enviada para a gestão!"
        }), 201

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao enviar a mensagem."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- GESTÃO ENVIA MENSAGEM PRA ALUNO(S) ----------
# Rota: POST /api/mensagens/para-aluno
# JSON: { "gestor_id": ..., "aluno_id": 3 ou null (= todos),
#         "assunto": "...", "texto": "..." }

@app.route('/api/mensagens/para-aluno', methods=['POST'])
def gestao_envia_mensagem():

    dados = request.get_json() or {}

    gestor_id = dados.get('gestor_id')
    aluno_id = dados.get('aluno_id') or None   # vazio/None = todos
    assunto = (dados.get('assunto') or '').strip()
    texto = (dados.get('texto') or '').strip()

    if not gestor_id:
        return jsonify({
            "sucesso": False,
            "mensagem": "Faça login como gestão para enviar mensagens."
        }), 400

    if not assunto or not texto:
        return jsonify({
            "sucesso": False,
            "mensagem": "Preencha o assunto e a mensagem."
        }), 400

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            INSERT INTO mensagens (direcao, id_aluno, id_gestor, assunto, texto)
            VALUES ('gestao_para_aluno', %s, %s, %s, %s)
            """,
            (aluno_id, gestor_id, assunto[:150], texto[:2000])
        )

        conexao.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Mensagem enviada!"
        }), 201

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao enviar a mensagem."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- CAIXA DE ENTRADA DO ALUNO (home) ----------
# Rota: GET /api/mensagens/aluno/<id_aluno>
# Devolve o que a gestão mandou pra esse aluno + os avisos pra todos.

@app.route('/api/mensagens/aluno/<int:id_aluno>', methods=['GET'])
def caixa_entrada_aluno(id_aluno):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.id_mensagem,
                m.assunto,
                m.texto,
                m.data_envio,
                m.id_aluno IS NULL AS para_todos,
                IF(m.id_aluno IS NULL, 1, m.lida) AS lida,
                g.nome AS nome_gestor
            FROM mensagens m
            LEFT JOIN gestão g ON g.id_gestor = m.id_gestor
            WHERE m.direcao = 'gestao_para_aluno'
              AND (m.id_aluno = %s OR m.id_aluno IS NULL)
            ORDER BY m.data_envio DESC
            """,
            (id_aluno,)
        )

        return jsonify({
            "sucesso": True,
            "mensagens": formatar_mensagens(cursor.fetchall())
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar as mensagens."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- CAIXA DE ENTRADA DA GESTÃO ----------
# Rota: GET /api/mensagens/gestao
# Devolve tudo que os alunos mandaram, da mais recente pra mais antiga.

@app.route('/api/mensagens/gestao', methods=['GET'])
def caixa_entrada_gestao():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.id_mensagem,
                m.id_aluno,
                m.assunto,
                m.texto,
                m.lida,
                m.data_envio,
                a.nome AS nome_aluno
            FROM mensagens m
            JOIN aluno a ON a.id_aluno = m.id_aluno
            WHERE m.direcao = 'aluno_para_gestao'
            ORDER BY m.data_envio DESC
            """
        )

        return jsonify({
            "sucesso": True,
            "mensagens": formatar_mensagens(cursor.fetchall())
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar as mensagens."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- ENVIADAS DO ALUNO (home) ----------
# Rota: GET /api/mensagens/aluno/<id_aluno>/enviadas
# Devolve o que esse aluno mandou pra gestão (e se já foi lida).

@app.route('/api/mensagens/aluno/<int:id_aluno>/enviadas', methods=['GET'])
def enviadas_aluno(id_aluno):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_mensagem, assunto, texto, lida, data_envio
            FROM mensagens
            WHERE direcao = 'aluno_para_gestao' AND id_aluno = %s
            ORDER BY data_envio DESC
            """,
            (id_aluno,)
        )

        return jsonify({
            "sucesso": True,
            "mensagens": formatar_mensagens(cursor.fetchall())
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar as mensagens enviadas."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- ENVIADAS DA GESTÃO ----------
# Rota: GET /api/mensagens/gestao/enviadas
# Devolve o que a gestão mandou (nome_aluno NULL = aviso pra todos).

@app.route('/api/mensagens/gestao/enviadas', methods=['GET'])
def enviadas_gestao():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.id_mensagem,
                m.assunto,
                m.texto,
                m.lida,
                m.data_envio,
                m.id_aluno IS NULL AS para_todos,
                a.nome AS nome_aluno
            FROM mensagens m
            LEFT JOIN aluno a ON a.id_aluno = m.id_aluno
            WHERE m.direcao = 'gestao_para_aluno'
            ORDER BY m.data_envio DESC
            """
        )

        return jsonify({
            "sucesso": True,
            "mensagens": formatar_mensagens(cursor.fetchall())
        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao buscar as mensagens enviadas."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------- MARCAR MENSAGEM COMO LIDA ----------
# Rota: PATCH /api/mensagens/<id_mensagem>/lida

@app.route('/api/mensagens/<int:id_mensagem>/lida', methods=['PATCH'])
def marcar_mensagem_lida(id_mensagem):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "UPDATE mensagens SET lida = 1 WHERE id_mensagem = %s",
            (id_mensagem,)
        )

        conexao.commit()

        return jsonify({"sucesso": True}), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao atualizar a mensagem."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= MODERAÇÃO DE IMAGEM (SIGHTENGINE) =================
#
# Manda a imagem pra Sightengine ANTES de salvar no disco/banco.
# Retorna (aprovada, motivo):
#   (True,  None)      -> pode publicar
#   (False, "texto")   -> bloqueada (motivo mostrado pra gestão)
# Se a verificação falhar (sem chave, sem internet, erro da API) a foto
# NÃO é publicada: melhor bloquear do que deixar passar sem checar.

LIMITE_NUDEZ_EXPLICITA = 0.5   # sexual_activity, sexual_display, erotica
LIMITE_NUDEZ_SUGESTIVA = 0.7   # very_suggestive
LIMITE_OFENSIVO = 0.5          # nazi, supremacist, terrorist, etc.
LIMITE_GORE = 0.5              # sangue / violência


def verificar_imagem_adequada(nome_arquivo, conteudo):

    if not SIGHTENGINE_USER or not SIGHTENGINE_SECRET:
        print("Sightengine: SIGHTENGINE_USER/SIGHTENGINE_SECRET não configurados.")
        return False, "Moderação de imagens não configurada no servidor."

    try:
        resposta = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            files={"media": (nome_arquivo, conteudo)},
            data={
                "models": "nudity-2.1,offensive-2.0,gore-2.0",
                "api_user": SIGHTENGINE_USER,
                "api_secret": SIGHTENGINE_SECRET
            },
            timeout=20
        )
        resultado = resposta.json()

    except (requests.RequestException, ValueError) as erro:
        print(f"Erro ao chamar a Sightengine: {erro}")
        return False, "Não foi possível verificar a imagem agora. Tente de novo."

    if resultado.get("status") != "success":
        print(f"Sightengine respondeu com erro: {resultado}")
        return False, "Não foi possível verificar a imagem agora. Tente de novo."

    # Nudez / conteúdo sexual
    nudez = resultado.get("nudity", {})
    explicito = max(
        nudez.get("sexual_activity", 0),
        nudez.get("sexual_display", 0),
        nudez.get("erotica", 0)
    )
    if explicito >= LIMITE_NUDEZ_EXPLICITA or \
            nudez.get("very_suggestive", 0) >= LIMITE_NUDEZ_SUGESTIVA:
        return False, "Imagem bloqueada: conteúdo sexual ou nudez."

    # Símbolos/gestos ofensivos (todas as chaves são probabilidades 0–1)
    ofensivo = resultado.get("offensive", {})
    if any(isinstance(v, (int, float)) and v >= LIMITE_OFENSIVO
           for v in ofensivo.values()):
        return False, "Imagem bloqueada: conteúdo ofensivo."

    # Violência / sangue
    if resultado.get("gore", {}).get("prob", 0) >= LIMITE_GORE:
        return False, "Imagem bloqueada: conteúdo violento."

    return True, None



# ================= INICIAR SERVIDOR =================

if __name__ == "__main__":

    # Inicia o servidor Flask na porta 5000
    app.run(
        host="localhost",
        port=5000,
        debug=True
    )