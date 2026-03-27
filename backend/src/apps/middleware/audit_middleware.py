import json
from django.utils import timezone
from src.models import AuditLog

class AuditMiddleware:
    """Middleware pour logger toutes les requêtes importantes"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Avant la vue
        request.audit_start_time = timezone.now()
        
        response = self.get_response(request)
        
        # Après la vue - logger les requêtes modifiant des données
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self._log_request(request, response)
        
        return response
    
    def _log_request(self, request, response):
        """Log une requête dans AuditLog"""
        try:
            user = request.user if request.user.is_authenticated else None
            
            # Ne pas logger les requêtes vers /admin
            if request.path.startswith('/admin/'):
                return
            
            # Déterminer l'entité concernée
            path_parts = request.path.split('/')
            entity_type = path_parts[3] if len(path_parts) > 3 else 'Unknown'
            
            # Ne pas logger si réponse en erreur
            if response.status_code >= 400:
                return
            
            AuditLog.objects.create(
                user=user,
                action=request.method,
                entity_type=entity_type,
                entity_id=request.resolver_match.kwargs.get('pk', ''),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
        except Exception as e:
            # Silent fail pour ne pas casser la requête
            pass