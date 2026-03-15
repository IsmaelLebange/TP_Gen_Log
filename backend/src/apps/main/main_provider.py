# src/apps/main/providers.py
import os
from django.utils.module_loading import import_string

class ServiceProvider:
    @staticmethod
    def get_auth_service():
        # On lit le chemin de la classe depuis les variables d'environnement (.env)
        # Exemple: AUTH_SERVICE_PATH=src.apps.main.services.authentication_service.AuthenticationService
        service_path = os.getenv(
            'AUTH_SERVICE_PATH', 
            'src.apps.main.services.authentication_service.AuthenticationService'
        )
        service_class = import_string(service_path)
        return service_class()