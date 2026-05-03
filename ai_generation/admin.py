from django.contrib import admin
from .models import GeneratedSummary, VerificationRequest


@admin.register(GeneratedSummary)
class GeneratedSummaryAdmin(admin.ModelAdmin):
    list_display    = ("id", "student_name", "is_premium", "status", "created_at")
    list_filter     = ("status", "is_premium")
    search_fields   = ("summary", "original_text", "student_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display    = ("id", "summary", "status", "requested_at", "responded_at")
    list_filter     = ("status",)
    readonly_fields = ("requested_at", "responded_at")
