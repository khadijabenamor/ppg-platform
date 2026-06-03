from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/ai/",         include("ai_generation.urls")),
    path("api/auth/",       include("authentication.urls")),
    path("api/accounts/",   include("accounts.urls")),
    path("api/evaluation/", include("auto_evaluation.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
'''if settings.DEBUG:'''
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)