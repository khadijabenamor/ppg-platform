from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .services import generate_summary, extract_keywords
from .models import GeneratedSummary, VerificationRequest
import pdfplumber
import io


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


class GenerateFromPDFView(APIView):
    """
    POST /api/ai/generate-from-pdf/
    Form-data : { "pdf": <fichier>, "student_name": "...", "is_premium": true/false }
    Extrait le texte du PDF puis génère résumé + mots-clés automatiquement.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        pdf_file     = request.FILES.get("pdf")
        student_name = request.data.get("student_name", "Étudiant").strip()
        is_premium   = request.data.get("is_premium", "false").lower() == "true"

        # Vérifications
        if not pdf_file:
            return Response(
                {"error": "Aucun fichier PDF fourni."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pdf_file.name.endswith(".pdf"):
            return Response(
                {"error": "Le fichier doit être un PDF (.pdf)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if pdf_file.size > 10 * 1024 * 1024:  # 10 MB max
            return Response(
                {"error": "Le fichier est trop grand. Maximum 10 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Extraction du texte depuis le PDF
            pdf_bytes = pdf_file.read()
            text = ""

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            text = text.strip()

            if not text:
                return Response(
                    {"error": "Impossible d'extraire le texte de ce PDF. Le fichier est peut-être scanné ou protégé."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(text) < 50:
                return Response(
                    {"error": "Le texte extrait est trop court pour générer un résumé."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Génération résumé + mots-clés
            summary_text = generate_summary(text)
            keywords     = extract_keywords(text)

            # Sauvegarde
            obj = GeneratedSummary.objects.create(
                original_text=text,
                summary=summary_text,
                keywords=keywords,
                student_name=student_name,
                is_premium=is_premium,
                source="pdf",
                file_name=pdf_file.name,
            )

            return Response(
                {
                    "id":            obj.id,
                    "summary":       summary_text,
                    "keywords":      keywords,
                    "status":        obj.status,
                    "is_premium":    obj.is_premium,
                    "student_name":  obj.student_name,
                    "file_name":     obj.file_name,
                    "pages":         len(pdf.pages) if 'pdf' in dir() else None,
                    "text_length":   len(text),
                    "created_at":    obj.created_at,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (ConnectionError, TimeoutError) as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": f"Erreur lors du traitement du PDF : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SummaryListView(APIView):
    """
    GET /api/ai/summaries/
    Retourne uniquement les résumés Premium avec demande de vérification.
    """
    def get(self, request):
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
                "source":       s.source,
                "file_name":    s.file_name,
                "created_at":   s.created_at,
                "verification": verification,
            })

        return Response(data, status=status.HTTP_200_OK)


class ValidateSummaryView(APIView):
    """
    PATCH /api/ai/summaries/<id>/validate/
    """
    def patch(self, request, pk):
        try:
            obj = GeneratedSummary.objects.get(pk=pk)
        except GeneratedSummary.DoesNotExist:
            return Response({"error": f"Résumé #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["validated", "rejected"]:
            return Response({"error": "Statut invalide."}, status=status.HTTP_400_BAD_REQUEST)

        obj.status = new_status
        obj.save()
        return Response({"id": obj.id, "status": obj.status}, status=status.HTTP_200_OK)


class RequestVerificationView(APIView):
    """
    POST /api/ai/summaries/<id>/request-verification/
    """
    def post(self, request, pk):
        try:
            summary = GeneratedSummary.objects.get(pk=pk)
        except GeneratedSummary.DoesNotExist:
            return Response({"error": f"Résumé #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if not summary.is_premium:
            return Response(
                {"error": "Cette fonctionnalité est réservée aux abonnés Premium."},
                status=status.HTTP_403_FORBIDDEN,
            )

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
    """
    def patch(self, request, pk):
        try:
            vr = VerificationRequest.objects.get(pk=pk)
        except VerificationRequest.DoesNotExist:
            return Response({"error": f"Demande #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        comment    = request.data.get("supervisor_comment", "").strip()

        if new_status not in ["correct", "incorrect"]:
            return Response({"error": "Statut invalide."}, status=status.HTTP_400_BAD_REQUEST)

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
                    "source":       vr.summary.source,
                    "file_name":    vr.summary.file_name,
                },
            }
            for vr in vrs
        ]
        return Response(data, status=status.HTTP_200_OK)
