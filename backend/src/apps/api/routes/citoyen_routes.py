from django.urls import path
from src.apps.api.controllers.citoyen_controllers.biometric_controller import BiometricController
from src.apps.api.controllers.citoyen_controllers.document_controller import DocumentController
from src.apps.api.controllers.citoyen_controllers.enrollment_controller import EnrollmentController

urlpatterns = [
    path('biometric/', BiometricController.as_view(), name='biometric-controller'),
    path('biometric/<str:action>/', BiometricController.as_view(), name='biometric_action'),
    path('enrollment/as_view', EnrollmentController.as_view(), name='enrollment'),
    path('documents/', DocumentController.as_view(), name='document'),
]