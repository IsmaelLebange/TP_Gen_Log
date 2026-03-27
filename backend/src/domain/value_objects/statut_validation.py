from enum import Enum

class StatutValidation(Enum):
    EN_ATTENTE = "EN_ATTENTE"
    VALIDE = "VALIDE"
    REJETE = "REJETE"
    EXPIRED = "EXPIRED"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Statut invalide: {value}")