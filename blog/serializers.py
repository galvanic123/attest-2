from rest_framework import serializers
from .models import User, Post, Comment
from django.contrib.auth.hashers import make_password
from .validators import (
    validate_password_complexity,
    validate_email_domain,
    validate_title_no_bad_words,
    validate_adult,
)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "phone", "birth_date"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"validators": [validate_email_domain]},
        }

    def validate_password(self, value):
        validate_password_complexity(value)
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "birth_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "email": {"validators": [validate_email_domain]},
        }


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = serializers.StringRelatedField(many=True, read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "text",
            "image",
            "author",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "title": {"validators": [validate_title_no_bad_words]},
        }

    def validate(self, data):
        # Проверка возраста автора
        author = self.context["request"].user
        if author.birth_date:
            validate_adult(author.birth_date)
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "text", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
