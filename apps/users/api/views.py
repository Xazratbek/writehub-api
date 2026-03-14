from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Profile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CurrentUserSerializer,
    PublicProfileSerializer,
    ProfileUpdateSerializer,
)


User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: UserSerializer},
        operation_summary="Register a new user",
        operation_description="Create a new user account with email, username, password, and password confirmation.",
        security=[],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_serializer = UserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: CurrentUserSerializer},
        operation_summary="Get current user",
        operation_description="Return the currently authenticated user.",
        security=[{"Bearer": []}],
    )
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicProfileAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: PublicProfileSerializer},
        operation_summary="Get public profile",
        operation_description="Return public profile information by username.",
        security=[],
    )
    def get(self, request, username):
        profile = get_object_or_404(
            Profile.objects.select_related("user"),
            user__username=username,
        )
        serializer = PublicProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        request_body=ProfileUpdateSerializer,
        responses={200: PublicProfileSerializer},
        operation_summary="Update my profile",
        operation_description="Partially update the authenticated user's profile.",
        security=[{"Bearer": []}],
    )
    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user.profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = PublicProfileSerializer(request.user.profile)
        return Response(response_serializer.data, status=status.HTTP_200_OK)