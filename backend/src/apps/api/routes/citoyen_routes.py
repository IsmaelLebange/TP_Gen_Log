from django.urls import path
from src.apps.api.controllers.citoyen_controllers.biometric_controller import BiometricController
from src.apps.api.controllers.citoyen_controllers.credential_controller import CredentialController, PasswordResetController, ProfileController
from src.apps.api.controllers.citoyen_controllers.document_controller import DocumentController
from src.apps.api.controllers.citoyen_controllers.enrollment_controller import EnrollmentController, QRController, EnrollmentCompleteController 

# Garde seulement :
urlpatterns = [
    path('biometric/', BiometricController.as_view(), name='biometric-controller'),
    path('enrollment/complete/', EnrollmentCompleteController.as_view(), name='enrollment_complete'),
    path('documents/', DocumentController.as_view(), name='document'),
    path('qr/', QRController.as_view(), name='citoyen_qr'),
    path('credential/', CredentialController.as_view(), name='credential'),
    path('password-reset/', PasswordResetController.as_view(), name='password_reset'),
    path('profile/', ProfileController.as_view(), name='citoyen_profile'),
]