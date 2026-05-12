from typing import List, Optional
from auto_evaluation.models import Quiz as QuizModel, Question as QuestionModel
from auto_evaluation.domain.entities import Quiz, Question
from auto_evaluation.domain.repository_interfaces.repositories import QuizRepositoryInterface, QuestionRepositoryInterface


class DjangoQuizRepository(QuizRepositoryInterface):
    """Implémentation Django du repository Quiz"""

    def create(self, quiz: Quiz) -> Quiz:
        model = QuizModel(
            title=quiz.title,
            description=quiz.description,
            course_id=quiz.course_id,
            difficulty=quiz.difficulty,
            created_by_id=quiz.created_by_id,
            is_ai_generated=quiz.is_ai_generated
        )
        model.save()
        quiz.id = model.id
        return quiz

    def get_by_id(self, quiz_id: int) -> Optional[Quiz]:
        try:
            model = QuizModel.objects.get(pk=quiz_id)
            return self._to_entity(model)
        except QuizModel.DoesNotExist:
            return None

    def get_all(self) -> List[Quiz]:
        models = QuizModel.objects.all()
        return [self._to_entity(m) for m in models]

    def get_by_course(self, course_id: str) -> List[Quiz]:
        models = QuizModel.objects.filter(course_id=course_id)
        return [self._to_entity(m) for m in models]

    def update(self, quiz: Quiz) -> Quiz:
        model = QuizModel.objects.get(pk=quiz.id)
        model.title = quiz.title
        model.description = quiz.description
        model.course_id = quiz.course_id
        model.difficulty = quiz.difficulty
        model.is_ai_generated = quiz.is_ai_generated
        model.save()
        return quiz

    def delete(self, quiz_id: int) -> bool:
        try:
            model = QuizModel.objects.get(pk=quiz_id)
            model.delete()
            return True
        except QuizModel.DoesNotExist:
            return False

    def _to_entity(self, model: QuizModel) -> Quiz:
        questions = []
        for q in model.questions.all():
            questions.append(Question(
                id=q.id,
                quiz_id=q.quiz_id,
                question_type=q.question_type,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                points=q.points,
                order=q.order
            ))

        return Quiz(
            id=model.id,
            title=model.title,
            description=model.description,
            course_id=model.course_id,
            difficulty=model.difficulty,
            created_by_id=model.created_by_id,
            is_ai_generated=model.is_ai_generated,
            created_at=model.created_at,
            updated_at=model.updated_at,
            _questions=questions
        )


class DjangoQuestionRepository(QuestionRepositoryInterface):
    """Implémentation Django du repository Question"""

    def create(self, question: Question) -> Question:
        model = QuestionModel(
            quiz_id=question.quiz_id,
            question_type=question.question_type,
            question_text=question.question_text,
            options=question.options,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            points=question.points,
            order=question.order
        )
        model.save()
        question.id = model.id
        return question

    def get_by_id(self, question_id: int) -> Optional[Question]:
        try:
            model = QuestionModel.objects.get(pk=question_id)
            return self._to_entity(model)
        except QuestionModel.DoesNotExist:
            return None

    def get_by_quiz(self, quiz_id: int) -> List[Question]:
        models = QuestionModel.objects.filter(quiz_id=quiz_id).order_by("order")
        return [self._to_entity(m) for m in models]

    def update(self, question: Question) -> Question:
        model = QuestionModel.objects.get(pk=question.id)
        model.question_type = question.question_type
        model.question_text = question.question_text
        model.options = question.options
        model.correct_answer = question.correct_answer
        model.explanation = question.explanation
        model.points = question.points
        model.order = question.order
        model.save()
        return question

    def delete(self, question_id: int) -> bool:
        try:
            model = QuestionModel.objects.get(pk=question_id)
            model.delete()
            return True
        except QuestionModel.DoesNotExist:
            return False

    def _to_entity(self, model: QuestionModel) -> Question:
        return Question(
            id=model.id,
            quiz_id=model.quiz_id,
            question_type=model.question_type,
            question_text=model.question_text,
            options=model.options,
            correct_answer=model.correct_answer,
            explanation=model.explanation,
            points=model.points,
            order=model.order
        )