"""Moderação de imagens com a Sightengine (roda antes de salvar a foto)."""
import requests

from config import SIGHTENGINE_USER, SIGHTENGINE_SECRET


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
