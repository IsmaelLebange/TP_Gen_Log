# src/apps/repositories/main_repositories/otp_repository.py
from datetime import timedelta
from django.utils import timezone
from typing import Optional

from src.models import OTP as OTPModel
from src.domain.entities.otp import OTP as OTPEntity
from src.domain.value_objects.otp import OTPCode
from src.apps.interfaces.main_interfaces.otp_interface import OTPRepositoryInterface

class OTPRepository(OTPRepositoryInterface):
    
    def create(self, user_id: int, purpose: str) -> OTPEntity:
        """
        Crée un OTP en suivant les règles métier et de sécurité.
        """
        # 1. SÉCURITÉ : Invalider les anciens codes non utilisés pour cet utilisateur/purpose
        # Cela évite qu'un utilisateur ait 5 codes valides en même temps
        OTPModel.objects.filter(
            user_id=user_id, 
            purpose=purpose, 
            is_used=False
        ).update(is_used=True)

        # 2. GÉNÉRATION : Utilisation du Value Object pour garantir le format
        # Si OTPCode() est appelé sans argument, il génère un code aléatoire
        new_code_vo = OTPCode() 
        expires_at = timezone.now() + timedelta(minutes=5)

        # 3. DOMAINE : Instanciation de l'Entité Domaine
        otp_entity = OTPEntity(
            code=str(new_code_vo),
            expires_at=expires_at,
            user_id=user_id,
            purpose=purpose
        )

        # 4. INFRASTRUCTURE : Persistance en base de données
        model = OTPModel.objects.create(
            user_id=otp_entity.user_id,
            code=str(otp_entity.code),
            expires_at=otp_entity.expires_at,
            purpose=otp_entity.purpose,
            is_used=otp_entity.is_used,
            attempts=0  # Initialisation du compteur de sécurité pour le brute-force
        )
        
        otp_entity.id = model.id
        return otp_entity

    def get_valid(self, user_id: int, code: str, purpose: str) -> Optional[OTPEntity]:
        """
        Récupère un code valide et le transforme en entité domaine.
        """
        try:
            model = OTPModel.objects.get(
                user_id=user_id,
                code=code,
                purpose=purpose,
                is_used=False,
                expires_at__gte=timezone.now()
            )
            
            # Reconstruction de l'entité à partir des données de la DB
            otp_entity = OTPEntity(
                code=model.code, 
                expires_at=model.expires_at, 
                user_id=model.user_id, 
                purpose=model.purpose
            )
            otp_entity.is_used = model.is_used
            otp_entity.id = model.id
            return otp_entity
            
        except OTPModel.DoesNotExist:
            return None

    def mark_as_used(self, otp_entity: OTPEntity) -> None:
        """
        Marque le code comme consommé.
        """
        otp_entity.use()  # Appelle la logique interne de l'entité
        OTPModel.objects.filter(id=otp_entity.id).update(is_used=True)

    def increment_attempts(self, otp_id: int) -> int:
        """
        Incrémente le nombre de tentatives en base (Anti Brute-force).
        """
        # On récupère le modèle, on incrémente et on vérifie si on doit bannir le code
        model = OTPModel.objects.get(id=otp_id)
        model.attempts += 1
        if model.attempts >= 3:
            model.is_used = True # On invalide le code après 3 échecs
        model.save()
        return model.attempts

    def delete_expired(self) -> int:
        """
        Nettoyage de la base de données.
        """
        deleted, _ = OTPModel.objects.filter(expires_at__lt=timezone.now()).delete()
        return deleted