#!/usr/bin/env python
import os
import sys
import django

# Ajoute le chemin racine du projet (là où se trouve manage.py)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from src.models import User

def reset_password(email='ismaellebange596@gmail.com', new_password='0123456'):
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        print(f"✅ Mot de passe de {email} changé avec succès en '{new_password}'")
    except User.DoesNotExist:
        print(f"❌ Utilisateur avec email {email} non trouvé.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == '__main__':
    email = sys.argv[1] if len(sys.argv) > 1 else 'ismaellebange596@gmail.com'
    reset_password(email)