# auth_dto.py - Data Transfer Objects pour l'authentification

from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()

class LoginRequestDTO(serializers.Serializer):
    """DTO pour la requête de connexion"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=6)

class TokenResponseDTO(serializers.Serializer):
    """DTO pour la réponse avec tokens"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField()
    user = serializers.DictField()

class RefreshTokenRequestDTO(serializers.Serializer):
    """DTO pour la requête de rafraîchissement de token"""
    refresh_token = serializers.CharField(required=True)

class UserProfileDTO(serializers.ModelSerializer):
    """DTO pour le profil utilisateur"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'nin', 'is_active']
        read_only_fields = ['id', 'is_active']

class RegisterRequestDTO(serializers.Serializer):
    """DTO pour l'inscription d'un nouvel utilisateur"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    password_confirm = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    nin = serializers.CharField(required=True, max_length=20)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

class OTPRequestDTO(serializers.Serializer):
    """DTO pour la requête OTP"""
    email = serializers.EmailField(required=True)

class OTPVerifyDTO(serializers.Serializer):
    """DTO pour la vérification OTP"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)