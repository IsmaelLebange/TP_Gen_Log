from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from src.apps.api.providers.citoyen_provider import CitoyenProvider
from src.apps.api.serializers.citoyen_serializers.biometric_serializer import (
    BiometricEnrollSerializer,
    BiometricVerifySerializer,
    BiometricStatusSerializer
)

@method_decorator(csrf_exempt, name='dispatch')
class BiometricController(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialisation sécurisée pour le 
        
        self._biometric_service = None

    @property
    def biometric_service(self):
        if self._biometric_service is None:
            self._biometric_service = CitoyenProvider.get_biometric_service()
        return self._biometric_service

    def post(self, request):
        action = request.query_params.get('action')
        if action == 'enroll':
            return self._enroll(request)
        elif action == 'verify':
            return self._verify(request)
        return Response({'error': 'Action non valide'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        action = request.query_params.get('action')
        if action == 'status':
            return self._status(request)
        return Response({'error': 'Action non valide'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return self._delete(request)

    def _enroll(self, request):
        serializer = BiometricEnrollSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # On utilise l'ID envoyé par le mobile
        citoyen_id = serializer.validated_data['citoyen_id']

        result = self.biometric_service.enroll(
            citoyen_id=citoyen_id, 
            biometric_type=serializer.validated_data['type'],
            image_base64=serializer.validated_data['image']
        )
        
        if result.get('success'):
            # Utilise aussi l'ID ici
            enrollment_service = CitoyenProvider.get_enrollment_service()
            enrollment_service.update_biometric_complete(citoyen_id, True)
            return Response(result, status=201)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def _verify(self, request):
        serializer = BiometricVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = self.biometric_service.verify(
            citoyen_id=request.user.id,
            image_base64=serializer.validated_data['image']
        )
        return Response(result, status=status.HTTP_200_OK)

    def _status(self, request):
        result = self.biometric_service.get_status(citoyen_id=request.user.id)
        return Response(result, status=status.HTTP_200_OK)

    def _delete(self, request):
        result = self.biometric_service.delete(citoyen_id=request.user.id)
        return Response(result, status=status.HTTP_200_OK)