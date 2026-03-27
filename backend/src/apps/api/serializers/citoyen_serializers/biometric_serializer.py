from rest_framework import serializers
from src.domain.entities.biometric import BiometricEntity
from src.domain.value_objects.biometrics import BiometricType

class BiometricEnrollSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[t.value for t in BiometricType])
    image = serializers.CharField()

    def to_domain(self, citoyen_id: int):
        try:
            return BiometricEntity.from_request(self.validated_data, citoyen_id)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

class BiometricVerifySerializer(serializers.Serializer):
    image = serializers.CharField()

    # Même pour la vérification, on peut passer par une entité éphémère
    # ou juste valider le format ici
    def validate_image(self, value):
        if not value.startswith('data:image/'):
            raise serializers.ValidationError("Format d'image invalide.")
        return value

class BiometricStatusSerializer(serializers.Serializer):
    enrolled = serializers.BooleanField()
    type = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)