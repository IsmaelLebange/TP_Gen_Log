# user_repository.py - Repository pour les utilisateurs

from typing import Optional, List, TYPE_CHECKING
from django.contrib.auth import get_user_model
from django.db import models
from src.apps.interfaces.main_interfaces.user_repository_interface import UserRepositoryInterface

User = get_user_model()
if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

class UserRepository(UserRepositoryInterface):
    """Implémentation Django du repository utilisateur"""

    def get_by_id(self, user_id: int) -> Optional["AbstractBaseUser"]:
        """Récupère un utilisateur par son ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional["AbstractBaseUser"]:
        """Récupère un utilisateur par son email"""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_by_nin(self, nin: str) -> Optional["AbstractBaseUser"]:
        """Récupère un utilisateur par son NIN"""
        try:
            return User.objects.get(nin=nin)
        except User.DoesNotExist:
            return None

    def save(self, user: "AbstractBaseUser") -> "AbstractBaseUser":
        """Sauvegarde un utilisateur"""
        user.save()
        return user

    def delete(self, user: "AbstractBaseUser") -> None:
        """Supprime un utilisateur"""
        user.delete()

    def exists_by_email(self, email: str) -> bool:
        """Vérifie si un utilisateur existe avec cet email"""
        return User.objects.filter(email=email).exists()

    def exists_by_nin(self, nin: str) -> bool:
        """Vérifie si un utilisateur existe avec ce NIN"""
        return User.objects.filter(nin=nin).exists()

    def get_active_users(self) -> List["AbstractBaseUser"]:
        """Récupère tous les utilisateurs actifs"""
        return list(User.objects.filter(is_active=True))

    def update_last_login(self, user: "AbstractBaseUser") -> None:
        """Met à jour la dernière connexion"""
        user.last_login = models.functions.Now()
        user.save(update_fields=['last_login'])