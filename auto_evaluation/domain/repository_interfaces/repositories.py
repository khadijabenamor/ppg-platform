from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities import Quiz, Question, Flashcard, QuizAttempt, StudentProgress


class QuizRepositoryInterface(ABC):
    """Interface pour le repository de Quiz"""

    @abstractmethod
    def create(self, quiz: Quiz) -> Quiz:
        pass

    @abstractmethod
    def get_by_id(self, quiz_id: int) -> Optional[Quiz]:
        pass

    @abstractmethod
    def get_all(self) -> List[Quiz]:
        pass

    @abstractmethod
    def get_by_course(self, course_id: str) -> List[Quiz]:
        pass

    @abstractmethod
    def update(self, quiz: Quiz) -> Quiz:
        pass

    @abstractmethod
    def delete(self, quiz_id: int) -> bool:
        pass


class QuestionRepositoryInterface(ABC):
    """Interface pour le repository de Question"""

    @abstractmethod
    def create(self, question: Question) -> Question:
        pass

    @abstractmethod
    def get_by_id(self, question_id: int) -> Optional[Question]:
        pass

    @abstractmethod
    def get_by_quiz(self, quiz_id: int) -> List[Question]:
        pass

    @abstractmethod
    def update(self, question: Question) -> Question:
        pass

    @abstractmethod
    def delete(self, question_id: int) -> bool:
        pass


class FlashcardRepositoryInterface(ABC):
    """Interface pour le repository de Flashcard"""

    @abstractmethod
    def create(self, flashcard: Flashcard) -> Flashcard:
        pass

    @abstractmethod
    def get_by_id(self, flashcard_id: int) -> Optional[Flashcard]:
        pass

    @abstractmethod
    def get_all(self) -> List[Flashcard]:
        pass

    @abstractmethod
    def get_by_course(self, course_id: str) -> List[Flashcard]:
        pass

    @abstractmethod
    def update(self, flashcard: Flashcard) -> Flashcard:
        pass

    @abstractmethod
    def delete(self, flashcard_id: int) -> bool:
        pass


class QuizAttemptRepositoryInterface(ABC):
    """Interface pour le repository de QuizAttempt"""

    @abstractmethod
    def create(self, attempt: QuizAttempt) -> QuizAttempt:
        pass

    @abstractmethod
    def get_by_id(self, attempt_id: int) -> Optional[QuizAttempt]:
        pass

    @abstractmethod
    def get_by_student(self, student_id: int) -> List[QuizAttempt]:
        pass

    @abstractmethod
    def get_by_student_and_course(self, student_id: int, course_id: str) -> List[QuizAttempt]:
        pass


class StudentProgressRepositoryInterface(ABC):
    """Interface pour le repository de StudentProgress"""

    @abstractmethod
    def create(self, progress: StudentProgress) -> StudentProgress:
        pass

    @abstractmethod
    def get_by_id(self, progress_id: int) -> Optional[StudentProgress]:
        pass

    @abstractmethod
    def get_by_student(self, student_id: int) -> List[StudentProgress]:
        pass

    @abstractmethod
    def get_by_student_and_course(self, student_id: int, course_id: str) -> Optional[StudentProgress]:
        pass

    @abstractmethod
    def update(self, progress: StudentProgress) -> StudentProgress:
        pass