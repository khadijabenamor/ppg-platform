from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet,
    FlashcardViewSet,
    QuizAttemptViewSet,
    StudentProgressViewSet,
    create_quiz_with_ai,
    generate_flashcards
)

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")
router.register(r"flashcards", FlashcardViewSet, basename="flashcard")
router.register(r"attempts", QuizAttemptViewSet, basename="attempt")
router.register(r"progress", StudentProgressViewSet, basename="progress")

urlpatterns = [
    path("quizzes/create-with-ai/", create_quiz_with_ai, name="quiz-create-with-ai"),
    path("flashcards/generate/", generate_flashcards, name="flashcard-generate"),
    path("flashcards/<int:pk>/mark-reviewed/", FlashcardViewSet.as_view({'post': 'mark_reviewed'}), name="flashcard-mark-reviewed"),
    path("", include(router.urls))
]