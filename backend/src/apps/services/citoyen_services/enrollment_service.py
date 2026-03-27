from src.domain.entities.citoyen import Citoyen
from src.apps.interfaces.citoyen_interfaces.citoyen_repository_interface import CitoyenRepositoryInterface

class EnrollmentService:
    """
    Service d'enrôlement d'un nouveau citoyen respectant le DDD.
    """

    def __init__(self, citoyen_repo: CitoyenRepositoryInterface):
        self.citoyen_repo = citoyen_repo

    def enroler(self, citoyen: Citoyen) -> Citoyen:
        """
        Logique métier pour l'enrôlement.
        """
        # 1. Vérification d'unicité de l'Email via le Repo
        if self.citoyen_repo.get_by_email(citoyen.email):
            raise ValueError(f"Un citoyen avec l'email {citoyen.email} existe déjà.")

        # 2. Vérification d'unicité du NIN (déjà généré dans l'entité)
        if self.citoyen_repo.get_by_nin(citoyen.nin):
            raise ValueError(f"Le NIN {citoyen.nin} est déjà attribué.")

        # 3. Persistence
        citoyen_sauvegarde = self.citoyen_repo.save(citoyen)

        if not citoyen_sauvegarde:
            raise Exception("Erreur lors de la persistence du citoyen.")

        return citoyen_sauvegarde