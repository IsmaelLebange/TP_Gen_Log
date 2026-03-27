# src/domain/value_objects/otp.py
import secrets
import hashlib
from datetime import datetime, timedelta

class OTPCode:
    """
    Value Object pour la génération et validation d'un code OTP.
    """

    def __init__(self, value: str = None):
        if value is None:
            self.value = self._generate()
        else:
            if not self._validate(value):
                raise ValueError("Code OTP invalide (doit être 6 chiffres)")
            self.value = value

    def _generate(self) -> str:
        # Génère un code à 6 chiffres aléatoire
        return ''.join(secrets.choice('0123456789') for _ in range(6))

    def _validate(self, value: str) -> bool:
        return value.isdigit() and len(value) == 6

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return isinstance(other, OTPCode) and self.value == other.value