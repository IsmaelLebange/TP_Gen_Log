# src/domain/interfaces/auth_service_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AuthenticationServiceInterface(ABC):
    """Interface définissant le contrat pour le service d'authentification"""

    @abstractmethod
    def login(self, email: str, password: str, request=None) -> Dict[str, Any]:
        """Authentifie un utilisateur et retourne tokens + infos"""
        pass

    @abstractmethod
    def register(self, email: str, password: str, first_name: str, 
                 last_name: str, nin: str, request=None, role: str = "CITOYEN") -> Dict[str, Any]:
        """Inscrit un nouvel utilisateur"""
        pass

    @abstractmethod
    def logout(self, user: Any, request=None) -> bool:
        """Déconnecte un utilisateur"""
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Génère un nouveau access token"""
        pass