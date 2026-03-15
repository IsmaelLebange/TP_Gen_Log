from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, nin, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        if not nin:
            raise ValueError('NIN obligatoire')

        # Supporte la compatibilité avec first_name / last_name
        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        if first_name:
            extra_fields.setdefault('prenom', first_name)
        if last_name:
            extra_fields.setdefault('nom', last_name)

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
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
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