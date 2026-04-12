import logging
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.interfaces.main_interfaces.otp_interface import OTPServiceInterface
from src.domain.exceptions.domain_exceptions import AuthenticationException
from typing import Dict, Any
from src.domain.entities.citoyen import Citoyen
from src.apps.interfaces.citoyen_interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.apps.interfaces.citoyen_interfaces.biometric_repository_interface import BiometricRepositoryInterface


logger = logging.getLogger(__name__)

class CredentialService:
    def __init__(self, user_repo: UserRepositoryInterface, otp_service: OTPServiceInterface = None):
        self.user_repo = user_repo
        self.otp_service = otp_service

    def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationException("Utilisateur non trouvé")
        if not user.check_password(old_password):
            raise AuthenticationException("Ancien mot de passe incorrect")
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise AuthenticationException(" ".join(e.messages))
        user.set_password(new_password)
        self.user_repo.save(user)
        return {"success": True, "message": "Mot de passe modifié avec succès"}

    def reset_password_request(self, email: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            # Ne pas révéler l'existence de l'email pour sécurité
            return {"success": True, "message": "Si l'email existe, un code de réinitialisation a été envoyé"}
        if not self.otp_service:
            raise AuthenticationException("Service OTP non disponible")
        result = self.otp_service.request_otp(email, purpose="RESET_PASSWORD")
        if not result['success']:
            raise AuthenticationException(result['message'])
        return {"success": True, "message": "Code de réinitialisation envoyé"}

    def reset_password_confirm(self, email: str, otp: str, new_password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationException("Utilisateur non trouvé")
        if not self.otp_service:
            raise AuthenticationException("Service OTP non disponible")
        verify_result = self.otp_service.verify_otp(email, otp, purpose="RESET_PASSWORD")
        if not verify_result['success']:
            raise AuthenticationException(verify_result['message'])
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise AuthenticationException(" ".join(e.messages))
        user.set_password(new_password)
        self.user_repo.save(user)
        return {"success": True, "message": "Mot de passe réinitialisé avec succès"}
    
from typing import Dict, Any
from src.domain.entities.citoyen import Citoyen
from src.apps.interfaces.citoyen_interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.apps.interfaces.citoyen_interfaces.biometric_repository_interface import BiometricRepositoryInterface
from src.domain.value_objects.email import Email
from src.domain.value_objects.nin import NIN

class ProfileService:
    def __init__(self, citoyen_repo: CitoyenRepositoryInterface, biometric_repo: BiometricRepositoryInterface):
        self.citoyen_repo = citoyen_repo
        self.biometric_repo = biometric_repo

    def get_profile(self, citoyen: Citoyen) -> Dict[str, Any]:
        # Récupérer l'utilisateur sous-jacent (objet Django) pour les champs non présents dans Citoyen ?
        # Idéalement, l'entité Citoyen devrait contenir tout. Mais pour l'instant, on utilise le repository pour obtenir les données additionnelles.
        user = self.citoyen_repo.get_by_id(citoyen.id)  # retourne l'instance User (Django)
        if not user:
            raise ValueError("Citoyen introuvable")

        # Photo
        photo_url = None
        biometric = self.biometric_repo.get_active_by_citoyen(citoyen.id)
        if biometric and biometric.image_path:
            photo_url = f"/media/{biometric.image_path}"  # À adapter selon config

        # Adresse (à partir des champs de l'entité Citoyen)
        adresse = {}
        if citoyen.adresse_province or citoyen.adresse_commune:
            adresse = {
                'province': citoyen.adresse_province,
                'commune': citoyen.adresse_commune,
                'quartier': citoyen.adresse_quartier,
                'avenue': citoyen.adresse_avenue,
                'numero': citoyen.adresse_numero,
                'full': f"{citoyen.adresse_avenue} {citoyen.adresse_numero}, {citoyen.adresse_quartier}, {citoyen.adresse_commune}" + (f", {citoyen.adresse_province}" if citoyen.adresse_province else "")
            }

        # Origine (à partir de lieu_origine_code, mais on peut enrichir)
        origine = {}
        if citoyen.lieu_origine_code:
            origine = {'full': citoyen.lieu_origine_code}  # À améliorer avec les noms via un repository géographique

        return {
            'id': citoyen.id,
            'email': str(citoyen.email),
            'nin': str(citoyen.nin),
            'nom': citoyen.nom,
            'prenom': citoyen.prenom,
            'postnom': citoyen.postnom,
            'sexe': citoyen.sexe,
            'date_naissance': citoyen.date_naissance.isoformat(),
            'telephone': citoyen.telephone,
            'is_validated': getattr(user, 'is_validated', False),
            'photo_url': photo_url,
            'adresse': adresse,
            'origine': origine,
            'nom_pere': citoyen.nom_du_pere,
            'nom_mere': citoyen.nom_de_la_mere,
        }


class ProfileService:
    def __init__(self, citoyen_repo: CitoyenRepositoryInterface, biometric_repo: BiometricRepositoryInterface):
        self.citoyen_repo = citoyen_repo
        self.biometric_repo = biometric_repo

    def get_profile(self, citoyen: Citoyen) -> Dict[str, Any]:
        # Récupérer l'utilisateur Django via le repo (retourne l'instance User)
        user = self.citoyen_repo.get_by_id(citoyen.id)
        if not user:
            raise ValueError("Citoyen introuvable")

        # Photo
        photo_url = None
        biometric = self.biometric_repo.get_active_by_citoyen(citoyen.id)
        if biometric and biometric.image_path:
            # Construire l'URL (à adapter selon ton stockage)
            photo_url = f"/media/{biometric.image_path}"

        # Adresse (les champs sont déjà dans l'entité Citoyen)
        adresse = {}
        if citoyen.adresse_province or citoyen.adresse_commune:
            adresse = {
                'province': citoyen.adresse_province,
                'commune': citoyen.adresse_commune,
                'quartier': citoyen.adresse_quartier,
                'avenue': citoyen.adresse_avenue,
                'numero': citoyen.adresse_numero,
                'full': f"{citoyen.adresse_avenue} {citoyen.adresse_numero}, {citoyen.adresse_quartier}, {citoyen.adresse_commune}" + (f", {citoyen.adresse_province}" if citoyen.adresse_province else "")
            }

        # Origine (à partir du code secteur, mais on peut enrichir plus tard)
        origine = {}
        if citoyen.lieu_origine_code:
            origine = {'full': citoyen.lieu_origine_code}

        return {
            'id': citoyen.id,
            'email': str(citoyen.email),
            'nin': str(citoyen.nin),
            'nom': citoyen.nom,
            'prenom': citoyen.prenom,
            'postnom': citoyen.postnom,
            'sexe': citoyen.sexe,
            'date_naissance': citoyen.date_naissance.isoformat(),
            'lieu_naissance': citoyen.lieu_naissance,
            'telephone': citoyen.telephone,
            'is_validated': getattr(user, 'is_validated', False),
            'photo_url': photo_url,
            'adresse': adresse,
            'origine': origine,
            'nom_pere': citoyen.nom_du_pere,
            'nom_mere': citoyen.nom_de_la_mere,
        }

    def update_profile(self, citoyen: Citoyen, data: Dict[str, Any]) -> Dict[str, Any]:
        allowed_fields = ['telephone', 'adresse', 'nom_pere', 'nom_mere', 'sexe', 'lieu_naissance']

        # Règles métier
        if 'nom_pere' in data and citoyen.nom_du_pere and citoyen.nom_du_pere.strip():
            raise ValueError("Le nom du père est déjà renseigné")
        if 'nom_mere' in data and citoyen.nom_de_la_mere and citoyen.nom_de_la_mere.strip():
            raise ValueError("Le nom de la mère est déjà renseigné")
        if 'sexe' in data and citoyen.sexe and citoyen.sexe.strip():
            raise ValueError("Le sexe est déjà renseigné")
        if 'lieu_naissance' in data and citoyen.lieu_naissance and citoyen.lieu_naissance.strip():
            raise ValueError("Le lieu de naissance est déjà renseigné")

        for field in allowed_fields:
            if field in data:
                setattr(citoyen, field, data[field])

        self.citoyen_repo.save(citoyen)
        return {'message': 'Profil mis à jour avec succès'}