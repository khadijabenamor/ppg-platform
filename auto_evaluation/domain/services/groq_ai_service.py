"""
Service IA pour la génération de contenu éducatif via Groq (Llama)
Architecture DDD - Domain Layer
"""
import os
import json
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class GeneratedQuizQuestion:
    """Question générée par l'IA"""
    question_text: str
    question_type: str  # 'qcm', 'true_false', 'open'
    options: List[str]
    correct_answer: str
    explanation: str
    points: int


@dataclass
class GeneratedFlashcard:
    """Flashcard générée par l'IA"""
    question: str
    answer: str
    tags: List[str]


class GroqAIServiceError(Exception):
    """Exception custom pour les erreurs du service IA"""
    pass


class GroqAIService:
    """
    Service IA pour générer des questions de quiz et des flashcards.
    Utilise l'API Groq avec le modèle Llama.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        if not self.api_key:
            raise GroqAIServiceError("GROQ_API_KEY non configurée")
    
    def _call_groq(self, prompt: str, max_tokens: int = 2000) -> str:
        """Appeler l'API Groq"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Tu es un assistant pédagogique expert en création de quiz et flashcards. Réponds uniquement en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            raise GroqAIServiceError(f"Erreur Groq: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def generate_quiz_questions(self, content: str, count: int = 5) -> List[GeneratedQuizQuestion]:
        """
        Générer des questions de quiz à partir d'un contenu.
        
        Args:
            content: Contenu du cours
            count: Nombre de questions à générer
            
        Returns:
            Liste de GeneratedQuizQuestion
        """
        prompt = f"""Génère {count} questions d'évaluation de type QCM (Multiple Choice) basées sur le contenu suivant.
Format JSON avec un tableau 'questions' contenant des objets avec:
- question_text: le texte de la question
- question_type: TOUJOURS 'qcm' 
- options: tableau de 4 options de réponse (A, B, C, D)
- correct_answer: la bonne réponse (A, B, C, ou D)
- explanation: explication courte de la réponse
- points: nombre de points (1-5)

IMPORTANT: Génère uniquement des questions QCM avec 4 options. Pas de questions true_false ou open.

Contenu du cours:
{content[:3000]}

Réponds uniquement avec ce JSON:
{{"questions": [...]}}"""
        
        try:
            response = self._call_groq(prompt, max_tokens=2000)
            data = json.loads(response)
            questions_data = data.get("questions", [])
            
            questions = []
            for i, q in enumerate(questions_data[:count]):
                questions.append(GeneratedQuizQuestion(
                    question_text=q.get("question_text", ""),
                    question_type=q.get("question_type", "qcm"),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", ""),
                    explanation=q.get("explanation", ""),
                    points=q.get("points", 1)
                ))
            
            return questions
            
        except json.JSONDecodeError as e:
            raise GroqAIServiceError(f"Erreur parsing JSON: {str(e)}")
        except Exception as e:
            raise GroqAIServiceError(f"Erreur génération questions: {str(e)}")
    
    def generate_flashcards(self, content: str, count: int = 5) -> List[GeneratedFlashcard]:
        """
        Générer des flashcards à partir d'un contenu.
        
        Args:
            content: Contenu du cours
            count: Nombre de flashcards à générer
            
        Returns:
            Liste de GeneratedFlashcard
        """
        prompt = f"""Génère {count} flashcards (questions/réponses) basées sur le contenu suivant.
Format JSON avec un tableau 'flashcards' contenant des objets avec:
- question: la question courte
- answer: la réponse courte (1-2 phrases max)
- tags: tableau de 2-3 tags pertinents

Contenu du cours:
{content[:3000]}

Réponds uniquement avec ce JSON:
{{"flashcards": [...]}}"""
        
        try:
            response = self._call_groq(prompt, max_tokens=1500)
            data = json.loads(response)
            flashcards_data = data.get("flashcards", [])
            
            flashcards = []
            for f in flashcards_data[:count]:
                flashcards.append(GeneratedFlashcard(
                    question=f.get("question", ""),
                    answer=f.get("answer", ""),
                    tags=f.get("tags", [])
                ))
            
            return flashcards
            
        except json.JSONDecodeError as e:
            raise GroqAIServiceError(f"Erreur parsing JSON: {str(e)}")
        except Exception as e:
            raise GroqAIServiceError(f"Erreur génération flashcards: {str(e)}")
    
    def validate_answer(self, question: str, user_answer: str, correct_answer: str) -> Dict[str, Any]:
        """
        Valider une réponse et fournir un feedback.
        
        Args:
            question: La question posée
            user_answer: La réponse de l'utilisateur
            correct_answer: La bonne réponse
            
        Returns:
            Dict avec 'is_correct', 'feedback', 'explanation'
        """
        prompt = f"""Tu dois valider une réponse de quiz.
Question: {question}
Réponse attendue: {correct_answer}
Réponse de l'utilisateur: {user_answer}

Réponds en JSON:
{{
    "is_correct": true/false,
    "feedback": "Courte appréciation",
    "explanation": "Explication si incorrect"
}}"""
        
        try:
            response = self._call_groq(prompt, max_tokens=500)
            return json.loads(response)
        except:
            # Fallback simple
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            return {
                "is_correct": is_correct,
                "feedback": "Correct!" if is_correct else "Incorrect",
                "explanation": correct_answer if not is_correct else ""
            }


class GroqAIServiceFactory:
    """Factory pour créer le service IA"""
    
    _instance: Optional[GroqAIService] = None
    
    @classmethod
    def get_service(cls, api_key: Optional[str] = None) -> GroqAIService:
        """Récupérer ou créer l'instance du service (Singleton)"""
        if cls._instance is None:
            cls._instance = GroqAIService(api_key=api_key)
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Réinitialiser l'instance (pour les tests)"""
        cls._instance = None