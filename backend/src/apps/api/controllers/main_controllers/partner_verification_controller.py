from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from src.apps.api.providers.main_provider import MainProvider
from src.apps.api.serializers.main_serializers.partner_verification_serializers import (
    PartnerVerifyRequestSerializer, PartnerVerifyResponseSerializer,
    QRCodeRequestSerializer, QRCodeResponseSerializer
)
from src.domain.exceptions.domain_exceptions import AuthenticationException
import logging

logger = logging.getLogger(__name__)

class PartnerVerificationController(APIView):
    permission_classes = [AllowAny]

    @property
    def partner_service(self):
        return MainProvider.get_partner_verification_service()

    def post(self, request):
        action = request.query_params.get('action')
        if action == 'verify':
            return self._verify(request)
        elif action == 'qr':
            return self._qr(request)
        else:
            return Response({'error': 'Action non valide'}, status=400)

    def _verify(self, request):
        serializer = PartnerVerifyRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            result = self.partner_service.verify_by_nin(
                token=serializer.validated_data['token'],
                nin=serializer.validated_data['nin']
            )
            response_serializer = PartnerVerifyResponseSerializer(result)
            return Response(response_serializer.data, status=200)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=401)
        except Exception as e:
            logger.exception("Erreur inattendue")
            return Response({'error': 'Erreur interne'}, status=500)

    def _qr(self, request):
        serializer = QRCodeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            result = self.partner_service.generate_qr_code(
                nin=serializer.validated_data['nin']
            )
            response_serializer = QRCodeResponseSerializer(result)
            return Response(response_serializer.data, status=200)
        except AuthenticationException as e:
            return Response({'error': str(e)}, status=401)
        except Exception as e:
            logger.exception("Erreur inattendue")
            return Response({'error': 'Erreur interne'}, status=500)