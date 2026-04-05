# src/apps/api/providers/admin_provider.py
from src.apps.repositories.admin_repositories.audit_repository import AuditRepository
from src.apps.repositories.citoyen_repositories.document_repository import DocumentRepository
from src.apps.repositories.main_repositories.user_repository import UserRepository
from src.apps.services.admin_services.audit_service import AuditService
from src.apps.services.admin_services.statistics_service import StatisticsService
from src.apps.services.admin_services.validation_workflow_service import ValidationWorkflowService

class AdminProvider:
    @staticmethod
    def get_document_repository():
        return DocumentRepository()

    @staticmethod
    def get_user_repository():
        return UserRepository()

    @staticmethod
    def get_validation_workflow_service():
        return ValidationWorkflowService(
            document_repo=AdminProvider.get_document_repository(),
            user_repo=AdminProvider.get_user_repository()
        )
    
    @staticmethod
    def get_statistics_service():
        return StatisticsService()
    
    @staticmethod
    def get_audit_repository():
        return AuditRepository()

    @staticmethod
    def get_audit_service():
        return AuditService(repo=AdminProvider.get_audit_repository())