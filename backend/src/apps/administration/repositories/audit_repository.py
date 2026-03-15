# audit_repository.py - Repository pour les logs d'audit

from typing import List, Optional
from django.db import models
from datetime import datetime, timedelta
from src.apps.administration.interfaces.audit_repository_interface import AuditRepositoryInterface

class AuditLog(models.Model):
    """Modèle pour les logs d'audit"""
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    resource = models.CharField(max_length=200, null=True, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['user_id']),
        ]

class DjangoAuditRepository(AuditRepositoryInterface):
    """Implémentation Django du repository d'audit"""

    def log_action(self, action: str, user_id: Optional[str] = None,
                   resource: Optional[str] = None, details: Optional[dict] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log une action"""
        AuditLog.objects.create(
            action=action,
            user_id=user_id,
            resource=resource,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

    def get_logs_by_user(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Récupère les logs pour un utilisateur"""
        return list(AuditLog.objects.filter(user_id=user_id)[:limit])

    def get_logs_by_action(self, action: str, limit: int = 100) -> List[AuditLog]:
        """Récupère les logs pour une action"""
        return list(AuditLog.objects.filter(action=action)[:limit])

    def get_logs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AuditLog]:
        """Récupère les logs dans une période"""
        return list(AuditLog.objects.filter(timestamp__range=(start_date, end_date)))

    def get_recent_logs(self, hours: int = 24) -> List[AuditLog]:
        """Récupère les logs récents"""
        since = datetime.now() - timedelta(hours=hours)
        return list(AuditLog.objects.filter(timestamp__gte=since))

    def search_logs(self, query: str, limit: int = 100) -> List[AuditLog]:
        """Recherche dans les logs"""
        from django.db.models import Q
        return list(AuditLog.objects.filter(
            Q(action__icontains=query) |
            Q(resource__icontains=query) |
            Q(details__icontains=query)
        )[:limit])