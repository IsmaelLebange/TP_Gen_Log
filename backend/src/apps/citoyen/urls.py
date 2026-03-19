from django.urls import include, path
from src.apps.citoyen.api.controllers import enrollment_controller, biometric_controller, document_controller, credential_controller
from src.apps.citoyen.api.routes import enrollment_route

app_name = 'citoyen'

urlpatterns = [
    path('enroll/', include(enrollment_route)),
    path('biometric/', include('src.apps.citoyen.api.routes.biometric_routes')),
    
]