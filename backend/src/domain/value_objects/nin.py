import re

class NIN:
    """Value Object pour le NIN (National ID Number)"""
    
    PATTERN = r'^[A-Z0-9]{12,20}$'  # Exemple: 12-20 caractères alphanumériques
    
    def __init__(self, value: str):
        self.value = self._validate(value)
    
    def _validate(self, value: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError("NIN doit être une chaîne de caractères")
        
        value = value.strip().upper()
        
        if not re.match(self.PATTERN, value):
            raise ValueError(f"NIN invalide: {value}")
        
        return value
    
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if not isinstance(other, NIN):
            return False
        return self.value == other.value