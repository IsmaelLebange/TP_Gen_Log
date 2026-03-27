from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from src.apps.api.providers.citoyen_provider import CitoyenProvider
from src.apps.api.serializers.citoyen_serializers.document_serializer import (
    DocumentUploadSerializer, DocumentResponseSerializer
)
from src.domain.exceptions.document_exceptions import (
    DocumentNotFoundError, DocumentPermissionError, InvalidDocumentTypeError, DocumentUploadError
)

class DocumentController(APIView):
    permission_classes = [IsAuthenticated]

    @property
    def document_service(self):
        return CitoyenProvider.get_document_service()

    def post(self, request):
        # Upload d'un document
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = self.document_service.upload_document(
                user_id=request.user.id,
                data=serializer.validated_data,
                file=request.FILES.get('fichier')
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except (InvalidDocumentTypeError, DocumentUploadError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        # Liste des documents de l'utilisateur ou un document spécifique
        doc_id = request.query_params.get('id')
        if doc_id:
            try:
                result = self.document_service.get_document(request.user.id, int(doc_id))
                serializer = DocumentResponseSerializer(result)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except (DocumentNotFoundError, DocumentPermissionError) as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception:
                return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                docs = self.document_service.list_documents(request.user.id)
                serializer = DocumentResponseSerializer(docs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception:
                return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        doc_id = request.query_params.get('id')
        if not doc_id:
            return Response({'error': 'id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            success = self.document_service.delete_document(request.user.id, int(doc_id))
            if success:
                return Response({'message': 'Document supprimé'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Suppression échouée'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except (DocumentNotFoundError, DocumentPermissionError) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)