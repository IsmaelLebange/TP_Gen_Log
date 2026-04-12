# src/apps/api/controllers/admin_controllers/validation_workflow_controller.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from src.apps.api.providers.admin_provider import AdminProvider
from src.apps.api.serializers.admin_serializers.validation_workflow_serializer import (
    DocumentRejectSerializer,
    DocumentResponseSerializer
)
from src.domain.exceptions.validation_exceptions import (
    DocumentNotFoundError, InvalidDocumentStatusError, RejectCommentRequiredError
)
import logging

logger = logging.getLogger(__name__)

class ValidationWorkflowController(APIView):
    permission_classes = [AllowAny]

    @property
    def validation_service(self):
        return AdminProvider.get_validation_workflow_service()

    def get(self, request):
        action = request.query_params.get('action')
        if action == 'pending':
            return self._get_pending(request)
        elif action == 'user':
            return self._get_by_user(request)
        return Response({'error': 'Action non valide'}, status=400)

    def post(self, request):
        doc_id = request.query_params.get('doc_id')
        if not doc_id:
            return Response({'error': 'doc_id requis'}, status=400)

        action = request.query_params.get('action')
        if action == 'validate':
            return self._validate(request, doc_id)
        elif action == 'reject':
            return self._reject(request, doc_id)
        return Response({'error': 'Action non valide'}, status=400)

    def _get_pending(self, request):
        try:
            docs = self.validation_service.get_pending_documents()
            serializer = DocumentResponseSerializer(docs, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.exception("Erreur lors de la récupération des documents en attente")
            return Response({'error': str(e)}, status=500)

    def _get_by_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requis'}, status=400)
        try:
            docs = self.validation_service.get_documents_by_user(int(user_id))
            serializer = DocumentResponseSerializer(docs, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.exception(f"Erreur lors de la récupération des documents de l'utilisateur {user_id}")
            return Response({'error': str(e)}, status=500)

    def _validate(self, request, doc_id):
        try:
            if request.user.role not in ['ADMIN', 'AGENT']:
                return Response({'error': "Vous n'avez pas les droits pour valider des documents"}, status=403)

            result = self.validation_service.validate_document(int(doc_id), request.user.id)
            serializer = DocumentResponseSerializer(result)
            return Response(serializer.data, status=200)
        except (DocumentNotFoundError, InvalidDocumentStatusError) as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            logger.exception(f"Erreur lors de la validation du document {doc_id}")
            return Response({'error': str(e)}, status=500)

    def _reject(self, request, doc_id):
        try:
            if request.user.role not in ['ADMIN', 'AGENT']:
                return Response({'error': "Vous n'avez pas les droits pour rejeter des documents"}, status=403)

            serializer = DocumentRejectSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=400)

            result = self.validation_service.reject_document(
                int(doc_id),
                request.user.id,
                serializer.validated_data['commentaire']
            )
            serializer_out = DocumentResponseSerializer(result)
            return Response(serializer_out.data, status=200)
        except (DocumentNotFoundError, InvalidDocumentStatusError, RejectCommentRequiredError) as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            logger.exception(f"Erreur lors du rejet du document {doc_id}")
            return Response({'error': str(e)}, status=500)