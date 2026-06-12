from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Abonnement
from .serializers import RegisterSerializer, UserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user   = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {"message": "Compte créé avec succès !", "user": UserSerializer(user).data, "tokens": tokens},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "").strip()

        if not username or not password:
            return Response({"error": "Username et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Identifiants incorrects."}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)
        return Response(
            {"message": f"Bienvenue {user.first_name or user.username} !", "user": UserSerializer(user, context={'request': request}).data, "tokens": tokens},

            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response({"message": "Déconnexion réussie."}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user,context={"request": request}).data)

    def patch(self, request):
        user = request.user
        for field in ["first_name", "last_name","username","email"]:
            if field in request.data:
                setattr(user, field, request.data[field])
            if "avatar" in request.FILES:
                user.avatar = request.FILES["avatar"]    
        user.save()
        return Response(UserSerializer(user,context={"request": request}).data)


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        old_password = request.data.get(
            "old_password"
        )

        new_password = request.data.get(
            "new_password"
        )

        if not request.user.check_password(
            old_password
        ):

            return Response(
                {
                    "error":
                    "Mot de passe incorrect"
                },
                status=400
            )

        request.user.set_password(
            new_password
        )

        request.user.save()

        return Response(
            {
                "message":
                "Mot de passe modifié"
            }
        )   

from rest_framework.permissions import IsAuthenticated
from authentication.models import User
from ai_generation.models import GeneratedSummary
from auto_evaluation.models import Flashcard, QuizAttempt

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "admin":
            return Response(
                {"error": "Accès refusé"},
                status=status.HTTP_403_FORBIDDEN
            )

        etudiants_free = []
        etudiants_premium = []
        superviseurs = []

        students = User.objects.filter(role="etudiant")

        for student in students:

            try:
                abonnement = student.abonnement.type
            except:
                abonnement = "free"
            
            summary_count = GeneratedSummary.objects.filter(student_name=student.username).count()
            flashcard_count = Flashcard.objects.filter(created_by=student).count()
            quiz_count = QuizAttempt.objects.filter(student=student).count()

            data = {
                "id": student.id,
                "username": student.username,
                "email": student.email,
                
                "summaries_count":GeneratedSummary.objects.filter( student_name=student.username).count(),
                "flashcards_count": Flashcard.objects.filter(created_by=student).count(),
                "quiz_attempts_count":QuizAttempt.objects.filter(student=student).count(),

            }

            if abonnement == "premium":

                data["superviseur"] = (
                    student.superviseur.username
                    if student.superviseur
                    else None
                )

                etudiants_premium.append(data)

            else:
                etudiants_free.append(data)

        supervisors = User.objects.filter(role="superviseur")

        for sup in supervisors:

            superviseurs.append({
                "id": sup.id,
                "username": sup.username,
                "email": sup.email,
                "etudiants": [
                    e.username
                    for e in sup.etudiants_supervises.all()
                ]
            })

        return Response({
            "etudiants_free": etudiants_free,
            "etudiants_premium": etudiants_premium,
            "superviseurs": superviseurs,
        })
