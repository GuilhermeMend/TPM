"""Fotos da galeria (upload, listagem, exclusão) e comentários."""
from flask import Blueprint, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
import mysql.connector
import os
import uuid

from config import PASTA_UPLOADS, extensao_permitida
from db import conectar_banco
from helpers import negar, valor, turma_existe, turma_do_aluno
from moderacao import verificar_imagem_adequada

bp = Blueprint('fotos', __name__)


# ================= SERVIR AS IMAGENS ENVIADAS =================
#
# Rota: GET /uploads/<nome_arquivo>
# Pra que serve: o navegador usa essa URL como "src" da tag <img> pra
# mostrar a foto. O Flask lê o arquivo direto da pasta PASTA_UPLOADS.

@bp.route('/uploads/<nome_arquivo>', methods=['GET'])
def servir_imagem(nome_arquivo):
    return send_from_directory(PASTA_UPLOADS, nome_arquivo)



# ================= PUBLICAR FOTO (GESTÃO) =================
#
# Rota: POST /api/fotos
# Pra que serve: a gestão envia um arquivo de imagem + uma legenda.
# O envio é multipart/form-data (não é JSON, porque tem arquivo junto),
# então os dados chegam em request.form (texto) e request.files (arquivo).

@bp.route('/api/fotos', methods=['POST'])
def publicar_foto():

    # Confere se o campo "imagem" veio no formulário
    if 'imagem' not in request.files:
        return jsonify({
            "sucesso": False,
            "mensagem": "Nenhuma imagem foi enviada."
        }), 400

    arquivo = request.files['imagem']
    legenda = request.form.get('legenda', '').strip()
    # Turma que pode ver a foto. Vazio = todas as turmas.
    turma_foto = request.form.get('turma', '').strip() or None
    gestor_id = session.get('gestor_id')

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

        if turma_foto and not turma_existe(cursor, turma_foto):
            if os.path.exists(caminho_completo):
                os.remove(caminho_completo)
            return jsonify({
                "sucesso": False,
                "mensagem": "Essa turma não existe."
            }), 400

        cursor.execute(
            """
            INSERT INTO fotos (nome_arquivo, legenda, id_gestor, turma)
            VALUES (%s, %s, %s, %s)
            """,
            (nome_no_disco, legenda, gestor_id, turma_foto)
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

@bp.route('/api/fotos', methods=['GET'])
def listar_fotos():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        filtros = []
        parametros = []

        if session.get('gestor_id'):
            # Gestão vê tudo e pode filtrar por turma (?turma=3_ano_B)
            filtro_turma = request.args.get('turma', '').strip()
            if filtro_turma:
                filtros.append("f.turma = %s")
                parametros.append(filtro_turma)
        else:
            # Aluno: fotos para todos (turma vazia) + as da sua turma
            turma_aluno = turma_do_aluno(cursor, session.get('aluno_id'))
            if turma_aluno:
                filtros.append("(f.turma IS NULL OR f.turma = %s)")
                parametros.append(turma_aluno)
            else:
                filtros.append("f.turma IS NULL")

        where = ("WHERE " + " AND ".join(filtros)) if filtros else ""

        cursor.execute(
            f"""
            SELECT
                f.id_foto,
                f.nome_arquivo,
                f.legenda,
                f.turma,
                f.data_postagem,
                g.nome AS nome_gestor,
                COUNT(c.id_comentario) AS total_comentarios
            FROM fotos f
            LEFT JOIN gestão g ON g.id_gestor = f.id_gestor
            LEFT JOIN comentarios c ON c.id_foto = f.id_foto
            {where}
            GROUP BY f.id_foto, f.nome_arquivo, f.legenda, f.turma,
                     f.data_postagem, g.nome
            ORDER BY f.data_postagem DESC
            """,
            tuple(parametros)
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

@bp.route('/api/fotos/<int:id_foto>', methods=['DELETE'])
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

@bp.route('/api/fotos/<int:id_foto>/comentarios', methods=['GET'])
def listar_comentarios(id_foto):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        if not _foto_visivel(cursor, id_foto):
            return jsonify({
                "sucesso": False,
                "mensagem": "Foto não encontrada."
            }), 404

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

@bp.route('/api/fotos/<int:id_foto>/comentarios', methods=['POST'])
def comentar_foto(id_foto):

    dados = request.get_json(silent=True) or {}

    aluno_id = session.get('aluno_id')
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

        if len(texto) > 500:
            return jsonify({
                "sucesso": False,
                "mensagem": "O comentário pode ter no máximo 500 caracteres."
            }), 400

        if not _foto_visivel(cursor, id_foto):
            return jsonify({
                "sucesso": False,
                "mensagem": "Foto não encontrada."
            }), 404

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


# ================= APOIO: VISIBILIDADE DE FOTOS =================

def _foto_visivel(cursor, id_foto):
    """Gestão vê toda foto; aluno só a geral (sem turma) ou a da própria turma."""
    cursor.execute("SELECT turma FROM fotos WHERE id_foto = %s", (id_foto,))
    foto = cursor.fetchone()
    if foto is None:
        return False
    turma_da_foto = valor(foto, 'turma')
    if session.get('gestor_id') or turma_da_foto is None:
        return True
    return turma_da_foto == turma_do_aluno(cursor, session.get('aluno_id'))


# ================= GESTÃO: APAGAR COMENTÁRIO =================
# Rota: DELETE /api/comentarios/<id>

@bp.route('/api/comentarios/<int:id_comentario>', methods=['DELETE'])
def excluir_comentario(id_comentario):

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "DELETE FROM comentarios WHERE id_comentario = %s", (id_comentario,)
        )
        if cursor.rowcount == 0:
            return negar("Comentário não encontrado.", 404)

        conexao.commit()
        return jsonify({"sucesso": True, "mensagem": "Comentário apagado!"}), 200

    except mysql.connector.Error as erro:
        print(f"Erro no banco: {erro}")
        if conexao:
            conexao.rollback()
        return negar("Erro ao apagar o comentário.", 500)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
