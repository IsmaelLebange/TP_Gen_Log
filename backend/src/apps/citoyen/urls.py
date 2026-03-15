from django.urls import path
from .controllers import enrollment_controller, biometric_controller, document_controller, credential_controller
from .routes import enrollment_route

app_name = 'citoyen'

urlpatterns = [
    path('enroll/', enrollment_route, name='enroll'),
    path('biometric/', biometric_controller.verify_biometric, name='verify_biometric'),
    path('document/', document_controller.upload_document, name='upload_document'),
    path('credential/', credential_controller.issue_credential, name='issue_credential'),
]