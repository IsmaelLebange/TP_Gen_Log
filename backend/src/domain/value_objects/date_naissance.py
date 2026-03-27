from datetime import date, datetime

class DateNaissance:
    def __init__(self, valeur):
        if isinstance(valeur, str):
            try:
                self.valeur = datetime.strptime(valeur, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Format de date invalide (YYYY-MM-DD)")
        elif isinstance(valeur, date):
            self.valeur = valeur
        else:
            raise ValueError("Type de date non supporté")

        self._verifier_majorite()

    def _verifier_majorite(self):
        today = date.today()
        age = today.year - self.valeur.year - ((today.month, today.day) < (self.valeur.month, self.valeur.day))
        if age < 18:
            raise ValueError("Le citoyen doit être majeur (18 ans).")

    def __str__(self):
        return self.valeur.isoformat()