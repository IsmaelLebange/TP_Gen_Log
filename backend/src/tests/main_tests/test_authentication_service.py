import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from src.apps.services.main_services.authentication_service import AuthenticationService
from src.domain.exceptions.domain_exceptions import AuthenticationException

User = get_user_model()

class TestAuthenticationService(TestCase):
    """Tests pour AuthenticationService (Architecture Propre)"""

    def setUp(self):
        self.service = AuthenticationService()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'prenom': 'Ismael',
            'nom': 'Samba',
            'nin': '123456789',
            'date_naissance': '2000-01-01'
        }

    # CRITIQUE : On patche là où authenticate est UTILISÉ dans ton service
    @patch('src.apps.services.main_services.authentication_service.authenticate')
    def test_login_success(self, mock_authenticate):
        """Test du login avec succès"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.is_active = True
        mock_authenticate.return_value = mock_user

        # Act
        result = self.service.login(self.user_data['email'], self.user_data['password'])

        # Assert
        self.assertIn('access_token', result)
        self.assertIn('user', result)
        mock_authenticate.assert_called_once()

    @patch('src.apps.services.main_services.authentication_service.authenticate')
    def test_login_failure(self, mock_authenticate):
        """Test d'échec de connexion (Identifiants invalides)"""
        # Arrange
        mock_authenticate.return_value = None

        # Act & Assert
        with self.assertRaises(AuthenticationException):
            self.service.login(self.user_data['email'], self.user_data['password'])

    def test_register_user_success(self):
        """Test d'inscription avec création d'utilisateur"""
        # Act
        result = self.service.register(
            email=self.user_data['email'],
            password=self.user_data['password'],
            prenom=self.user_data['prenom'],
            nom=self.user_data['nom'],
            nin=self.user_data['nin'],
            date_naissance=self.user_data['date_naissance']
        )

        # Assert
        self.assertIn('access_token', result)
        self.assertEqual(result['user']['email'], self.user_data['email'])
        self.assertEqual(result['user']['nin'], self.user_data['nin'])

    def test_refresh_token_success(self):
        """Test de rafraîchissement du token JWT"""
        # Arrange
        reg_result = self.service.register(**self.user_data)
        refresh_token = reg_result['refresh_token']

        # Act
        new_tokens = self.service.refresh_token(refresh_token)

        # Assert
        self.assertIn('access_token', new_tokens)