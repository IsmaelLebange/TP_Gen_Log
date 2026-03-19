from django.urls import path
from src.apps.main.api.controllers.token_controller import RefreshTokenController, VerifyTokenController   # 👈 importer les nouveaux

urlpatterns = [
    path('refresh/', RefreshTokenController.as_view(), name='token_refresh'),
    path('verify/', VerifyTokenController.as_view(), name='token_verify'),
]