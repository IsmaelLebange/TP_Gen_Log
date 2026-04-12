#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import random
import string
from datetime import timedelta, date

# Ajout du chemin racine du projet (backend)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

# Import des modèles Django
from src.models import (
    User, Province, Territoire, SecteurChefferie, Adresse,
    Document, BiometricData, Partenaire, AuditLog, OTP
)

from django.core.files.base import ContentFile
from django.utils import timezone
from faker import Faker

fake = Faker('fr_FR')


class NIN:
    """
    Format : code_secteur(7) + jj(2) + mm(2) + aa(2) + sexe(1) + cle(2)
    Le code secteur est normalisé à 7 chiffres (troncature à gauche si >7, padding à gauche si <7)
    """
    def __init__(self, valeur: str):
        if not self._valider_format(valeur):
            raise ValueError(f"Format NIN invalide : {valeur}")
        self.valeur = valeur

    @classmethod
    def generer(cls, code_secteur: str, date_naissance: date, sexe: str) -> 'NIN':
        # Normalisation : 7 chiffres
        code_secteur = str(code_secteur).zfill(7)
        if len(code_secteur) > 7:
            code_secteur = code_secteur[:7]  # tronquer les chiffres en trop

        jour = date_naissance.strftime("%d")
        mois = date_naissance.strftime("%m")
        annee = date_naissance.strftime("%y")
        sexe_lettre = sexe.upper()[0]

        base = f"{code_secteur}{jour}{mois}{annee}{sexe_lettre}"
        total = sum(int(ch) for ch in base if ch.isdigit())
        cle = str(total % 100).zfill(2)

        return cls(f"{base}{cle}")

    @staticmethod
    def _valider_format(valeur: str) -> bool:
        return bool(re.match(r'^\d{7}\d{6}[MF]\d{2}$', valeur))

    def __str__(self):
        return self.valeur


def promote_existing_admin():
    email = "ismaellebange596@gmail.com"
    try:
        user = User.objects.get(email=email)
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        print(f"✅ {email} promu administrateur.")
    except User.DoesNotExist:
        print(f"⚠️ {email} inexistant ")
        


