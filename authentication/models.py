from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("etudiant",    "Étudiant"),
        ("superviseur", "Superviseur"),
        ("admin","administrateur"),
    ]
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default="etudiant")
    '''avatar     = models.CharField(max_length=255, blank=True, default="")'''
    avatar = models.ImageField(upload_to="avatars/",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    superviseur = models.ForeignKey(
    'self',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    limit_choices_to={'role': 'superviseur'},
    related_name='etudiants_supervises'
)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_premium(self):
        try:
            return self.abonnement.type == "premium" and self.abonnement.is_active
        except:
            return False


class Abonnement(models.Model):
    TYPE_CHOICES = [
        ("free",    "Gratuit"),
        ("premium", "Premium"),
        
    ]
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name="abonnement")
    type      = models.CharField(max_length=10, choices=TYPE_CHOICES, default="free")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_type_display()}"