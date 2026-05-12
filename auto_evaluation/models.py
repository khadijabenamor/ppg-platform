from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Quiz(models.Model):
    """Quiz pour l'auto-évaluation"""
    DIFFICULTY_CHOICES = [
        ("easy", "Facile"),
        ("medium", "Moyen"),
        ("hard", "Difficile"),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre du quiz")
    description = models.TextField(blank=True, verbose_name="Description")
    course_id = models.CharField(max_length=100, verbose_name="ID du cours")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_quizzes")
    is_ai_generated = models.BooleanField(default=False, verbose_name="Généré par IA")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):
    """Question d'un quiz"""
    TYPE_CHOICES = [
        ("qcm", "QCM"),
        ("true_false", "Vrai/Faux"),
        ("open", "Ouverte"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="qcm")
    question_text = models.TextField(verbose_name="Texte de la question")
    options = models.JSONField(default=list, verbose_name="Options (pour QCM)")
    correct_answer = models.TextField(verbose_name="Bonne réponse")
    explanation = models.TextField(blank=True, verbose_name="Explication")
    points = models.PositiveIntegerField(default=1, verbose_name="Points")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ["order"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"Question {self.order}: {self.question_text[:50]}..."


class Flashcard(models.Model):
    """Carte mémoire pour la révision"""
    course_id = models.CharField(max_length=100, verbose_name="ID du cours")
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    tags = models.JSONField(default=list, verbose_name="Tags")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_flashcards")
    is_ai_generated = models.BooleanField(default=False, verbose_name="Générée par IA")
    is_reviewed = models.BooleanField(default=False, verbose_name="Révisée")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Flashcard"
        verbose_name_plural = "Flashcards"

    def __str__(self):
        return f"Flashcard: {self.question[:30]}..."


class QuizAttempt(models.Model):
    """Tentative de quiz par un étudiant"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts", null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveIntegerField(default=0, verbose_name="Score obtenu")
    total_points = models.PositiveIntegerField(default=0, verbose_name="Points totaux")
    answers = models.JSONField(default=dict, verbose_name="Réponses données")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Tentative de quiz"
        verbose_name_plural = "Tentatives de quiz"

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}/{self.total_points}"

    @property
    def percentage(self):
        if self.total_points == 0:
            return 0
        return round((self.score / self.total_points) * 100, 2)


class StudentProgress(models.Model):
    """Suivi de la progression d'un étudiant"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress")
    course_id = models.CharField(max_length=100, verbose_name="ID du cours")
    total_quizzes = models.PositiveIntegerField(default=0, verbose_name="Total des quizzes")
    completed_quizzes = models.PositiveIntegerField(default=0, verbose_name="Quizzes complétés")
    total_score = models.PositiveIntegerField(default=0, verbose_name="Score total")
    average_score = models.FloatField(default=0, verbose_name="Score moyen")
    streak_days = models.PositiveIntegerField(default=0, verbose_name="Jours de suite")
    last_activity = models.DateField(null=True, blank=True, verbose_name="Dernière activité")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["student", "course_id"]
        verbose_name = "Progression étudiant"
        verbose_name_plural = "Progressions étudiants"

    def __str__(self):
        return f"{self.student.username} - {self.course_id} - {self.average_score}%"