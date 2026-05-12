from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    """Question Entity - Part de l'agregat Quiz"""
    id: Optional[int] = None
    quiz_id: Optional[int] = None
    question_type: str = "qcm"
    question_text: str = ""
    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    points: int = 1
    order: int = 0

    TYPE_QCM = "qcm"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_OPEN = "open"

    def is_correct(self, answer: str) -> bool:
        """Vérifier si la réponse est correcte"""
        return answer.strip().lower() == self.correct_answer.strip().lower()

    def validate(self) -> List[str]:
        """Valider les invariants de la question"""
        errors = []
        if not self.question_text:
            errors.append("Le texte de la question est requis")
        if self.question_type not in [self.TYPE_QCM, self.TYPE_TRUE_FALSE, self.TYPE_OPEN]:
            errors.append("Le type de question doit être qcm, true_false ou open")
        if self.points < 1:
            errors.append("Les points doivent être >= 1")

        if self.question_type == self.TYPE_QCM and len(self.options) < 2:
            errors.append("Un QCM doit avoir au moins 2 options")

        if not self.correct_answer:
            errors.append("La bonne réponse est requise")

        if self.question_type == self.TYPE_QCM:
            if self.correct_answer not in self.options:
                errors.append("La bonne réponse doit être parmi les options")

        return errors

    def has_options(self) -> bool:
        """Retourne True si la question a des options (QCM)"""
        return self.question_type == self.TYPE_QCM and len(self.options) > 0

    def get_shuffled_options(self) -> List[str]:
        """Retourne les options mélangées (pour affichage)"""
        import random
        return random.sample(self.options, len(self.options))

    def __str__(self) -> str:
        return f"Question {self.order}: {self.question_text[:30]}..."