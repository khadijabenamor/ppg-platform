from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .services import generate_summary, extract_keywords
from .models import GeneratedSummary


# ──────────────────────────────────────────────
# Tests du service IA
# ──────────────────────────────────────────────

class GenerateSummaryServiceTests(TestCase):

    @patch("ai_generation.services._call_ollama")
    def test_generate_summary_success(self, mock_ollama):
        """Vérifie qu'un résumé est bien retourné."""
        mock_ollama.return_value = "Ceci est un résumé de test."
        result = generate_summary("Un texte de cours quelconque.")
        self.assertEqual(result, "Ceci est un résumé de test.")

    def test_generate_summary_empty_text(self):
        """Vérifie qu'une ValueError est levée si le texte est vide."""
        with self.assertRaises(ValueError):
            generate_summary("")

    def test_generate_summary_whitespace_only(self):
        """Vérifie qu'une ValueError est levée si le texte ne contient que des espaces."""
        with self.assertRaises(ValueError):
            generate_summary("   ")


class ExtractKeywordsServiceTests(TestCase):

    @patch("ai_generation.services._call_ollama")
    def test_extract_keywords_success(self, mock_ollama):
        """Vérifie que les mots-clés sont retournés en liste."""
        mock_ollama.return_value = "Python, Django, API, résumé, IA"
        result = extract_keywords("Un texte sur Python et Django.")
        self.assertIsInstance(result, list)
        self.assertIn("Python", result)
        self.assertIn("Django", result)

    def test_extract_keywords_empty_text(self):
        """Vérifie qu'une ValueError est levée si le texte est vide."""
        with self.assertRaises(ValueError):
            extract_keywords("")


# ──────────────────────────────────────────────
# Tests des endpoints API
# ──────────────────────────────────────────────

class GenerateSummaryViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url    = reverse("generate-summary")

    @patch("ai_generation.views.generate_summary")
    @patch("ai_generation.views.extract_keywords")
    def test_post_success(self, mock_keywords, mock_summary):
        """Vérifie qu'un POST valide retourne 201."""
        mock_summary.return_value  = "Résumé généré."
        mock_keywords.return_value = ["mot1", "mot2"]

        response = self.client.post(self.url, {"text": "Un texte valide."}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("summary",  response.data)
        self.assertIn("keywords", response.data)
        self.assertEqual(response.data["status"], "pending")

    def test_post_missing_text(self):
        """Vérifie qu'un POST sans texte retourne 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_empty_text(self):
        """Vérifie qu'un POST avec texte vide retourne 400."""
        response = self.client.post(self.url, {"text": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ValidateSummaryViewTests(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.summary = GeneratedSummary.objects.create(
            original_text="Texte original.",
            summary="Résumé test.",
            keywords=["mot1", "mot2"],
        )

    def test_validate_summary_success(self):
        url      = reverse("validate-summary", kwargs={"pk": self.summary.pk})
        response = self.client.patch(url, {"status": "validated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "validated")

    def test_reject_summary_success(self):
        url      = reverse("validate-summary", kwargs={"pk": self.summary.pk})
        response = self.client.patch(url, {"status": "rejected"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "rejected")

    def test_invalid_status(self):
        url      = reverse("validate-summary", kwargs={"pk": self.summary.pk})
        response = self.client.patch(url, {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_summary_not_found(self):
        url      = reverse("validate-summary", kwargs={"pk": 9999})
        response = self.client.patch(url, {"status": "validated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
