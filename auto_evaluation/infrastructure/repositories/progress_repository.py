from typing import List, Optional
from auto_evaluation.models import StudentProgress as StudentProgressModel
from auto_evaluation.domain.entities import StudentProgress
from auto_evaluation.domain.repository_interfaces.repositories import StudentProgressRepositoryInterface


class DjangoStudentProgressRepository(StudentProgressRepositoryInterface):
    """Implémentation Django du repository StudentProgress"""

    def create(self, progress: StudentProgress) -> StudentProgress:
        model = StudentProgressModel(
            student_id=progress.student_id,
            course_id=progress.course_id,
            total_quizzes=progress.total_quizzes,
            completed_quizzes=progress.completed_quizzes,
            total_score=progress.total_score,
            average_score=progress.average_score,
            streak_days=progress.streak_days,
            last_activity=progress.last_activity
        )
        model.save()
        progress.id = model.id
        return progress

    def get_by_id(self, progress_id: int) -> Optional[StudentProgress]:
        try:
            model = StudentProgressModel.objects.get(pk=progress_id)
            return self._to_entity(model)
        except StudentProgressModel.DoesNotExist:
            return None

    def get_by_student(self, student_id: int) -> List[StudentProgress]:
        models = StudentProgressModel.objects.filter(student_id=student_id)
        return [self._to_entity(m) for m in models]

    def get_by_student_and_course(self, student_id: int, course_id: str) -> Optional[StudentProgress]:
        try:
            model = StudentProgressModel.objects.get(student_id=student_id, course_id=course_id)
            return self._to_entity(model)
        except StudentProgressModel.DoesNotExist:
            return None

    def create(self, progress: StudentProgress) -> StudentProgress:
        model = StudentProgressModel.objects.create(
            student_id=progress.student_id,
            course_id=progress.course_id,
            total_quizzes=progress.total_quizzes,
            completed_quizzes=progress.completed_quizzes,
            total_score=progress.total_score,
            average_score=progress.average_score,
            streak_days=progress.streak_days,
            last_activity=progress.last_activity
        )
        progress.id = model.id
        return progress

    def update(self, progress: StudentProgress) -> StudentProgress:
        try:
            model = StudentProgressModel.objects.get(pk=progress.id)
        except StudentProgressModel.DoesNotExist:
            return self.create(progress)
        model.total_quizzes = progress.total_quizzes
        model.completed_quizzes = progress.completed_quizzes
        model.total_score = progress.total_score
        model.average_score = progress.average_score
        model.streak_days = progress.streak_days
        model.last_activity = progress.last_activity
        model.save()
        return progress

    def _to_entity(self, model: StudentProgressModel) -> StudentProgress:
        return StudentProgress(
            id=model.id,
            student_id=model.student_id,
            course_id=model.course_id,
            total_quizzes=model.total_quizzes,
            completed_quizzes=model.completed_quizzes,
            total_score=model.total_score,
            average_score=model.average_score,
            streak_days=model.streak_days,
            last_activity=model.last_activity,
            created_at=model.created_at,
            updated_at=model.updated_at
        )