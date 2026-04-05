
from src.domain.entities.citoyen import Citoyen
from src.apps.interfaces.citoyen_interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from src.shared.utils.qrcode_utils import QRCodeService
from django.db import transaction
import logging




logger = logging.getLogger(__name__)

class EnrollmentService:
    """
    Service d'enrôlement d'un nouveau citoyen respectant le DDD.
    """

    def __init__(self, citoyen_repo):
        self.citoyen_repo = citoyen_repo

    def enroler(self, citoyen: Citoyen)-> Citoyen:
        """
        Logique métier avec transaction atomique.
        """
        try:
            # On ouvre un bloc atomique : tout ce qui est dedans est "tout ou rien"
            with transaction.atomic():
                # 1. Vérification d'unicité (Email)
                if self.citoyen_repo.get_by_email(citoyen.email):
                    raise ValueError(f"L'email {citoyen.email} est déjà utilisé.")

                # 2. Vérification d'unicité (NIN)
                if self.citoyen_repo.get_by_nin(citoyen.nin):
                    raise ValueError(f"Le NIN {citoyen.nin} est déjà attribué.")

                # 3. Persistence
                citoyen_sauvegarde = self.citoyen_repo.save(citoyen)

                if not citoyen_sauvegarde:
                    raise Exception("Erreur lors de la persistence du citoyen.")

                # 🚀 ASTUCE : Si tu voulais que ce soit parfait, 
                # il faudrait appeler la biométrie ICI.
                # Mais pour l'instant, ça sécurise déjà la création civile.
                
                return citoyen_sauvegarde

        except Exception as e:
            logger.error(f"Échec de l'enrôlement : {str(e)}")
            # La transaction s'annule (Rollback) automatiquement ici
            raise e
    def get_my_qr_code(self, user_id: int) -> dict:
        """
        Récupère les infos et génère le QR Code en Base64.
        """
        # CORRECTION : On utilise self.citoyen_repo (défini dans le __init__)
        user = self.citoyen_repo.get_by_id(user_id)
        
        if not user:
            logger.error(f"Tentative de génération QR pour user_id {user_id} inexistant")
            raise ValueError("Utilisateur non trouvé")
            
        # Construction de la data (NIN + Infos de base)
        # On utilise getattr pour le postnom au cas où il est optionnel
        postnom = getattr(user, 'postnom', '')
        data = f"NIN:{user.nin}|NOM:{user.nom}|PRENOM:{user.prenom}|POSTNOM:{postnom}"
        
        # Appel à l'utilitaire
        qr_base64 = QRCodeService.generate_base64(data)
        
        return {
            'nin': user.nin,
            'qr_code': qr_base64,
            'owner': f"{user.prenom} {user.nom}"
        }
    
    def complete_biometric_if_done(self, user_id: int) -> None:
        from src.apps.api.providers.citoyen_provider import CitoyenProvider
        biometric_service = CitoyenProvider.get_biometric_service()
        active_types = biometric_service.get_active_types(user_id)
        # Définir les types obligatoires (ex: face et fingerprint)
        required = {'face', 'fingerprint'}
        if required.issubset(set(active_types)):
            self.citoyen_repo.update_biometric_complete(user_id, True)

    def update_biometric_complete(self, user_id: int, completed: bool) -> None:
        self.citoyen_repo.update_biometric_complete(user_id, completed)