def generate_test_users(total=120):
    provinces = list(Province.objects.all())
    secteurs = list(SecteurChefferie.objects.all())
    if not provinces or not secteurs:
        print("❌ Aucune province ou secteur/chefferie trouvé. Importez d'abord les données géographiques.")
        return

    roles = [User.Role.CITOYEN, User.Role.AGENT, User.Role.ADMIN]
    role_weights = [0.85, 0.10, 0.05]

    for i in range(total):
        secteur = random.choice(secteurs)
        code_secteur = secteur.code
        sexe = random.choice(['Masculin', 'Feminin'])
        date_naissance = fake.date_of_birth(minimum_age=18, maximum_age=90)
        nin_obj = NIN.generer(code_secteur, date_naissance, sexe)
        nin = str(nin_obj)
        while User.objects.filter(nin=nin).exists():
            date_naissance = fake.date_of_birth(minimum_age=18, maximum_age=90)
            nin_obj = NIN.generer(code_secteur, date_naissance, sexe)
            nin = str(nin_obj)

        prenom = fake.first_name_male() if sexe == 'M' else fake.first_name_female()
        nom = fake.last_name()
        postnom = fake.last_name() if random.choice([True, False]) else ''
        email = f"{fake.user_name()}_{i}@example.com"
        telephone = fake.phone_number()[:20]
        role = random.choices(roles, weights=role_weights)[0]
        nom_du_pere = fake.last_name()
        nom_de_la_mere = fake.last_name()
        is_staff = (role == User.Role.AGENT or role == User.Role.ADMIN)
        is_superuser = (role == User.Role.ADMIN)
        is_validated = random.choice([True, False])
        biometric_completed = random.choice([True, False])

        user = User.objects.create_user(
            email=email,
            nin=nin,
            password='Test123!',
            prenom=prenom,
            nom=nom,
            postnom=postnom,
            sexe= sexe,
            telephone=telephone,
            date_naissance=date_naissance,
            role=role,
            lieu_origine=secteur,
            nom_du_pere=nom_du_pere,
            nom_de_la_mere=nom_de_la_mere,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_validated=is_validated,
            biometric_completed=biometric_completed
        )
        if hasattr(user, 'mot_de_passe'):
            user.mot_de_passe = user.password
            user.save(update_fields=['mot_de_passe'])

        # Adresse
        Adresse.objects.create(
            citoyen=user,
            province=random.choice(provinces),
            commune=fake.city()[:100],
            quartier=fake.street_name()[:100],
            avenue=fake.street_name()[:100],
            numero=str(random.randint(1, 999))
        )

        # Documents (1 à 3)
        for _ in range(random.randint(1, 3)):
            doc_type = random.choice([t[0] for t in Document.TypeDocument.choices])
            numero = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            date_emission = fake.date_between(start_date='-10y', end_date='today')
            date_expiration = date_emission + timedelta(days=random.randint(365, 3650))
            statut = random.choice([s[0] for s in Document.Statut.choices])
            doc = Document.objects.create(
                user=user,
                type=doc_type,
                numero=numero,
                fichier=ContentFile(b"Fichier factice", name=f"doc_{numero}.pdf"),
                date_emission=date_emission,
                date_expiration=date_expiration,
                statut=statut,
                commentaire_rejet=fake.sentence() if statut == Document.Statut.REJETE else ''
            )
            if statut == Document.Statut.VALIDE:
                validateur = User.objects.filter(role=User.Role.AGENT).first()
                if validateur:
                    doc.valide_par = validateur
                    doc.date_validation = timezone.now()
                    doc.save()

        # Biométrie (0 à 2)
        for btype in random.sample(['face', 'fingerprint', 'iris'], random.randint(0, 2)):
            BiometricData.objects.create(
                citoyen=user,
                biometric_type=btype,
                image=ContentFile(b"Biometric fake", name=f"bio_{btype}_{user.id}.jpg"),
                template=None,
                is_active=True
            )

        # OTP (1-2)
        for _ in range(random.randint(1, 2)):
            OTP.objects.create(
                user=user,
                code=''.join(random.choices(string.digits, k=6)),
                created_at=timezone.now() - timedelta(hours=random.randint(0, 48)),
                expires_at=timezone.now() + timedelta(minutes=10),
                is_used=random.choice([True, False]),
                purpose=random.choice(['LOGIN', 'REGISTER']),
                attempts=random.randint(0, 3)
            )

        # Audit logs (0-5)
        for _ in range(random.randint(0, 5)):
            AuditLog.objects.create(
                user=user,
                action=random.choice([a[0] for a in AuditLog.Action.choices]),
                entity_type=random.choice(['User', 'Document']),
                entity_id=str(user.id),
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent()
            )

        if (i + 1) % 20 == 0:
            print(f"{i+1} utilisateurs créés...")

    print(f"✅ {total} utilisateurs générés.")


def create_partenaires_if_needed():
    if Partenaire.objects.exists():
        return
    for data in [
        {"nom": "Banque Nationale", "email": "contact@banque.cd"},
        {"nom": "Assurance Vie", "email": "support@assurance.cd"},
        {"nom": "Télécom RDC", "email": "api@telecom.cd"},
    ]:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        Partenaire.objects.create(nom=data["nom"], email=data["email"], token=token, is_active=True)
    print("Partenaires créés.")


if __name__ == "__main__":
    total = 120
    if len(sys.argv) > 2 and sys.argv[1] == '--total':
        try:
            total = int(sys.argv[2])
        except ValueError:
            pass
    promote_existing_admin()
    create_partenaires_if_needed()
    generate_test_users(total)