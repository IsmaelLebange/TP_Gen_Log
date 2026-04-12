from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    
class ProfileUpdateSerializer(serializers.Serializer):
    telephone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    adresse = serializers.CharField(required=False, allow_blank=True)
    nom_pere = serializers.CharField(required=False, allow_blank=True, max_length=100)
    nom_mere = serializers.CharField(required=False, allow_blank=True, max_length=100)
    sexe = serializers.CharField(required=False, allow_blank=True, max_length=15)
    lieu_naissance = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    def validate_nom_pere(self, value):
        # Exemple de validation supplémentaire
        if value and len(value) < 2:
            raise serializers.ValidationError("Le nom du père doit faire au moins 2 caractères")
        return value

    def validate_nom_mere(self, value):
        if value and len(value) < 2:
            raise serializers.ValidationError("Le nom de la mère doit faire au moins 2 caractères")
        return value