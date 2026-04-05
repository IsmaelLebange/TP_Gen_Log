from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from src.apps.api.providers.admin_provider import AdminProvider
from src.apps.api.serializers.admin_serializers.statistics_serializers import StatisticsSerializer

class StatisticsController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Vérifier que l'utilisateur est admin
        if request.user.role not in ['ADMIN']:
            return Response({'error': 'Accès réservé aux administrateurs'}, status=403)

        service = AdminProvider.get_statistics_service()
        data = service.get_dashboard_stats()
        serializer = StatisticsSerializer(data)
        return Response(serializer.data, status=200)