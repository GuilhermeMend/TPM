"""Turmas: listar, criar, detalhar, editar, excluir, alunos da turma e painel."""
from flask import Blueprint, request, jsonify, session
import mysql.connector

from db import conectar_banco
from helpers import negar

bp = Blueprint('turmas', __name__)


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

@bp.route('/api/turmas', methods=['GET'])
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

@bp.route('/api/estatisticas', methods=['GET'])
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

        # Professores: nomes diferentes entre as turmas cadastradas
        cursor.execute(
            "SELECT COUNT(DISTINCT professor) FROM turmas_cadastradas"
        )
        total_professores = cursor.fetchone()[0]

        # Fotos publicadas
        cursor.execute("SELECT COUNT(*) FROM fotos")
        total_fotos = cursor.fetchone()[0]

        return jsonify({
            "sucesso": True,
            "total_turmas": total_turmas,
            "total_alunos": total_alunos,
            "total_professores": total_professores,
            "total_fotos": total_fotos
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

@bp.route('/api/turmas', methods=['POST'])
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

@bp.route('/api/turmas/<turma>/alunos', methods=['GET'])
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
            SELECT id_aluno, ra_aluno, nome_aluno,
                   (id_login IS NOT NULL) AS tem_login
            FROM turmas
            WHERE turma = %s
            ORDER BY nome_aluno
            """,
            (turma,)
        )

        alunos_lista = cursor.fetchall()

        # O RA é dado pessoal: só a gestão recebe. Aluno vê só nome.
        if not session.get('gestor_id'):
            for aluno in alunos_lista:
                aluno.pop('ra_aluno', None)

        # Ficha da turma (professor responsável, turno). Turmas antigas, que
        # só existem pelos alunos, não têm ficha: nesse caso vai None.
        cursor.execute(
            """
            SELECT nome, professor, turno
            FROM turmas_cadastradas
            WHERE codigo = %s
            """,
            (turma,)
        )
        ficha = cursor.fetchone()

        return jsonify({
            "sucesso": True,
            "turma": ficha,
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


# ================= GESTÃO: DETALHES / EDITAR / EXCLUIR TURMA =================
# Rotas: GET, PUT e DELETE em /api/turmas/<turma>   (só gestão)

@bp.route('/api/turmas/<turma>', methods=['GET'])
def detalhes_turma(turma):

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT codigo, nome, professor, turno, cor
            FROM turmas_cadastradas WHERE codigo = %s
            """,
            (turma,)
        )
        dados = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) AS total FROM turmas WHERE turma = %s", (turma,))
        total_alunos = cursor.fetchone()['total']

        # Turma antiga, que só existe porque tem alunos (sem ficha cadastrada)
        if dados is None:
            if total_alunos == 0:
                return negar("Turma não encontrada.", 404)
            dados = {"codigo": turma, "nome": None, "professor": None,
                     "turno": None, "cor": None}

        cursor.execute("SELECT COUNT(*) AS total FROM fotos WHERE turma = %s", (turma,))

        dados['total_alunos'] = total_alunos
        dados['total_fotos'] = cursor.fetchone()['total']

        return jsonify({"sucesso": True, "turma": dados}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        return negar("Erro ao buscar a turma.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@bp.route('/api/turmas/<turma>', methods=['PUT'])
def editar_turma(turma):

    dados = request.get_json(silent=True) or {}
    nome = (dados.get('nome') or '').strip()
    professor = (dados.get('professor') or '').strip()
    turno = (dados.get('turno') or '').strip()
    cor = (dados.get('cor') or '').strip()

    if not nome or not professor:
        return negar("Preencha nome e professor.", 400)

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("SELECT 1 FROM turmas_cadastradas WHERE codigo = %s", (turma,))
        ja_tem_ficha = cursor.fetchone() is not None

        if ja_tem_ficha:
            cursor.execute(
                """
                UPDATE turmas_cadastradas
                SET nome = %s, professor = %s, turno = %s, cor = %s
                WHERE codigo = %s
                """,
                (nome[:100], professor[:100], turno[:20], cor[:100], turma)
            )
        else:
            # Turma antiga que só existia pelos alunos: cria a ficha agora
            cursor.execute("SELECT 1 FROM turmas WHERE turma = %s LIMIT 1", (turma,))
            if cursor.fetchone() is None:
                return negar("Turma não encontrada.", 404)

            cursor.execute(
                """
                INSERT INTO turmas_cadastradas (codigo, nome, professor, turno, cor)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (turma[:50], nome[:100], professor[:100], turno[:20], cor[:100])
            )

        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Turma atualizada!"}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if conexao:
            conexao.rollback()
        return negar("Erro ao atualizar a turma.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@bp.route('/api/turmas/<turma>', methods=['DELETE'])
def excluir_turma(turma):

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        # Não apaga turma que ainda tem gente ou foto dentro (evita perder dado)
        cursor.execute("SELECT COUNT(*) FROM turmas WHERE turma = %s", (turma,))
        total_alunos = cursor.fetchone()[0]
        if total_alunos > 0:
            return negar(
                f"Esta turma ainda tem {total_alunos} aluno(s). "
                "Mova ou exclua os alunos antes de excluir a turma.", 409)

        cursor.execute("SELECT COUNT(*) FROM fotos WHERE turma = %s", (turma,))
        total_fotos = cursor.fetchone()[0]
        if total_fotos > 0:
            return negar(
                f"Esta turma ainda tem {total_fotos} foto(s) publicada(s) só para ela. "
                "Exclua as fotos antes de excluir a turma.", 409)

        cursor.execute("DELETE FROM turmas_cadastradas WHERE codigo = %s", (turma,))
        if cursor.rowcount == 0:
            return negar("Turma não encontrada.", 404)

        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Turma excluída!"}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if conexao:
            conexao.rollback()
        return negar("Erro ao excluir a turma.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
