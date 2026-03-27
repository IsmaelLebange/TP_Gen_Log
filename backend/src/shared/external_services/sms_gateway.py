# src/shared/external_services/sms_gateway.py
import logging
logger = logging.getLogger(__name__)

class SmsGateway:
    def send_sms(self, phone_number: str, message: str):
        # Simule l'envoi de SMS
        logger.info(f"SMS envoyé à {phone_number}: {message}")
        print(f"[SMS] {phone_number} -> {message}")
        return True