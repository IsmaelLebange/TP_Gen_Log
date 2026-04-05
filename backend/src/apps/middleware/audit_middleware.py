class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # On n'audit que les modifications réussies et les utilisateurs connectés
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and response.status_code < 400:
            if request.user.is_authenticated:
                from src.apps.api.providers.admin_provider import AdminProvider
                audit_service = AdminProvider.get_audit_service()
                
                audit_service.log(
                    action=f"{request.method}_{request.resolver_match.url_name}",
                    user_id=request.user.id,
                    resource=request.path,
                    details={'status': response.status_code},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
        return response