from src.domain.entities.citoyen import Citoyen
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email
from src.apps.citoyen.interfaces.citoyen_repository_interface import CitoyenRepositoryInterface
from datetime import date
from typing import Optional

class EnrollmentService:
    """
    Service d'enrôlement d'un nouveau citoyen.
    """

    def __init__(self, citoyen_repo: CitoyenRepositoryInterface):
        self.citoyen_repo = citoyen_repo

    def enroler(
        self,
        nin: str,
        email: str,
        nom: str,
        prenom: str,
        date_naissance: date,
        telephone: Optional[str] = None
    ) -> Citoyen:
        
        # Création des value objects (validation)
        nin_vo = NIN(nin)
        email_vo = Email(email)

        # Vérification d'unicité
        existing = self.citoyen_repo.get_by_nin(nin_vo)
        if existing:
            raise ValueError(f"Un citoyen avec le NIN {nin} existe déjà.")

        existing = self.citoyen_repo.get_by_email(email_vo)
        if existing:
            raise ValueError(f"Un citoyen avec l'email {email} existe déjà.")

        # Création de l'entité domaine
        citoyen = Citoyen(
            nin=nin_vo,
            email=email_vo,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            telephone=telephone,
            id=None  # Pas encore d'ID
        )
