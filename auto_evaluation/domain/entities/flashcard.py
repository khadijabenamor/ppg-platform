from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Flashcard:
    """Flashcard Entity - Aggregate Root"""
    id: Optional[int] = None
    course_id: str = ""
    question: str = ""
    answer: str = ""
    tags: List[str] = field(default_factory=list)
    created_by_id: Optional[int] = None
    is_ai_generated: bool = False
    is_reviewed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def mark_as_reviewed(self) -> None:
        """Marquer la flashcard comme révisée"""
        self.is_reviewed = True
        self.updated_at = datetime.now()

    def update_content(self, question: str, answer: str, tags: List[str] = None) -> None:
        """Mettre à jour le contenu de la flashcard"""
        self.question = question
        self.answer = answer
        if tags is not None:
            self.tags = tags
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Ajouter un tag"""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Supprimer un tag"""
        if tag in self.tags:
            self.tags.remove(tag)

    def validate(self) -> List[str]:
        """Valider les invariants"""
        errors = []
        if not self.question:
            errors.append("La question est requise")
        if not self.answer:
            errors.append("La réponse est requise")
        if not self.course_id:
            errors.append("L'ID du cours est requis")
        return errors

    def get_formatted_display(self) -> dict:
        """Retourne un format display pour l'API"""
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "tags": self.tags,
            "is_reviewed": self.is_reviewed
        }

    def __str__(self) -> str:
        return f"Flashcard: {self.question[:30]}..."