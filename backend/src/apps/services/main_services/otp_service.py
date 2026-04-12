from src.apps.interfaces.main_interfaces.otp_interface import OTPSenderInterface
from src.shared.external_services.sms_gateway import SmsGateway
from src.apps.interfaces.main_interfaces.otp_interface import OTPSenderInterface
from django.core.mail import send_mail
from django.conf import settings
from src.apps.interfaces.main_interfaces.otp_interface import OTPRepositoryInterface
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface
import threading


# src/apps/services/main_services/otp_service.py
class OTPSenderSms(OTPSenderInterface):
    def __init__(self):
        self.sms_gateway = SmsGateway()

    def send(self, user, code: str = None, message: str = None) -> bool:
        if not user.telephone:
            return False
        if message:
            content = message
        else:
            content = f"Votre code de vérification est: {code}"
        return self.sms_gateway.send_sms(user.telephone, content)
    


class OTPSenderEmail(OTPSenderInterface):
    def send(self, user, code: str = None, message: str = None) -> bool:
        """
        Envoie un email de manière asynchrone (non bloquante).
        Retourne True si le thread a été démarré, False en cas d'erreur immédiate.
        """
        try:
            if message:
                final_message = message
                subject = "📧 Notification SEIP"
            else:
                subject = "🛡️ Alerte de sécurité - Connexion SEIP"
                final_message = (
                    f"Bonjour {user.prenom} {user.nom},\n\n"
                    f"Votre code de vérification est : {code}\n\n"
                    "Si vous n'êtes pas à l'origine, contactez l'administrateur.\n\n"
                    "Système d'Identification Électronique de la Population."
                )

            # Lance l'envoi dans un thread séparé
            thread = threading.Thread(
                target=self._send_email_thread,
                args=(subject, final_message, user.email)
            )
            thread.start()
            return True
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du thread email : {str(e)}")
            return False

    def _send_email_thread(self, subject, message, recipient_email):
        """
        Méthode exécutée dans le thread pour envoyer réellement l'email.
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            print(f"✅ Email envoyé à : {recipient_email}")
        except Exception as e:
            print(f"❌ Erreur SMTP (thread) : {str(e)}")
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