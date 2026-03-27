from unittest.mock import patch, Mock
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date

User = get_user_model()

class DocumentControllerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass",
            nin="123456789012",
            nom="Samba",
            prenom="Ismael"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('document')

    def _get_mock_doc_data(self):
        """Utilitaire pour générer des données que le Serializer peut lire"""
        return {
            'id': 1,
            'type': 'CNI',
            'numero': '12345',
            'fichier_url': '/media/documents/test.pdf',
            'date_emission': date(2020, 1, 1),
            'date_expiration': date(2030, 1, 1),
            'statut': 'EN_ATTENTE',
            'created_at': timezone.now(),
            'updated_at': timezone.now()
        }

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_document_service')
    def test_upload_document_success(self, mock_get_service):
        mock_service = Mock()
        # Le service renvoie les données brutes après création
        mock_service.upload_document.return_value = self._get_mock_doc_data()
        mock_get_service.return_value = mock_service

        fake_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        data = {
            'type': 'CNI',
            'numero': '12345',
            'date_emission': '2020-01-01',
            'date_expiration': '2030-01-01',
            'fichier': fake_file
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['type'], 'CNI')

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_document_service')
    def test_upload_document_invalid_type(self, mock_get_service):
        mock_service = Mock()
        # On ne mocke pas d'exception ici car le Serializer valide AVANT le service
        mock_get_service.return_value = mock_service

        data = {
            'type': 'INVALID_TYPE', 
            'numero': '12345',
            'date_emission': '2020-01-01'
        }
        response = self.client.post(self.url, data, format='multipart')
        
        # Le DocumentUploadSerializer va lever une erreur de validation (400)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data) # DRF met l'erreur dans la clé du champ

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_document_service')
    def test_list_documents_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.list_documents.return_value = [self._get_mock_doc_data()]
        mock_get_service.return_value = mock_service

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero'], '12345')

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_document_service')
    def test_get_document_detail_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.get_document.return_value = self._get_mock_doc_data()
        mock_get_service.return_value = mock_service

        response = self.client.get(self.url, {'id': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['fichier_url'], '/media/documents/test.pdf')

    @patch('src.apps.api.providers.citoyen_provider.CitoyenProvider.get_document_service')
    def test_delete_document_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.delete_document.return_value = True
        mock_get_service.return_value = mock_service

        response = self.client.delete(f"{self.url}?id=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Document supprimé')