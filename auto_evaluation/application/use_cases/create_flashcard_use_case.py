from typing import Dict, Any, Optional
from auto_evaluation.domain.entities import Flashcard


class CreateFlashcardUseCase:
    """Use Case pour créer une flashcard"""

    def __init__(self, flashcard_repository):
        self.flashcard_repository = flashcard_repository

    def execute(self, data: Dict[str, Any], created_by_id: Optional[int] = None) -> Dict[str, Any]:
        """Executer le use case"""
        flashcard = Flashcard(
            course_id=data.get("course_id", ""),
            question=data.get("question", ""),
            answer=data.get("answer", ""),
            tags=data.get("tags", []),
            created_by_id=created_by_id
        )

        errors = flashcard.validate()
        if errors:
            return {
                "success": False,
                "errors": errors
            }

        created_flashcard = self.flashcard_repository.create(flashcard)

        return {
            "success": True,
            "flashcard": created_flashcard
        }


class UpdateFlashcardUseCase:
    """Use Case pour mettre à jour une flashcard"""

    def __init__(self, flashcard_repository):
        self.flashcard_repository = flashcard_repository

    def execute(self, flashcard_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executer le use case"""
        flashcard = self.flashcard_repository.get_by_id(flashcard_id)
        if not flashcard:
            return {
                "success": False,
                "errors": ["Flashcard non trouvée"]
            }

        if "question" in data:
            flashcard.question = data["question"]
        if "answer" in data:
            flashcard.answer = data["answer"]
        if "tags" in data:
            flashcard.tags = data["tags"]

        errors = flashcard.validate()
        if errors:
            return {
                "success": False,
                "errors": errors
            }

        updated_flashcard = self.flashcard_repository.update(flashcard)

        return {
            "success": True,
            "flashcard": updated_flashcard
        }


class MarkFlashcardReviewedUseCase:
    """Use Case pour marquer une flashcard comme révisée"""

    def __init__(self, flashcard_repository):
        self.flashcard_repository = flashcard_repository

    def execute(self, flashcard_id: int) -> Dict[str, Any]:
        """Executer le use case"""
        flashcard = self.flashcard_repository.get_by_id(flashcard_id)
        if not flashcard:
            return {
                "success": False,
                "errors": ["Flashcard non trouvée"]
            }

        flashcard.mark_as_reviewed()
        updated_flashcard = self.flashcard_repository.update(flashcard)

        return {
            "success": True,
            "flashcard": updated_flashcard
        }