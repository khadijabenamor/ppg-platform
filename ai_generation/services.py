import requests
from django.conf import settings


def _call_ollama(prompt: str) -> str:
    """
    Envoie un prompt à Ollama (qui tourne en local sur le PC)
    et retourne la réponse texte.
    """
    url = f"{settings.OLLAMA_URL}/api/generate"

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,   # on veut la réponse complète d'un coup
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Impossible de contacter Ollama. "
            "Assure-toi qu'Ollama est lancé sur ton PC (ollama serve)."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama met trop de temps à répondre. Réessaie.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erreur Ollama : {str(e)}")


def generate_summary(text: str) -> str:
    """
    Génère un résumé automatique depuis un texte brut via Ollama.

    Args:
        text: Le texte source à résumer.

    Returns:
        Le résumé généré sous forme de string.

    Raises:
        ValueError: Si le texte fourni est vide.
    """
    if not text or not text.strip():
        raise ValueError("Le texte fourni est vide.")

    prompt = (
        "Tu es un assistant pédagogique expert. "
        "Génère un résumé clair, structuré et en français "
        "du texte suivant, en 5 à 10 lignes maximum. "
        "Le résumé doit capturer les points essentiels du cours.\n\n"
        f"Texte :\n{text}\n\nRésumé :"
    )

    return _call_ollama(prompt)


def extract_keywords(text: str) -> list:
    """
    Extrait les mots-clés importants d'un texte via Ollama.

    Args:
        text: Le texte source.

    Returns:
        Une liste de mots-clés extraits.

    Raises:
        ValueError: Si le texte fourni est vide.
    """
    if not text or not text.strip():
        raise ValueError("Le texte fourni est vide.")

    prompt = (
        "Tu es un assistant pédagogique. "
        "Extrais les 10 mots-clés les plus importants du texte suivant. "
        "Réponds UNIQUEMENT avec les mots séparés par des virgules, "
        "sans numérotation, sans explication, sans ponctuation finale.\n\n"
        f"Texte :\n{text}\n\nMots-clés :"
    )

    raw = _call_ollama(prompt)
    keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
    return keywords
