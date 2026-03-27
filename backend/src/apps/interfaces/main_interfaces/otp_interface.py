# src/apps/interfaces/main_interfaces/otp_repository_interface.py
from abc import ABC, abstractmethod
from typing import Optional
from src.models import OTP
from src.models import User

class OTPRepositoryInterface(ABC):
    @abstractmethod
    def create(self, user_id: int, purpose: str) -> OTP:
        """Crée un nouveau code OTP pour l'utilisateur."""
        pass

    @abstractmethod
    def get_valid(self, user_id: int, code: str, purpose: str) -> Optional[OTP]:
        """Récupère un code valide non utilisé et non expiré."""
        pass

    @abstractmethod
    def mark_as_used(self, otp: OTP) -> None:
        """Marque un code comme utilisé."""
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        """Supprime les codes expirés (nettoyage)."""
        pass



class OTPSenderInterface(ABC):
    @abstractmethod
    def send(self, user: User, code: str) -> bool:
        """Envoie le code OTP à l'utilisateur (SMS ou email)."""
        pass