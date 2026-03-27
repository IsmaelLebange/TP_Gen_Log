import logging
from typing import List, Dict, Any
from django.core.exceptions import ValidationError as DjangoValidationError
from src.apps.interfaces.citoyen_interfaces.document_interface import DocumentRepositoryInterface
from src.domain.exceptions.document_exceptions import (
    DocumentNotFoundError, DocumentPermissionError, InvalidDocumentTypeError, DocumentUploadError
)
from src.models import Document

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, repository: DocumentRepositoryInterface):
        self.repository = repository

    def upload_document(self, user_id: int, data: dict, file) -> Dict[str, Any]:
        try:
            # Vérifier le type de document
            if data.get('type') not in dict(Document.TypeDocument.choices):
                raise InvalidDocumentTypeError(f"Type de document invalide: {data.get('type')}")

            # Ajouter le fichier
            data['fichier'] = file
            doc = self.repository.create(user_id, data)

            return {
                'id': doc.id,
                'type': doc.type,
                'numero': doc.numero,
                'statut': doc.statut,
                'created_at': doc.created_at.isoformat(),
                'fichier_url': doc.fichier.url if doc.fichier else None
            }
        except (InvalidDocumentTypeError, DjangoValidationError) as e:
            logger.warning(f"Erreur lors de l'upload du document pour l'utilisateur {user_id}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Erreur inattendue lors de l'upload du document pour l'utilisateur {user_id}")
            raise DocumentUploadError(str(e))

    def list_documents(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            docs = self.repository.get_by_user(user_id)
            return [self._format_document(doc) for doc in docs]
        except Exception as e:
            logger.exception(f"Erreur lors de la récupération des documents de l'utilisateur {user_id}")
            raise

    def get_document(self, user_id: int, doc_id: int) -> Dict[str, Any]:
        try:
            doc = self.repository.get_by_id(doc_id)
            if not doc:
                raise DocumentNotFoundError(f"Document {doc_id} introuvable")
            if doc.user_id != user_id:
                raise DocumentPermissionError("Vous n'avez pas accès à ce document")
            return self._format_document(doc)
        except (DocumentNotFoundError, DocumentPermissionError) as e:
            raise
        except Exception as e:
            logger.exception(f"Erreur lors de la récupération du document {doc_id}")
            raise

    def delete_document(self, user_id: int, doc_id: int) -> bool:
        try:
            doc = self.repository.get_by_id(doc_id)
            if not doc:
                raise DocumentNotFoundError(f"Document {doc_id} introuvable")
            if doc.user_id != user_id:
                raise DocumentPermissionError("Vous n'avez pas le droit de supprimer ce document")
            return self.repository.delete(doc_id)
        except (DocumentNotFoundError, DocumentPermissionError) as e:
            raise
        except Exception as e:
            logger.exception(f"Erreur lors de la suppression du document {doc_id}")
            raise

    def _format_document(self, doc: Document) -> Dict[str, Any]:
        return {
            'id': doc.id,
            'type': doc.type,
            'numero': doc.numero,
            'fichier_url': doc.fichier.url if doc.fichier else None,
            'date_emission': doc.date_emission.isoformat() if doc.date_emission else None,
            'date_expiration': doc.date_expiration.isoformat() if doc.date_expiration else None,
            'statut': doc.statut,
            'created_at': doc.created_at.isoformat(),
            'updated_at': doc.updated_at.isoformat(),
        }