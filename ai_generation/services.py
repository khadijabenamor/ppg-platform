import requests
from django.conf import settings

# Limite le texte à 3000 caractères max pour éviter les timeouts
MAX_TEXT_LENGTH = 3000

def _call_ollama(prompt: str) -> str:
    url = f"{settings.OLLAMA_URL}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 400,   # limite la longueur de la réponse
            "temperature": 0.5,
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Impossible de contacter Ollama. Assure-toi qu'Ollama est lancé.")
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama met trop de temps à répondre. Réessaie.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erreur Ollama : {str(e)}")


def generate_summary(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Le texte fourni est vide.")

    # Tronque le texte si trop long
    text_court = text[:MAX_TEXT_LENGTH]

    prompt = (
        "Tu es un assistant pédagogique expert. "
        "Génère un résumé clair, structuré et en français "
        "du texte suivant, en 5 à 10 lignes maximum. "
        "Le résumé doit capturer les points essentiels du cours.\n\n"
        f"Texte :\n{text_court}\n\nRésumé :"
    )
    return _call_ollama(prompt)


def extract_keywords(text: str) -> list:
    if not text or not text.strip():
        raise ValueError("Le texte fourni est vide.")

    # Tronque le texte si trop long
    text_court = text[:MAX_TEXT_LENGTH]

    prompt = (
        "Tu es un assistant pédagogique. "
        "Extrais les 10 mots-clés les plus importants du texte suivant. "
        "Réponds UNIQUEMENT avec les mots séparés par des virgules, "
        "sans numérotation, sans explication, sans ponctuation finale.\n\n"
        f"Texte :\n{text_court}\n\nMots-clés :"
    )
    raw = _call_ollama(prompt)
    keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
    return keywords