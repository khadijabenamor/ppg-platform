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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Résumé généré"
        verbose_name_plural = "Résumés générés"

    def __str__(self):
        return f"Résumé #{self.id} — {self.get_status_display()}"
