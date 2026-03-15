# src/apps/main/api/controllers/auth_controllers.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from src.apps.main.interfaces.auth_interface import AuthenticationServiceInterface
from src.apps.main.main_provider import ServiceProvider
from src.domain.exceptions.domain_exceptions import AuthenticationException

class BaseAuthController(APIView):
    """Classe de base pour injecter le service"""
    def __init__(self, auth_service: AuthenticationServiceInterface = None, **kwargs):
        super().__init__(**kwargs)
        # Injection manuelle (ou via un conteneur si tu en as un)
        self.auth_service = ServiceProvider.get_auth_service() if auth_service is None else auth_service

# ... (tes imports restent les mêmes)

class LoginController(BaseAuthController):
    permission_classes = [AllowAny]
    
    def post(self, request):
        from src.apps.main.api.serializers.auth_serializers import LoginSerializer
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = self.auth_service.login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                request=request
            )
            return Response(result, status=status.HTTP_200_OK)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterController(BaseAuthController):
    permission_classes = [AllowAny]

    def post(self, request):
        from src.apps.main.api.serializers.auth_serializers import RegisterSerializer
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- MODIFICATION ICI ---
            # On récupère les données validées
            data = serializer.validated_data.copy()
            # On retire password_confirm pour ne pas faire planter le service
            data.pop('password_confirm', None) 
            
            # On passe les données nettoyées au service
            result = self.auth_service.register(
                **data,
                request=request
            )
            # ------------------------
            return Response(result, status=status.HTTP_201_CREATED)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ... (LogoutController reste le même)
class LogoutController(BaseAuthController):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        self.auth_service.logout(request.user, request)
        return Response({'message': 'Déconnecté'}, status=status.HTTP_200_OK)