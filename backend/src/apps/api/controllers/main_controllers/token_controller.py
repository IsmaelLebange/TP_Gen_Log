from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from src.apps.interfaces.main_interfaces.auth_interface import AuthenticationServiceInterface
from src.apps.api.providers.main_provider import MainProvider
from src.domain.exceptions.domain_exceptions import AuthenticationException
from src.apps.api.serializers.main_serializers.token_serializers import (
    RefreshTokenSerializer, TokenResponseSerializer,
    TokenVerifySerializer, TokenVerifyResponseSerializer
)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import logging

logger = logging.getLogger(__name__)

class BaseTokenController(APIView):
    """Classe de base pour injecter le service d'auth"""
    def __init__(self, auth_service: AuthenticationServiceInterface = None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = MainProvider.get_auth_service() if auth_service is None else auth_service

class RefreshTokenController(BaseTokenController):
    """
    Controller pour rafraîchir un token d'accès à l'aide d'un refresh token.
    POST /api/main/token/refresh/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Appel au service existant
            result = self.auth_service.refresh_token(
                refresh_token=serializer.validated_data['refresh_token']
            )
            # On peut valider la réponse avec le serializer
            response_serializer = TokenResponseSerializer(data=result)
            response_serializer.is_valid()  # normalement toujours vrai
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception("Erreur inattendue lors du refresh token")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTokenController(BaseTokenController):
    """
    Controller pour vérifier la validité d'un token d'accès.
    POST /api/main/token/verify/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token_str = serializer.validated_data['token']
        try:
            # Décoder le token sans vérifier la signature ? Non, on vérifie.
            access_token = AccessToken(token_str)
            # Si on arrive ici, le token est valide (signature, expiration, etc.)
            payload = access_token.payload
            response_data = {
                'valid': True,
                'user_id': payload.get('user_id'),
                'exp': payload.get('exp')
            }
            response_serializer = TokenVerifyResponseSerializer(data=response_data)
            response_serializer.is_valid()
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        except (InvalidToken, TokenError) as e:
            return Response({'valid': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception("Erreur inattendue lors de la vérification du token")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)