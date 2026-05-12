from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Abonnement


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_premium", "created_at")
    list_filter  = ("role",)
    fieldsets    = UserAdmin.fieldsets + (
        ("Infos PPG", {"fields": ("role", "avatar")}),
    )


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "is_active", "created_at")
    list_filter  = ("type", "is_active")