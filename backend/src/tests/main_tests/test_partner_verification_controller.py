from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from src.domain.exceptions.domain_exceptions import AuthenticationException
from src.models import Partenaire

User = get_user_model()

class PartnerVerificationControllerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass",
            nin="123456789012",
            nom="Dupont",
            prenom="Jean"
        )
        self.partenaire = Partenaire.objects.create(
            nom="Partenaire Test",
            email="partenaire@example.com",
            token="valid_token_123"
        )
        self.url = reverse('partner_verify')

    @patch('src.apps.api.providers.main_provider.MainProvider.get_partner_verification_service')
    def test_verify_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.verify_by_nin.return_value = {
            'nin': '123456789012',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'postnom': '',
            'date_naissance': None,
            'lieu_origine': None
        }
        mock_get_service.return_value = mock_service

        data = {'token': 'valid_token_123', 'nin': '123456789012'}
        response = self.client.post(f"{self.url}?action=verify", data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nin'], '123456789012')
        self.assertEqual(response.data['nom'], 'Dupont')
        mock_service.verify_by_nin.assert_called_once_with(token='valid_token_123', nin='123456789012')

    @patch('src.apps.api.providers.main_provider.MainProvider.get_partner_verification_service')
    def test_verify_invalid_token(self, mock_get_service):
        mock_service = Mock()
        mock_service.verify_by_nin.side_effect = AuthenticationException("Token partenaire invalide")
        mock_get_service.return_value = mock_service

        data = {'token': 'invalid', 'nin': '123456789012'}
        response = self.client.post(f"{self.url}?action=verify", data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('invalide', response.data['error'])