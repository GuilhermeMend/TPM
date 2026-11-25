"""Configurações lidas do .env e constantes do projeto."""
import os

# Lê o arquivo .env (se existir) para as chaves e segredos
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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



def extensao_permitida(nome_arquivo):
    # Confere se o arquivo tem um "." e se a extensão depois do "."
    # está na lista de extensões permitidas
    return '.' in nome_arquivo and \
        nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS
