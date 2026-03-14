from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import Profile

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = ["full_name","bio","avatar","website","location","birth_date" ]

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
            "profile"
        ]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)
    password_confirm = serializers.CharField(write_only=True,min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm"
        ]

    def validate(self, attrs):
        self.password = attrs.get("password")
        self.password_confirm = attrs.get("password_confirm")

        if self.password != self.password_confirm:
            raise serializers.ValidationError(
                {
                    "password_confirm": "Passwordlar bir biriga mos kelmadi"
                }
            )

        return attrs


    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email = validated_data["email"],
            username = validated_data["username"],
            password = validated_data["password"],)
        return user
