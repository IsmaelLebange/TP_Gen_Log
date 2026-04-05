# src/apps/api/serializers/admin_serializers/validation_workflow_serializers.py
from rest_framework import serializers

class DocumentRejectSerializer(serializers.Serializer):
    commentaire = serializers.CharField(required=True, min_length=1)

class DocumentResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    type = serializers.CharField()
    numero = serializers.CharField()
    fichier_url = serializers.CharField(allow_null=True)
    date_emission = serializers.DateField()
    date_expiration = serializers.DateField(allow_null=True)
    statut = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    valide_par_id = serializers.IntegerField(allow_null=True)
    date_validation = serializers.DateTimeField(allow_null=True)
    commentaire_rejet = serializers.CharField()