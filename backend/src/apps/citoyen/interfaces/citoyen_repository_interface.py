# citoyen_repository_interface.py - Interface pour le repository citoyen

from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser as User
else:
    User = get_user_model()

class CitoyenRepositoryInterface(ABC):
    """Interface abstraite pour le repository citoyen"""

    @abstractmethod
    def get_by_id(self, citoyen_id: int) -> Optional["User"]:
        """Récupère un citoyen par son ID"""
        pass

    @abstractmethod
    def get_by_nin(self, nin: str) -> Optional["User"]:
        """Récupère un citoyen par son NIN"""
        pass

    @abstractmethod
    def get_all_citoyens(self) -> List["User"]:
        """Récupère tous les citoyens actifs"""
        pass

    @abstractmethod
    def save(self, citoyen: "User") -> "User":
        """Sauvegarde un citoyen"""
        pass

    @abstractmethod
    def exists_by_nin(self, nin: str) -> bool:
        """Vérifie si un citoyen existe avec ce NIN"""
        pass

    @abstractmethod
    def search_by_name(self, first_name: str, last_name: str) -> List["User"]:
        """Recherche des citoyens par nom"""
        pass

    @abstractmethod
    def get_citoyens_by_age_range(self, min_age: int, max_age: int) -> List["User"]:
        """Récupère les citoyens dans une tranche d'âge"""
        pass