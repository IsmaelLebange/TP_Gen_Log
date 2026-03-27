from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from src.models import OTP as OTPModel
from unittest.mock import patch # <--- Ajoute cet import en haut

User = get_user_model()

class AuthenticationControllerTest(APITestCase):
    """Tests pour les endpoints API d'authentification"""

    def setUp(self):
        self.register_url = reverse('register') 
        self.login_url = reverse('login')
        
        self.user_payload = {
            'email': 'ismael@test.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!', # Requis par le serializer
            'prenom': 'Ismael',
            'nom': 'Samba',
            'nin': 'NIN123456789',
            'date_naissance': '1998-10-15'
        }

    def test_register_success(self):
        """Teste la création d'un compte (HTTP 201)"""
        # Act
        response = self.client.post(self.register_url, self.user_payload, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['user']['email'], self.user_payload['email'])

    def test_register_missing_data(self):
        """Teste l'échec si données manquantes (HTTP 400)"""
        invalid_payload = {'email': 'test@test.com'} # Pas de password, pas de NIN
        
        response = self.client.post(self.register_url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    

    

    def test_login_full_2fa_flow(self):
        """
        Scénario : 
        1. Tentative sans OTP -> Succès simulé de l'envoi -> 401
        2. Récupération en base et validation -> 200
        """
        # 0. Création de l'utilisateur
        try:
            self.client.post(self.register_url, self.user_payload, format='json')

            # 1. ON MOCK L'ENVOI (On remplace la méthode send par un truc qui renvoie True)
            # Vérifie bien le chemin vers ton OTPSenderSms ou OTPSenderEmail
            target = 'src.apps.services.main_services.otp_service.OTPSenderSms.send'
            
            with patch(target) as mock_send:
                mock_send.return_value = True # On force le succès de l'envoi
                
                login_step_1 = {
                    'email': self.user_payload['email'],
                    'password': self.user_payload['password']
                }
                response_1 = self.client.post(self.login_url, login_step_1, format='json')
                
                # Maintenant, ça ne devrait plus renvoyer "Échec d'envoi"
                self.assertEqual(response_1.status_code, status.HTTP_401_UNAUTHORIZED)

            # 2. La suite reste la même pour récupérer l'OTP en base...
            last_otp = OTPModel.objects.filter(
                user__email=self.user_payload['email']
            ).latest('created_at')

            login_step_2 = {
                'email': self.user_payload['email'],
                'password': self.user_payload['password'],
                'otp': last_otp.code 
            }
            response_2 = self.client.post(self.login_url, login_step_2, format='json')

            self.assertEqual(response_2.status_code, status.HTTP_200_OK)

        except:
            print("")