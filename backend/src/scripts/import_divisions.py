#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import re
from pathlib import Path

# Ajoute le chemin du projet (backend) dans sys.path
# parents[2] remonte de src/generationScripts/ → src/ → backend/
project_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_path))

# Définit le module de settings (adapté à ta structure)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from src.models import Province, Territoire, SecteurChefferie

# ... reste du code (clean_name, import_divisions, etc.)


def clean_name(name: str) -> str:
    # Supprime les espaces multiples et nettoie
    return re.sub(r'\s+', ' ', name).strip()

def import_divisions(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for province_nom, province_data in data.items():
        province_code = province_data['code']
        province, created = Province.objects.get_or_create(
            code=province_code,
            defaults={'nom': clean_name(province_nom)}
        )
        print(f"{'✅ Créée' if created else '⚠️ Déjà existante'} : Province {province.nom} ({province.code})")

        for territoire_nom, territoire_data in province_data.get('territoires', {}).items():
            territoire_code = territoire_data['code']
            territoire, created = Territoire.objects.get_or_create(
                code=territoire_code,
                defaults={'nom': clean_name(territoire_nom), 'province': province}
            )
            print(f"  {'✅ Créé' if created else '⚠️ Déjà existant'} : Territoire {territoire.nom} ({territoire.code})")

            for secteur_nom, secteur_data in territoire_data.get('secteurs', {}).items():
                secteur_code = secteur_data['code']
                type_val = secteur_data['type']
                secteur, created = SecteurChefferie.objects.get_or_create(
                    code=secteur_code,
                    defaults={
                        'nom': clean_name(secteur_nom),
                        'territoire': territoire,
                        'type': type_val
                    }
                )
                if created:
                    print(f"    ✅ Créé : {type_val} {secteur.nom} ({secteur.code})")

    print("🎉 Import terminé.")

if __name__ == '__main__':
    json_file = Path(__file__).parent / 'divisions.json'
    if not json_file.exists():
        print(f"Fichier {json_file} introuvable.")
        sys.exit(1)
    import_divisions(json_file)