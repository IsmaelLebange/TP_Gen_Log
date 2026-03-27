# src/apps/main/providers.py
import os
from django.utils.module_loading import import_string
from src.apps.repositories.main_repositories.user_repository import UserRepository
from src.apps.repositories.main_repositories.otp_repository import OTPRepository
from src.apps.services.main_services.authentication_service import AuthenticationService
from src.apps.services.main_services.otp_service import OTPSenderEmail, OTPSenderSms
from src.apps.services.main_services.otp_service import OTPService


# Ce provider centralise la création des services et repositories pour éviter les imports directs dans les views
class MainProvider:
    @staticmethod
    def get_auth_service():
        # Récupération du service OTP
        otp_service = MainProvider.get_otp_service()
        return AuthenticationService(otp_service=otp_service)
        
    @staticmethod
    def get_user_repository():
        return UserRepository()

    @staticmethod
    def get_otp_repository():
        return OTPRepository()

    @staticmethod
    def get_otp_sender():
        sender_type = os.getenv('OTP_SENDER', 'sms')
        if sender_type == 'email':
            return OTPSenderEmail()
        return OTPSenderSms()

    @staticmethod
    def get_otp_service():
        return OTPService(
            user_repo=MainProvider.get_user_repository(),
            otp_repo=MainProvider.get_otp_repository(),
            sender=MainProvider.get_otp_sender()
        )