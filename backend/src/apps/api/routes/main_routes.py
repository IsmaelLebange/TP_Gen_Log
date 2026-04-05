from django.urls import path
# Importe les classes directement depuis ton fichier de contrôleurs
from src.apps.api.controllers.main_controllers.authentication_controller import LoginController, RegisterController, LogoutController
from src.apps.api.controllers.main_controllers.partner_verification_controller import PartnerVerificationController
from src.apps.api.controllers.main_controllers.token_controller import RefreshTokenController,VerifyTokenController

urlpatterns = [
    # Utilise .as_view() pour transformer la classe en vue Django
    path('auth/login/', LoginController.as_view(), name='login'),
    path('auth/register/', RegisterController.as_view(), name='register'),
    path('auth/logout/', LogoutController.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenController.as_view(), name='token_refresh'),
    path('token/verify/', VerifyTokenController.as_view(), name='token_verify'),
    path('verify/', PartnerVerificationController.as_view(), name='partner_verify'),
]
