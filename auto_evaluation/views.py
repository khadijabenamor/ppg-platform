from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

from auto_evaluation.infrastructure.repositories import (
    DjangoQuizRepository,
    DjangoQuestionRepository,
    DjangoFlashcardRepository,
    DjangoQuizAttemptRepository,
    DjangoStudentProgressRepository
)

from auto_evaluation.application.use_cases import (
    CreateQuizUseCase,
    UpdateQuizUseCase,
    DeleteQuizUseCase,
    SubmitQuizUseCase,
    GetAttemptHistoryUseCase,
    GenerateQuestionsUseCase,
    CreateFlashcardUseCase,
    UpdateFlashcardUseCase,
    MarkFlashcardReviewedUseCase,
    GenerateFlashcardsUseCase,
    GetProgressUseCase,
    GetStatisticsUseCase
)

from .serializers_ddd import (
    QuizSerializer,
    FlashcardSerializer,
    QuizAttemptSerializer,
    StudentProgressSerializer
)
from .serializers import QuestionSerializer
from auto_evaluation.domain.services.groq_ai_service import GroqAIServiceFactory, GroqAIServiceError


quiz_repository = DjangoQuizRepository()
question_repository = DjangoQuestionRepository()
flashcard_repository = DjangoFlashcardRepository()
attempt_repository = DjangoQuizAttemptRepository()
progress_repository = DjangoStudentProgressRepository()


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet pour les quizzes - Presentation Layer"""
    permission_classes = [AllowAny]
    serializer_class = QuizSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get("course_id")
        if course_id:
            return quiz_repository.get_by_course(course_id)
        return quiz_repository.get_all()

    def create(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None

        use_case = CreateQuizUseCase(quiz_repository)
        result = use_case.execute(request.data, user_id)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            QuizSerializer(result["quiz"]).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"])
    def create_with_ai(self, request):
        """Créer un quiz avec génération automatique de questions via IA"""
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None

        title = request.data.get("title", "")
        description = request.data.get("description", "")
        course_id = request.data.get("course_id", "")
        difficulty = request.data.get("difficulty", "medium")
        course_content = request.data.get("course_content", "")
        count = request.data.get("count", 5)

        if not title or not course_id:
            return Response(
                {"errors": ["Le titre et l'ID du cours sont requis"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not course_content:
            return Response(
                {"errors": ["Le contenu du cours est requis pour la génération IA"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        quiz_data = {
            "title": title,
            "description": description,
            "course_id": course_id,
            "difficulty": difficulty
        }

        create_use_case = CreateQuizUseCase(quiz_repository)
        result = create_use_case.execute(quiz_data, user_id)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        quiz = result["quiz"]

        generate_use_case = GenerateQuestionsUseCase(quiz_repository, question_repository)
        gen_result = generate_use_case.execute(quiz.id, course_content, count=count)

        if not gen_result["success"]:
            quiz.delete()
            return Response({"errors": gen_result["errors"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        updated_quiz = quiz_repository.get_by_id(quiz.id)

        return Response(
            QuizSerializer(updated_quiz).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"])
    def preview_questions(self, request):
        """Générer un aperçu des questions sans créer le quiz"""
        course_content = request.data.get("course_content", "")
        count = request.data.get("count", 5)

        if not course_content:
            return Response(
                {"error": "Le contenu du cours est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_service = GroqAIServiceFactory.get_service()
            questions = ai_service.generate_quiz_questions(course_content, count)
            return Response({
                "questions": [q.__dict__ for q in questions]
            })
        except GroqAIServiceError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        quiz_id = kwargs.get("pk")
        use_case = UpdateQuizUseCase(quiz_repository)
        result = use_case.execute(quiz_id, request.data)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(QuizSerializer(result["quiz"]).data)

    def destroy(self, request, *args, **kwargs):
        quiz_id = kwargs.get("pk")
        use_case = DeleteQuizUseCase(quiz_repository)
        result = use_case.execute(quiz_id)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(result["message"], status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def generate_questions(self, request, pk=None):
        course_content = request.data.get("course_content", "")

        if not course_content:
            return Response(
                {"error": "Le contenu du cours est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = GenerateQuestionsUseCase(quiz_repository, question_repository)
        result = use_case.execute(pk, course_content)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": f"{result['count']} questions générées",
            "questions": QuestionSerializer(result["questions"], many=True).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None

        answers = request.data.get("answers", [])
        if not answers:
            return Response(
                {"error": "Aucune réponse fournie."},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"DEBUG SUBMIT: quiz_id={pk}, answers={answers}")

        use_case = SubmitQuizUseCase(
            quiz_repository,
            attempt_repository,
            progress_repository
        )
        result = use_case.execute(pk, answers, user_id)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        print(f"DEBUG RESULT: score={result['attempt'].score}, total={result['attempt'].total_points}, percentage={result['attempt'].percentage}")

        return Response({
            "score": result["attempt"].score,
            "total_points": result["attempt"].total_points,
            "percentage": result["attempt"].percentage,
            "graded_answers": result["attempt"].answers,
            "progress": result["progress"]
        })


class FlashcardViewSet(viewsets.ModelViewSet):
    """ViewSet pour les flashcards - Presentation Layer"""
    permission_classes = [AllowAny]
    serializer_class = FlashcardSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get("course_id")
        if course_id:
            return flashcard_repository.get_by_course(course_id)
        return flashcard_repository.get_all()

    def create(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None

        use_case = CreateFlashcardUseCase(flashcard_repository)
        result = use_case.execute(request.data, user_id)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            FlashcardSerializer(result["flashcard"]).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        flashcard_id = kwargs.get("pk")
        use_case = UpdateFlashcardUseCase(flashcard_repository)
        result = use_case.execute(flashcard_id, request.data)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(FlashcardSerializer(result["flashcard"]).data)

    def destroy(self, request, *args, **kwargs):
        flashcard_id = kwargs.get("pk")
        success = flashcard_repository.delete(flashcard_id)
        
        if not success:
            return Response({"error": "Flashcard non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def mark_reviewed(self, request, pk=None):
        use_case = MarkFlashcardReviewedUseCase(flashcard_repository)
        result = use_case.execute(pk)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(FlashcardSerializer(result["flashcard"]).data)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None

        course_content = request.data.get("course_content", "")
        course_id = request.data.get("course_id", "")
        count = request.data.get("count", 5)

        if not course_content:
            return Response(
                {"error": "Le contenu du cours est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_case = GenerateFlashcardsUseCase(flashcard_repository)
        result = use_case.execute(course_content, course_id, count=count, created_by_id=user_id)

        if not result["success"]:
            return Response({"errors": result["errors"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "count": result["count"],
            "flashcards": FlashcardSerializer(result["flashcards"], many=True).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def preview(self, request):
        """Générer un aperçu des flashcards sans créer"""
        course_content = request.data.get("course_content", "")
        count = request.data.get("count", 5)

        if not course_content:
            return Response(
                {"error": "Le contenu du cours est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_service = GroqAIServiceFactory.get_service()
            flashcards = ai_service.generate_flashcards(course_content, count)
            return Response({
                "flashcards": [f.__dict__ for f in flashcards]
            })
        except GroqAIServiceError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet en lecture seule pour les tentatives"""
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return attempt_repository.get_by_student(self.request.user.id)


class StudentProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet en lecture seule pour la progression"""
    serializer_class = StudentProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return []

    def list(self, request):
        """Return aggregated progress for authenticated user"""
        user_id = request.user.id
        
        all_progress = progress_repository.get_by_student(user_id)
        all_attempts = attempt_repository.get_by_student(user_id)
        
        total_completed = sum(p.completed_quizzes for p in all_progress)
        total_score = sum(p.total_score for p in all_progress)
        avg_score = round(total_score / total_completed, 1) if total_completed > 0 else 0
        max_streak = max((p.streak_days for p in all_progress), default=0)
        
        attempts_data = []
        for attempt in all_attempts:
            quiz = quiz_repository.get_by_id(attempt.quiz_id)
            attempts_data.append({
                'quiz_title': quiz.title if quiz else f'Quiz {attempt.quiz_id}',
                'score': round(attempt.percentage, 1),
                'attempted_at': attempt.completed_at.isoformat() if attempt.completed_at else None
            })
        
        from auto_evaluation.models import Flashcard
        flashcards_reviewed = Flashcard.objects.filter(is_reviewed=True).count()
        
        return Response({
            'quizzes_completed': total_completed,
            'average_score': avg_score,
            'streak': max_streak,
            'flashcards_reviewed': flashcards_reviewed,
            'attempts': attempts_data
        })

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        use_case = GetStatisticsUseCase(progress_repository, attempt_repository)
        result = use_case.execute(request.user.id)

        if not result["success"]:
            return Response(
                {"error": result.get("message", "Erreur")},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(result["statistics"])


# ============= Standalone API Views =============

@api_view(['POST'])
@permission_classes([AllowAny])
def create_quiz_with_ai(request):
    """Créer un quiz avec génération automatique de questions via IA"""
    from auto_evaluation.application.use_cases import CreateQuizUseCase, GenerateQuestionsUseCase
    
    user = request.user if request.user.is_authenticated else None
    user_id = user.id if user else None

    title = request.data.get("title", "")
    description = request.data.get("description", "")
    course_id = request.data.get("course_id", "")
    difficulty = request.data.get("difficulty", "medium")
    course_content = request.data.get("course_content", "")
    count = int(request.data.get("count", 5))

    if not title or not course_id:
        return Response(
            {"errors": ["Le titre et l'ID du cours sont requis"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not course_content:
        return Response(
            {"errors": ["Le contenu du cours est requis pour la génération IA"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    quiz_data = {
        "title": title,
        "description": description,
        "course_id": course_id,
        "difficulty": difficulty
    }

    create_use_case = CreateQuizUseCase(quiz_repository)
    result = create_use_case.execute(quiz_data, user_id)

    if not result["success"]:
        return Response({"errors": result["errors"]}, status=status.HTTP_400_BAD_REQUEST)

    quiz = result["quiz"]

    generate_use_case = GenerateQuestionsUseCase(quiz_repository, question_repository)
    gen_result = generate_use_case.execute(quiz.id, course_content, count=count)

    if not gen_result["success"]:
        quiz.delete()
        return Response({"errors": gen_result["errors"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    updated_quiz = quiz_repository.get_by_id(quiz.id)

    return Response(
        QuizSerializer(updated_quiz).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_flashcards(request):
    """Générer des flashcards avec l'IA"""
    from auto_evaluation.application.use_cases import GenerateFlashcardsUseCase
    
    user = request.user if request.user.is_authenticated else None
    user_id = user.id if user else None

    course_id = request.data.get("course_id", "")
    course_content = request.data.get("course_content", "")
    count = int(request.data.get("count", 5))
    tags = request.data.get("tags", [])

    if not course_id:
        return Response(
            {"errors": ["L'ID du cours est requis"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not course_content:
        return Response(
            {"errors": ["Le contenu du cours est requis pour la génération IA"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    use_case = GenerateFlashcardsUseCase(flashcard_repository)
    result = use_case.execute(course_content, course_id, count, user_id, tags)

    if not result["success"]:
        return Response({"errors": result["errors"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(
        FlashcardSerializer(result["flashcards"], many=True).data,
        status=status.HTTP_201_CREATED
    )