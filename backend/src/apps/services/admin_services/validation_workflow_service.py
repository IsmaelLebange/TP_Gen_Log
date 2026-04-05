# src/apps/services/admin_services/validation_workflow_service.py
import logging
from typing import List, Dict, Any
from django.utils import timezone
from src.apps.interfaces.citoyen_interfaces.document_interface import DocumentRepositoryInterface
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface
from src.domain.entities.document import Document
from src.domain.exceptions.validation_exceptions import (
    DocumentNotFoundError, InvalidDocumentStatusError, RejectCommentRequiredError
)
from src.domain.value_objects.statut_validation import StatutValidation

logger = logging.getLogger(__name__)

class ValidationWorkflowService:
    def __init__(self, document_repo: DocumentRepositoryInterface, user_repo: UserRepositoryInterface):
        self.document_repo = document_repo
        self.user_repo = user_repo

    def get_pending_documents(self) -> List[Dict[str, Any]]:
        try:
            models = self.document_repo.get_pending_documents()
            return [self._format_model(m) for m in models]
        except Exception as e:
            logger.exception("Erreur lors de la récupération des documents en attente")
            raise

    def get_documents_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            models = self.document_repo.get_by_user(user_id)
            return [self._format_model(m) for m in models]
        except Exception as e:
            logger.exception(f"Erreur lors de la récupération des documents de l'utilisateur {user_id}")
            raise

    def validate_document(self, doc_id: int, agent_id: int) -> Dict[str, Any]:
        try:
            entity = self.document_repo.get_entity_by_id(doc_id)
            if not entity:
                raise DocumentNotFoundError(f"Document {doc_id} introuvable")

            # Utiliser la méthode métier de l'entité
            entity.valider(agent_id)

            # Sauvegarder l'entité mise à jour
            saved_entity = self.document_repo.save_entity(entity)

            logger.info(f"Document {doc_id} validé par l'agent {agent_id}")
            return self._format_entity(saved_entity)
        except ValueError as e:
            raise InvalidDocumentStatusError(str(e))
        except (DocumentNotFoundError, InvalidDocumentStatusError) as e:
            logger.warning(f"Validation échouée: {e}")
            raise
        except Exception as e:
            logger.exception(f"Erreur inattendue lors de la validation du document {doc_id}")
            raise

    def reject_document(self, doc_id: int, agent_id: int, commentaire: str) -> Dict[str, Any]:
        try:
            if not commentaire or not commentaire.strip():
                raise RejectCommentRequiredError("Un commentaire est requis pour le rejet")

            entity = self.document_repo.get_entity_by_id(doc_id)
            if not entity:
                raise DocumentNotFoundError(f"Document {doc_id} introuvable")

            entity.rejeter(agent_id, commentaire)

            saved_entity = self.document_repo.save_entity(entity)

            logger.info(f"Document {doc_id} rejeté par l'agent {agent_id} : {commentaire}")
            return self._format_entity(saved_entity)
        except ValueError as e:
            raise InvalidDocumentStatusError(str(e))
        except (DocumentNotFoundError, InvalidDocumentStatusError, RejectCommentRequiredError) as e:
            logger.warning(f"Rejet échoué: {e}")
            raise
        except Exception as e:
            logger.exception(f"Erreur inattendue lors du rejet du document {doc_id}")
            raise

    def _format_model(self, model: Document) -> Dict[str, Any]:
        return {
            'id': model.id,
            'user_id': model.user_id,
            'type': model.type,
            'numero': model.numero,
            'fichier_url': model.fichier.url if model.fichier else None,
            'date_emission': model.date_emission.isoformat(),
            'date_expiration': model.date_expiration.isoformat() if model.date_expiration else None,
            'statut': model.statut,
            'created_at': model.created_at.isoformat(),
            'updated_at': model.updated_at.isoformat(),
            'valide_par_id': model.valide_par_id,
            'date_validation': model.date_validation.isoformat() if model.date_validation else None,
            'commentaire_rejet': model.commentaire_rejet,
        }

    def _format_entity(self, entity: Document) -> Dict[str, Any]:
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'type': entity.type,
            'numero': entity.numero,
            'fichier_url': entity.fichier,
            'date_emission': entity.date_emission.isoformat(),
            'date_expiration': entity.date_expiration.isoformat() if entity.date_expiration else None,
            'statut': entity.statut.value,
            'created_at': entity.created_at.isoformat(),
            'updated_at': entity.updated_at.isoformat(),
            'valide_par_id': entity.valide_par_id,
            'date_validation': entity.date_validation.isoformat() if entity.date_validation else None,
            'commentaire_rejet': entity.commentaire_rejet,
        }