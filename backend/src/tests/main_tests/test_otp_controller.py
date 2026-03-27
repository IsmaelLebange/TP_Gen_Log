import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass",
        nin="123456789012",
        nom="Dupont",
        prenom="Jean",
        telephone="+243123456789"
    )

@pytest.mark.django_db
class TestOTPController:

    @patch('src.apps.api.providers.main_provider.MainProvider.get_otp_service')
    def test_request_otp_success(self, mock_get_service, api_client, user):
        # Mock du service
        mock_service = mock_get_service.return_value
        mock_service.request_otp.return_value = {
            'success': True,
            'message': 'Code envoyé',
            'expires_in': 5
        }

        url = reverse('otp')  # nom de la route défini dans main_routes
        data = {'email': user.email, 'purpose': 'LOGIN'}
        response = api_client.post(f"{url}?action=request", data, format='json')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'expires_in' in response.data
        mock_service.request_otp.assert_called_once_with(user.email, 'LOGIN')

    @patch('src.apps.api.providers.main_provider.MainProvider.get_otp_service')
    def test_request_otp_user_not_found(self, mock_get_service, api_client):
        mock_service = mock_get_service.return_value
        mock_service.request_otp.return_value = {
            'success': False,
            'message': 'Utilisateur non trouvé'
        }

        url = reverse('otp')
        data = {'email': 'unknown@example.com', 'purpose': 'LOGIN'}
        response = api_client.post(f"{url}?action=request", data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'Utilisateur non trouvé' in response.data['message']

    @patch('src.apps.api.providers.main_provider.MainProvider.get_otp_service')
    def test_request_otp_invalid_purpose(self, mock_get_service, api_client, user):
        # Le service peut renvoyer une erreur pour un purpose invalide (on mock)
        mock_service = mock_get_service.return_value
        mock_service.request_otp.return_value = {
            'success': False,
            'message': 'Purpose invalide'
        }

        url = reverse('otp')
        data = {'email': user.email, 'purpose': 'INVALID'}
        response = api_client.post(f"{url}?action=request", data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'invalide' in response.data['message'].lower()

    @patch('src.apps.api.providers.main_provider.MainProvider.get_otp_service')
    def test_verify_otp_success(self, mock_get_service, api_client, user):
        mock_service = mock_get_service.return_value
        mock_service.verify_otp.return_value = {
            'success': True,
            'message': 'Code vérifié',
            'user_id': user.id,
            'email': user.email
        }

        url = reverse('otp')
        data = {'email': user.email, 'code': '123456', 'purpose': 'LOGIN'}
        response = api_client.post(f"{url}?action=verify", data, format='json')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['user_id'] == user.id
        mock_service.verify_otp.assert_called_once_with(user.email, '123456', 'LOGIN')

    @patch('src.apps.api.providers.main_provider.MainProvider.get_otp_service')
    def test_verify_otp_invalid_code(self, mock_get_service, api_client, user):
        mock_service = mock_get_service.return_value
        mock_service.verify_otp.return_value = {
            'success': False,
            'message': 'Code invalide ou expiré'
        }

        url = reverse('otp')
        data = {'email': user.email, 'code': '000000', 'purpose': 'LOGIN'}
        response = api_client.post(f"{url}?action=verify", data, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'invalide' in response.data['message'].lower()

    def test_verify_otp_missing_action(self, api_client):
        url = reverse('otp')
        data = {'email': 'test@example.com', 'code': '123456'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
        assert 'Action non valide' in response.data['error']