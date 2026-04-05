from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional, Dict
from src.domain.value_objects.nin import NIN
from src.domain.value_objects.email import Email
from src.domain.value_objects.biometrics import BiometricType

@dataclass(frozen=True)
class EnrollmentData:
    # 1. Champs obligatoires (SANS valeur par défaut)
    email: str
    mot_de_passe: str
    nom: str
    postnom: str
    prenom: str
    nin: str
    date_naissance: date
    
    # 2. Champs optionnels (AVEC valeur par défaut, TOUJOURS à la fin)
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    province_origine: Optional[str] = None
    territoire_origine: Optional[str] = None
    secteur_origine: Optional[str] = None
    biometrics: Optional[Dict[BiometricType, str]] = None 
    nom_du_pere: Optional[str] = None
    nom_de_la_mere: Optional[str] = None



@dataclass
class Citoyen:
    nom: str
    postnom: str
    prenom: str
    date_naissance: date
    sexe: str 
    lieu_origine_code: str 
    email: Email
    mot_de_passe: str
    nom_du_pere: str
    nom_de_la_mere: str
    province_origine: Optional[str] = None
    territoire_origine: Optional[str] = None
    secteur_origine: Optional[str] = None
    telephone: Optional[str] = None
    adresse_province: Optional[str] = None
    adresse_commune: Optional[str] = None
    adresse_quartier: Optional[str] = None
    adresse_avenue: Optional[str] = None
    adresse_numero: Optional[str] = None
    id: Optional[int] = None
    nin: Optional[NIN] = None

    def __post_init__(self):
        if not self.est_majeur():
            raise ValueError("Le citoyen doit être majeur (18 ans minimum).")
        
        # Génération automatique si non fourni
        if self.nin is None:
            self.nin = NIN.generer(
                code_secteur=self.lieu_origine_code,
                date_naissance=self.date_naissance,
                sexe=self.sexe
            )

    def est_majeur(self) -> bool:
        today = date.today()
        age = today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
        return age >= 18

    @classmethod
    def from_request(cls, data: Dict[str, Any], code_secteur: str):
        """
        Crée l'entité à partir des données validées du Serializer et du code secteur trouvé.
        """
        d_naiss = data.get('date_naissance')
        if isinstance(d_naiss, str):
            d_naiss = date.fromisoformat(d_naiss)
            
        return cls(
            nom=data.get('nom', '').upper(),
            postnom=data.get('postnom', '').upper(),
            prenom=data.get('prenom', '').capitalize(),
            date_naissance=d_naiss,
            sexe=data.get('sexe'),
            lieu_origine_code=code_secteur, # Utilise le code technique récupéré
            email=Email(data.get('email')),
            mot_de_passe=data.get('mot_de_passe'),
            nom_du_pere=data.get('nom_du_pere'),
            nom_de_la_mere=data.get('nom_de_la_mere'),
            province_origine=data.get('province_origine'),
            territoire_origine=data.get('territoire_origine'),
            secteur_origine=data.get('secteur_origine'),
            telephone=data.get('telephone'),
            adresse_province=data.get('adresse_province'),
            adresse_commune=data.get('adresse_commune'),
            adresse_quartier=data.get('adresse_quartier'),
            adresse_avenue=data.get('adresse_avenue'),
            adresse_numero=data.get('adresse_numero'),
        )

    def to_dict(self):
        data = asdict(self)
        data['nin'] = str(self.nin) if self.nin else None
        data['email'] = str(self.email) if self.email else None
        data.pop('mot_de_passe', None) 
        return data