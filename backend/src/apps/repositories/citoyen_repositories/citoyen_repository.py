import logging
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from django.contrib.auth import get_user_model
from src.domain.entities.biometric import BiometricEntity
from src.apps.interfaces.citoyen_interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.domain.entities.citoyen import Citoyen, EnrollmentData
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email
from src.models import BiometricData, SecteurChefferie


logger = logging.getLogger(__name__)    

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
    # src/apps/repositories/citoyen_repositories/citoyen_repository.py

    def get_entity_by_id(self, citoyen_id: int) -> Optional[Citoyen]:
        try:
            user = User.objects.get(id=citoyen_id, is_active=True)
        except User.DoesNotExist:
            return None

        # Récupérer l'adresse
        adresse = getattr(user, 'adresse_actuelle', None)
        adresse_province = adresse.province.nom if adresse and adresse.province else None
        adresse_commune = adresse.commune if adresse else None
        adresse_quartier = adresse.quartier if adresse else None
        adresse_avenue = adresse.avenue if adresse else None
        adresse_numero = adresse.numero if adresse else None

        lieu_origine_code = user.lieu_origine.code if user.lieu_origine else None

        return Citoyen(
            id=user.id,
            email=Email(user.email),
            nin=NIN(user.nin),
            nom=user.nom,
            prenom=user.prenom,
            postnom=user.postnom,
            sexe=user.sexe,
            date_naissance=user.date_naissance,
            lieu_naissance=user.lieu_naissance,
            telephone=user.telephone,
            nom_du_pere=user.nom_du_pere,
            nom_de_la_mere=user.nom_de_la_mere,
            mot_de_passe=user.password,  # ← Ajout obligatoire
            lieu_origine_code=lieu_origine_code,
            adresse_province=adresse_province,
            adresse_commune=adresse_commune,
            adresse_quartier=adresse_quartier,
            adresse_avenue=adresse_avenue,
            adresse_numero=adresse_numero,
        )
    
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

    def trouver_code_secteur(self, nom_secteur: str, nom_territoire: str) -> str:
        if not nom_secteur or not nom_territoire:
            return "0000000"

        try:
            # Recherche précise en ignorant la casse
            secteur = SecteurChefferie.objects.filter(
                nom__iexact=nom_secteur.strip(),
                territoire__nom__iexact=nom_territoire.strip()
            ).first()

            if secteur:
                return secteur.code
            
            logger.warning(f"⚠️ Localisation introuvable: {nom_secteur} / {nom_territoire}")
            return "0000000" 
        except Exception as e:
            print(f"❌ Erreur Géo: {e}") 
            return "0000000"

    def save(self, citoyen_entity: Citoyen) -> Citoyen:
        from src.models import User, Adresse, Province, SecteurChefferie

        # Récupération de l'objet Secteur pour la FK
        secteur_obj = None
        if citoyen_entity.secteur_origine:
            secteur_obj = SecteurChefferie.objects.filter(
                nom__iexact=citoyen_entity.secteur_origine,
                territoire__nom__iexact=citoyen_entity.territoire_origine
            ).first()

        user, created = User.objects.update_or_create(
            email=str(citoyen_entity.email),
            defaults={
                'nin': str(citoyen_entity.nin),
                'prenom': citoyen_entity.prenom,
                'nom': citoyen_entity.nom,
                'postnom': citoyen_entity.postnom,
                'sexe': citoyen_entity.sexe,
                'date_naissance': citoyen_entity.date_naissance,
                'lieu_naissance': citoyen_entity.lieu_naissance,
                'lieu_origine': secteur_obj,
                'nom_du_pere': citoyen_entity.nom_du_pere,
                'nom_de_la_mere': citoyen_entity.nom_de_la_mere,
                'telephone': citoyen_entity.telephone or '',
                'is_active': True,
                'biometric_completed': False # Sera mis à True au final
            }
        )

        # Gestion de l'adresse physique actuelle
        province_obj = None
        if citoyen_entity.adresse_province:
            province_obj = Province.objects.filter(nom__iexact=citoyen_entity.adresse_province).first()
            # Optionnel : lever une erreur si la province n'existe pas
            # if not province_obj: raise ValueError(f"Province '{citoyen_entity.adresse_province}' introuvable")

        adresse_data = {
            'province': province_obj,
            'commune': citoyen_entity.adresse_commune or '',
            'quartier': citoyen_entity.adresse_quartier or '',
            'avenue': citoyen_entity.adresse_avenue or '',
            'numero': citoyen_entity.adresse_numero or '',
        }
        Adresse.objects.update_or_create(citoyen=user, defaults=adresse_data)

        citoyen_entity.id = user.id
        return citoyen_entity

    def exists_by_nin(self, nin: NIN) -> bool:
        """Vérifie l'existence via le Value Object"""
        return User.objects.filter(nin=str(nin)).exists()

    def get_all_citoyens(self) -> List["AbstractBaseUser"]:
        return list(User.objects.filter(is_active=True))

    def search_by_name(self, nom: str = "", postnom: str = "", prenom: str = "") -> List["AbstractBaseUser"]:
        queryset = User.objects.filter(is_active=True)
        if nom:
            queryset = queryset.filter(nom__icontains=nom)
        if postnom:
            queryset = queryset.filter(postnom__icontains=postnom)
        if prenom:
            queryset = queryset.filter(prenom__icontains=prenom)
        return list(queryset)

    def get_citoyens_by_age_range(self, min_age: int, max_age: int) -> List["AbstractBaseUser"]:
        today = date.today()
        date_naissance_min = today.replace(year=today.year - max_age - 1)
        date_naissance_max = today.replace(year=today.year - min_age)

        return list(User.objects.filter(
            is_active=True,
            date_naissance__gt=date_naissance_min,
            date_naissance__lte=date_naissance_max
        ))
    
    
        
    def update_biometric_complete(self, user_id: int, completed: bool) -> None:
        from src.models import User
        User.objects.filter(id=user_id).update(biometric_completed=completed)
        
    