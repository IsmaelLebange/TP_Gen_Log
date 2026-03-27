from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src.apps.api.providers.citoyen_provider import CitoyenProvider
from src.apps.api.serializers.citoyen_serializers.enrollment_serializer import EnrollmentSerializer
from src.domain.entities.citoyen import Citoyen

class EnrollmentController(APIView):
    def post(self, request):
        # 1. Validation syntaxique via Serializer
        serializer = EnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Récupération du repository pour chercher le code géographique
            repository = CitoyenProvider.get_citoyen_repository()
            
            # 2. On récupère le code de 7 chiffres (ex: 2201401) via les noms
            code_secteur = repository.trouver_code_secteur(
                nom_secteur=serializer.validated_data.get('secteur_origine'),
                nom_territoire=serializer.validated_data.get('territoire_origine')
            )

            # 3. Conversion en objet Domaine (le NIN est généré ici)
            citoyen_entity = Citoyen.from_request(
                serializer.validated_data, 
                code_secteur=code_secteur
            )

            # 4. Appel au Service pour la logique d'enrôlement
            service = CitoyenProvider.get_enrollment_service()
            service.enroler(citoyen_entity)

            # 5. Réponse succès
            return Response(citoyen_entity.to_dict(), status=status.HTTP_201_CREATED)

        except ValueError as e:
            # Captures les erreurs métier (Déjà existant, Mineur, Secteur introuvable)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Erreur imprévue
            return Response({'error': "Une erreur interne est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)