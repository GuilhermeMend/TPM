"""Funções pequenas usadas por mais de um arquivo de rotas."""
from flask import jsonify


def negar(mensagem, status):
    return jsonify({"sucesso": False, "mensagem": mensagem}), status


def valor(linha, chave, posicao=0):
    """Lê o valor de uma linha de cursor comum (tupla) ou dictionary (dict)."""
    if linha is None:
        return None
    return linha[chave] if isinstance(linha, dict) else linha[posicao]


def turma_existe(cursor, codigo):
    cursor.execute(
        """
        SELECT 1 FROM turmas_cadastradas WHERE codigo = %s
        UNION
        SELECT 1 FROM turmas WHERE turma = %s
        """,
        (codigo, codigo)
    )
    return cursor.fetchone() is not None


def turma_do_aluno(cursor, aluno_id):
    """Turma do aluno logado (pela matrícula ligada ao login) ou None."""
    if not aluno_id:
        return None
    cursor.execute(
        "SELECT turma FROM turmas WHERE id_login = %s LIMIT 1", (aluno_id,)
    )
    return valor(cursor.fetchone(), 'turma')


def validar_nome_ra(nome, ra):
    if not nome or not ra:
        return "Nome e RA são obrigatórios."
    if len(nome) > 50 or len(ra) > 50:
        return "Nome e RA podem ter no máximo 50 caracteres."
    return None
