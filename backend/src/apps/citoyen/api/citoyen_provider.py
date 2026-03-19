# src/apps/citoyen/providers.py
from src.apps.citoyen.repositories.biometric_repository import BiometricRepository
from src.apps.citoyen.repositories.citoyen_repository import DjangoCitoyenRepository
from src.apps.citoyen.services.enrollment_service import EnrollmentService
from src.apps.citoyen.services.biometric_service import BiometricService

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