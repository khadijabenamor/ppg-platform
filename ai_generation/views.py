from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import generate_summary, extract_keywords
from .models import GeneratedSummary, VerificationRequest
import openai


class GenerateSummaryView(APIView):
    """
    POST /api/ai/generate-summary/
    Body : { "text": "...", "student_name": "...", "is_premium": true/false }
    """
    def post(self, request):
        text         = request.data.get("text", "").strip()
        student_name = request.data.get("student_name", "Étudiant").strip()
        is_premium   = request.data.get("is_premium", False)

        if not text:
            return Response(
                {"error": "Le champ 'text' est requis et ne peut pas être vide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            summary_text = generate_summary(text)
            keywords     = extract_keywords(text)

            obj = GeneratedSummary.objects.create(
                original_text=text,
                summary=summary_text,
                keywords=keywords,
                student_name=student_name,
                is_premium=is_premium,
            )

            return Response(
                {
                    "id":           obj.id,
                    "summary":      summary_text,
                    "keywords":     keywords,
                    "status":       obj.status,
                    "is_premium":   obj.is_premium,
                    "student_name": obj.student_name,
                    "created_at":   obj.created_at,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (ConnectionError, TimeoutError) as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": f"Erreur interne : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SummaryListView(APIView):
    """
    GET /api/ai/summaries/
    Retourne uniquement les résumés qui ont une demande de vérification.
    """
    def get(self, request):
        # On ne montre que les résumés Premium avec demande de vérification
        summaries = GeneratedSummary.objects.filter(
            is_premium=True,
            verification_request__isnull=False
        )
        data = []
        for s in summaries:
            try:
                vr = s.verification_request
                verification = {
                    "id":                 vr.id,
                    "status":             vr.status,
                    "supervisor_comment": vr.supervisor_comment,
                    "requested_at":       vr.requested_at,
                    "responded_at":       vr.responded_at,
                }
            except VerificationRequest.DoesNotExist:
                verification = None

            data.append({
                "id":           s.id,
                "summary":      s.summary,
                "keywords":     s.keywords,
                "status":       s.status,
                "student_name": s.student_name,
                "is_premium":   s.is_premium,
                "created_at":   s.created_at,
                "verification": verification,
            })

        return Response(data, status=status.HTTP_200_OK)

class ValidateSummaryView(APIView):
    """
    PATCH /api/ai/summaries/<id>/validate/
    Body : { "status": "validated" } ou { "status": "rejected" }
    """
    def patch(self, request, pk):
        try:
            obj = GeneratedSummary.objects.get(pk=pk)
        except GeneratedSummary.DoesNotExist:
            return Response({"error": f"Résumé #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["validated", "rejected"]:
            return Response({"error": "Statut invalide. Valeurs : 'validated' ou 'rejected'"}, status=status.HTTP_400_BAD_REQUEST)

        obj.status = new_status
        obj.save()

        return Response({"id": obj.id, "status": obj.status}, status=status.HTTP_200_OK)


class RequestVerificationView(APIView):
    """
    POST /api/ai/summaries/<id>/request-verification/
    Réservé aux étudiants Premium — crée une demande de vérification.
    """
    def post(self, request, pk):
        try:
            summary = GeneratedSummary.objects.get(pk=pk)
        except GeneratedSummary.DoesNotExist:
            return Response({"error": f"Résumé #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier abonnement premium
        if not summary.is_premium:
            return Response(
                {"error": "Cette fonctionnalité est réservée aux abonnés Premium."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Vérifier qu'une demande n'existe pas déjà
        if hasattr(summary, 'verification_request'):
            return Response(
                {"error": "Une demande de vérification existe déjà pour ce résumé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vr = VerificationRequest.objects.create(summary=summary)

        return Response(
            {
                "id":           vr.id,
                "summary_id":   summary.id,
                "status":       vr.status,
                "requested_at": vr.requested_at,
                "message":      "Demande envoyée au superviseur avec succès !",
            },
            status=status.HTTP_201_CREATED,
        )


class RespondVerificationView(APIView):
    """
    PATCH /api/ai/verification/<id>/respond/
    Body : { "status": "correct"/"incorrect", "supervisor_comment": "..." }
    Permet au superviseur de répondre à une demande de vérification.
    """
    def patch(self, request, pk):
        try:
            vr = VerificationRequest.objects.get(pk=pk)
        except VerificationRequest.DoesNotExist:
            return Response({"error": f"Demande #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        comment    = request.data.get("supervisor_comment", "").strip()

        if new_status not in ["correct", "incorrect"]:
            return Response(
                {"error": "Statut invalide. Valeurs : 'correct' ou 'incorrect'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_status == "incorrect" and not comment:
            return Response(
                {"error": "Un commentaire est obligatoire si le résumé est incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vr.status             = new_status
        vr.supervisor_comment = comment
        vr.responded_at       = timezone.now()
        vr.save()

        return Response(
            {
                "id":                 vr.id,
                "status":             vr.status,
                "supervisor_comment": vr.supervisor_comment,
                "responded_at":       vr.responded_at,
            },
            status=status.HTTP_200_OK,
        )


class VerificationListView(APIView):
    """
    GET /api/ai/verifications/
    Liste toutes les demandes de vérification (pour le superviseur).
    """
    def get(self, request):
        vrs = VerificationRequest.objects.select_related("summary").all()
        data = [
            {
                "id":                 vr.id,
                "status":             vr.status,
                "supervisor_comment": vr.supervisor_comment,
                "requested_at":       vr.requested_at,
                "responded_at":       vr.responded_at,
                "summary": {
                    "id":           vr.summary.id,
                    "summary":      vr.summary.summary,
                    "keywords":     vr.summary.keywords,
                    "student_name": vr.summary.student_name,
                },
            }
            for vr in vrs
        ]
        return Response(data, status=status.HTTP_200_OK)
