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
    

class OTPSenderEmail(OTPSenderInterface):
    def send(self, user, code: str) -> bool:
        try:
            subject = "🛡️ Alerte de sécurité - Connexion SEIP"
            
            # On personnalise le message avec les données du user
            message = (
                f"Bonjour {user.prenom} {user.nom},\n\n"
                f"Une nouvelle connexion a été détectée sur votre compte Agent SEIP.\n"
                f"Votre code de session actuel est : {code}\n\n"
                "Si vous n'êtes pas à l'origine de cette action, veuillez contacter l'administrateur.\n\n"
                "Système d'Identification Électronique de la Population."
            )
            
            # send_mail va puiser les infos (HOST, PORT, USER, PASSWORD) 
            # directement dans ton fichier settings.py que tu viens de modifier.
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False, 
            )
            
            print(f"✅ Mail de sécurité envoyé avec succès à : {user.email}")
            return True
            
        except Exception as e:
            # Si le mot de passe de 16 caractères est faux ou pas d'internet, 
            # l'erreur s'affichera ici dans ton terminal Ubuntu.
            print(f"❌ Erreur SMTP critique : {str(e)}")
            return False

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