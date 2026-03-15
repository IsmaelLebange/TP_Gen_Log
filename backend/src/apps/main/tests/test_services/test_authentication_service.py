# test_authentication_service.py - Tests pour le service d'authentification

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from src.apps.main.services.authentication_service import AuthenticationService
from src.domain.exceptions.domain_exceptions import AuthenticationException

User = get_user_model()

class TestAuthenticationService(TestCase):
    """Tests pour AuthenticationService"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.service = AuthenticationService()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'nin': '123456789'
        }

    @patch('src.apps.main.services.authentication_service.authenticate')
    def test_authenticate_success(self, mock_authenticate):
        """Test d'authentification réussie"""
        # Arrange
        mock_user = Mock()
        mock_authenticate.return_value = mock_user

        # Act
        result = self.service.authenticate(self.user_data['email'], self.user_data['password'])

        # Assert
        self.assertEqual(result, mock_user)
        mock_authenticate.assert_called_once_with(
            email=self.user_data['email'],
            password=self.user_data['password']
        )

    @patch('src.apps.main.services.authentication_service.authenticate')
    def test_authenticate_failure(self, mock_authenticate):
        """Test d'authentification échouée"""
        # Arrange
        mock_authenticate.return_value = None

        # Act & Assert
        with self.assertRaises(AuthenticationException):
            self.service.authenticate(self.user_data['email'], self.user_data['password'])

    def test_generate_tokens(self):
        """Test de génération de tokens"""
        # Arrange
        user = User.objects.create_user(**self.user_data)

        # Act
        tokens = self.service.generate_tokens(user)

        # Assert
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)
        self.assertIn('token_type', tokens)
        self.assertEqual(tokens['token_type'], 'Bearer')

    def test_refresh_access_token(self):
        """Test de rafraîchissement de token d'accès"""
        # Arrange
        user = User.objects.create_user(**self.user_data)
        tokens = self.service.generate_tokens(user)

        # Act
        new_tokens = self.service.refresh_access_token(tokens['refresh_token'])

        # Assert
        self.assertIn('access_token', new_tokens)
        self.assertIn('token_type', new_tokens)
        self.assertEqual(new_tokens['token_type'], 'Bearer')

    def test_register_user_success(self):
        """Test que l'inscription crée un utilisateur et renvoie des tokens"""
        result = self.service.register(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            nin=self.user_data['nin'],
        )

        self.assertIn('access_token', result)
        self.assertIn('refresh_token', result)
        self.assertIn('user', result)
        self.assertEqual(result['user']['email'], self.user_data['email'])
        self.assertEqual(result['user']['nin'], self.user_data['nin'])