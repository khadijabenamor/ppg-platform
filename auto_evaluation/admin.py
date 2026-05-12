from django.contrib import admin
from .models import Quiz, Question, Flashcard, QuizAttempt, StudentProgress


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "course_id", "difficulty", "is_ai_generated", "created_at"]
    list_filter = ["difficulty", "is_ai_generated", "course_id"]
    search_fields = ["title", "description"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["quiz", "question_type", "question_text", "points", "order"]
    list_filter = ["question_type"]


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ["question", "course_id", "is_ai_generated", "is_reviewed", "created_at"]
    list_filter = ["is_ai_generated", "is_reviewed", "course_id"]
    search_fields = ["question", "answer"]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ["student", "quiz", "score", "total_points", "percentage", "started_at", "completed_at"]
    list_filter = ["quiz"]
    search_fields = ["student__username", "quiz__title"]


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "course_id", "completed_quizzes", "average_score", "streak_days", "last_activity"]
    list_filter = ["course_id"]
    search_fields = ["student__username"]