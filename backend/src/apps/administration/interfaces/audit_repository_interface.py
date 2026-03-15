# audit_repository_interface.py - Interface pour le repository d'audit

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class AuditRepositoryInterface(ABC):
    """Interface abstraite pour le repository d'audit"""

    @abstractmethod
    def log_action(self, action: str, user_id: Optional[str] = None,
                   resource: Optional[str] = None, details: Optional[dict] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log une action"""
        pass

    @abstractmethod
    def get_logs_by_user(self, user_id: str, limit: int = 100) -> List:
        """Récupère les logs pour un utilisateur"""
        pass

    @abstractmethod
    def get_logs_by_action(self, action: str, limit: int = 100) -> List:
        """Récupère les logs pour une action"""
        pass

    @abstractmethod
    def get_logs_by_date_range(self, start_date: datetime, end_date: datetime) -> List:
        """Récupère les logs dans une période"""
        pass

    @abstractmethod
    def get_recent_logs(self, hours: int = 24) -> List:
        """Récupère les logs récents"""
        pass

    @abstractmethod
    def search_logs(self, query: str, limit: int = 100) -> List:
        """Recherche dans les logs"""
        pass