from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    """Value Object pour un score"""
    points: int
    total_points: int

    @property
    def percentage(self) -> float:
        if self.total_points == 0:
            return 0.0
        return round((self.points / self.total_points) * 100, 2)

    @property
    def is_passed(self) -> bool:
        return self.percentage >= 50

    def __str__(self) -> str:
        return f"{self.points}/{self.total_points} ({self.percentage}%)"


@dataclass(frozen=True)
class QuestionType:
    """Value Object pour le type de question"""
    QCM = "qcm"
    TRUE_FALSE = "true_false"
    OPEN = "open"

    ALL = [QCM, TRUE_FALSE, OPEN]


@dataclass(frozen=True)
class Difficulty:
    """Value Object pour la difficulté"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    ALL = [EASY, MEDIUM, HARD]

    @staticmethod
    def get_display_name(level: str) -> str:
        names = {
            Difficulty.EASY: "Facile",
            Difficulty.MEDIUM: "Moyen",
            Difficulty.HARD: "Difficile"
        }
        return names.get(level, level)


@dataclass(frozen=True)
class PerformanceLevel:
    """Value Object pour le niveau de performance"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    NEEDS_IMPROVEMENT = "needs_improvement"

    ALL = [EXCELLENT, GOOD, AVERAGE, NEEDS_IMPROVEMENT]

    @staticmethod
    def get_display_name(level: str) -> str:
        names = {
            PerformanceLevel.EXCELLENT: "Excellent",
            PerformanceLevel.GOOD: "Bien",
            PerformanceLevel.AVERAGE: "Moyen",
            PerformanceLevel.NEEDS_IMPROVEMENT: "À améliorer"
        }
        return names.get(level, level)