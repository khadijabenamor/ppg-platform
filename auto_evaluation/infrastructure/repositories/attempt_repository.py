from typing import List, Optional
from auto_evaluation.models import QuizAttempt as QuizAttemptModel
from auto_evaluation.domain.entities import QuizAttempt
from auto_evaluation.domain.repository_interfaces.repositories import QuizAttemptRepositoryInterface


class DjangoQuizAttemptRepository(QuizAttemptRepositoryInterface):
    """Implémentation Django du repository QuizAttempt"""

    def create(self, attempt: QuizAttempt) -> QuizAttempt:
        model = QuizAttemptModel(
            student_id=attempt.student_id,
            quiz_id=attempt.quiz_id,
            score=attempt.score,
            total_points=attempt.total_points,
            answers=attempt.answers,
            completed_at=attempt.completed_at
        )
        model.save()
        attempt.id = model.id
        return attempt

    def get_by_id(self, attempt_id: int) -> Optional[QuizAttempt]:
        try:
            model = QuizAttemptModel.objects.get(pk=attempt_id)
            return self._to_entity(model)
        except QuizAttemptModel.DoesNotExist:
            return None

    def get_by_student(self, student_id: int) -> List[QuizAttempt]:
        models = QuizAttemptModel.objects.filter(student_id=student_id).order_by("-started_at")
        return [self._to_entity(m) for m in models]

    def get_by_student_and_course(self, student_id: int, course_id: str) -> List[QuizAttempt]:
        models = QuizAttemptModel.objects.filter(
            student_id=student_id,
            quiz__course_id=course_id
        ).order_by("-started_at")
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: QuizAttemptModel) -> QuizAttempt:
        return QuizAttempt(
            id=model.id,
            student_id=model.student_id,
            quiz_id=model.quiz_id,
            score=model.score,
            total_points=model.total_points,
            answers=model.answers,
            started_at=model.started_at,
            completed_at=model.completed_at
        )