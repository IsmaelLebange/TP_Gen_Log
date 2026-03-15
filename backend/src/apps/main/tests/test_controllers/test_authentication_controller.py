import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class AuthenticationControllerTest(APITestCase):
    """
    Tests fonctionnels pour le contrôleur d'authentification.
    On teste ici le cycle : Request -> Controller -> Service -> Response.
    """

    def setUp(self):
        # On crée un utilisateur de test en base
        self.email = "ismael@test.com"
        self.password = "password123"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Ismael",
            last_name="Samba",
            nin="NIN123456"
        )
        
        # Noms des routes (à adapter selon tes fichiers urls.py)
        # Si tu as un namespace 'main', utilise 'main:login'
        self.login_url = reverse('main:login') 
        self.register_url = reverse('main:register')

    def test_login_success(self):
        """Teste qu'un utilisateur valide peut se connecter"""
        payload = {
            "email": self.email,
            "password": self.password
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data) # Vérifie si le token est présent
        self.assertIn('refresh_token', response.data)

    def test_login_invalid_password(self):
        """Teste qu'un mauvais mot de passe est refusé"""
        payload = {
            "email": self.email,
            "password": "wrong_password"
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_success(self):
        """Teste la création d'un nouveau compte via le contrôleur"""
        payload = {
            "email": "nouveau@test.com",
            "password": "strong_password123",
            "password_confirm": "strong_password123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "nin": "NIN999888"
        }
        response = self.client.post(self.register_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], payload['email'])

    def test_register_passwords_dont_match(self):
        """Teste que l'inscription échoue si les mots de passe sont différents"""
        payload = {
            "email": "error@test.com",
            "password": "pass1",
            "password_confirm": "pass2",
            "first_name": "Test",
            "last_name": "User",
            "nin": "NIN000"
        }
        response = self.client.post(self.register_url, payload, format='json')
        
        # Le Serializer/DTO doit rejeter ça en 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)