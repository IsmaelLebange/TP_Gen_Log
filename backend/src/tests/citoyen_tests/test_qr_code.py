from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class QRTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass",
            nin="123456789012",
            nom="Dupont",
            prenom="Jean"
        )
        self.client.force_authenticate(user=self.user)
        # Vérifie que 'citoyen_qr' pointe bien vers QRController ou EnrollmentController.get(?action=qr)
        self.url = reverse('citoyen_qr') 

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_enrollment_service')
    def test_get_qr_code_success(self, mock_get_service):
        # 1. On simule le service
        mock_service = MagicMock()
        # 2. On définit ce que le service doit renvoyer
        mock_service.get_my_qr_code.return_value = {
            'qr_code': "data:image/png;base64,fakebase64"
        }
        mock_get_service.return_value = mock_service

        # 3. Appel de l'API
        response = self.client.get(self.url)

        # 4. Vérifications
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('qr_code', response.data)
        self.assertEqual(response.data['qr_code'], "data:image/png;base64,fakebase64")
        mock_service.get_my_qr_code.assert_called_once()

    def test_get_qr_code_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)