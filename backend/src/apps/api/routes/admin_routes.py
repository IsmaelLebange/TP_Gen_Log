# src/apps/api/routes/admin_routes.py
from django.urls import path
from src.apps.api.controllers.admin_controllers.audit_controller import AuditController
from src.apps.api.controllers.admin_controllers.statistics_controller import StatisticsController
from src.apps.api.controllers.admin_controllers.validation_workflow_controller import ValidationWorkflowController

urlpatterns = [
    path('validation/', ValidationWorkflowController.as_view(), name='admin_validation'),
    path('stats/', StatisticsController.as_view(), name='admin_stats'),
    path('audit/', AuditController.as_view(), name='admin_audit'),
]