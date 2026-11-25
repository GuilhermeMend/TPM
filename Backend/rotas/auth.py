"""Login, logout e sessão (aluno e gestão)."""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
import mysql.connector

from db import conectar_banco
from helpers import negar

bp = Blueprint('auth', __name__)


# ---------- QUEM ESTÁ LOGADO (usado pelo front pra proteger as páginas) ----------
# Rota: GET /api/sessao

@bp.route('/api/sessao', methods=['GET'])
def sessao_atual():

    if session.get('gestor_id'):
        return jsonify({
            "sucesso": True,
            "tipo": "gestao",
            "id": session['gestor_id'],
            "nome": session.get('gestor_nome', '')
        }), 200

    if session.get('aluno_id'):
        return jsonify({
            "sucesso": True,
            "tipo": "aluno",
            "id": session['aluno_id'],
            "nome": session.get('aluno_nome', '')
        }), 200

    return negar("Não há login ativo.", 401)


# ---------- SAIR ----------
# Rota: POST /logout — apaga a sessão no servidor

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"sucesso": True}), 200


# ================= LOGIN DO ALUNO =================

@bp.route('/login', methods=['POST'])
def login():

    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json(silent=True) or {}


    # Pega o RA enviado pelo aluno (o login do aluno é pelo RA, não pelo nome)
    ra_recebido = str(dados.get('ra') or '').strip()

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



        # Procura o aluno pelo RA. O RA fica na matrícula (tabela `turmas`),
        # que se liga ao login (tabela `aluno`) pelo id_login.
        cursor.execute(
            """
            SELECT a.id_aluno, a.nome, a.senha
            FROM turmas t
            JOIN aluno a ON a.id_aluno = t.id_login
            WHERE t.ra_aluno = %s
            """,
            (ra_recebido,)
        )


        # Guarda o resultado encontrado e confere a senha com o hash
        usuario_encontrado = cursor.fetchone()

        if usuario_encontrado and not check_password_hash(
                usuario_encontrado['senha'], senha_recebida or ''):
            usuario_encontrado = None



        # Caso o usuário exista
        if usuario_encontrado:

            session.clear()
            session.permanent = True
            session['aluno_id'] = usuario_encontrado['id_aluno']
            session['aluno_nome'] = usuario_encontrado['nome']

            return jsonify({

                "sucesso": True,

                "mensagem": f"Bem-vindo, {usuario_encontrado['nome']}!",

                # Envia o ID e o nome do aluno para o sistema
                "usuario_id": usuario_encontrado['id_aluno'],
                "nome": usuario_encontrado['nome']

            }), 200



        # Caso RA ou senha estejam errados (mesma mensagem nos dois casos,
        # pra não revelar se o RA existe)
        else:

            return jsonify({

                "sucesso": False,

                "mensagem": "RA ou senha incorretos."

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


# ================= LOGIN DA GESTÃO =================

@bp.route('/login_gestao', methods=['POST'])
def login_gestao():


    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json(silent=True) or {}


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
            session.clear()
            session.permanent = True
            session['gestor_id'] = gestor_encontrado['id_gestor']
            session['gestor_nome'] = gestor_encontrado['nome']


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
