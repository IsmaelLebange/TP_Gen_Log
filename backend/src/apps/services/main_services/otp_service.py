from src.apps.interfaces.main_interfaces.otp_interface import OTPSenderInterface
from src.shared.external_services.sms_gateway import SmsGateway
from src.apps.interfaces.main_interfaces.otp_interface import OTPSenderInterface
from django.core.mail import send_mail
from django.conf import settings
from src.apps.interfaces.main_interfaces.otp_interface import OTPRepositoryInterface
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface


# src/apps/services/main_services/otp_service.py
class OTPSenderSms(OTPSenderInterface):
    def __init__(self):
        self.sms_gateway = SmsGateway()

    def send(self, user, code: str) -> bool:
        if not user.telephone:
            return False
        message = f"Votre code de vérification est: {code}"
        return self.sms_gateway.send_sms(user.telephone, message)
    

# src/apps/services/main_services/otp_service.py
class OTPSenderEmail(OTPSenderInterface):
    def send(self, user, code: str) -> bool:
        subject = "Votre code de vérification"
        message = f"Bonjour,\n\nVotre code OTP est: {code}\nIl expire dans 5 minutes."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return True
    

# src/apps/services/main_services/otp_service.py
class OTPService:
    
    def __init__(self,
                 user_repo: UserRepositoryInterface,
                 otp_repo: OTPRepositoryInterface,
                 sender: OTPSenderInterface):
        self.user_repo = user_repo
        self.otp_repo = otp_repo
        self.sender = sender
     
    def request_otp(self, email: str, purpose: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            return {'success': False, 'message': 'Utilisateur non trouvé'}

        otp_entity = self.otp_repo.create(user.id, purpose)
        sent = self.sender.send(user, str(otp_entity.code))
        if not sent:
            return {'success': False, 'message': 'Échec d’envoi du code'}

        return {
            'success': True,
            'message': 'Code envoyé',
            'expires_in': 5   # minutes
        }

    def verify_otp(self, email: str, code: str, purpose: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            return {'success': False, 'message': 'Utilisateur non trouvé'}

        otp_entity = self.otp_repo.get_valid(user.id, code, purpose)
        if not otp_entity or not otp_entity.is_valid():
            return {'success': False, 'message': 'Code invalide ou expiré'}
        
        if otp_entity.is_used:
            return {'success': False, 'message': 'Code déjà utilisé'}
        if otp_entity.attempts >= 5:
            return {'success': False, 'message': 'Nombre de tentatives dépassé'}


        self.otp_repo.mark_as_used(otp_entity)

        return {
            'success': True,
            'message': 'Code vérifié',
            'user_id': user.id,
            'email': user.email
        }