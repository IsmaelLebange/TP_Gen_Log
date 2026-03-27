# src/apps/citoyen/repositories/biometric_repository.py
import pickle
from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from src.models import BiometricData
from src.apps.interfaces.citoyen_interfaces.biometric_repository_interface import BiometricRepositoryInterface
from src.domain.entities.biometric import BiometricEntity
from src.domain.value_objects.biometrics import BiometricType
from src.domain.value_objects.biometrics import BiometricTemplate
from src.domain.exceptions.biometric_exceptions import BiometricNotFoundError

class BiometricRepository(BiometricRepositoryInterface):
    """Implémentation Django du repository biométrique."""

    def get_active_by_citoyen(self, citoyen_id: int) -> Optional[BiometricEntity]:
        try:
            instance = BiometricData.objects.get(citoyen_id=citoyen_id, is_active=True)
            return self._to_entity(instance)
        except ObjectDoesNotExist:
            return None

    def get_by_citoyen_and_type(self, citoyen_id: int, biometric_type: BiometricType) -> Optional[BiometricEntity]:
        try:
            instance = BiometricData.objects.get(
                citoyen_id=citoyen_id,
                biometric_type=biometric_type.value
            )
            return self._to_entity(instance)
        except ObjectDoesNotExist:
            return None

    def list_by_citoyen(self, citoyen_id: int) -> List[BiometricEntity]:
        instances = BiometricData.objects.filter(citoyen_id=citoyen_id)
        return [self._to_entity(inst) for inst in instances]

    def save(self, entity: BiometricEntity) -> BiometricEntity:
        # Convertir l'entité en dictionnaire pour mise à jour ou création
        data = {
            'citoyen_id': entity.citoyen_id,
            'biometric_type': entity.biometric_type.value,
            'template': pickle.dumps(entity.template.features),
            'image': entity.image_path,
            'is_active': entity.is_active,
        }
        if entity.id:
            # Mise à jour
            BiometricData.objects.filter(id=entity.id).update(**data)
            instance = BiometricData.objects.get(id=entity.id)
        else:
            # Création
            instance = BiometricData.objects.create(**data)
        return self._to_entity(instance)

    def delete(self, entity: BiometricEntity) -> None:
        # Soft delete
        BiometricData.objects.filter(id=entity.id).update(is_active=False)

    def _to_entity(self, instance: BiometricData) -> BiometricEntity:
        """Convertit une instance Django en entité du domaine."""
        return BiometricEntity(
            id=instance.id,
            citoyen_id=instance.citoyen_id,
            biometric_type=BiometricType.from_string(instance.biometric_type),
            template=BiometricTemplate(features=pickle.loads(instance.template)),
            image_path=instance.image.name if instance.image else None,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
            is_active=instance.is_active
        )