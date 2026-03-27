from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=4)
    otp = serializers.CharField(required=False, max_length=6, allow_blank=True)

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=4)
    password_confirm = serializers.CharField(required=True, write_only=True)
    nom = serializers.CharField(required=True, max_length=100)
    prenom = serializers.CharField(required=True, max_length=100)
    postnom = serializers.CharField(required=False, allow_blank=True, max_length=100)
    nin = serializers.CharField(required=True, min_length=12, max_length=20)
    date_naissance = serializers.DateField(required=True) # DRF valide le format YYYY-MM-DD tout seul !
    telephone = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # Vérification de la correspondance des mots de passe
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return data


class RefreshTokenSerializer(serializers.Serializer):
    """Valide que le client envoie bien un refresh token valide"""
    refresh = serializers.CharField(required=True)

class TokenVerifySerializer(serializers.Serializer):
    """Valide le token avant de vérifier sa signature"""
    token = serializers.CharField(required=True)

class TokenResponseSerializer(serializers.Serializer):
    """Utilisé pour formater la RÉPONSE (Sortie) vers le client"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()