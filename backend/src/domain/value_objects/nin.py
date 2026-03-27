import re
from datetime import date

class NIN:
    """
    Format : code_secteur(7) + jj(2) + mm(2) + aa(2) + sexe(1) + cle(2)
    Exemple : 2201401 + 01 + 01 + 00 + M + 45
    """
    def __init__(self, valeur: str):
        if not self._valider_format(valeur):
            raise ValueError(f"Format NIN invalide : {valeur}")
        self.valeur = valeur

    @classmethod
    def generer(cls, code_secteur: str, date_naissance: date, sexe: str) -> 'NIN':
        # On s'assure que le code secteur fait bien 7 chiffres (ex: 2201401)
        code_secteur = str(code_secteur).zfill(7)
        
        jour = date_naissance.strftime("%d")
        mois = date_naissance.strftime("%m")
        annee = date_naissance.strftime("%y")
        sexe_lettre = sexe.upper()[0] 

        base = f"{code_secteur}{jour}{mois}{annee}{sexe_lettre}"
        
        # Clé de contrôle simple
        total = sum(int(ch) for ch in base if ch.isdigit())
        cle = str(total % 100).zfill(2)

        return cls(f"{base}{cle}")

    @staticmethod
    def _valider_format(valeur: str) -> bool:
        # 7(secteur) + 6(date) + 1(sexe) + 2(clé) = 16 caractères
        return bool(re.match(r'^\d{7}\d{6}[MF]\d{2}$', valeur))

    def __str__(self):
        return self.valeur