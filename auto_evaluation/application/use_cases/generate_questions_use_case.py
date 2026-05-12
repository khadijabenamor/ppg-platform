from typing import Dict, Any
from django.conf import settings
from auto_evaluation.domain.services.groq_ai_service import GroqAIService, GroqAIServiceFactory, GroqAIServiceError


class GenerateQuestionsUseCase:
    """Use Case pour générer des questions via IA (Groq/Llama)"""

    def __init__(self, quiz_repository, question_repository, ai_service=None):
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.ai_service = ai_service

    def _get_ai_service(self):
        """Récupérer le service IA (Groq par défaut)"""
        if self.ai_service:
            return self.ai_service
        
        # Utiliser Groq selon la config
        if getattr(settings, 'IA_PROVIDER', 'groq') == 'groq':
            try:
                return GroqAIServiceFactory.get_service()
            except GroqAIServiceError:
                return None
        return None

    def execute(self, quiz_id: int, course_content: str, count: int = 5) -> Dict[str, Any]:
        """Executer le use case"""
        quiz = self.quiz_repository.get_by_id(quiz_id)
        if not quiz:
            return {
                "success": False,
                "errors": ["Quiz non trouvé"]
            }

        if not course_content:
            return {
                "success": False,
                "errors": ["Le contenu du cours est requis"]
            }

        ai_service = self._get_ai_service()
        
        if not ai_service:
            return {
                "success": False,
                "errors": ["Service IA non disponible. Vérifiez GROQ_API_KEY."]
            }

        try:
            generated_questions = ai_service.generate_quiz_questions(course_content, count)

            created_questions = []
            for i, q in enumerate(generated_questions):
                from auto_evaluation.domain.entities import Question
                question = Question(
                    quiz_id=quiz_id,
                    question_type=q.question_type,
                    question_text=q.question_text,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    points=q.points,
                    order=i + 1
                )
                created_question = self.question_repository.create(question)
                created_questions.append(created_question)

            quiz.is_ai_generated = True
            self.quiz_repository.update(quiz)

            return {
                "success": True,
                "questions": created_questions,
                "count": len(created_questions),
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