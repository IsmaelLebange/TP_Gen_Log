from datetime import datetime, timedelta
from src.domain.value_objects.otp import OTPCode

class OTP:
    """
    Entité domaine OTP.
    Contient la logique d’expiration, validation, etc.
    """
    def __init__(self, code: str, expires_at: datetime, user_id: int, purpose: str):
        self.code = OTPCode(code)       # value object
        self.expires_at = expires_at
        self.user_id = user_id
        self.purpose = purpose
        self.is_used = False
        self.id = None                  # pour l’ID en base (optionnel)

    def is_valid(self) -> bool:
        return not self.is_used and datetime.now() <= self.expires_at

    def use(self):
        self.is_used = True

    def to_dict(self):
        return {
            'code': str(self.code),
            'expires_at': self.expires_at.isoformat(),
            'user_id': self.user_id,
            'purpose': self.purpose,
            'is_used': self.is_used,
        }