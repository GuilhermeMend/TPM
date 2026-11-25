"""Cadastro, edição, exclusão de alunos e redefinição de senha (só gestão)."""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
import mysql.connector

from db import conectar_banco
from helpers import negar, turma_existe, validar_nome_ra

bp = Blueprint('alunos', __name__)


# ================= CADASTRO DO ALUNO (SÓ GESTÃO) =================
#
# Rota: POST /cadastro
# JSON: { "nome": "...", "ra": "...", "senha": "...", "turma": "3_ano_B" }
# Só funciona com a gestão logada (cookie de sessão criado no
# /login_gestao). Cria o login do aluno (tabela `aluno`, senha com hash)
# e coloca o aluno na turma (tabela `turmas`), tudo na mesma transação.

@bp.route('/cadastro', methods=['POST'])
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
        id_login = cursor.lastrowid

        # Vínculo com a turma. id_login liga a matrícula ao login que acabou
        # de ser criado (chave estrangeira: apagar o login apaga a matrícula).
        cursor.execute(
            """
            INSERT INTO turmas (id_login, ra_aluno, nome_aluno, turma)
            VALUES (%s, %s, %s, %s)
            """,
            (id_login, ra, nome, turma)
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


# ================= GESTÃO: EDITAR / EXCLUIR ALUNO / REDEFINIR SENHA =================
# O aluno é identificado pela MATRÍCULA (turmas.id_aluno, o mesmo id que
# /api/turmas/<turma>/alunos devolve). O login fica em turmas.id_login.

def _buscar_matricula(cursor, id_matricula):
    cursor.execute(
        """
        SELECT id_aluno, id_login, nome_aluno, ra_aluno, turma
        FROM turmas WHERE id_aluno = %s
        """,
        (id_matricula,)
    )
    return cursor.fetchone()


@bp.route('/api/matriculas/<int:id_matricula>', methods=['PUT'])
def editar_aluno(id_matricula):

    dados = request.get_json(silent=True) or {}
    nome = (dados.get('nome') or '').strip()
    ra = (dados.get('ra') or '').strip()
    turma = (dados.get('turma') or '').strip()

    erro_validacao = validar_nome_ra(nome, ra)
    if erro_validacao or not turma:
        return negar(erro_validacao or "Escolha a turma.", 400)

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        atual = _buscar_matricula(cursor, id_matricula)
        if atual is None:
            return negar("Aluno não encontrado.", 404)

        # Pode mover pra qualquer turma que exista (ou ficar na mesma)
        if turma != atual['turma'] and not turma_existe(cursor, turma):
            return negar("Essa turma não existe.", 400)

        # Nome é o usuário de login: não pode repetir
        cursor.execute(
            "SELECT 1 FROM turmas WHERE nome_aluno = %s AND id_aluno <> %s",
            (nome, id_matricula)
        )
        repetido = cursor.fetchone()
        if not repetido:
            cursor.execute(
                "SELECT 1 FROM aluno WHERE nome = %s AND id_aluno <> %s",
                (nome, atual['id_login'] or -1)
            )
            repetido = cursor.fetchone()
        if repetido:
            return negar("Já existe um aluno com esse nome.", 409)

        cursor.execute(
            "SELECT 1 FROM turmas WHERE ra_aluno = %s AND id_aluno <> %s",
            (ra, id_matricula)
        )
        if cursor.fetchone():
            return negar("Já existe um aluno com esse RA.", 409)

        cursor.execute(
            "UPDATE turmas SET nome_aluno = %s, ra_aluno = %s, turma = %s WHERE id_aluno = %s",
            (nome, ra, turma, id_matricula)
        )

        if atual['id_login']:
            cursor.execute(
                "UPDATE aluno SET nome = %s WHERE id_aluno = %s",
                (nome, atual['id_login'])
            )

        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Aluno atualizado!"}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if conexao:
            conexao.rollback()
        return negar("Erro ao atualizar o aluno.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@bp.route('/api/matriculas/<int:id_matricula>/senha', methods=['POST'])
def redefinir_senha_aluno(id_matricula):

    dados = request.get_json(silent=True) or {}
    senha = dados.get('senha') or ''

    if len(senha) < 4:
        return negar("A senha precisa ter pelo menos 4 caracteres.", 400)

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        atual = _buscar_matricula(cursor, id_matricula)
        if atual is None:
            return negar("Aluno não encontrado.", 404)

        senha_hash = generate_password_hash(senha)

        if atual['id_login']:
            cursor.execute(
                "UPDATE aluno SET senha = %s WHERE id_aluno = %s",
                (senha_hash, atual['id_login'])
            )
            mensagem = "Senha redefinida!"

        else:
            # Matrícula sem login (ex: dados de exemplo): cria o login agora
            cursor.execute("SELECT 1 FROM aluno WHERE nome = %s", (atual['nome_aluno'],))
            if cursor.fetchone():
                return negar("Já existe um login com o nome desse aluno.", 409)

            cursor.execute(
                "INSERT INTO aluno (nome, senha) VALUES (%s, %s)",
                (atual['nome_aluno'], senha_hash)
            )
            cursor.execute(
                "UPDATE turmas SET id_login = %s WHERE id_aluno = %s",
                (cursor.lastrowid, id_matricula)
            )
            mensagem = "Login criado com a senha informada!"

        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": mensagem}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if conexao:
            conexao.rollback()
        return negar("Erro ao redefinir a senha.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@bp.route('/api/matriculas/<int:id_matricula>', methods=['DELETE'])
def excluir_aluno(id_matricula):

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        atual = _buscar_matricula(cursor, id_matricula)
        if atual is None:
            return negar("Aluno não encontrado.", 404)

        id_login = atual['id_login']

        if id_login:
            # Apaga o que o aluno escreveu antes de apagar o login
            cursor.execute("DELETE FROM comentarios WHERE id_aluno = %s", (id_login,))
            cursor.execute("DELETE FROM mensagens WHERE id_aluno = %s", (id_login,))

        cursor.execute("DELETE FROM turmas WHERE id_aluno = %s", (id_matricula,))

        if id_login:
            cursor.execute("DELETE FROM aluno WHERE id_aluno = %s", (id_login,))

        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Aluno excluído!"}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if conexao:
            conexao.rollback()
        return negar("Erro ao excluir o aluno.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
