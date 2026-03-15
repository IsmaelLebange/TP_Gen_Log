from django.urls import path
from citoyen.controllers.enrollment_controller import EnrollmentController

urlpatterns = [
    path('as_view', EnrollmentController.as_view(), name='citoyen_enrollment'),
]