from rest_framework import serializers

class RefreshTokenSerializer(serializers.Serializer):
    """Serializer pour la demande de rafraîchissement de token"""
    refresh_token = serializers.CharField(required=True, help_text="JWT refresh token")

class TokenResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse contenant un nouveau token"""
    access_token = serializers.CharField()
    token_type = serializers.CharField(default='Bearer')
    expires_in = serializers.IntegerField(default=3600)

class TokenVerifySerializer(serializers.Serializer):
    """Serializer pour la vérification d'un token"""
    token = serializers.CharField(required=True, help_text="JWT access token à vérifier")

class TokenVerifyResponseSerializer(serializers.Serializer):
    """Réponse après vérification de token"""
    valid = serializers.BooleanField()
    user_id = serializers.IntegerField(required=False)
    exp = serializers.IntegerField(required=False)  # timestamp d'expiration