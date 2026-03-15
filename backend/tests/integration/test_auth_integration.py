# test_auth_integration.py - Tests d'intégration pour l'authentification

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class TestAuthenticationIntegration(APITestCase):
    """Tests d'intégration pour le système d'authentification"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user_data = {
            'email': 'integration@example.com',
            'password': 'integration123',
            'first_name': 'Integration',
            'last_name': 'Test',
            'nin': '987654321'
        }

    def test_complete_authentication_flow(self):
        """Test du flux complet d'authentification"""
        # 1. Créer un utilisateur (simuler l'enrôlement)
        user = User.objects.create_user(**self.user_data)

        # 2. Se connecter
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }

        login_response = self.client.post(
            reverse('auth_login'),
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']

        # 3. Accéder à une ressource protégée
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_response = self.client.get(reverse('auth_me'))

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['email'], self.user_data['email'])

        # 4. Rafraîchir le token
        refresh_data = {'refresh_token': refresh_token}
        refresh_response = self.client.post(
            reverse('auth_refresh'),
            data=json.dumps(refresh_data),
            content_type='application/json'
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_access_token = refresh_response.data['access_token']

        # 5. Vérifier que le nouveau token fonctionne
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        me_response_2 = self.client.get(reverse('auth_me'))

        self.assertEqual(me_response_2.status_code, status.HTTP_200_OK)

    def test_unauthorized_access(self):
        """Test d'accès non autorisé"""
        # Tenter d'accéder à une ressource protégée sans token
        response = self.client.get(reverse('auth_me'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token(self):
        """Test avec un token invalide"""
        # Utiliser un token invalide
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(reverse('auth_me'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)