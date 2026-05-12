from typing import Dict, Any, Optional
from auto_evaluation.domain.entities import QuizAttempt, StudentProgress
from auto_evaluation.domain.services.quiz_scoring_service import QuizScoringService
from datetime import date, timedelta


class SubmitQuizUseCase:
    """Use Case pour soumettre un quiz et calculer le score"""

    def __init__(self, quiz_repository, attempt_repository, progress_repository):
        self.quiz_repository = quiz_repository
        self.attempt_repository = attempt_repository
        self.progress_repository = progress_repository
        self.scoring_service = QuizScoringService()

    def execute(self, quiz_id: int, answers: list, student_id: int) -> Dict[str, Any]:
        """Executer le use case"""
        quiz = self.quiz_repository.get_by_id(quiz_id)
        if not quiz:
            return {
                "success": False,
                "errors": ["Quiz non trouvé"]
            }

        validation_errors = self.scoring_service.validate_answers_format(answers)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors
            }

        attempt = self.scoring_service.calculate_score(quiz, answers)
        attempt.student_id = student_id
        attempt.quiz_id = quiz_id

        saved_attempt = self.attempt_repository.create(attempt)

        # Only track progress for authenticated users
        if student_id:
            progress = self.progress_repository.get_by_student_and_course(student_id, quiz.course_id)
            if not progress:
                progress = StudentProgress(
                    student_id=student_id,
                    course_id=quiz.course_id,
                    total_quizzes=0,
                    completed_quizzes=0,
                    total_score=0,
                    average_score=0,
                    streak_days=0,
                    last_activity=None
                )

            total_attempts = len(self.attempt_repository.get_by_student_and_course(student_id, quiz.course_id))
            is_new_quiz = total_attempts == 1
            progress.update_after_attempt(attempt.score, is_new_quiz)

            self.progress_repository.update(progress)

            progress_data = {
                "completed_quizzes": progress.completed_quizzes,
                "average_score": progress.average_score,
                "streak_days": progress.streak_days,
                "completion_rate": progress.completion_rate
            }
        else:
            progress_data = None

        return {
            "success": True,
            "attempt": saved_attempt,
            "progress": progress_data
        }


class GetAttemptHistoryUseCase:
    """Use Case pour récupérer l'historique des tentatives"""

    def __init__(self, attempt_repository):
        self.attempt_repository = attempt_repository

    def execute(self, student_id: int, course_id: Optional[str] = None) -> Dict[str, Any]:
        """Executer le use case"""
        if course_id:
            attempts = self.attempt_repository.get_by_student_and_course(student_id, course_id)
        else:
            attempts = self.attempt_repository.get_by_student(student_id)

        return {
            "success": True,
            "attempts": attempts,
            "total": len(attempts)
        }