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
        from django.core.files.base import ContentFile
        import base64
        import uuid

        data = {
            'citoyen_id': entity.citoyen_id,
            'biometric_type': entity.biometric_type.value,
            'template': pickle.dumps(entity.template.features),
            'is_active': entity.is_active,
        }

        # Gestion de l'image à partir du base64
        if entity.image_base64:
            # Séparer le préfixe (data:image/jpeg;base64,)
            if ',' in entity.image_base64:
                format, imgstr = entity.image_base64.split(';base64,')
                ext = format.split('/')[-1]  # jpeg, png, etc.
            else:
                imgstr = entity.image_base64
                ext = 'jpg'
            img_data = base64.b64decode(imgstr)
            filename = f"face_{entity.citoyen_id}_{uuid.uuid4().hex}.{ext}"
            data['image'] = ContentFile(img_data, name=filename)

        if entity.id:
            BiometricData.objects.filter(id=entity.id).update(**data)
            instance = BiometricData.objects.get(id=entity.id)
        else:
            instance = BiometricData.objects.create(**data)

        # Mettre à jour l'entité avec l'ID et le chemin de l'image
        entity.id = instance.id
        entity.image_path = instance.image.name if instance.image else None
        return entity

    def delete(self, entity: BiometricEntity) -> None:
        # Soft delete
        BiometricData.objects.filter(id=entity.id).update(is_active=False)
        
    def list_active_by_citoyen(self, citoyen_id: int) -> List[BiometricEntity]:
        instances = BiometricData.objects.filter(citoyen_id=citoyen_id, is_active=True)
        return [self._to_entity(inst) for inst in instances]

    def _to_entity(self, instance: BiometricData) -> BiometricEntity:
        """Convertit une instance Django en entité du domaine."""
        return BiometricEntity(
            id=instance.id,
            citoyen_id=instance.citoyen_id,
            biometric_type=BiometricType.from_string(instance.biometric_type),
            image_base64="",  # On ne stocke pas l'image brute dans l'entité retournée
            template=BiometricTemplate(features=pickle.loads(instance.template)),
            image_path=instance.image.name if instance.image else None,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
            is_active=instance.is_active
        )