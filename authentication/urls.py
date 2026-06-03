from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, ProfileView
from .views import AdminDashboardView , ChangePasswordView

urlpatterns = [
    path("register/",      RegisterView.as_view(),     name="auth-register"),
    path("login/",         LoginView.as_view(),         name="auth-login"),
    path("logout/",        LogoutView.as_view(),        name="auth-logout"),
    path("profile/",       ProfileView.as_view(),       name="auth-profile"),
    path("token/refresh/", TokenRefreshView.as_view(),  name="token-refresh"),
    path("admin-dashboard/",AdminDashboardView.as_view(),name="admin-dashboard"),
    path("change-password/",ChangePasswordView.as_view(),name="change-password"),
]