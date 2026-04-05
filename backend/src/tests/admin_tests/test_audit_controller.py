from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

class AuditControllerTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="adminpass",
            nin="111", nom="Admin", prenom="Super", role="ADMIN"
        )
        self.agent = User.objects.create_user(
            email="agent@example.com", password="agentpass",
            nin="222", nom="Agent", prenom="User", role="AGENT"
        )
        self.regular = User.objects.create_user(
            email="user@example.com", password="userpass",
            nin="333", nom="User", prenom="Regular", role="CITOYEN"
        )
        self.url = reverse('admin_audit')

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_audit_service')
    def test_get_logs_as_admin_success(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        mock_service.get_recent.return_value = [
            {'id': 1, 'user_id': 1, 'user_email': 'admin@example.com', 'action': 'LOGIN',
             'entity_type': 'User', 'entity_id': '1', 'old_data': None, 'new_data': None,
             'ip_address': '127.0.0.1', 'user_agent': 'test', 'created_at': datetime.now().isoformat()}
        ]
        mock_get_service.return_value = mock_service

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['action'], 'LOGIN')

    def test_get_logs_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_audit_service')
    def test_filter_by_action(self, mock_get_service):
        self.client.force_authenticate(user=self.admin)
        mock_service = Mock()
        mock_service.get_by_action.return_value = []
        mock_get_service.return_value = mock_service

        response = self.client.get(self.url, {'action': 'LOGIN'})
        self.assertEqual(response.status_code, 200)
        mock_service.get_by_action.assert_called_once_with('LOGIN', 100)