from abc import ABC, abstractmethod
from typing import List, Optional
from src.models import Document as DocumentModel
from src.domain.entities.document import Document  # à créer éventuellement, ou on utilise le modèle directement

class DocumentRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, doc_id: int) -> Optional[DocumentModel]:
        pass

    @abstractmethod
    def get_by_user(self, user_id: int) -> List[DocumentModel]:
        pass

    @abstractmethod
    def create(self, user_id: int, data: dict) -> DocumentModel:
        pass

    @abstractmethod
    def delete(self, doc_id: int) -> bool:
        pass