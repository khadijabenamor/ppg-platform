from typing import Optional, Dict, Any
from auto_evaluation.domain.entities import Quiz
from auto_evaluation.domain.services.quiz_scoring_service import QuizValidationService


class CreateQuizUseCase:
    """Use Case pour créer un quiz"""

    def __init__(self, quiz_repository):
        self.quiz_repository = quiz_repository
        self.validation_service = QuizValidationService()

    def execute(self, data: Dict[str, Any], created_by_id: Optional[int] = None) -> Dict[str, Any]:
        """Executer le use case"""
        quiz = Quiz(
            title=data.get("title", ""),
            description=data.get("description", ""),
            course_id=data.get("course_id", ""),
            difficulty=data.get("difficulty", "medium"),
            created_by_id=created_by_id
        )

        validation = self.validation_service.validate_quiz(quiz, allow_empty=True)
        if not validation["is_valid"]:
            return {
                "success": False,
                "errors": validation["errors"]
            }

        created_quiz = self.quiz_repository.create(quiz)

        return {
            "success": True,
            "quiz": created_quiz,
            "warnings": validation["warnings"]
        }


class UpdateQuizUseCase:
    """Use Case pour mettre à jour un quiz"""

    def __init__(self, quiz_repository):
        self.quiz_repository = quiz_repository

    def execute(self, quiz_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executer le use case"""
        quiz = self.quiz_repository.get_by_id(quiz_id)
        if not quiz:
            return {
                "success": False,
                "errors": ["Quiz non trouvé"]
            }

        if "title" in data:
            quiz.title = data["title"]
        if "description" in data:
            quiz.description = data["description"]
        if "difficulty" in data:
            quiz.difficulty = data["difficulty"]

        updated_quiz = self.quiz_repository.update(quiz)

        return {
            "success": True,
            "quiz": updated_quiz
        }


class DeleteQuizUseCase:
    """Use Case pour supprimer un quiz"""

    def __init__(self, quiz_repository):
        self.quiz_repository = quiz_repository

    def execute(self, quiz_id: int) -> Dict[str, Any]:
        """Executer le use case"""
        success = self.quiz_repository.delete(quiz_id)

        if not success:
            return {
                "success": False,
                "errors": ["Quiz non trouvé"]
            }

        return {
            "success": True,
            "message": "Quiz supprimé avec succès"
        }