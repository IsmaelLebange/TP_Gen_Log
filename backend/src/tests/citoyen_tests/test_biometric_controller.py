import json
from unittest.mock import MagicMock, patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from src.domain.value_objects.biometrics import BiometricType

User = get_user_model()

class BiometricControllerTest(APITestCase):
    """Tests pour le contrôleur biométrique (Enroll, Verify, Status, Delete)"""

    def setUp(self):
        self.client = APIClient()
        # 1. Création d'un utilisateur de test
        self.user = User.objects.create_user(
            email="test.biometry@unikin.cd",
            password="SecurePassword123!",
            nom="Samba",
            prenom="Ismael",
            nin="1234567890123456"
        )
        # 2. Authentification (Obligatoire car permission_classes = [IsAuthenticated])
        self.client.force_authenticate(user=self.user)
        
        self.url = reverse('biometric-controller') # Assure-toi que le name dans urls.py est celui-ci
        
        # Image factice en Base64 (Data URI)
        self.valid_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_biometric_service')
    def test_enroll_biometric_success(self, mock_get_service):
        """Vérifie l'enrôlement réussi d'une donnée biométrique"""
        # Mock du retour du service
        mock_service = MagicMock()
        mock_service.enroll.return_value = {
            'success': True,
            'message': 'Enrôlement réussi',
            'data': {'id': 1, 'type': 'face'}
        }
        mock_get_service.return_value = mock_service

        payload = {
            "type": "face",
            "image": self.valid_image
        }
        
        # Action : POST avec action=enroll
        response = self.client.post(f"{self.url}?action=enroll", payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        mock_service.enroll.assert_called_once()

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_biometric_service')
    def test_verify_biometric_match(self, mock_get_service):
        """Vérifie la correspondance biométrique (Match)"""
        mock_service = MagicMock()
        mock_service.verify.return_value = {
            'success': True,
            'data': {'matched': True, 'confidence': 95.5}
        }
        mock_get_service.return_value = mock_service

        payload = {"image": self.valid_image}
        
        # Action : POST avec action=verify
        response = self.client.post(f"{self.url}?action=verify", payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['matched'])

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_biometric_service')
    def test_get_biometric_status(self, mock_get_service):
        """Vérifie la récupération du statut biométrique"""
        mock_service = MagicMock()
        mock_service.get_status.return_value = {
            'enrolled': True,
            'type': 'face',
            'created_at': '2026-03-25T10:00:00'
        }
        mock_get_service.return_value = mock_service

        # Action : GET avec action=status
        response = self.client.get(f"{self.url}?action=status")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'face')
        self.assertTrue(response.data['enrolled'])

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_biometric_service')
    def test_delete_biometric(self, mock_get_service):
        """Vérifie la suppression des données biométriques"""
        mock_service = MagicMock()
        mock_service.delete.return_value = {
            'success': True, 
            'message': 'Données supprimées avec succès.'
        }
        mock_get_service.return_value = mock_service

        # Action : DELETE
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_invalid_action(self):
        """Vérifie qu'une action inconnue renvoie une 400"""
        response = self.client.post(f"{self.url}?action=dormir", {"data": "..."})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Action non valide')

    def test_enroll_invalid_payload(self):
        """Vérifie la validation du Serializer (type manquant)"""
        payload = {"image": self.valid_image} # Manque 'type'
        response = self.client.post(f"{self.url}?action=enroll", payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)