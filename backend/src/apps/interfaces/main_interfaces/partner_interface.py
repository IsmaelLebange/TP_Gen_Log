from abc import ABC, abstractmethod
from typing import Optional
from src.models import Partenaire

class PartenaireRepositoryInterface(ABC):
    @abstractmethod
    def get_by_token(self, token: str) -> Optional[Partenaire]:
        pass