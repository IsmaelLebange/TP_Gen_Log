# src/apps/citoyen/controllers/biometric_controller.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from src.apps.citoyen.api.citoyen_provider import CitoyenProvider
from src.apps.citoyen.api.serializers.biometric_serializer import (
    BiometricEnrollSerializer,
    BiometricVerifySerializer,
    BiometricStatusSerializer
)

@method_decorator(csrf_exempt, name='dispatch')
class BiometricController(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # On obtient le service via le provider
        self.biometric_service = CitoyenProvider.get_biometric_service()

    def post(self, request):
        action = request.query_params.get('action')
        if action == 'enroll':
            return self._enroll(request)
        elif action == 'verify':
            return self._verify(request)
        else:
            return Response({'error': 'Action non valide'}, status=400)

    def get(self, request):
        action = request.query_params.get('action')
        if action == 'status':
            return self._status(request)
        return Response({'error': 'Action non valide'}, status=400)

    def delete(self, request):
        return self._delete(request)

    def _enroll(self, request):
        serializer = BiometricEnrollSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        citoyen_id = request.user.id
        result = self.biometric_service.enroll(
            citoyen_id,
            serializer.validated_data['type'],
            serializer.validated_data['image']
        )
        if result['success']:
            return Response(result, status=201)
        return Response(result, status=400)

    def _verify(self, request):
        serializer = BiometricVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        citoyen_id = request.user.id
        result = self.biometric_service.verify(
            citoyen_id,
            serializer.validated_data['image']
        )
        if result['success']:
            return Response(result, status=200)
        return Response(result, status=400)

    def _status(self, request):
        citoyen_id = request.user.id
        data = self.biometric_service.get_status(citoyen_id)
        serializer = BiometricStatusSerializer(data=data)
        serializer.is_valid()  # toujours vrai car c'est un simple dict
        return Response(serializer.data, status=200)

    def _delete(self, request):
        citoyen_id = request.user.id
        result = self.biometric_service.delete(citoyen_id)
        if result['success']:
            return Response(result, status=200)
        return Response(result, status=404)