from django.urls import path
from src.apps.citoyen.api.controllers.enrollment_controller import EnrollmentController



urlpatterns = [
    path('as_view', EnrollmentController.as_view(), name='enrollment'),
]