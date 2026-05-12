from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Quiz, Question, Flashcard, QuizAttempt, StudentProgress

User = get_user_model()


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id", "question_type", "question_text", "options",
            "correct_answer", "explanation", "points", "order"
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id", "title", "description", "course_id", "difficulty",
            "created_by", "created_by_username", "is_ai_generated",
            "created_at", "updated_at", "questions"
        ]
        read_only_fields = ["created_by", "is_ai_generated", "created_at", "updated_at"]


class QuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "course_id", "difficulty"]


class FlashcardSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Flashcard
        fields = [
            "id", "course_id", "question", "answer", "tags",
            "created_by", "created_by_username", "is_ai_generated",
            "is_reviewed", "created_at", "updated_at"
        ]
        read_only_fields = ["created_by", "is_ai_generated", "created_at", "updated_at"]


class FlashcardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ["id", "course_id", "question", "answer", "tags"]


class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField()


class QuizSubmitSerializer(serializers.Serializer):
    answers = AnswerSubmissionSerializer(many=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id", "student", "student_username", "quiz", "quiz_title",
            "score", "total_points", "percentage", "answers",
            "started_at", "completed_at"
        ]


class StudentProgressSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = StudentProgress
        fields = [
            "id", "student", "student_username", "course_id",
            "total_quizzes", "completed_quizzes", "total_score",
            "average_score", "streak_days", "last_activity",
            "created_at", "updated_at"
        ]