from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from src.apps.api.providers.admin_provider import AdminProvider
from src.apps.api.serializers.admin_serializers.audit_serializers import (
    AuditLogSerializer, AuditFilterSerializer
)

class AuditController(APIView):
    permission_classes = [IsAuthenticated]

    @property
    def audit_service(self):
        return AdminProvider.get_audit_service()

    def get(self, request):
        # Vérifier les droits
        if request.user.role not in ['ADMIN', 'AGENT']:
            return Response({'error': 'Permission refusée'}, status=403)

        serializer = AuditFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data

        if data.get('query'):
            logs = self.audit_service.search(data['query'], data.get('limit', 100))
        elif data.get('user_id'):
            logs = self.audit_service.get_by_user(data['user_id'], data.get('limit', 100))
        elif data.get('action'):
            logs = self.audit_service.get_by_action(data['action'], data.get('limit', 100))
        elif data.get('start_date') and data.get('end_date'):
            logs = self.audit_service.get_by_date_range(data['start_date'], data['end_date'])
        elif data.get('hours'):
            logs = self.audit_service.get_recent(data['hours'])
        else:
            logs = self.audit_service.get_recent(24)

        result_serializer = AuditLogSerializer(logs, many=True)
        return Response(result_serializer.data, status=200)