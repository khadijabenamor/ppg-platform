from django.contrib import admin
from .models import GeneratedSummary


@admin.register(GeneratedSummary)
class GeneratedSummaryAdmin(admin.ModelAdmin):
    list_display  = ("id", "status", "created_at", "updated_at")
    list_filter   = ("status",)
    search_fields = ("summary", "original_text")
    readonly_fields = ("created_at", "updated_at")
