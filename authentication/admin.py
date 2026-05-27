from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Abonnement

'''
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_premium", "created_at")
    list_filter  = ("role",)
    fieldsets    = UserAdmin.fieldsets + (
        ("Infos PPG", {"fields": ("role", "avatar")}),
    )'''
@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "get_abonnement",
        "superviseur",
        "created_at",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "username",
        "email",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Infos PPG",
            {
                "fields": (
                    "role",
                    "avatar",
                    "superviseur",
                )
            },
        ),
    )

    def get_abonnement(self, obj):
        try:
            return obj.abonnement.type
        except:
            return "Aucun"

    get_abonnement.short_description = "Abonnement"


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "is_active", "created_at")
    list_filter  = ("type", "is_active")