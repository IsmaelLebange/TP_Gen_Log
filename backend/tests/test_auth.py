import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from src.main.models import User

@pytest.mark.django_db
class TestAuthentication:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            nin='ID123456789',
            nom='Dupont',
            prenom='Jean',
            password='testpass123'
        )
    
    def test_login_success(self):
        """Test connexion réussie"""
        url = '/api/login/'
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        assert response.data['user']['email'] == 'test@example.com'
    
    def test_login_failed_wrong_password(self):
        """Test connexion avec mauvais mot de passe"""
        url = '/api/login/'
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == 401
        assert 'error' in response.data
    
    def test_login_failed_user_not_found(self):
        """Test connexion avec email inexistant"""
        url = '/api/login/'
        data = {
            'email': 'unknown@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == 401
        assert 'error' in response.data
    
    def test_me_authenticated(self):
        """Test endpoint /me avec authentification"""
        # D'abord login pour obtenir le token
        login_url = '/api/login/'
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        token = login_response.data['access_token']
        
        # Puis requête /me avec token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        me_url = '/api/me/'
        response = self.client.get(me_url)
        
        assert response.status_code == 200
        assert response.data['email'] == 'test@example.com'
        assert response.data['nin'] == 'ID123456789'