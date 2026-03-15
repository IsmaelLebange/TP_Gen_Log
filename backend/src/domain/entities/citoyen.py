from dataclasses import dataclass
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email  # on va créer Email plus tard
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class EnrollmentData:
    email: str
    mot_de_passe: str
    nom: str
    postnom: str
    prenom: str
    nin: str
    date_of_birth: date
    phone_number: Optional[str] = None
    address: Optional[str] = None

class Citoyen:
    """
    Entité représentant un citoyen dans le domaine.
    """

    def __init__(
        self,
        nin: NIN,
        email: Email,
        nom: str,
        postnom: str,
        prenom: str,
        date_naissance: date,
        telephone: Optional[str] = None,
        id: Optional[int] = None,
        adresse: Optional[str] = None
    ):
        self.id = id
        self.nin = nin
        self.email = email
        self.nom = nom
        self.postnom = postnom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.telephone = telephone
        self.adresse = adresse
        # On pourrait ajouter d'autres attributs comme adresse, etc.

    def __repr__(self):
        return f"<Citoyen {self.nin}: {self.prenom} {self.nom}>"

    def est_majeur(self) -> bool:
        """Vérifie si le citoyen est majeur (18 ans ou plus)."""
        today = date.today()
        age = today.year - self.date_naissance.year
        if today.month < self.date_naissance.month or (today.month == self.date_naissance.month and today.day < self.date_naissance.day):
            age -= 1
        return age >= 18