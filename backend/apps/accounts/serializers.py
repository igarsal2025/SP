from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AccessPolicy, UserProfile


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "company",
            "role",
            "department",
            "location",
            "phone",
            "preferences",
            "last_login_at",
            "created_at",
            "updated_at",
        ]


class AccessPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPolicy
        fields = [
            "id",
            "company",
            "action",
            "conditions",
            "effect",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]
