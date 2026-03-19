from typing import Optional, List, TYPE_CHECKING
from datetime import date
from django.contrib.auth import get_user_model
from src.apps.citoyen.interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.domain.entities.citoyen import Citoyen, EnrollmentData
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

# On récupère le modèle User de ton projet
User = get_user_model()

class DjangoCitoyenRepository(CitoyenRepositoryInterface):
    """Implémentation Django du repository citoyen respectant les Value Objects"""

    def get_by_id(self, citoyen_id: int) -> Optional["AbstractBaseUser"]:
        try:
            return User.objects.get(id=citoyen_id, is_active=True)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: Email) -> Optional["AbstractBaseUser"]:
        """Recherche par Value Object Email"""
        try:
            # On convertit le VO en string pour la requête Django
            return User.objects.get(email=str(email))
        except User.DoesNotExist:
            return None

    def get_by_nin(self, nin: NIN) -> Optional["AbstractBaseUser"]:
        """Recherche par Value Object NIN"""
        try:
            # On convertit le VO en string pour la requête Django
            return User.objects.get(nin=str(nin))
        except User.DoesNotExist:
            return None

    def save(self, citoyen_entity: Citoyen) -> Citoyen:
        """
        Sauvegarde une entité Citoyen. 
        C'est ici qu'on résout l'erreur 'Citoyen object has no attribute save'.
        """
        # On extrait les données de l'entité et de ses VO pour l'ORM Django
        user, created = User.objects.update_or_create(
            nin=str(citoyen_entity.nin),
            defaults={
                'email': str(citoyen_entity.email),
                'nom': citoyen_entity.prenom,
                'last_name': citoyen_entity.nom,
                'postnom': citoyen_entity.postnom, # Ajouté car présent dans l'entité
                'date_naissance': citoyen_entity.date_naissance,
                'telephone': citoyen_entity.telephone,
                'is_active': True
            }
        )
        
        # On met à jour l'ID de l'entité domaine avec celui généré par la DB
        citoyen_entity.id = user.id
        return citoyen_entity

    def exists_by_nin(self, nin: NIN) -> bool:
        """Vérifie l'existence via le Value Object"""
        return User.objects.filter(nin=str(nin)).exists()

    def get_all_citoyens(self) -> List["AbstractBaseUser"]:
        return list(User.objects.filter(is_active=True))

    def search_by_name(self, first_name: str = "", last_name: str = "") -> List["AbstractBaseUser"]:
        queryset = User.objects.filter(is_active=True)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return list(queryset)

    def get_citoyens_by_age_range(self, min_age: int, max_age: int) -> List["AbstractBaseUser"]:
        today = date.today()
        birth_date_min = today.replace(year=today.year - max_age - 1)
        birth_date_max = today.replace(year=today.year - min_age)

        return list(User.objects.filter(
            is_active=True,
            date_of_birth__gt=birth_date_min,
            date_of_birth__lte=birth_date_max
        ))
    
    def save_new_citoyen(self, data: EnrollmentData) -> "AbstractBaseUser":
        """Ancienne méthode si tu utilises encore la Dataclass"""
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