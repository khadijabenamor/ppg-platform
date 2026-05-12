from typing import List, Optional
from auto_evaluation.models import Flashcard as FlashcardModel
from auto_evaluation.domain.entities import Flashcard
from auto_evaluation.domain.repository_interfaces.repositories import FlashcardRepositoryInterface


class DjangoFlashcardRepository(FlashcardRepositoryInterface):
    """Implémentation Django du repository Flashcard"""

    def create(self, flashcard: Flashcard) -> Flashcard:
        model = FlashcardModel(
            course_id=flashcard.course_id,
            question=flashcard.question,
            answer=flashcard.answer,
            tags=flashcard.tags,
            created_by_id=flashcard.created_by_id,
            is_ai_generated=flashcard.is_ai_generated,
            is_reviewed=flashcard.is_reviewed
        )
        model.save()
        flashcard.id = model.id
        return flashcard

    def get_by_id(self, flashcard_id: int) -> Optional[Flashcard]:
        try:
            model = FlashcardModel.objects.get(pk=flashcard_id)
            return self._to_entity(model)
        except FlashcardModel.DoesNotExist:
            return None

    def get_all(self) -> List[Flashcard]:
        models = FlashcardModel.objects.all()
        return [self._to_entity(m) for m in models]

    def get_by_course(self, course_id: str) -> List[Flashcard]:
        models = FlashcardModel.objects.filter(course_id=course_id)
        return [self._to_entity(m) for m in models]

    def update(self, flashcard: Flashcard) -> Flashcard:
        model = FlashcardModel.objects.get(pk=flashcard.id)
        model.course_id = flashcard.course_id
        model.question = flashcard.question
        model.answer = flashcard.answer
        model.tags = flashcard.tags
        model.is_reviewed = flashcard.is_reviewed
        model.save()
        return flashcard

    def delete(self, flashcard_id: int) -> bool:
        try:
            model = FlashcardModel.objects.get(pk=flashcard_id)
            model.delete()
            return True
        except FlashcardModel.DoesNotExist:
            return False

    def _to_entity(self, model: FlashcardModel) -> Flashcard:
        return Flashcard(
            id=model.id,
            course_id=model.course_id,
            question=model.question,
            answer=model.answer,
            tags=model.tags,
            created_by_id=model.created_by_id,
            is_ai_generated=model.is_ai_generated,
            is_reviewed=model.is_reviewed,
            created_at=model.created_at,
            updated_at=model.updated_at
        )