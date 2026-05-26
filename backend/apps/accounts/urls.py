from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AnonymousLoginView,
    ClaimAccountView,
    GoogleAuthView,
    PlayerProfileView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("anonymous/", AnonymousLoginView.as_view(), name="auth-anonymous"),
    path("claim/", ClaimAccountView.as_view(), name="auth-claim"),
    path("google/", GoogleAuthView.as_view(), name="auth-google"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("me/", PlayerProfileView.as_view(), name="auth-me"),
]
