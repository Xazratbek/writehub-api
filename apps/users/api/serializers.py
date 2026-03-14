from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import Profile


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "bio",
            "avatar",
            "website",
            "location",
            "birth_date",
        ]


class PublicProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "is_verified",
            "full_name",
            "bio",
            "avatar",
            "website",
            "location",
            "birth_date",
            "created_at",
            "updated_at",
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "bio",
            "avatar",
            "website",
            "location",
            "birth_date",
        ]


class CurrentUserSerializer(serializers.ModelSerializer):
    profile = PublicProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "is_verified",
            "created_at",
            "profile",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "is_verified",
            "created_at",
            "profile",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )

        return user