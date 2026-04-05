from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from src.domain.exceptions.domain_exceptions import AuthenticationException

User = get_user_model()

class CredentialControllerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="oldpass123",
            nin="123456789012",
            nom="Dupont",
            prenom="Jean"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('credential')

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_credential_service')
    def test_change_password_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.change_password.return_value = {"success": True, "message": "Mot de passe modifié"}
        mock_get_service.return_value = mock_service

        data = {"old_password": "oldpass123", "new_password": "newpass123"}
        response = self.client.post(f"{self.url}?action=change_password", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_credential_service')
    def test_change_password_wrong_old(self, mock_get_service):
        mock_service = Mock()
        mock_service.change_password.side_effect = AuthenticationException("Ancien mot de passe incorrect")
        mock_get_service.return_value = mock_service

        data = {"old_password": "wrong", "new_password": "newpass123"}
        response = self.client.post(f"{self.url}?action=change_password", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("incorrect", response.data['error'])

class PasswordResetControllerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="oldpass123",
            nin="123456789012",
            nom="Dupont",
            prenom="Jean"
        )
        self.url = reverse('password_reset')

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_credential_service')
    def test_reset_request_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.reset_password_request.return_value = {"success": True, "message": "Code envoyé"}
        mock_get_service.return_value = mock_service

        data = {"email": "test@example.com"}
        response = self.client.post(f"{self.url}?action=request", data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_credential_service')
    def test_reset_confirm_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.reset_password_confirm.return_value = {"success": True, "message": "Mot de passe réinitialisé"}
        mock_get_service.return_value = mock_service

        data = {"email": "test@example.com", "otp": "123456", "new_password": "newpass"}
        response = self.client.post(f"{self.url}?action=confirm", data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])