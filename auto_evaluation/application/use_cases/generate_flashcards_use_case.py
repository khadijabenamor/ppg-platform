from typing import Dict, Any, Optional
from django.conf import settings
from auto_evaluation.domain.entities import Flashcard
from auto_evaluation.domain.services.groq_ai_service import GroqAIService, GroqAIServiceFactory, GroqAIServiceError


class GenerateFlashcardsUseCase:
    """Use Case pour générer des flashcards via IA (Groq/Llama)"""

    def __init__(self, flashcard_repository, ai_service=None):
        self.flashcard_repository = flashcard_repository
        self.ai_service = ai_service

    def _get_ai_service(self):
        """Récupérer le service IA (Groq par défaut)"""
        if self.ai_service:
            return self.ai_service
        
        if getattr(settings, 'IA_PROVIDER', 'groq') == 'groq':
            try:
                return GroqAIServiceFactory.get_service()
            except GroqAIServiceError:
                return None
        return None

    def execute(self, course_content: str, course_id: str, count: int = 5, created_by_id: Optional[int] = None, tags: list = None) -> Dict[str, Any]:
        """Executer le use case"""
        if not course_content:
            return {
                "success": False,
                "errors": ["Le contenu du cours est requis"]
            }

        user_tags = tags or []

        ai_service = self._get_ai_service()
        
        if not ai_service:
            return {
                "success": False,
                "errors": ["Service IA non disponible. Vérifiez GROQ_API_KEY."]
            }

        try:
            generated_flashcards = ai_service.generate_flashcards(course_content, count)

            created_flashcards = []
            for fc in generated_flashcards:
                combined_tags = list(set(fc.tags + user_tags))
                flashcard = Flashcard(
                    course_id=course_id,
                    question=fc.question,
                    answer=fc.answer,
                    tags=combined_tags,
                    created_by_id=created_by_id,
                    is_ai_generated=True
                )

                errors = flashcard.validate()
                if errors:
                    continue

                created = self.flashcard_repository.create(flashcard)
                created_flashcards.append(created)

            return {
                "success": True,
                "flashcards": created_flashcards,
                "count": len(created_flashcards),
                "provider": "groq"
            }

        except GroqAIServiceError as e:
            return {
                "success": False,
                "errors": [str(e)]
            }
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Erreur lors de la génération: {str(e)}"]
            }