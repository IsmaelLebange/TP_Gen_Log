from django.db import models
from src.apps.main.models import User

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Création'
        UPDATE = 'UPDATE', 'Modification'
        DELETE = 'DELETE', 'Suppression'
        VIEW = 'VIEW', 'Consultation'
        LOGIN = 'LOGIN', 'Connexion'
        LOGOUT = 'LOGOUT', 'Déconnexion'
        VALIDATE = 'VALIDATE', 'Validation'
        REJECT = 'REJECT', 'Rejet'
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    entity_type = models.CharField(max_length=50)  # 'Citoyen', 'Document', etc.
    entity_id = models.CharField(max_length=50)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} - {self.entity_type} - {self.created_at}"
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']