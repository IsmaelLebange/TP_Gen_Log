import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from src.apps.api.providers.main_provider import MainProvider
from src.domain.value_objects.biometrics import BiometricType
from src.apps.api.providers.citoyen_provider import CitoyenProvider
from src.apps.api.serializers.citoyen_serializers.enrollment_serializer import EnrollmentCompleteSerializer, EnrollmentSerializer
from src.domain.entities.citoyen import Citoyen
# Utiliser l'utilitaire si nécessaire, mais ici on passe par le service pour la Clean Arch
from src.shared.utils.qrcode_utils import QRCodeService

logger = logging.getLogger(__name__)

class EnrollmentController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            repository = CitoyenProvider.get_citoyen_repository()
            code_secteur = repository.trouver_code_secteur(
                nom_secteur=serializer.validated_data.get('secteur_origine'),
                nom_territoire=serializer.validated_data.get('territoire_origine')
            )

            citoyen_entity = Citoyen.from_request(
                serializer.validated_data, 
                code_secteur=code_secteur
            )

            service = CitoyenProvider.get_enrollment_service()
            service.enroler(citoyen_entity)

            return Response(citoyen_entity.to_dict(), status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Erreur lors de l'enrôlement")
            return Response({'error': "Une erreur interne est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        action = request.query_params.get('action')
        if action == 'qr':
            return self._get_qr(request)
        return Response({'error': 'Action non valide'}, status=400)

    def _get_qr(self, request):
        try:
            service = CitoyenProvider.get_enrollment_service()
            # On s'assure que le service renvoie bien un dict {'qr_code': '...'}
            result = service.get_my_qr_code(request.user.id)
            return Response(result, status=200)
        except Exception as e:
            logger.exception("Erreur QR code")
            return Response({'error': str(e)}, status=400)
        
from django.db import transaction

class EnrollmentCompleteController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        
        
        serializer = EnrollmentCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)  # Debug des erreurs de validation
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- DÉBUT DE LA TRANSACTION ---
            with transaction.atomic():
                # A. Récupération du code secteur (ton code actuel)
                repository = CitoyenProvider.get_citoyen_repository()
                
                code_secteur = repository.trouver_code_secteur(
                    nom_secteur=serializer.validated_data.get('secteur_origine'),
                    nom_territoire=serializer.validated_data.get('territoire_origine')
                )

                # B. Création de l'entité Citoyen (ton code actuel)
                citoyen_entity = Citoyen.from_request(
                    serializer.validated_data, 
                    code_secteur=code_secteur
                )
                # C. Enrôlement Civil via le service
                service_civil = CitoyenProvider.get_enrollment_service()
                citoyen_sauvegarde = service_civil.enroler(citoyen_entity)

                # D. Enrôlement Biométrique IMMÉDIAT
                # On utilise l'ID que Django vient de générer
                service_bio = CitoyenProvider.get_biometric_service()
                res_bio = service_bio.enroll(
                    citoyen_id=citoyen_sauvegarde.id,
                    biometric_type=BiometricType(serializer.validated_data.get('biometric_type')),
                    image_base64=serializer.validated_data.get('biometric_image')
                )
                print(f"✅ Résultat biométrie: {res_bio}")

                # E. Si la biométrie échoue (ex: pas de visage détecté par OpenCV)
                if not res_bio.get('success'):
                    # On lève une erreur pour forcer le ROLLBACK (annulation) du citoyen
                    print(f"❌ Biometrie échouée: {res_bio.get('message')}")
                    raise ValueError(f"Biométrie invalide : {res_bio.get('message')}")

                # F. Si tout est bon, on marque le statut complet
                service_civil.update_biometric_complete(citoyen_sauvegarde.id, True)
                print(f"✅ Enrôlement complet pour le citoyen ID: {citoyen_sauvegarde.id}")
                # On retourne le profil complet avec le NIN
                service_civil.update_biometric_complete(citoyen_sauvegarde.id, True) # Marque le citoyen comme ayant complété la biométrie
                email_sender = MainProvider.get_otp_sender('email')
                message = (
                    f"Bonjour {citoyen_sauvegarde.prenom},\n\n"
                    f"Votre enrôlement dans le SEIP est validé.\n"
                    f"Votre NIN : {citoyen_sauvegarde.nin}\n\n"
                    "Cordialement."
                )
                email_sender.send(user=citoyen_sauvegarde, message=message)
                return  Response({
                            'success': True,
                            'nin': citoyen_sauvegarde.nin,
                            'nom': citoyen_sauvegarde.nom,
                            'postnom': getattr(citoyen_sauvegarde, 'postnom', ''),
                            'prenom': citoyen_sauvegarde.prenom,
                            'sexe': citoyen_sauvegarde.sexe,
                            'message': 'Enrôlement réussi'
                        }, status=status.HTTP_201_CREATED)
                # --- FIN DE LA TRANSACTION ---

        except ValueError as e:
            # Ici, le citoyen n'est PAS créé en base de données (Rollback)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Erreur Fatale Enrôlement")
            return Response({'error': "Erreur serveur."}, status=500)

class QRController(APIView):
    """
    Contrôleur dédié pour le QR Code (plus propre pour la Clean Architecture)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        if not user.biometric_completed:
            return Response(
                {'error': 'Biométrie non complétée. Veuillez enrôler votre visage et empreinte.'},
                status=403
            )
        
        if not user.is_validated:
            return Response(
                {'error': 'Enrôlement en attente de validation. Veuillez patienter.'},
                status=403
            )
        service = CitoyenProvider.get_enrollment_service()
        result = service.get_my_qr_code(user.id)
        return Response(result, status=200)