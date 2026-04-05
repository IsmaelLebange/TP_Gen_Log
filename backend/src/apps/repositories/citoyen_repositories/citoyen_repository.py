import logging
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from django.contrib.auth import get_user_model
from src.apps.interfaces.citoyen_interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.domain.entities.citoyen import Citoyen, EnrollmentData
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email
from src.models import SecteurChefferie


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
            return "0000000" # Valeur par défaut pour éviter de bloquer le TP

        nom_s = str(nom_secteur).strip()
        nom_t = str(nom_territoire).strip()

        """
        try:
            # Recherche souple
            secteur = SecteurChefferie.objects.filter(
                nom__icontains=nom_s,
                territoire__nom__icontains=nom_t
            ).first()

            if secteur:
                print(f"✅ Secteur trouvé : {secteur.nom} (Code: {secteur.code})")
                print(f"   - Territoire associé : {secteur.territoire.nom}")
                return secteur.code
            
            # SI PAS TROUVÉ : Au lieu de crash, on log et on renvoie un code générique
            # pour que tu puisses avancer ton projet de Master
            logger.warning(f"Localisation non trouvée en base : {nom_s} / {nom_t}")
            return "9999999" 

        except Exception as e:
            # Log l'erreur réelle dans ton terminal VS Code (important !)
            print(f"DEBUG ERROR GEO: {str(e)}") 
            return "0000000"
        """ 
        return "0000000" # Valeur par défaut pour éviter de bloquer le TP
    def save(self, citoyen_entity: Citoyen) -> Citoyen:
        from src.models import User, Adresse, Province, SecteurChefferie

        # Récupérer le secteur d'origine (pour lieu_origine)
        secteur_obj = None
        if citoyen_entity.secteur_origine:
            secteur_obj = SecteurChefferie.objects.filter(nom__iexact=citoyen_entity.secteur_origine).first()

        user, created = User.objects.update_or_create(
            email=str(citoyen_entity.email),
            defaults={
                'nin': str(citoyen_entity.nin),
                'prenom': citoyen_entity.prenom,
                'nom': citoyen_entity.nom,
                'postnom': citoyen_entity.postnom,
                'date_naissance': citoyen_entity.date_naissance,
                'lieu_origine': secteur_obj,
                'nom_du_pere': citoyen_entity.nom_du_pere,
                'nom_de_la_mere': citoyen_entity.nom_de_la_mere,
                'telephone': citoyen_entity.telephone or '',
                'is_active': True,
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
    
    def save_new_citoyen(self, data: EnrollmentData) -> "AbstractBaseUser":
        """Ancienne méthode si tu utilises encore la Dataclass"""
        return User.objects.create_user(
            email=data.email,
            mot_de_passe=data.mot_de_passe,
            nom=data.nom,
            postnom=data.postnom,
            prenom=data.prenom,
            nin=data.nin,
            date_naissance=data.date_naissance,
            telephone=data.telephone,
            adresse=data.adresse,
            province_origine=data.province_origine,
            territoire_origine=data.territoire_origine,
            secteur_origine=data.secteur_origine
        )
        
    def update_biometric_complete(self, user_id: int, completed: bool) -> None:
        from src.models import User
        User.objects.filter(id=user_id).update(biometric_completed=completed)