from rest_framework import serializers
from src.models import Document

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['type', 'numero', 'fichier', 'date_emission', 'date_expiration']
        extra_kwargs = {
            'fichier': {'write_only': True},
            'date_emission': {'required': True},
            'date_expiration': {'required': False, 'allow_null': True},
        }

    def validate_type(self, value):
        if value not in dict(Document.TypeDocument.choices):
            raise serializers.ValidationError(f"Type invalide. Choisir parmi {list(dict(Document.TypeDocument.choices).keys())}")
        return value

class DocumentResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    numero = serializers.CharField()
    fichier_url = serializers.CharField(allow_null=True)
    date_emission = serializers.DateField()
    date_expiration = serializers.DateField(allow_null=True)
    statut = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()