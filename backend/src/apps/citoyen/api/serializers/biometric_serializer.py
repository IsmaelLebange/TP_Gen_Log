# src/apps/citoyen/serializers/biometric_serializer.py
from rest_framework import serializers
from src.apps.citoyen.models import BiometricData
from src.domain.value_objects.biometrics import BiometricType
from src.apps.citoyen.dto.biometric_dto import BiometricEnrollRequestDTO, BiometricVerifyRequestDTO

class BiometricDataSerializer(serializers.ModelSerializer):
    """Lecture seule des données biométriques (sans l'image brute pour alléger)."""
    biometric_type_label = serializers.CharField(source='get_biometric_type_display', read_only=True)

    class Meta:
        model = BiometricData
        # On évite de renvoyer 'image' (Base64 énorme) dans les listes
        fields = ['id', 'citoyen', 'biometric_type', 'biometric_type_label', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']

class BiometricEnrollSerializer(serializers.Serializer):
    """Validation et conversion en DTO pour l'enrôlement."""
    type = serializers.ChoiceField(choices=[t.value for t in BiometricType])
    image = serializers.CharField()

    def validate_image(self, value):
        if not value.startswith('data:image/'):
            raise serializers.ValidationError("Le format doit être un Data URI (data:image/...).")
        return value

    def to_dto(self) -> BiometricEnrollRequestDTO:
        """Transforme les données validées en DTO de domaine."""
        return BiometricEnrollRequestDTO.from_dict(self.validated_data)

class BiometricVerifySerializer(serializers.Serializer):
    """Validation et conversion en DTO pour la vérification."""
    image = serializers.CharField()

    def to_dto(self) -> BiometricVerifyRequestDTO:
        return BiometricVerifyRequestDTO.from_dict(self.validated_data)