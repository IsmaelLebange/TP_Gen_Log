# src/apps/main/api/controllers/auth_controllers.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from src.apps.api.providers.main_provider import MainProvider
from src.domain.exceptions.domain_exceptions import AuthenticationException
from src.apps.api.serializers.main_serializers.auth_serializers import LoginSerializer,RegisterSerializer

class BaseAuthController(APIView):
    """Classe de base pour injecter le service"""
    @property
    def auth_service(self):
        # On récupère le service via le provider seulement quand on en a besoin
        return MainProvider.get_auth_service()

# ... (tes imports restent les mêmes)

class LoginController(BaseAuthController):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Appel au service avec le champ 'login'
            result = self.auth_service.login(
                login_input=serializer.validated_data['login'],
                password=serializer.validated_data['password'],
                request=request
            )
            return Response(result, status=status.HTTP_200_OK)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterController(BaseAuthController):
    permission_classes = [AllowAny]

    def post(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        
        # 1. Validation technique (DRF s'occupe des types et champs requis)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. On récupère les données validées et on retire ce qui ne va pas au service
            clean_data = serializer.validated_data.copy()
            clean_data.pop('password_confirm', None) 
            
            # 3. Appel au service (qui utilisera tes Value Objects NIN, Email, etc.)
            result = self.auth_service.register(
                **clean_data,
                request=request
            )
            return Response(result, status=status.HTTP_201_CREATED)
            
        except (AuthenticationException, ValueError) as e:
            # On attrape la ValueError levée par tes Value Objects (ex: NIN invalide)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ... (LogoutController reste le même)
class LogoutController(BaseAuthController):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        self.auth_service.logout(request.user, request)
        return Response({'message': 'Déconnecté'}, status=status.HTTP_200_OK)