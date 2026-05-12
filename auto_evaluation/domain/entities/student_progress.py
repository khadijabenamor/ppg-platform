from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class StudentProgress:
    """StudentProgress Entity"""
    id: Optional[int] = None
    student_id: Optional[int] = None
    course_id: str = ""
    total_quizzes: int = 0
    completed_quizzes: int = 0
    total_score: int = 0
    average_score: float = 0.0
    streak_days: int = 0
    last_activity: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def completion_rate(self) -> float:
        """Taux de completion des quizzes"""
        if self.total_quizzes == 0:
            return 0.0
        return round((self.completed_quizzes / self.total_quizzes) * 100, 2)

    @property
    def is_active_streak(self) -> bool:
        """Vérifie si le streak est actif (activity today or yesterday)"""
        if not self.last_activity:
            return False
        today = date.today()
        return self.last_activity in [today, today - timedelta(days=1)]

    def update_after_attempt(self, score: int, is_new_quiz: bool = False) -> None:
        """Mettre à jour la progression après une tentative"""
        if is_new_quiz:
            self.total_quizzes += 1
        self.completed_quizzes += 1
        self.total_score += score

        # Moyenne glissante des scores
        if self.completed_quizzes > 0:
            self.average_score = round(self.total_score / self.completed_quizzes, 2)

        self._update_streak()
        self.updated_at = datetime.now()

    def _update_streak(self) -> None:
        """Mettre à jour le compteur de jours consécutifs"""
        today = date.today()

        if self.last_activity is None:
            self.streak_days = 1
        elif self.last_activity == today:
            pass  # Déjà actif aujourd'hui
        elif self.last_activity == today - timedelta(days=1):
            self.streak_days += 1  # Continuité du streak
        else:
            self.streak_days = 1  # Nouveau streak

        self.last_activity = today

    def reset_streak(self) -> None:
        """Réinitialiser le streak"""
        self.streak_days = 0

    def get_performance_level(self) -> str:
        """Retourne le niveau de performance"""
        if self.average_score >= 80:
            return "excellent"
        elif self.average_score >= 60:
            return "good"
        elif self.average_score >= 40:
            return "average"
        else:
            return "needs_improvement"

    def __str__(self) -> str:
        return f"Progress: {self.completed_quizzes}/{self.total_quizzes} quizzes, {self.average_score}% avg, {self.streak_days} days streak"


# Import timedelta pour _update_streak
from datetime import timedelta