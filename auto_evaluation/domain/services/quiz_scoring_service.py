from typing import List, Dict
from ..entities import Quiz, Question, QuizAttempt


class QuizScoringService:
    """Domain Service pour le scoring des quizzes"""

    def calculate_score(self, quiz: Quiz, answers: List[Dict]) -> QuizAttempt:
        """Calculer le score d'une tentative de quiz"""
        attempt = QuizAttempt()

        questions = {q.id: q for q in quiz.questions}

        for answer_data in answers:
            question_id = answer_data.get("question_id")
            user_answer = answer_data.get("answer", "").strip()

            if question_id not in questions:
                continue

            question = questions[question_id]
            
            # Debug logging
            print(f"DEBUG: question_id={question_id}, user_answer='{user_answer}', correct_answer='{question.correct_answer}', is_correct check: '{user_answer.lower()}' == '{question.correct_answer.strip().lower()}'")
            
            is_correct = question.is_correct(user_answer)
            # Pass full question points to add_answer (it handles scoring correctly)
            # The add_answer method will only add to score if answer is correct
            earned_points = question.points if is_correct else 0

            attempt.add_answer(
                question_id=question_id,
                question_text=question.question_text,
                user_answer=user_answer,
                correct_answer=question.correct_answer.strip(),
                is_correct=is_correct,
                earned_points=earned_points,
                max_points=question.points
            )

        attempt.complete()
        return attempt

    def validate_answers_format(self, answers: List[Dict]) -> List[str]:
        """Valider le format des réponses"""
        errors = []

        if not answers:
            errors.append("Aucune réponse fournie")
            return errors

        for i, answer in enumerate(answers):
            if "question_id" not in answer:
                errors.append(f"Réponse {i}: question_id manquant")
            if "answer" not in answer:
                errors.append(f"Réponse {i}: answer manquant")

            if "question_id" in answer and not isinstance(answer["question_id"], int):
                errors.append(f"Réponse {i}: question_id doit être un entier")

        return errors


class QuizValidationService:
    """Domain Service pour la validation des quizzes"""

    def validate_quiz(self, quiz: Quiz, allow_empty: bool = False) -> Dict[str, any]:
        """Valider un quiz complet"""
        errors = quiz.validate()

        if not allow_empty and not quiz.can_be_submitted():
            errors.append("Le quiz doit contenir au moins une question")

        for question in quiz.questions:
            question_errors = question.validate()
            errors.extend([f"Q{question.order}: {e}" for e in question_errors])

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": self._get_warnings(quiz)
        }

    def _get_warnings(self, quiz: Quiz) -> List[str]:
        """Retourner les avertissements"""
        warnings = []

        if quiz.question_count == 0:
            warnings.append("Le quiz n'a pas de questions")

        if quiz.question_count < 3:
            warnings.append("Il est recommandé d'avoir au moins 3 questions")

        return warnings