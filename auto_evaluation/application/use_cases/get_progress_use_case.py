from typing import Dict, Any, Optional


class GetProgressUseCase:
    """Use Case pour récupérer la progression d'un étudiant"""

    def __init__(self, progress_repository, attempt_repository):
        self.progress_repository = progress_repository
        self.attempt_repository = attempt_repository

    def execute(self, student_id: int, course_id: Optional[str] = None) -> Dict[str, Any]:
        """Executer le use case"""
        if course_id:
            progress = self.progress_repository.get_by_student_and_course(student_id, course_id)
            if not progress:
                return {
                    "success": True,
                    "progress": None,
                    "message": "Aucune progression trouvée pour ce cours"
                }
            return {
                "success": True,
                "progress": progress
            }

        all_progress = self.progress_repository.get_by_student(student_id)

        total_quizzes = sum(p.total_quizzes for p in all_progress)
        total_completed = sum(p.completed_quizzes for p in all_progress)
        total_score = sum(p.total_score for p in all_progress)

        overall_average = total_score / total_completed if total_completed > 0 else 0

        return {
            "success": True,
            "progress": all_progress,
            "summary": {
                "total_quizzes": total_quizzes,
                "completed_quizzes": total_completed,
                "total_score": total_score,
                "overall_average": round(overall_average, 2)
            }
        }


class GetStatisticsUseCase:
    """Use Case pour récupérer les statistiques globales"""

    def __init__(self, progress_repository, attempt_repository):
        self.progress_repository = progress_repository
        self.attempt_repository = attempt_repository

    def execute(self, student_id: int) -> Dict[str, Any]:
        """Executer le use case"""
        all_progress = self.progress_repository.get_by_student(student_id)
        all_attempts = self.attempt_repository.get_by_student(student_id)

        if not all_attempts:
            return {
                "success": True,
                "statistics": None,
                "message": "Aucune tentative trouvée"
            }

        total_attempts = len(all_attempts)
        total_correct = sum(a.get_correct_count() for a in all_attempts)
        total_questions = sum(len(a.answers) for a in all_attempts)

        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

        best_attempt = max(all_attempts, key=lambda a: a.percentage) if all_attempts else None

        return {
            "success": True,
            "statistics": {
                "total_attempts": total_attempts,
                "total_questions": total_questions,
                "correct_answers": total_correct,
                "overall_accuracy": round(overall_accuracy, 2),
                "best_score": best_attempt.percentage if best_attempt else 0,
                "best_score_quiz": best_attempt.quiz_id if best_attempt else None,
                "courses_progress": [
                    {
                        "course_id": p.course_id,
                        "completed_quizzes": p.completed_quizzes,
                        "average_score": p.average_score,
                        "streak_days": p.streak_days,
                        "performance_level": p.get_performance_level()
                    }
                    for p in all_progress
                ]
            }
        }