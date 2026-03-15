# src/apps/citoyen/providers.py
from src.apps.citoyen.repositories.citoyen_repository import DjangoCitoyenRepository
from src.apps.citoyen.services.enrollment_service import EnrollmentService

class CitoyenProvider:
    @staticmethod
    def get_citoyen_repository():
        return DjangoCitoyenRepository()

    @staticmethod
    def get_enrollment_service():
        # On injecte le repo dans le service ici !
        repo = CitoyenProvider.get_citoyen_repository()
        return EnrollmentService(citoyen_repo=repo)