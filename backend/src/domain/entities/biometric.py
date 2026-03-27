from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from src.domain.value_objects.biometrics import BiometricType, BiometricTemplate

@dataclass
class BiometricEntity:
    citoyen_id: int
    biometric_type: BiometricType
    image_base64: str  # Donnée brute pour le traitement
    template: Optional[BiometricTemplate] = None
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None

    def __post_init__(self):
        # On garde ta validation cruciale
        if not self.image_base64.startswith('data:image/'):
            raise ValueError("L'image doit être au format Data URI (base64).")

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def update_template(self, new_template: BiometricTemplate):
        self.template = new_template
        self.updated_at = datetime.now()

    @classmethod
    def from_request(cls, data: Dict[str, Any], citoyen_id: int):
        return cls(
            citoyen_id=citoyen_id,
            biometric_type=data.get('type'),
            image_base64=data.get('image'),
            created_at=datetime.now()
        )

    def to_dict(self):
        # On transforme l'objet en dictionnaire pour le Serializer
        data = asdict(self)
        # On nettoie l'image_base64 de la sortie pour ne pas saturer le JSON
        data.pop('image_base64', None)
        return data