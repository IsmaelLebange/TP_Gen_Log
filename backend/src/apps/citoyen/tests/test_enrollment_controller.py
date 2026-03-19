from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class EnrollmentControllerTest(APITestCase):
    """Tests exhaustifs pour l'enrôlement des citoyens (Architecture N-Tier)"""

    def setUp(self):
        self.enroll_url = reverse('citoyen:enrollment')
        self.valid_payload = {
            "email": "ismael.samba@unikin.cd",
            "password": "SecurePassword123!",
            "nom": "Samba",
            "postnom": "Lebange",
            "prenom": "Ismael",
            "nin": "123456789012", # Format correct 12 chiffres
            "date_naissance": "2000-01-01",
            "telephone": "+243810000000"
        }

    # --- 1. TESTS DE SUCCÈS ---
    def test_enrollment_success(self):
        """Vérifie que l'enrôlement fonctionne avec des données valides"""
        response = self.client.post(self.enroll_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nin'], self.valid_payload['nin'])

    # --- 2. TESTS DE DOUBLONS (Règles Métier) ---
    def test_enrollment_duplicate_nin(self):
        """Vérifie que le service rejette un NIN déjà utilisé"""
        self.client.post(self.enroll_url, self.valid_payload, format='json')
        response = self.client.post(self.enroll_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_duplicate_email(self):
        """Vérifie que le service rejette un Email déjà utilisé"""
        self.client.post(self.enroll_url, self.valid_payload, format='json')
        # Nouveau payload avec même email mais NIN différent
        payload = self.valid_payload.copy()
        payload['nin'] = "000000000000"
        response = self.client.post(self.enroll_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 3. TESTS DE VALIDATION (Value Objects & Formats) ---
    def test_enrollment_invalid_nin_format(self):
        """Vérifie que le Value Object NIN bloque les mauvais formats (ex: trop court)"""
        payload = self.valid_payload.copy()
        payload['nin'] = "123" # Invalide
        response = self.client.post(self.enroll_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_invalid_email_format(self):
        """Vérifie que le Value Object Email bloque les adresses mal formées"""
        payload = self.valid_payload.copy()
        payload['email'] = "ismael-sans-arobase.cd"
        response = self.client.post(self.enroll_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 4. TESTS DE STRUCTURE (Contrôleur) ---
    def test_enrollment_missing_required_fields(self):
        """Vérifie que l'absence de champs obligatoires renvoie une 400"""
        payload = {"nom": "Samba"} # Manque prenom, nin, email, etc.
        response = self.client.post(self.enroll_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_invalid_date_format(self):
        """Vérifie que le contrôleur rejette une date mal formatée"""
        payload = self.valid_payload.copy()
        payload['date_naissance'] = "15/05/1998" # Format FR au lieu de ISO YYYY-MM-DD
        response = self.client.post(self.enroll_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)