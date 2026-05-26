import os
import requests
from django.conf import settings

MAX_TEXT_LENGTH = 3000


def _call_groq(prompt: str) -> str:
    """
    Appelle l'API Groq (cloud) pour générer du texte.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY non configurée dans le fichier .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Tu es un assistant pédagogique expert. Réponds toujours en français."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.5,
        "max_tokens": 1000,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Impossible de contacter l'API Groq. Vérifie ta connexion Internet.")
    except requests.exceptions.Timeout:
        raise TimeoutError("L'API Groq met trop de temps à répondre. Réessaie.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erreur API Groq : {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Erreur inattendue : {str(e)}")


def generate_summary(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Le texte fourni est vide.")

    text_court = text[:MAX_TEXT_LENGTH]

    prompt = (
        "Tu es un assistant pédagogique expert. "
        "Génère un résumé clair, structuré et en français "
        "du texte suivant, en 5 à 10 lignes maximum. "
        "Le résumé doit capturer les points essentiels du cours.\n\n"
        f"Texte :\n{text_court}\n\nRésumé :"
    )
    return _call_groq(prompt)


def extract_keywords(text: str) -> list:
    if not text or not text.strip():
        raise ValueError("Le texte fourni est vide.")

    text_court = text[:MAX_TEXT_LENGTH]

    prompt = (
        "Tu es un assistant pédagogique. "
        "Extrais les 10 mots-clés les plus importants du texte suivant. "
        "Réponds UNIQUEMENT avec les mots séparés par des virgules, "
        "sans numérotation, sans explication, sans ponctuation finale.\n\n"
        f"Texte :\n{text_court}\n\nMots-clés :"
    )
    raw = _call_groq(prompt)
    keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
    return keywords