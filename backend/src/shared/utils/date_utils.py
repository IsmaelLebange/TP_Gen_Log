# date_utils.py - Utilitaires pour les dates

from datetime import datetime, date, timedelta
from typing import Optional, Tuple

def calculate_age(birth_date: date, reference_date: Optional[date] = None) -> int:
    """Calcule l'âge à partir de la date de naissance"""
    if reference_date is None:
        reference_date = date.today()

    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def is_adult(birth_date: date, adult_age: int = 18) -> bool:
    """Vérifie si la personne est adulte"""
    return calculate_age(birth_date) >= adult_age

def format_date_for_display(date_obj: date) -> str:
    """Formate une date pour l'affichage"""
    return date_obj.strftime("%d/%m/%Y")

def parse_date_from_string(date_str: str) -> Optional[date]:
    """Parse une date depuis une chaîne (format DD/MM/YYYY)"""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        return None

def get_date_range_for_month(year: int, month: int) -> Tuple[date, date]:
    """Retourne les dates de début et fin pour un mois donné"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    return start_date, end_date