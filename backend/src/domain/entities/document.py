from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from src.domain.value_objects.statut_validation import StatutValidation

@dataclass
class Document:
    id: Optional[int]
    user_id: int
    type: str
    numero: str
    fichier: str
    date_emission: date
    date_expiration: Optional[date]
    statut: StatutValidation
    created_at: datetime
    updated_at: datetime
    valide_par_id: Optional[int]
    date_validation: Optional[datetime]
    commentaire_rejet: str

    def valider(self, agent_id: int) -> None:
        if self.statut != StatutValidation.EN_ATTENTE:
            raise ValueError("Seul un document en attente peut être validé")
        self.statut = StatutValidation.VALIDE
        self.valide_par_id = agent_id
        self.date_validation = datetime.now()
        self.commentaire_rejet = ""

    def rejeter(self, agent_id: int, commentaire: str) -> None:
        if self.statut != StatutValidation.EN_ATTENTE:
            raise ValueError("Seul un document en attente peut être rejeté")
        if not commentaire:
            raise ValueError("Un commentaire est requis pour le rejet")
        self.statut = StatutValidation.REJETE
        self.valide_par_id = agent_id
        self.date_validation = datetime.now()
        self.commentaire_rejet = commentaire

    def peut_etre_valide(self) -> bool:
        return self.statut == StatutValidation.EN_ATTENTE