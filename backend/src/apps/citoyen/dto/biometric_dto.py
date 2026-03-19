# src/apps/citoyen/dto/biometric_dto.py
from dataclasses import dataclass, asdict, field
from typing import Optional, Any, Dict
from datetime import datetime

@dataclass(frozen=True) # Rendre le DTO immuable est une bonne pratique
class BiometricEnrollRequestDTO:
    """DTO pour la requête d'enrôlement."""
    type: str
    image: str  # base64

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(type=data['type'], image=data['image'])

@dataclass(frozen=True)
class BiometricVerifyRequestDTO:
    """DTO pour la requête de vérification."""
    image: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(image=data['image'])

@dataclass
class BiometricResponseDTO:
    """DTO pour les réponses standardisées."""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self):
        # On filtre les None pour avoir un JSON propre
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class BiometricStatusDTO:
    """DTO pour le statut d'enrôlement avec formatage ISO."""
    enrolled: bool
    type: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'enrolled': self.enrolled,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }