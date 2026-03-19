# src/domain/valueobjects/biometric_type.py
from enum import Enum
from dataclasses import dataclass
from typing import List
import numpy as np

class BiometricType(Enum):
    FACE = "face"
    FINGERPRINT = "fingerprint"
    IRIS = "iris"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Type biométrique invalide : {value}")
        

# src/domain/valueobjects/biometric_template.py


@dataclass(frozen=True)
class BiometricTemplate:
    """
    Value object représentant le template biométrique (features).
    Immutable.
    """
    features: List[float]

    def to_numpy(self) -> np.ndarray:
        return np.array(self.features)

    @classmethod
    def from_numpy(cls, arr: np.ndarray):
        return cls(features=arr.flatten().tolist())