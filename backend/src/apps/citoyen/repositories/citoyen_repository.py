# citoyen_repository.py - Repository pour les citoyens

from typing import Optional, List, TYPE_CHECKING
from datetime import date
from django.contrib.auth import get_user_model
from src.apps.citoyen.interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.domain.entities.citoyen import EnrollmentData

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

# On récupère le modèle dynamiquement
User = get_user_model()

class DjangoCitoyenRepository(CitoyenRepositoryInterface):
    """Implémentation Django du repository citoyen"""

    def get_by_id(self, citoyen_id: int) -> Optional["AbstractBaseUser"]:
        """Récupère un citoyen par son ID"""
        try:
            return User.objects.get(id=citoyen_id, is_active=True)
        except User.DoesNotExist:
            return None

    def get_by_nin(self, nin: str) -> Optional["AbstractBaseUser"]:
        """Récupère un citoyen par son NIN"""
        try:
            return User.objects.get(nin=nin, is_active=True)
        except User.DoesNotExist:
            return None

    def get_all_citoyens(self) -> List["AbstractBaseUser"]:
        """Récupère tous les citoyens actifs"""
        return list(User.objects.filter(is_active=True))

    def save(self, citoyen: "AbstractBaseUser") -> "AbstractBaseUser":
        """Sauvegarde un citoyen"""
        citoyen.save()
        return citoyen

    def exists_by_nin(self, nin: str) -> bool:
        """Vérifie si un citoyen existe avec ce NIN"""
        return User.objects.filter(nin=nin, is_active=True).exists()

    def search_by_name(self, first_name: str = "", last_name: str = "") -> List["AbstractBaseUser"]:
        """Recherche des citoyens par nom"""
        queryset = User.objects.filter(is_active=True)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return list(queryset)

    def get_citoyens_by_age_range(self, min_age: int, max_age: int) -> List["AbstractBaseUser"]:
        """
        Récupère les citoyens dans une tranche d'âge directement via SQL.
        C'est beaucoup plus performant que de boucler en Python.
        """
        today = date.today()
        # Date de naissance la plus ancienne (pour l'âge max)
        birth_date_min = today.replace(year=today.year - max_age - 1)
        # Date de naissance la plus récente (pour l'âge min)
        birth_date_max = today.replace(year=today.year - min_age)

        return list(User.objects.filter(
            is_active=True,
            date_of_birth__gt=birth_date_min,
            date_of_birth__lte=birth_date_max
        ))
    
    def save_new_citoyen(self, data: EnrollmentData) -> "AbstractBaseUser":
        """Crée un utilisateur Django à partir de la Dataclass d'enrôlement"""
        return User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            nin=data.nin,
            date_of_birth=data.date_of_birth,
            phone_number=data.phone_number,
            address=data.address
        )