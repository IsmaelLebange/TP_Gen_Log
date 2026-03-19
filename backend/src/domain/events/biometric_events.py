# src/domain/events/biometric_events.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True) # On utilise frozen pour que l'événement soit immuable
class BiometricEvent:
    """Événement de base avec ID unique et timestamp automatique."""
    citoyen_id: int
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class BiometricEnrolled(BiometricEvent):
    """Émis après un enrôlement réussi."""
    biometric_type: str  # ex: 'FINGERPRINT', 'IRIS', 'FACE'
    operator_id: int = None # Pour savoir quel agent a fait l'enrôlement

@dataclass(frozen=True)
class BiometricVerified(BiometricEvent):
    """Émis après une tentative de vérification."""
    success: bool
    confidence: float # Le score de correspondance (ex: 0.98)
    method: str = "MATCHING_1_1" # 1:1 ou 1:N

@dataclass(frozen=True)
class BiometricDeleted(BiometricEvent):
    """Émis après une suppression (Révocation des droits)."""
    reason: str = "USER_REQUEST" # Raison de la suppression