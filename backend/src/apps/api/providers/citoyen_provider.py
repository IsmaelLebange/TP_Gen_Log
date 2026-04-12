# src/apps/citoyen/providers.py
from src.apps.api.providers.main_provider import MainProvider
from src.apps.repositories.citoyen_repositories.biometric_repository import BiometricRepository
from src.apps.repositories.citoyen_repositories.citoyen_repository import DjangoCitoyenRepository
from src.apps.repositories.citoyen_repositories.document_repository import DocumentRepository
from src.apps.repositories.main_repositories.user_repository import UserRepository
from src.apps.services.citoyen_services.credential_service import CredentialService
from src.apps.services.citoyen_services.document_service import DocumentService
from src.apps.services.citoyen_services.enrollment_service import EnrollmentService
from src.apps.services.citoyen_services.biometric_service import BiometricService

class CitoyenProvider:
    @staticmethod
    def get_citoyen_repository():
        return DjangoCitoyenRepository()

    @staticmethod
    def get_enrollment_service():
        # On injecte le repo dans le service ici !
        repo = CitoyenProvider.get_citoyen_repository()
        return EnrollmentService(citoyen_repo=repo)
    
    @staticmethod
    def get_biometric_repository():
        # Ici on pourrait choisir une autre implémentation (mock, autre DB)
        return BiometricRepository()

    @staticmethod
    def get_biometric_service():
        repo =CitoyenProvider.get_biometric_repository()
        return BiometricService(repository=repo)
    
    @staticmethod
    def get_document_repository():
        return DocumentRepository()

    @staticmethod
    def get_document_service():
        return DocumentService(repository=CitoyenProvider.get_document_repository())
    

    @staticmethod
    def get_credential_service():
        return CredentialService(
            user_repo=UserRepository(),
            otp_service=MainProvider.get_otp_service()
        )
    
    @staticmethod
    def get_profile_service():
        from src.apps.services.citoyen_services.credential_service import ProfileService
        return ProfileService(
            citoyen_repo=CitoyenProvider.get_citoyen_repository(),
            biometric_repo=CitoyenProvider.get_biometric_repository()
        )