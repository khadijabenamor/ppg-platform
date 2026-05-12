from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/ai/", include("ai_generation.urls")),
    path("api/evaluation/", include("auto_evaluation.urls")),
]
