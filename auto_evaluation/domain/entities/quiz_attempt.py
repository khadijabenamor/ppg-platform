from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List


@dataclass
class GradedAnswer:
    """Value Object pour une réponse notée"""
    question_id: int
    question_text: str = ""
    user_answer: str = ""
    correct_answer: str = ""
    is_correct: bool = False
    points_earned: int = 0


@dataclass
class QuizAttempt:
    """QuizAttempt Entity"""
    id: Optional[int] = None
    student_id: Optional[int] = None
    quiz_id: Optional[int] = None
    score: int = 0
    total_points: int = 0
    answers: Dict[str, Dict] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @property
    def percentage(self) -> float:
        """Calculer le pourcentage de réussite"""
        if self.total_points == 0:
            return 0.0
        return round((self.score / self.total_points) * 100, 2)

    @property
    def is_completed(self) -> bool:
        """Vérifier si la tentative est complétée"""
        return self.completed_at is not None

    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculer la durée en minutes"""
        if not self.completed_at:
            return None
        delta = self.completed_at - self.started_at
        return round(delta.total_seconds() / 60, 2)

    def add_answer(self, question_id: int, question_text: str, user_answer: str, correct_answer: str, is_correct: bool, earned_points: int = 0, max_points: int = 0) -> None:
        """Ajouter une réponse notée"""
        self.answers[str(question_id)] = {
            "question_text": question_text,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "points_earned": earned_points,
            "max_points": max_points
        }
        if is_correct:
            self.score += earned_points
        self.total_points += max_points

    def get_graded_answers(self) -> List[GradedAnswer]:
        """Retourne la liste des réponses notées"""
        return [
            GradedAnswer(
                question_id=int(q_id),
                question_text=data.get("question_text", ""),
                user_answer=data["user_answer"],
                correct_answer=data["correct_answer"],
                is_correct=data["is_correct"],
                points_earned=data["points_earned"]
            )
            for q_id, data in self.answers.items()
        ]

    def get_correct_count(self) -> int:
        """Nombre de réponses correctes"""
        return sum(1 for a in self.answers.values() if a.get("is_correct", False))

    def get_incorrect_count(self) -> int:
        """Nombre de réponses incorrectes"""
        return sum(1 for a in self.answers.values() if not a.get("is_correct", False))

    def complete(self) -> None:
        """Marquer la tentative comme terminée"""
        self.completed_at = datetime.now()

    def __str__(self) -> str:
        return f"Attempt: {self.score}/{self.total_points} ({self.percentage}%)"