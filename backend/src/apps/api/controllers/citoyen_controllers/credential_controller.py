from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from src.apps.api.providers.citoyen_provider import CitoyenProvider
from src.apps.api.serializers.citoyen_serializers.credential_serializer import (
    ChangePasswordSerializer, ResetPasswordRequestSerializer, ResetPasswordConfirmSerializer
)
from src.domain.exceptions.domain_exceptions import AuthenticationException

class CredentialController(APIView):
    permission_classes = [IsAuthenticated]

    @property
    def credential_service(self):
        return CitoyenProvider.get_credential_service()

    def post(self, request):
        action = request.query_params.get('action')
        if action == 'change_password':
            return self._change_password(request)
        else:
            return Response({'error': 'Action non valide'}, status=400)

    def _change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        try:
            result = self.credential_service.change_password(
                user_id=request.user.id,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )
            return Response(result, status=200)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=400)

class PasswordResetController(APIView):
    permission_classes = [AllowAny]

    @property
    def credential_service(self):
        return CitoyenProvider.get_credential_service()

    def post(self, request):
        action = request.query_params.get('action')
        if action == 'request':
            return self._reset_request(request)
        elif action == 'confirm':
            return self._reset_confirm(request)
        else:
            return Response({'error': 'Action non valide'}, status=400)

    def _reset_request(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        try:
            result = self.credential_service.reset_password_request(
                email=serializer.validated_data['email']
            )
            return Response(result, status=200)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=400)

    def _reset_confirm(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        try:
            result = self.credential_service.reset_password_confirm(
                email=serializer.validated_data['email'],
                otp=serializer.validated_data['otp'],
                new_password=serializer.validated_data['new_password']
            )
            return Response(result, status=200)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=400)