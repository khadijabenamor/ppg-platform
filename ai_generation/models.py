from django.db import models


class GeneratedSummary(models.Model):
    STATUS_CHOICES = [
        ("pending",   "En attente"),
        ("validated", "Validé"),
        ("rejected",  "Rejeté"),
    ]

    SOURCE_CHOICES = [
        ("text", "Texte brut"),
        ("pdf",  "Fichier PDF"),
    ]

    original_text = models.TextField(verbose_name="Texte original")
    summary       = models.TextField(verbose_name="Résumé généré")
    keywords      = models.JSONField(default=list, verbose_name="Mots-clés")
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    student_name  = models.CharField(max_length=100, default="Étudiant")
    is_premium    = models.BooleanField(default=False)
    source        = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="text")
    file_name     = models.CharField(max_length=255, blank=True, default="")
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Résumé généré"
        verbose_name_plural = "Résumés générés"

    def __str__(self):
        return f"Résumé #{self.id} ({self.source}) — {self.get_status_display()}"


class VerificationRequest(models.Model):
    STATUS_CHOICES = [
        ("pending",   "En attente"),
        ("correct",   "Correct ✅"),
        ("incorrect", "À corriger ❌"),
    ]

    summary            = models.OneToOneField(GeneratedSummary, on_delete=models.CASCADE, related_name="verification_request")
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    supervisor_comment = models.TextField(blank=True, default="")
    requested_at       = models.DateTimeField(auto_now_add=True)
    responded_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Demande de vérification"

    def __str__(self):
        return f"Vérification résumé #{self.summary.id} — {self.get_status_display()}"
