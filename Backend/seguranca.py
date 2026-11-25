"""Permissões por rota, bloqueio de tentativas de login e cache.

registrar_seguranca(app) liga tudo no app. As tabelas abaixo usam o NOME DA
FUNÇÃO da rota (ex.: 'login'), sem o prefixo do blueprint (ex.: 'auth.login').
"""
import time

from flask import request, session

from helpers import negar

# ================= AUTENTICAÇÃO E PERMISSÕES =================
#
# Quem está logado fica guardado na SESSÃO do Flask (cookie assinado com a
# SECRET_KEY): session['aluno_id'] para aluno e session['gestor_id'] para
# gestão. O navegador não consegue forjar isso, ao contrário de um id
# mandado no corpo da requisição.
#
# A tabela abaixo diz quem pode chamar cada rota (pelo nome da função).
# Rota que NÃO está na tabela exige login: o padrão é negar.

ACESSO_PUBLICO = {'login', 'login_gestao', 'servir_imagem', 'sessao_atual', 'logout'}

ACESSO_GESTAO = {
    'cadastro', 'adicionar_turma', 'publicar_foto',
    'excluir_foto', 'gestao_envia_mensagem', 'listar_alunos',
    'caixa_entrada_gestao', 'enviadas_gestao',
    'detalhes_turma', 'editar_turma', 'excluir_turma',
    'editar_aluno', 'redefinir_senha_aluno', 'excluir_aluno',
    'excluir_comentario'
}

ACESSO_ALUNO = {
    'comentar_foto', 'aluno_envia_mensagem',
    'caixa_entrada_aluno', 'enviadas_aluno'
}

# Rotas do aluno que têm o id do aluno na URL: só o próprio aluno acessa
ROTAS_COM_ID_DO_ALUNO = {'caixa_entrada_aluno', 'enviadas_aluno'}


def _nome_da_rota():
    # request.endpoint vem como 'blueprint.funcao'; a tabela usa só 'funcao'
    if request.endpoint is None:
        return None
    return request.endpoint.rsplit('.', 1)[-1]


# ---------- limite de tentativas de login (por IP) ----------
# Guarda em memória os horários das falhas de cada IP. Passou de
# MAX_FALHAS_LOGIN dentro da janela, o IP fica bloqueado até a janela esvaziar.
# (Zera quando o servidor reinicia — suficiente pra um projeto escolar.)

MAX_FALHAS_LOGIN = 5
JANELA_LOGIN_SEG = 300
_falhas_login = {}


def _falhas_recentes(ip):
    agora = time.time()
    recentes = [t for t in _falhas_login.get(ip, []) if agora - t < JANELA_LOGIN_SEG]
    if recentes:
        _falhas_login[ip] = recentes
    else:
        _falhas_login.pop(ip, None)
    return recentes


def _login_bloqueado():
    return len(_falhas_recentes(request.remote_addr)) >= MAX_FALHAS_LOGIN


def registrar_seguranca(app):

    @app.before_request
    def verificar_permissao():

        # Pré-requisição do CORS (OPTIONS) e rotas inexistentes passam direto
        if request.method == 'OPTIONS' or request.endpoint is None:
            return None

        endpoint = _nome_da_rota()

        # Trava de tentativas nos logins (força bruta)
        if endpoint in ('login', 'login_gestao') and _login_bloqueado():
            return negar("Muitas tentativas. Espere alguns minutos e tente de novo.", 429)

        if endpoint in ACESSO_PUBLICO:
            return None

        eh_gestor = bool(session.get('gestor_id'))
        eh_aluno = bool(session.get('aluno_id'))

        if endpoint in ACESSO_GESTAO:
            if not eh_gestor:
                return negar("Acesso restrito à gestão. Faça login como gestão.", 401)
            return None

        if endpoint in ACESSO_ALUNO:
            if not eh_aluno:
                return negar("Acesso restrito a alunos. Faça login como aluno.", 401)
            if endpoint in ROTAS_COM_ID_DO_ALUNO and \
                    request.view_args.get('id_aluno') != session.get('aluno_id'):
                return negar("Você só pode ver as suas próprias mensagens.", 403)
            return None

        # Todas as outras: qualquer usuário logado (aluno ou gestão)
        if not (eh_gestor or eh_aluno):
            return negar("Faça login para continuar.", 401)

        return None

    @app.after_request
    def contar_falhas_de_login(resposta):
        # Respostas da API nunca ficam guardadas em cache (dados de quem está logado)
        endpoint = _nome_da_rota()
        if request.path.startswith('/api/') or endpoint in ('login', 'login_gestao', 'logout'):
            resposta.headers['Cache-Control'] = 'no-store'
        if endpoint in ('login', 'login_gestao'):
            ip = request.remote_addr
            if resposta.status_code == 401:
                _falhas_login.setdefault(ip, []).append(time.time())
            elif resposta.status_code == 200:
                _falhas_login.pop(ip, None)
        return resposta
