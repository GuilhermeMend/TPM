from flask import Flask
from flask_cors import CORS
from datetime import timedelta
import os

# config.py lê o .env, então precisa ser importado antes do resto
import config  # noqa: F401
from seguranca import registrar_seguranca
from rotas import TODOS as BLUEPRINTS

# Criação da aplicação Flask
app = Flask(__name__)

# Chave usada para assinar o cookie de sessão (login da gestão).
# Defina SECRET_KEY no .env; sem ela, é gerada uma aleatória a cada
# inicialização (o login da gestão cai sempre que o servidor reinicia).
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)

# O cookie de sessão não pode ser lido por JavaScript (HttpOnly) e só é
# enviado em navegação do próprio site (SameSite=Lax), o que também
# barra CSRF vindo de outros sites. Em produção com HTTPS, defina
# SESSION_COOKIE_SECURE=1 no .env.
# Login expira após 30 min SEM usar o site (cada requisição renova o prazo).
app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE') == '1'
)

# Limite de tamanho do arquivo enviado (5 MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Permite que o JavaScript do navegador (Live Server, porta 5501) acesse
# o Flask e envie o cookie de sessão junto (supports_credentials).
# IMPORTANTE: abra o site por http://localhost:5501 (não 127.0.0.1),
# senão o navegador não envia o cookie.
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5501", "http://127.0.0.1:5501"]
)

# Permissões por rota, trava de tentativas de login e cache
registrar_seguranca(app)

# Rotas: cada arquivo em rotas/ é um Blueprint
for blueprint in BLUEPRINTS:
    app.register_blueprint(blueprint)


# ================= INICIAR SERVIDOR =================

if __name__ == "__main__":

    # Inicia o servidor Flask na porta 5000
    app.run(
        host="localhost",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
