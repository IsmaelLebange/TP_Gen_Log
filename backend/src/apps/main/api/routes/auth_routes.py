from django.urls import path
# Importe les classes directement depuis ton fichier de contrôleurs
from src.apps.main.api.controllers.authentication_controller import LoginController, RegisterController, LogoutController

urlpatterns = [
    # Utilise .as_view() pour transformer la classe en vue Django
    path('login/', LoginController.as_view(), name='login'),
    path('register/', RegisterController.as_view(), name='register'),
    path('logout/', LogoutController.as_view(), name='logout'),
]