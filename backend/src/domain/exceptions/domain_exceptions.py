class DomainException(Exception):
    """Exception de base pour le domaine"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or "DOMAIN_ERROR"
        super().__init__(self.message)

class CitoyenNotFoundException(DomainException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"Citoyen non trouvé: {identifier}",
            code="CITOYEN_NOT_FOUND"
        )

class DocumentNotFoundException(DomainException):
    def __init__(self, document_id: int):
        super().__init__(
            message=f"Document non trouvé: {document_id}",
            code="DOCUMENT_NOT_FOUND"
        )

class AuthenticationException(DomainException):
    def __init__(self, message: str = "Erreur d'authentification"):
        super().__init__(
            message=message,
            code="AUTH_ERROR"
        )

class ValidationException(DomainException):
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR"
        )

class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Accès non autorisé"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED"
        )