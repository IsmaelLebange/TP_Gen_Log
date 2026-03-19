# src/apps/main/services/authentication_service.py
import logging
from typing import Dict, Any, TYPE_CHECKING
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from src.apps.main.interfaces.auth_interface import AuthenticationServiceInterface
from src.domain.exceptions.domain_exceptions import AuthenticationException
from src.apps.main.models import User

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

logger = logging.getLogger(__name__)

class AuthenticationService(AuthenticationServiceInterface):
    """Implémentation concrète du service d'authentification"""

    def _generate_tokens(self, user: "AbstractBaseUser") -> Dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': 3600,
        }

    def login(self, email: str, password: str, request=None) -> Dict[str, Any]:
        user = authenticate(request, email=email, password=password) if request else authenticate(email=email, password=password)

        if not user or not user.is_active:
            logger.warning(f"Échec connexion: {email}")
            raise AuthenticationException("Identifiants invalides ou compte inactif")

        tokens = self._generate_tokens(user)
        
        if request:
            self._log_audit(user, 'LOGIN', request)

        return {
            **tokens,
            'user': self._format_user_data(user)
        }

    def register(self, email: str, password: str, nom: str, prenom: str, 
                 nin: str, request=None, role: str = User.Role.CITOYEN,date_naissance: str=None) -> Dict[str, Any]:
        
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(nin=nin).exists():
            raise AuthenticationException("Email ou NIN déjà utilisé")

        user = User.objects.create_user(
            email=email, nin=nin, password=password,
            prenom=prenom, nom=nom, role=role, date_naissance=date_naissance
        )

        if request:
            self._log_audit(user, 'REGISTER', request)

        return {**self._generate_tokens(user), 'user': self._format_user_data(user)}

    def logout(self, user: Any, request=None) -> bool:
        if request:
            self._log_audit(user, 'LOGOUT', request)
        logger.info(f"Déconnexion: {user.email}")
        return True

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        try:
            refresh = RefreshToken(refresh_token)
            return {
                'access_token': str(refresh.access_token),
                'token_type': 'Bearer',
                'expires_in': 3600
            }
        except Exception:
            raise AuthenticationException("Token invalide ou expiré")

    def _format_user_data(self, user: Any) -> Dict:
        return {
            'id': user.id, 'email': user.email, 'nin': user.nin,
            'nom': user.last_name, 'prenom': user.first_name, 'role': user.role
        }

    def _log_audit(self, user: Any, action: str, request):
        try:
            from src.apps.administration.models import AuditLog
            AuditLog.objects.create(
                user=user, action=action, entity_type='User', entity_id=str(user.id),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            logger.exception("Erreur AuditLog")