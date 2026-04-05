from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone


class Province(models.Model):
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Territoire(models.Model):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='territoires')

    def __str__(self):
        return f"{self.nom} ({self.province.nom})"

class SecteurChefferie(models.Model):
    TYPE_CHOICES = [
        ('SECTEUR', 'Secteur'),
        ('CHEFFERIE', 'Chefferie'),
    ]
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=200)
    territoire = models.ForeignKey(Territoire, on_delete=models.CASCADE, related_name='secteurs_chefferies')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SECTEUR')

    def __str__(self):
        return f"{self.nom} ({self.territoire.nom})"

class Adresse(models.Model):
    citoyen = models.OneToOneField('User', on_delete=models.CASCADE, related_name='adresse_actuelle')
    province = models.ForeignKey('Province', on_delete=models.SET_NULL, null=True, blank=True)
    commune = models.CharField(max_length=100, blank=True)
    quartier = models.CharField(max_length=100, blank=True)
    avenue = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    

    def __str__(self):
        parts = []
        if self.avenue: parts.append(self.avenue)
        if self.numero: parts.append(self.numero)
        if self.quartier: parts.append(self.quartier)
        if self.commune: parts.append(self.commune)
        elif self.province: parts.append(str(self.province))
        return ", ".join(parts) or "Adresse non renseignée"

class UserManager(BaseUserManager):
    def create_user(self, email, nin, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        if not nin:
            raise ValueError('NIN obligatoire')

        # Supporte la compatibilité avec first_name / last_name
        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        postnom = extra_fields.pop('postnom', None)
        if first_name:
            extra_fields.setdefault('prenom', first_name)

        if last_name:
            extra_fields.setdefault('nom', last_name)

        if postnom:
            extra_fields.setdefault('postnom', postnom)

        email = self.normalize_email(email)
        user = self.model(email=email, nin=nin, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nin, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')

        return self.create_user(email, nin, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CITOYEN = 'CITOYEN', 'Citoyen'
        AGENT = 'AGENT', 'Agent'
        ADMIN = 'ADMIN', 'Administrateur'
    
    email = models.EmailField(unique=True)
    nin = models.CharField('NIN', max_length=20, unique=True)  # National ID Number
    nom = models.CharField(max_length=100)
    postnom = models.CharField(max_length=100, blank=True)  # Nouveau champ pour le postnom
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITOYEN)
    lieu_origine = models.ForeignKey(SecteurChefferie, on_delete=models.SET_NULL, null=True, blank=True, related_name='citoyens')
    nom_du_pere = models.CharField(max_length=100, blank=True)
    nom_de_la_mere = models.CharField(max_length=100, blank=True)
    mot_de_passe = models.CharField(max_length=128)  # Champ pour stocker le mot de passe haché
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_validated = models.BooleanField(default=False)
    biometric_completed = models.BooleanField(default=False)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='main_user_set',
        related_query_name='main_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='main_user_set',
        related_query_name='main_user',
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nin', 'nom', 'prenom']
    
    def __str__(self):
        return f"{self.nin} - {self.prenom} {self.nom}"
    def est_majeur(self):
        from datetime import date
        if not self.date_naissance:
            return False
        today = date.today()
        age = today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        return age >= 18

    @property
    def first_name(self):
        return self.prenom

    @first_name.setter
    def first_name(self, value):
        self.prenom = value

    @property
    def last_name(self):
        return self.nom

    @last_name.setter
    def last_name(self, value):
        self.nom = value
    
    class Meta:
        db_table = 'users'
















class Document(models.Model):
    class TypeDocument(models.TextChoices):
        CARTE_IDENTITE = 'CNI', "Carte d'identité"
        PASSEPORT = 'PAS', 'Passeport'
        PERMIS_CONDUITE = 'PER', 'Permis de conduire'
        ACTE_NAISSANCE = 'ACT', "Acte de naissance"
        JUSTIF_DOMICILE = 'DOM', 'Justificatif de domicile'
    
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDE = 'VALIDE', 'Validé'
        REJETE = 'REJETE', 'Rejeté'
        EXPIRED = 'EXPIRE', 'Expiré'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    type = models.CharField(max_length=20, choices=TypeDocument.choices)
    numero = models.CharField(max_length=50)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    date_emission = models.DateField()
    date_expiration = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_rejet = models.TextField(blank=True)
    
    
    def __str__(self):
        return f"{self.type} - {self.numero} - {self.user.nin}"
    
    class Meta:
        db_table = 'documents'




class BiometricData(models.Model):
    BIOMETRIC_TYPES = [
        ('face', 'Visage'),
        ('fingerprint', 'Empreinte digitale'),
        ('iris', 'Iris'),
    ]

    citoyen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biometric_data')
    biometric_type = models.CharField(max_length=20, choices=BIOMETRIC_TYPES)
    image = models.ImageField(upload_to='biometrics/%Y/%m/%d/', null=True, blank=True)
    template = models.BinaryField(null=True, blank=True)  # features extraits sérialisés (pickle)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['citoyen', 'biometric_type', 'is_active']
        db_table = 'citoyen_biometric_data'  # optionnel, mais cohérent avec Document

    def __str__(self):
        return f"{self.citoyen.username} - {self.biometric_type}"







class Partenaire(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True)  # token pour l'API
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        db_table = 'partenaires'













class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Création'
        UPDATE = 'UPDATE', 'Modification'
        DELETE = 'DELETE', 'Suppression'
        VIEW = 'VIEW', 'Consultation'
        LOGIN = 'LOGIN', 'Connexion'
        LOGOUT = 'LOGOUT', 'Déconnexion'
        VALIDATE = 'VALIDATE', 'Validation'
        REJECT = 'REJECT', 'Rejet'
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    entity_type = models.CharField(max_length=50)  # 'Citoyen', 'Document', etc.
    entity_id = models.CharField(max_length=50)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} - {self.entity_type} - {self.created_at}"
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']




class OTP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, default='LOGIN')  # LOGIN, REGISTER, etc.
    attempts = models.IntegerField(default=0)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    class Meta:
        db_table = 'otp'
        ordering = ['-created_at']