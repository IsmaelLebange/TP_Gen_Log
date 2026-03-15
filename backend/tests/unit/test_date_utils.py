# test_date_utils.py - Tests unitaires pour les utilitaires de dates

import unittest
from datetime import date, datetime
from src.shared.utils.date_utils import (
    calculate_age, is_adult, format_date_for_display,
    parse_date_from_string, get_date_range_for_month
)

class TestDateUtils(unittest.TestCase):
    """Tests unitaires pour date_utils"""

    def test_calculate_age(self):
        """Test du calcul d'âge"""
        # Test âge normal
        birth_date = date(1990, 5, 15)
        reference_date = date(2023, 5, 15)
        self.assertEqual(calculate_age(birth_date, reference_date), 33)

        # Test anniversaire pas encore passé
        reference_date = date(2023, 5, 14)
        self.assertEqual(calculate_age(birth_date, reference_date), 32)

        # Test âge actuel (sans référence)
        today = date.today()
        birth_year = today.year - 25
        birth_date = date(birth_year, today.month, today.day)
        self.assertEqual(calculate_age(birth_date), 25)

    def test_is_adult(self):
        """Test de vérification de majorité"""
        # Majeur
        adult_birth = date(1990, 1, 1)
        self.assertTrue(is_adult(adult_birth))

        # Mineur
        minor_birth = date(2010, 1, 1)
        self.assertFalse(is_adult(minor_birth))

        # Âge limite
        limit_birth = date.today().year - 18, date.today().month, date.today().day
        if isinstance(limit_birth, tuple):
            limit_birth = date(*limit_birth)
        self.assertTrue(is_adult(limit_birth))

    def test_format_date_for_display(self):
        """Test du formatage de date pour l'affichage"""
        test_date = date(2023, 12, 25)
        self.assertEqual(format_date_for_display(test_date), "25/12/2023")

    def test_parse_date_from_string(self):
        """Test du parsing de date depuis une chaîne"""
        # Date valide
        date_str = "25/12/2023"
        parsed = parse_date_from_string(date_str)
        self.assertEqual(parsed, date(2023, 12, 25))

        # Date invalide
        invalid_date_str = "invalid"
        parsed_invalid = parse_date_from_string(invalid_date_str)
        self.assertIsNone(parsed_invalid)

    def test_get_date_range_for_month(self):
        """Test de récupération de la plage de dates pour un mois"""
        # Mois normal
        start, end = get_date_range_for_month(2023, 5)
        self.assertEqual(start, date(2023, 5, 1))
        self.assertEqual(end, date(2023, 5, 31))

        # Décembre (fin d'année)
        start, end = get_date_range_for_month(2023, 12)
        self.assertEqual(start, date(2023, 12, 1))
        self.assertEqual(end, date(2023, 12, 31))

if __name__ == '__main__':
    unittest.main()