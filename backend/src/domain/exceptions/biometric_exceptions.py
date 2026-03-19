import inspect

class BiometricDomainError(Exception):
    """
    Classe de base avec support pour les codes d'erreur et 
    localisation automatique de l'exception (Classe.methode).
    """
    def __init__(self, message: str = "Une erreur biométrique est survenue.", code: str = "BIOMETRIC_ERROR"):
        self.message = message
        self.code = code
        
        # --- Extraction du contexte d'appel ---
        stack = inspect.stack()
        # On remonte à la stack [1] (l'endroit où l'erreur est levée)
        caller_frame = stack[1]
        self.function_name = caller_frame.function
        
        # Tentative de récupération du nom de la classe (si applicable)
        self.class_name = ""
        if 'self' in caller_frame.frame.f_locals:
            self.class_name = caller_frame.frame.f_locals['self'].__class__.__name__
        
        # Construction du chemin : "MaClasse.ma_methode()" ou "ma_fonction()"
        self.location = (
            f"{self.class_name}.{self.function_name}()" 
            if self.class_name else f"{self.function_name}()"
        )
        
        # Formatage du message final pour le développeur
        self.full_log = f"[{self.code}] @ {self.location} : {self.message}"
        super().__init__(self.full_log)

    def to_dict(self):
        """Retourne un dictionnaire pour les réponses API JSON."""
        return {
            "success": False,
            "error": {
                "code": self.code,
                "location": self.location,
                "message": self.message
            }
        }

# --- Classes dérivées (héritent de l'introspection) ---

class BiometricNotFoundError(BiometricDomainError):
    def __init__(self, message="Données biométriques introuvables."):
        super().__init__(message, code="BIOMETRIC_NOT_FOUND")

class BiometricAlreadyExistsError(BiometricDomainError):
    def __init__(self, message="Une donnée biométrique active existe déjà."):
        super().__init__(message, code="BIOMETRIC_ALREADY_EXISTS")

class BiometricExtractionError(BiometricDomainError):
    def __init__(self, message="Échec de l'extraction des points caractéristiques (minutiae)."):
        super().__init__(message, code="EXTRACTION_FAILED")

class BiometricVerificationError(BiometricDomainError):
    def __init__(self, message="Le score de correspondance est insuffisant."):
        super().__init__(message, code="VERIFICATION_FAILED")