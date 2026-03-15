# citoyen_dto.py - Data Transfer Objects pour les citoyens

from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()

class CitoyenProfileDTO(serializers.ModelSerializer):
    """DTO pour le profil citoyen"""
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'nin',
            'date_of_birth', 'phone_number', 'address', 'is_active',
            'date_joined', 'age', 'full_name'
        ]
        read_only_fields = ['id', 'is_active', 'date_joined']

    def get_age(self, obj) -> Optional[int]:
        if obj.date_of_birth:
            from src.shared.utils.date_utils import calculate_age
            return calculate_age(obj.date_of_birth)
        return None

    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

class EnrollmentRequestDTO(serializers.Serializer):
    """DTO pour la requête d'enrôlement"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    password_confirm = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    nin = serializers.CharField(required=True, max_length=20)
    date_of_birth = serializers.DateField(required=True)
    phone_number = serializers.CharField(required=False, max_length=15)
    address = serializers.CharField(required=False, max_length=255)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")

        # Vérifier l'âge minimum
        from src.shared.utils.date_utils import is_adult
        if not is_adult(data['date_of_birth']):
            raise serializers.ValidationError("L'utilisateur doit être majeur")

        return data

class UpdateProfileDTO(serializers.Serializer):
    """DTO pour la mise à jour du profil"""
    first_name = serializers.CharField(required=False, max_length=30)
    last_name = serializers.CharField(required=False, max_length=30)
    phone_number = serializers.CharField(required=False, max_length=15)
    address = serializers.CharField(required=False, max_length=255)