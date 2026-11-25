"""Mensagens entre aluno e gestão."""
from flask import Blueprint, request, jsonify, session
import mysql.connector

from db import conectar_banco

bp = Blueprint('mensagens', __name__)


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

@bp.route('/api/alunos', methods=['GET'])
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

@bp.route('/api/mensagens/para-gestao', methods=['POST'])
def aluno_envia_mensagem():

    dados = request.get_json() or {}

    aluno_id = session.get('aluno_id')
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

@bp.route('/api/mensagens/para-aluno', methods=['POST'])
def gestao_envia_mensagem():

    dados = request.get_json() or {}

    gestor_id = session.get('gestor_id')
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

@bp.route('/api/mensagens/aluno/<int:id_aluno>', methods=['GET'])
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

@bp.route('/api/mensagens/gestao', methods=['GET'])
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

@bp.route('/api/mensagens/aluno/<int:id_aluno>/enviadas', methods=['GET'])
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

@bp.route('/api/mensagens/gestao/enviadas', methods=['GET'])
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

@bp.route('/api/mensagens/<int:id_mensagem>/lida', methods=['PATCH'])
def marcar_mensagem_lida(id_mensagem):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            UPDATE mensagens SET lida = 1
            WHERE id_mensagem = %s
              AND ( (direcao = 'aluno_para_gestao' AND %s = 1)
                 OR (direcao = 'gestao_para_aluno' AND id_aluno = %s) )
            """,
            (id_mensagem,
             1 if session.get('gestor_id') else 0,
             session.get('aluno_id') or -1)
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
