from typing import List, Dict, Any, Optional
from datetime import datetime
from src.apps.interfaces.admin_interfaces.audit_repository_interface import AuditRepositoryInterface

class AuditService:
    def __init__(self, repo: AuditRepositoryInterface):
        self.repo = repo

    def log(self, action: str, user_id: Optional[int] = None, resource: Optional[str] = None,
            details: Optional[dict] = None, ip_address: Optional[str] = None,
            user_agent: Optional[str] = None):
        self.repo.log_action(
            action=action,
            user_id=str(user_id) if user_id else None,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def get_by_user(self, user_id: int, limit: int = 100) -> List[Dict]:
        logs = self.repo.get_logs_by_user(str(user_id), limit)
        return [self._serialize(log) for log in logs]

    def get_by_action(self, action: str, limit: int = 100) -> List[Dict]:
        logs = self.repo.get_logs_by_action(action, limit)
        return [self._serialize(log) for log in logs]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Dict]:
        logs = self.repo.get_logs_by_date_range(start, end)
        return [self._serialize(log) for log in logs]

    def get_recent(self, hours: int = 24) -> List[Dict]:
        logs = self.repo.get_recent_logs(hours)
        return [self._serialize(log) for log in logs]
    def get_by_province(self, province: str, limit: int = 100) -> List[Dict]:
        logs=self.repo.get_logs_by_province(province,limit)
        return [self._serialize(log) for log in logs]
    def get_by_territoire(self, territoire: str, limit: int = 100) -> List[Dict]:
        logs=self.repo.get_logs_by_territoire(territoire,limit)
        return [self._serialize(log) for log in logs]
    def get_by_secteur(self, secteur: str, limit: int = 100) -> List[Dict]:
        logs=self.repo.get_logs_by_secteur(secteur,limit)
        return [self._serialize(log) for log in logs]

    def search(self, query: str, limit: int = 100) -> List[Dict]:
        logs = self.repo.search_logs(query, limit)
        return [self._serialize(log) for log in logs]
    

    def _serialize(self, log) -> Dict:
        return {
            'id': log.id,
            'user_id': log.user_id,
            'user_email': log.user.email if log.user else None,
            'action': log.action,
            'entity_type': log.entity_type,
            'entity_id': log.entity_id,
            'old_data': log.old_data,
            'new_data': log.new_data,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'created_at': log.created_at.isoformat()
        }