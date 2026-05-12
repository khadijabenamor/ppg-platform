from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
<<<<<<< HEAD
    path("api/auth/", include("accounts.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/ai/", include("ai_generation.urls")),
    path("api/evaluation/", include("auto_evaluation.urls")),
]
=======
    path("api/ai/",   include("ai_generation.urls")),
    path("api/auth/", include("authentication.urls")),
]
>>>>>>> e7bee7e4fca30b4c5f71fd137f001beed19bd32a
