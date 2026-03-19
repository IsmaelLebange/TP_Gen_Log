# src/apps/main/providers.py
import os
from django.utils.module_loading import import_string

class ServiceProvider:
    @staticmethod
    def get_auth_service():
        service_path = os.getenv(
            'AUTH_SERVICE_PATH', 
            'src.apps.main.services.authentication_service.AuthenticationService'
        )
        try:
            service_class = import_string(service_path)
            return service_class()  # <--- CRUCIAL : On instancie la classe ici !
        except ImportError as e:
            # Si le chemin dans le .env est faux, ça va crash proprement ici
            print(f"Erreur d'import du service : {e}")
            return None