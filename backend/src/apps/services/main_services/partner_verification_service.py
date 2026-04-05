import logging
from typing import Dict, Any
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.interfaces.main_interfaces.partner_interface import PartenaireRepositoryInterface
from src.domain.exceptions.domain_exceptions import AuthenticationException
from src.shared.utils.qrcode_utils import QRCodeService

logger = logging.getLogger(__name__)

class PartnerVerificationService:
    def __init__(self, user_repo: UserRepositoryInterface, partenaire_repo: PartenaireRepositoryInterface):
        self.user_repo = user_repo
        self.partenaire_repo = partenaire_repo

    def verify_by_nin(self, token: str, nin: str) -> Dict[str, Any]:
        """
        Vérifie un citoyen via son NIN.
        Le partenaire doit fournir un token valide.
        """
        # Vérifier le token partenaire
        partenaire = self.partenaire_repo.get_by_token(token)
        if not partenaire:
            raise AuthenticationException("Token partenaire invalide")

        # Récupérer le citoyen
        user = self.user_repo.get_by_nin(nin)
        if not user:
            raise AuthenticationException("Citoyen non trouvé")

        # Retourner les infos publiques
        return {
            'nin': user.nin,
            'nom': user.nom,
            'prenom': user.prenom,
            'postnom': getattr(user, 'postnom', ''),
            'date_naissance': user.date_naissance.isoformat() if user.date_naissance else None,
            'lieu_origine': str(user.lieu_origine) if user.lieu_origine else None,
        }

    # src/apps/services/main_services/partner_verification_service.py
    def generate_qr_code(self, token: str, nin: str) -> Dict[str, Any]:
        """
        Génère un QR code pour un citoyen (en utilisant son NIN).
        Le partenaire doit fournir un token valide.
        """
        # Vérifier le token partenaire
        partenaire = self.partenaire_repo.get_by_token(token)
        if not partenaire:
            raise AuthenticationException("Token partenaire invalide")

        user = self.user_repo.get_by_nin(nin)
        if not user:
            raise AuthenticationException("Citoyen non trouvé")
        # Générer le QR code avec les infos pertinentes
        data = f"NIN:{nin}|NOM:{user.nom}|PRENOM:{user.prenom}"
        qr_base64 = QRCodeService.generate_base64(data)
        return {
            'nin': nin,
            'qr_code': qr_base64,
        }