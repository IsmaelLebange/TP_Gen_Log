from django.db import models
from src.apps.main.models import User

class Document(models.Model):
    class TypeDocument(models.TextChoices):
        CARTE_IDENTITE = 'CNI', "Carte d'identité"
        PASSEPORT = 'PAS', 'Passeport'
        PERMIS_CONDUITE = 'PER', 'Permis de conduire'
        ACTE_NAISSANCE = 'ACT', "Acte de naissance"
        JUSTIF_DOMICILE = 'DOM', 'Justificatif de domicile'
    
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDE = 'VALIDE', 'Validé'
        REJETE = 'REJETE', 'Rejeté'
        EXPIRED = 'EXPIRE', 'Expiré'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    type = models.CharField(max_length=20, choices=TypeDocument.choices)
    numero = models.CharField(max_length=50)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    date_emission = models.DateField()
    date_expiration = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_rejet = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.type} - {self.numero} - {self.user.nin}"
    
    class Meta:
        db_table = 'documents'