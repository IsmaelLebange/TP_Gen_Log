import re

class Email:
    """
    Value Object pour l'email.
    Valide le format et normalise en minuscules.
    """
    PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __init__(self, value: str):
        self.value = self._validate(value)

    def _validate(self, value: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError("Email doit être une chaîne de caractères")
        value = value.strip().lower()
        if not re.match(self.PATTERN, value):
            raise ValueError(f"Email invalide: {value}")
        return value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if not isinstance(other, Email):
            return False
        return self.value == other.value