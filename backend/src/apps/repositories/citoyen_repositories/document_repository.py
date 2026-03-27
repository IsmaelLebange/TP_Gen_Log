from typing import List, Optional
from django.db import transaction
from src.models import Document
from src.apps.interfaces.citoyen_interfaces.document_interface import DocumentRepositoryInterface
from src.domain.exceptions.document_exceptions import DocumentNotFoundError

class DocumentRepository(DocumentRepositoryInterface):
    def get_by_id(self, doc_id: int) -> Optional[Document]:
        try:
            return Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            return None

    def get_by_user(self, user_id: int) -> List[Document]:
        return list(Document.objects.filter(user_id=user_id).order_by('-created_at'))

    def create(self, user_id: int, data: dict) -> Document:
        with transaction.atomic():
            doc = Document.objects.create(user_id=user_id, **data)
        return doc

    def delete(self, doc_id: int) -> bool:
        try:
            doc = Document.objects.get(id=doc_id)
            doc.delete()
            return True
        except Document.DoesNotExist:
            raise DocumentNotFoundError(f"Document {doc_id} introuvable")