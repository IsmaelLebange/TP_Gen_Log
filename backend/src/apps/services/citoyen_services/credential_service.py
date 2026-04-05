import logging
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.interfaces.main_interfaces.otp_interface import OTPServiceInterface
from src.domain.exceptions.domain_exceptions import AuthenticationException

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