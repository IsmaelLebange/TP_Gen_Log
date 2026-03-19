# src/domain/entities/biometric_entity.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from src.domain.value_objects.biometrics import BiometricTemplate
from src.domain.value_objects.biometrics import BiometricType

@dataclass
class BiometricEntity:
    """
    Entité biométrique du domaine.
    Elle ne connaît ni Django ni la base de données.
    """
    citoyen_id: int
    biometric_type: BiometricType
    template: BiometricTemplate
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def update_template(self, new_template: BiometricTemplate):
        self.template = new_template
        self.updated_at = datetime.now()