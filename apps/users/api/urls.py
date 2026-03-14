from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterAPIView,
    MeAPIView,
    PublicProfileAPIView,
    MyProfileUpdateAPIView,
)


urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeAPIView.as_view(), name="auth-me"),

    path("profiles/me/", MyProfileUpdateAPIView.as_view(), name="profile-me-update"),
    path("profiles/<str:username>/", PublicProfileAPIView.as_view(), name="profile-public"),
]