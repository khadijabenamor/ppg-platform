from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import generate_summary, extract_keywords
from .models import GeneratedSummary


class GenerateSummaryView(APIView):
    """
    POST /api/ai/generate-summary/
    Body : { "text": "..." }
    Génère un résumé + mots-clés via Ollama et sauvegarde en BDD.
    """

    def post(self, request):
        text = request.data.get("text", "").strip()

        if not text:
            return Response(
                {"error": "Le champ 'text' est requis et ne peut pas être vide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            summary  = generate_summary(text)
            keywords = extract_keywords(text)

            obj = GeneratedSummary.objects.create(
                original_text=text,
                summary=summary,
                keywords=keywords,
            )

            return Response(
                {
                    "id":         obj.id,
                    "summary":    summary,
                    "keywords":   keywords,
                    "status":     obj.status,
                    "created_at": obj.created_at,
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
    Retourne la liste de tous les résumés (pour le superviseur).
    """

    def get(self, request):
        summaries = GeneratedSummary.objects.all()
        data = [
            {
                "id":         s.id,
                "summary":    s.summary,
                "keywords":   s.keywords,
                "status":     s.status,
                "created_at": s.created_at,
            }
            for s in summaries
        ]
        return Response(data, status=status.HTTP_200_OK)


class ValidateSummaryView(APIView):
    """
    PATCH /api/ai/summaries/<id>/validate/
    Body : { "status": "validated" } ou { "status": "rejected" }
    Permet au superviseur de valider ou rejeter un résumé.
    """

    def patch(self, request, pk):
        try:
            obj = GeneratedSummary.objects.get(pk=pk)
        except GeneratedSummary.DoesNotExist:
            return Response(
                {"error": f"Résumé avec l'id {pk} introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")
        allowed    = ["validated", "rejected"]

        if new_status not in allowed:
            return Response(
                {"error": f"Statut invalide. Valeurs acceptées : {allowed}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.status = new_status
        obj.save()

        return Response(
            {"id": obj.id, "status": obj.status, "updated_at": obj.updated_at},
            status=status.HTTP_200_OK,
        )
