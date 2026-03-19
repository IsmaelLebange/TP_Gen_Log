from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # Pour l'instant, on autorise tout le monde à s'enrôler
from src.apps.citoyen.api.citoyen_provider import CitoyenProvider
from src.apps.citoyen.repositories.citoyen_repository import DjangoCitoyenRepository
from datetime import datetime

class EnrollmentController(APIView):
    """
    Controller pour l'enrôlement des citoyens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Récupération des données de la requête
        data = request.data
        try:
            # Conversion de la date
            date_naissance = datetime.strptime(data['date_naissance'], '%Y-%m-%d').date()

            # Instanciation du service avec le repository concret
            repo = CitoyenProvider.get_citoyen_repository()
            service = CitoyenProvider.get_enrollment_service()

            # Appel du service
            citoyen = service.enroler(
                nin=data['nin'],
                email=data['email'],
                nom=data['nom'],
                postnom=data.get('postnom'),  # postnom est optionnel
                prenom=data['prenom'],
                date_naissance=date_naissance,
                telephone=data.get('telephone')
            )

            # Construction de la réponse
            response_data = {
                'id': citoyen.id,
                'nin': str(citoyen.nin),
                'email': str(citoyen.email),
                'nom': citoyen.nom,
                'postnom': citoyen.postnom,
                'prenom': citoyen.prenom,
                'date_naissance': citoyen.date_naissance.isoformat(),
                'telephone': citoyen.telephone
            }
            return Response(response_data, status=status.HTTP_201_CREATED)


        except ValueError as e:
            return Response({'error EnrollCOntr valueError': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error EnrollCOntr KeyError': f"Champ manquant : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # On renvoie l'erreur réelle pour savoir ce qui casse
            return Response({'error EnrollCOntr exception': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)