from django.urls import path
from src.apps.citoyen.api.controllers.biometric_controller import BiometricController

urlpatterns = [
    path('/', BiometricController.as_view(), name='biometric'),
    path('<str:action>/', BiometricController.as_view(), name='biometric_action'),
]