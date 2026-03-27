#!/usr/bin/env python
import os
import sys
import django
import re

# Configuration du chemin pour atteindre la racine 'backend'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Utilise ton module de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Import des modèles depuis src.models
from src.models import Province, Territoire, SecteurChefferie

def clean_name(name):
    """Nettoie les résidus de numéros de page ou compteurs en fin de ligne"""
    return re.sub(r'\s+\d+$', '', name).strip()

def main():
    # Chemin vers ton fichier texte
    file_path = os.path.join(os.path.dirname(__file__), 'divisions.txt')
    
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} est introuvable.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_province = None
    current_territoire = None

    # Patterns Regex
    province_pattern = re.compile(r'^(\d{1,2})\s+([A-Z][a-zA-Z\s\-]+)$')
    territoire_pattern = re.compile(r'^\d+\s+(\d{4,5})\s+Territoire\s+de\s+(.+)$')
    sect_cheff_pattern = re.compile(r'^(\d{7,8})\s+(Secteur|Chefferie)\s+de\s+(.+)$')

    print("--- Début de l'importation des divisions administratives ---")

    for line in lines:
        line = line.strip()
        if not line or "NIVEAU" in line or "Nbre" in line:
            continue

        # 1. PROVINCE
        m_prov = province_pattern.match(line)
        if m_prov:
            p_code, p_nom = m_prov.groups()
            current_province, _ = Province.objects.get_or_create(
                code=p_code, 
                defaults={'nom': p_nom.strip()}
            )
            print(f"📍 Province : {p_nom.strip()}")
            continue

        # 2. TERRITOIRE
        m_terr = territoire_pattern.match(line)
        if m_terr and current_province:
            t_code, t_nom = m_terr.groups()
            t_nom = clean_name(t_nom)
            current_territoire, _ = Territoire.objects.get_or_create(
                code=t_code,
                province=current_province,
                defaults={'nom': t_nom}
            )
            print(f"  📂 Territoire : {t_nom}")
            continue

        # 3. SECTEUR / CHEFFERIE
        m_sect = sect_cheff_pattern.match(line)
        if m_sect and current_territoire:
            s_code, s_type, s_nom = m_sect.groups()
            s_nom = clean_name(s_nom)
            SecteurChefferie.objects.update_or_create(
                code=s_code,
                defaults={
                    'nom': s_nom,
                    'territoire': current_territoire,
                    'type': s_type.upper()
                }
            )

    print("--- Importation terminée avec succès ! ---")

if __name__ == '__main__':
    main()