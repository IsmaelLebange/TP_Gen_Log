from unittest.mock import patch, Mock
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, datetime
from django.utils import timezone

from src.domain.exceptions.validation_exceptions import (
    DocumentNotFoundError,
    InvalidDocumentStatusError,
    RejectCommentRequiredError
)

User = get_user_model()

class ValidationWorkflowControllerTest(APITestCase):

    def setUp(self):
        # Créer un utilisateur admin
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            nin="999999999999",
            nom="Admin",
            prenom="Super",
            role="ADMIN"
        )
        self.agent = User.objects.create_user(
            email="agent@example.com",
            password="agentpass",
            nin="888888888888",
            nom="Agent",
            prenom="User",
            role="AGENT"
        )
        self.regular = User.objects.create_user(
            email="user@example.com",
            password="userpass",
            nin="777777777777",
            nom="User",
            prenom="Regular",
            role="CITOYEN"
        )
        self.url = reverse('admin_validation')  # nom défini dans admin_routes

    def _get_mock_doc_data(self, statut='EN_ATTENTE', doc_id=1, user_id=1):
        """Retourne un dictionnaire représentant un document, identique à celui du serializer."""
        return {
            'id': doc_id,
            'user_id': user_id,
            'type': 'CNI',
            'numero': '12345',
            'fichier_url': '/media/documents/test.pdf',
            'date_emission': date(2020, 1, 1),
            'date_expiration': date(2030, 1, 1),
            'statut': statut,
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
            'valide_par_id': None,
            'date_validation': None,
            'commentaire_rejet': ''
        }

    # --- GET endpoints ---

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_get_pending_documents_success(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        mock_service.get_pending_documents.return_value = [self._get_mock_doc_data()]
        mock_get_service.return_value = mock_service

        response = self.client.get(self.url, {'action': 'pending'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'CNI')
        mock_service.get_pending_documents.assert_called_once()

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_get_documents_by_user_success(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        mock_service.get_documents_by_user.return_value = [self._get_mock_doc_data()]
        mock_get_service.return_value = mock_service

        response = self.client.get(self.url, {'action': 'user', 'user_id': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 1)
        mock_service.get_documents_by_user.assert_called_once_with(1)

    # --- POST validation ---

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_validate_document_success(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        # Le service renvoie le document après validation (statut VALIDE)
        validated_doc = self._get_mock_doc_data(statut='VALIDE')
        validated_doc['valide_par_id'] = self.admin.id
        validated_doc['date_validation'] = timezone.now().isoformat()
        mock_service.validate_document.return_value = validated_doc
        mock_get_service.return_value = mock_service

        response = self.client.post(f"{self.url}?action=validate&doc_id=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'VALIDE')
        self.assertEqual(response.data['valide_par_id'], self.admin.id)
        mock_service.validate_document.assert_called_once_with(1, self.admin.id)

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_validate_document_not_found(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        mock_service.validate_document.side_effect = DocumentNotFoundError("Document 999 introuvable")
        mock_get_service.return_value = mock_service

        response = self.client.post(f"{self.url}?action=validate&doc_id=999")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('introuvable', response.data['error'])

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_validate_document_invalid_status(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        mock_service.validate_document.side_effect = InvalidDocumentStatusError("Document déjà validé")
        mock_get_service.return_value = mock_service

        response = self.client.post(f"{self.url}?action=validate&doc_id=1")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('déjà validé', response.data['error'])

    # --- POST rejet ---

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_reject_document_success(self, mock_get_service):
        self.client.force_authenticate(user=self.agent)
        mock_service = Mock()
        rejected_doc = self._get_mock_doc_data(statut='REJETE')
        rejected_doc['valide_par_id'] = self.agent.id
        rejected_doc['date_validation'] = timezone.now().isoformat()
        rejected_doc['commentaire_rejet'] = 'Document non conforme'
        mock_service.reject_document.return_value = rejected_doc
        mock_get_service.return_value = mock_service

        data = {'commentaire': 'Document non conforme'}
        response = self.client.post(f"{self.url}?action=reject&doc_id=1", data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'REJETE')
        self.assertEqual(response.data['commentaire_rejet'], 'Document non conforme')
        mock_service.reject_document.assert_called_once_with(1, self.agent.id, 'Document non conforme')

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_reject_document_missing_comment(self, mock_get_service):
        self.client.force_authenticate(user=self.agent)
        # Le service n'est même pas appelé car le serializer détecte d'abord l'absence du champ
        mock_get_service.return_value = Mock()  # pas besoin de mock précis

        response = self.client.post(f"{self.url}?action=reject&doc_id=1", {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('commentaire', response.data)  # DRF renvoie une erreur sur le champ commentaire

    # --- Permissions ---

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_validate_document_forbidden_regular_user(self, mock_get_service):
        self.client.force_authenticate(user=self.regular)
        response = self.client.post(f"{self.url}?action=validate&doc_id=1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_get_service.assert_not_called()

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_validation_workflow_service')
    def test_reject_document_forbidden_regular_user(self, mock_get_service):
        self.client.force_authenticate(user=self.regular)
        data = {'commentaire': 'test'}
        response = self.client.post(f"{self.url}?action=reject&doc_id=1", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_get_service.assert_not_called()

    # --- Cas supplémentaires : utilisateur non authentifié ---

    def test_unauthenticated_access(self):
        """Un utilisateur non connecté ne peut pas accéder à l'endpoint."""
        response = self.client.get(self.url, {'action': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)