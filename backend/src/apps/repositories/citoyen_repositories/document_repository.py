# src/apps/repositories/citoyen_repositories/document_repository.py
from typing import List, Optional
from django.db import transaction
from src.models import Document as DocumentModel
from src.apps.interfaces.citoyen_interfaces.document_interface import DocumentRepositoryInterface
from src.domain.entities.document import Document
from src.domain.value_objects.statut_validation import StatutValidation
from src.domain.exceptions.document_exceptions import DocumentNotFoundError

class DocumentRepository(DocumentRepositoryInterface):
    def get_by_id(self, doc_id: int) -> Optional[DocumentModel]:
        try:
            return DocumentModel.objects.get(id=doc_id)
        except DocumentModel.DoesNotExist:
            return None

    def get_entity_by_id(self, doc_id: int) -> Optional[Document]:
        model = self.get_by_id(doc_id)
        return self._to_entity(model) if model else None

    def get_by_user(self, user_id: int) -> List[DocumentModel]:
        return list(DocumentModel.objects.filter(user_id=user_id).order_by('-created_at'))

    def get_pending_documents(self) -> List[DocumentModel]:
        return list(DocumentModel.objects.filter(statut=StatutValidation.EN_ATTENTE.value).order_by('created_at'))

    def create(self, user_id: int, data: dict) -> DocumentModel:
        with transaction.atomic():
            doc = DocumentModel.objects.create(user_id=user_id, **data)
        return doc

    def save_entity(self, entity: Document) -> Document:
        try:
            model = DocumentModel.objects.get(id=entity.id)
        except DocumentModel.DoesNotExist:
            model = DocumentModel()

        model.user_id = entity.user_id
        model.type = entity.type
        model.numero = entity.numero
        # fichier : on ne modifie pas le fichier existant
        # model.fichier = entity.fichier  # ne pas faire, c'est un chemin
        model.date_emission = entity.date_emission
        model.date_expiration = entity.date_expiration
        model.statut = entity.statut.value
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.valide_par_id = entity.valide_par_id
        model.date_validation = entity.date_validation
        model.commentaire_rejet = entity.commentaire_rejet

        model.save()
        entity.id = model.id
        return entity

    def delete(self, doc_id: int) -> bool:
        try:
            doc = DocumentModel.objects.get(id=doc_id)
            doc.delete()
            return True
        except DocumentModel.DoesNotExist:
            raise DocumentNotFoundError(f"Document {doc_id} introuvable")

    def _to_entity(self, model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            user_id=model.user_id,
            type=model.type,
            numero=model.numero,
            fichier=model.fichier.name if model.fichier else "",
            date_emission=model.date_emission,
            date_expiration=model.date_expiration,
            statut=StatutValidation.from_string(model.statut),
            created_at=model.created_at,
            updated_at=model.updated_at,
            valide_par_id=model.valide_par_id,
            date_validation=model.date_validation,
            commentaire_rejet=model.commentaire_rejet
        )