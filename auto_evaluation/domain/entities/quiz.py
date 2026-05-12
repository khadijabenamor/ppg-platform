from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from .question import Question


@dataclass
class Quiz:
    """Quiz Entity - Aggregate Root"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    course_id: str = ""
    difficulty: str = "medium"
    created_by_id: Optional[int] = None
    is_ai_generated: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _questions: List[Question] = field(default_factory=list)

    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"

    @property
    def questions(self) -> List[Question]:
        return self._questions

    @property
    def total_points(self) -> int:
        return sum(q.points for q in self._questions)

    @property
    def question_count(self) -> int:
        return len(self._questions)

    def add_question(self, question: Question) -> None:
        """Ajouter une question au quiz"""
        question.order = len(self._questions) + 1
        self._questions.append(question)

    def add_questions(self, questions: List[Question]) -> None:
        """Ajouter plusieurs questions"""
        for q in questions:
            self.add_question(q)

    def remove_question(self, question_id: int) -> bool:
        """Supprimer une question par ID"""
        for i, q in enumerate(self._questions):
            if q.id == question_id:
                self._questions.pop(i)
                self._reorder_questions()
                return True
        return False

    def _reorder_questions(self) -> None:
        """Réordonner les questions après suppression"""
        for i, q in enumerate(self._questions):
            q.order = i + 1

    def validate(self) -> List[str]:
        """Valider les invariants du quiz"""
        errors = []
        if not self.title or len(self.title.strip()) == 0:
            errors.append("Le titre du quiz est requis")
        if not self.course_id:
            errors.append("L'ID du cours est requis")
        if self.difficulty not in [self.DIFFICULTY_EASY, self.DIFFICULTY_MEDIUM, self.DIFFICULTY_HARD]:
            errors.append("La difficulté doit être easy, medium ou hard")
        return errors

    def can_be_submitted(self) -> bool:
        """Vérifier si le quiz peut être soumis"""
        return len(self._questions) > 0

    def __str__(self) -> str:
        return f"Quiz: {self.title} ({self.question_count} questions)"