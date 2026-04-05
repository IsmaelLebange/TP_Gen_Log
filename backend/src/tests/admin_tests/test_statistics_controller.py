from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class StatisticsControllerTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            nin="999999999999",
            nom="Admin",
            prenom="Super",
            role="ADMIN"
        )
        self.regular = User.objects.create_user(
            email="user@example.com",
            password="userpass",
            nin="888888888888",
            nom="User",
            prenom="Regular",
            role="CITOYEN"
        )
        self.url = reverse('admin_stats')

    @patch('src.apps.api.providers.admin_provider.AdminProvider.get_statistics_service')
    def test_get_stats_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.get_dashboard_stats.return_value = {
            'total_citoyens': 100,
            'total_citoyens_30d': 10,
            'sexe_repartition': [{'sexe': 'M', 'count': 60}, {'sexe': 'F', 'count': 40}],
            'age_repartition': {'0-18': 20, '19-35': 50, '36-60': 20, '60+': 10},
            'top_provinces': [{'lieu_origine__territoire__province__nom': 'Kinshasa', 'count': 30}],
            'enrollments_by_day': [],
            'documents_status': [{'statut': 'EN_ATTENTE', 'count': 5}],
            'top_validators': [],
            'recent_audits': []
        }
        mock_get_service.return_value = mock_service

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_citoyens'], 100)
        mock_service.get_dashboard_stats.assert_called_once()

    def test_get_stats_forbidden_for_regular_user(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_stats_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)