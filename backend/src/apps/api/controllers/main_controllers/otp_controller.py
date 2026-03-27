from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from src.apps.api.serializers.main_serializers import OTPRequestSerializer, OTPVerifySerializer
from src.apps.api.providers.main_provider import MainProvider

class OTPController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        action = request.query_params.get('action')
        if action == 'request':
            return self._request(request)
        elif action == 'verify':
            return self._verify(request)
        return Response({'error': 'Action non valide'}, status=400)

    def _request(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        service = MainProvider.get_otp_service()
        result = service.request_otp(
            email=serializer.validated_data['email'],
            purpose=serializer.validated_data['purpose']
        )
        status_code = 200 if result['success'] else 400
        return Response(result, status=status_code)

    def _verify(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        service = MainProvider.get_otp_service()
        result = service.verify_otp(
            email=serializer.validated_data['email'],
            code=serializer.validated_data['code'],
            purpose=serializer.validated_data['purpose']
        )
        status_code = 200 if result['success'] else 400
        return Response(result, status=status_code)