from django.db import models


class GeneratedSummary(models.Model):
    STATUS_CHOICES = [
        ("pending",   "En attente"),
        ("validated", "Validé"),
        ("rejected",  "Rejeté"),
    ]

    original_text = models.TextField(verbose_name="Texte original")
    summary       = models.TextField(verbose_name="Résumé généré")
    keywords      = models.JSONField(default=list, verbose_name="Mots-clés")
    status        = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Statut",
    )
    # Qui a demandé ce résumé
    student_name  = models.CharField(max_length=100, default="Étudiant", verbose_name="Nom étudiant")
    is_premium    = models.BooleanField(default=False, verbose_name="Abonnement Premium")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Résumé généré"
        verbose_name_plural = "Résumés générés"

    def __str__(self):
        return f"Résumé #{self.id} — {self.get_status_display()}"


class VerificationRequest(models.Model):
    STATUS_CHOICES = [
        ("pending",   "En attente"),
        ("correct",   "Correct ✅"),
        ("incorrect", "À corriger ❌"),
    ]

    summary        = models.OneToOneField(
        GeneratedSummary,
        on_delete=models.CASCADE,
        related_name="verification_request",
        verbose_name="Résumé concerné",
    )
    status         = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Statut vérification",
    )
    supervisor_comment = models.TextField(
        blank=True,
        default="",
        verbose_name="Commentaire du superviseur",
    )
    requested_at   = models.DateTimeField(auto_now_add=True)
    responded_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Demande de vérification"
        verbose_name_plural = "Demandes de vérification"

    def __str__(self):
        return f"Vérification résumé #{self.summary.id} — {self.get_status_display()}"
