from typing import Optional
from datetime import date
from src.domain.entities.citoyen import Citoyen
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email
from src.apps.citoyen.interfaces.citoyen_repository_interface import CitoyenRepositoryInterface

class EnrollmentService:
    """
    Service d'enrôlement d'un nouveau citoyen respectant le DDD.
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
        postnom: Optional[str] = None, # Optionnel comme tu l'as défini
        telephone: Optional[str] = None
    ) -> Citoyen:
        
        # 1. Validation via les Value Objects
        # Si le NIN ou l'Email est mal formé, ça lèvera une exception ici
        nin_vo = NIN(nin)
        email_vo = Email(email)

        # 2. Vérification d'unicité (C'est ça qui fait passer le test 400)
        # On utilise les VO pour la recherche
        if self.citoyen_repo.get_by_nin(nin_vo):
            raise ValueError(f"Un citoyen avec le NIN {nin} existe déjà.")

        if self.citoyen_repo.get_by_email(email_vo):
            raise ValueError(f"Un citoyen avec l'email {email} existe déjà.")

        # 3. Création de l'entité domaine
        citoyen_entity = Citoyen(
            nin=nin_vo,
            email=email_vo,
            nom=nom,
            postnom=postnom,
            prenom=prenom,
            date_naissance=date_naissance,
            telephone=telephone,
            id=None  # L'ID sera attribué par la persistence
        )

        # 4. Persistence
        # On demande au repository de sauvegarder l'entité domaine
        # IMPORTANT : Ton repo doit renvoyer l'entité avec son nouvel ID
        citoyen_sauvegarde = self.citoyen_repo.save(citoyen_entity)

        if not citoyen_sauvegarde:
            raise Exception("Erreur lors de la persistence du citoyen.")

        return citoyen_sauvegarde