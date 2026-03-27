from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from src.models import Province, SecteurChefferie, Territoire

User = get_user_model()

class EnrollmentControllerTest(APITestCase):
    """Tests exhaustifs pour l'enrôlement des citoyens (Architecture N-Tier)"""

    def setUp(self):
        self.province = Province.objects.create(code="22", nom="Kongo Central")
        self.territoire = Territoire.objects.create(
            code="2201", 
            nom="Kasangulu", 
            province=self.province
        )
        self.secteur = SecteurChefferie.objects.create(
            code="2201401", 
            nom="Kasangulu", # Ton script importe souvent le chef-lieu avec le même nom
            territoire=self.territoire,
            type="SECTEUR"
        )
        self.enroll_url = reverse('enrollment')
        self.valid_payload = {
            "email": "ismael.samba@unikin.cd",
            "mot_de_passe": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "nom": "Samba",
            "postnom": "Lebange",
            "prenom": "Ismael",
            "nin": "123456789012", # Format correct 12 chiffres
            "date_naissance": "2000-01-01",
            "telephone": "+243810000000",
            "province_origine": "Kongo Central",
            "territoire_origine": "Kasangulu",
            "secteur_origine": "Kasangulu", # Le repo doit trouver le code 2201401
            "nom_du_pere": "Jean Samba",
            "nom_de_la_mere": "Marie Lebange",
            "sexe": "M"
        }

    def test_enrollment_success(self):
        # On n'envoie plus de NIN, le système le déduit
        payload = self.valid_payload.copy()
        del payload['nin'] 
    
        response = self.client.post(self.enroll_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
        # On vérifie que le NIN généré en base est correct
        user = User.objects.get(email=payload['email'])
        self.assertEqual(len(user.nin), 16) 
        self.assertTrue(user.nin.startswith("2201")) # Exemple pour Kongo Central

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