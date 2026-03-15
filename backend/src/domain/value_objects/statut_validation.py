from enum import Enum

class StatutValidation(Enum):
    EN_ATTENTE = "EN_ATTENTE"
    VALIDE = "VALIDE"
    REJETE = "REJETE"
    EXPIRE = "EXPIRE"
    
    def peut_etre_modifie(self):
        """Vérifie si un document avec ce statut peut être modifié"""
        return self in [StatutValidation.EN_ATTENTE, StatutValidation.REJETE]
    
    def est_valide(self):
        return self == StatutValidation.VALIDE
    
    def est_rejete(self):
        return self == StatutValidation.REJETE
    
    def __str__(self):
        return self.value