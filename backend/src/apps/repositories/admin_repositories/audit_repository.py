from typing import List, Optional
from datetime import datetime, timedelta
from django.db.models import Q
from src.models import AuditLog
from src.apps.interfaces.admin_interfaces.audit_repository_interface import AuditRepositoryInterface

class AuditRepository(AuditRepositoryInterface):
    def log_action(self, action: str, user_id: Optional[str] = None,
                   resource: Optional[str] = None, details: Optional[dict] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            entity_type=resource or '',
            entity_id=details.get('entity_id', '') if details else '',
            old_data=details.get('old_data') if details else None,
            new_data=details.get('new_data') if details else None,
            ip_address=ip_address or '',
            user_agent=user_agent or ''
        )

    def get_logs_by_user(self, user_id: str, limit: int = 100) -> List:
        return list(AuditLog.objects.filter(user_id=user_id).order_by('-created_at')[:limit])

    def get_logs_by_action(self, action: str, limit: int = 100) -> List:
        return list(AuditLog.objects.filter(action=action).order_by('-created_at')[:limit])

    def get_logs_by_date_range(self, start_date: datetime, end_date: datetime) -> List:
        return list(AuditLog.objects.filter(created_at__range=(start_date, end_date)).order_by('-created_at'))

    def get_recent_logs(self, hours: int = 24) -> List:
        since = datetime.now() - timedelta(hours=hours)
        return list(AuditLog.objects.filter(created_at__gte=since).order_by('-created_at'))

    def search_logs(self, query: str, limit: int = 100) -> List:
        return list(AuditLog.objects.filter(
            Q(action__icontains=query) |
            Q(entity_type__icontains=query) |
            Q(entity_id__icontains=query) |
            Q(old_data__icontains=query) |
            Q(new_data__icontains=query) |
            Q(ip_address__icontains=query) |
            Q(user_agent__icontains=query)
        ).order_by('-created_at')[:limit])