# src/apps/citoyen/interfaces/biometric_repository_interface.py
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.biometric import BiometricEntity
from src.domain.value_objects.biometrics import BiometricType

class BiometricRepositoryInterface(ABC):
    """Interface du repository pour les données biométriques."""

    @abstractmethod
    def get_active_by_citoyen(self, citoyen_id: int) -> Optional[BiometricEntity]:
        """Récupère la donnée biométrique active d'un citoyen."""
        pass

    @abstractmethod
    def get_by_citoyen_and_type(self, citoyen_id: int, biometric_type: BiometricType) -> Optional[BiometricEntity]:
        """Récupère une donnée spécifique (même inactive)."""
        pass

    @abstractmethod
    def list_by_citoyen(self, citoyen_id: int) -> List[BiometricEntity]:
        """Liste toutes les données biométriques d'un citoyen."""
        pass

    @abstractmethod
    def save(self, entity: BiometricEntity) -> BiometricEntity:
        """Sauvegarde (crée ou met à jour) une entité."""
        pass

    @abstractmethod
    def delete(self, entity: BiometricEntity) -> None:
        """Supprime logiquement (soft delete) une entité."""
        pass

    @abstractmethod
    def list_active_by_citoyen(self, citoyen_id: int) -> List[BiometricEntity]:
        pass