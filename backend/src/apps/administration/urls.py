from django.urls import path
from .controllers import validation_workflow_controller, statistics_controller

app_name = 'admin'

urlpatterns = [
    path('validate/', validation_workflow_controller.validate, name='validate'),
    path('stats/', statistics_controller.get_stats, name='get_stats'),
]