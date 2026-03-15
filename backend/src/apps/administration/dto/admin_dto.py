# admin_dto.py - Data Transfer Objects pour l'administration

from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import Optional, Dict, Any

User = get_user_model()

class UserManagementDTO(serializers.ModelSerializer):
    """DTO pour la gestion des utilisateurs en admin"""
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'nin',
            'date_of_birth', 'phone_number', 'address', 'is_active',
            'is_staff', 'is_superuser', 'date_joined', 'last_login',
            'age', 'full_name', 'status'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_age(self, obj) -> Optional[int]:
        if obj.date_of_birth:
            from src.shared.utils.date_utils import calculate_age
            return calculate_age(obj.date_of_birth)
        return None

    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

    def get_status(self, obj) -> str:
        if obj.is_superuser:
            return "Super Admin"
        elif obj.is_staff:
            return "Admin"
        elif obj.is_active:
            return "Citoyen Actif"
        else:
            return "Inactif"

class StatisticsDTO(serializers.Serializer):
    """DTO pour les statistiques générales"""
    total_citoyens = serializers.IntegerField()
    citoyens_actifs = serializers.IntegerField()
    nouveaux_citoyens_ce_mois = serializers.IntegerField()
    citoyens_par_tranche_age = serializers.DictField()
    repartition_geographique = serializers.DictField()

class AuditLogDTO(serializers.Serializer):
    """DTO pour les logs d'audit"""
    id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    action = serializers.CharField()
    user_id = serializers.CharField(allow_null=True)
    resource = serializers.CharField(allow_null=True)
    details = serializers.DictField()
    ip_address = serializers.IPAddressField(allow_null=True)

class ValidationWorkflowDTO(serializers.Serializer):
    """DTO pour le workflow de validation"""
    citoyen_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['pending', 'approved', 'rejected'])
    validator_id = serializers.IntegerField(allow_null=True)
    validation_date = serializers.DateTimeField(allow_null=True)
    comments = serializers.CharField(allow_blank=True)
    documents_validated = serializers.ListField(child=serializers.CharField())

class BulkActionDTO(serializers.Serializer):
    """DTO pour les actions en masse"""
    action = serializers.ChoiceField(choices=['activate', 'deactivate', 'delete'])
    user_ids = serializers.ListField(child=serializers.IntegerField())
    reason = serializers.CharField(required=False)