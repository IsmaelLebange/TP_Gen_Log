# src/apps/citoyen/services/biometric_service.py
import cv2
import numpy as np
import logging
from typing import Dict, Any
from src.apps.citoyen.interfaces.biometric_repository_interface import BiometricRepositoryInterface
from src.domain.entities.biometric import BiometricEntity
from src.domain.value_objects.biometrics import BiometricType
from src.domain.value_objects.biometrics import BiometricTemplate
from src.domain.exceptions.biometric_exceptions import (
    BiometricExtractionError,
    BiometricNotFoundError,
    BiometricAlreadyExistsError
)
from src.shared.utils.image_utils import base64_to_cv2

logger = logging.getLogger(__name__)

class BiometricService:
    """
    Service applicatif pour la biométrie.
    Dépend d'une abstraction (interface) du repository.
    """

    def __init__(self, repository: BiometricRepositoryInterface):
        self.repository = repository

    def enroll(self, citoyen_id: int, biometric_type: str, image_base64: str) -> Dict[str, Any]:
        try:
            # Vérifier si une donnée active existe déjà
            existing = self.repository.get_active_by_citoyen(citoyen_id)
            if existing and existing.biometric_type.value == biometric_type:
                raise BiometricAlreadyExistsError("Une donnée biométrique active existe déjà pour ce type.")

            img = base64_to_cv2(image_base64)
            features = self._extract_features(img, biometric_type)
            if features is None:
                raise BiometricExtractionError("Impossible d'extraire les caractéristiques.")

            template = BiometricTemplate(features=features)
            entity = BiometricEntity(
                citoyen_id=citoyen_id,
                biometric_type=BiometricType.from_string(biometric_type),
                template=template,
                # image_path sera géré par le repository
            )

            saved_entity = self.repository.save(entity)

            return {
                'success': True,
                'message': 'Enrôlement réussi',
                'data': {
                    'id': saved_entity.id,
                    'type': saved_entity.biometric_type.value,
                    'created_at': saved_entity.created_at.isoformat() if saved_entity.created_at else None
                }
            }
        except (BiometricExtractionError, BiometricAlreadyExistsError) as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            logger.exception("Erreur inattendue")
            return {'success': False, 'message': 'Erreur interne'}

    def verify(self, citoyen_id: int, image_base64: str) -> Dict[str, Any]:
        try:
            entity = self.repository.get_active_by_citoyen(citoyen_id)
            if not entity:
                raise BiometricNotFoundError("Aucune donnée biométrique active trouvée.")

            img = base64_to_cv2(image_base64)
            new_features = self._extract_features(img, entity.biometric_type.value)
            if new_features is None:
                raise BiometricExtractionError("Impossible d'extraire les caractéristiques.")

            stored = np.array(entity.template.features)
            new = np.array(new_features)
            distance = np.linalg.norm(stored - new)

            threshold = 15.0
            match = distance < threshold
            confidence = max(0, 100 - distance)

            return {
                'success': True,
                'data': {
                    'matched': match,
                    'confidence': round(confidence, 2),
                    'distance': round(float(distance), 4)
                }
            }
        except BiometricNotFoundError as e:
            return {'success': False, 'message': str(e)}
        except BiometricExtractionError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            logger.exception("Erreur inattendue")
            return {'success': False, 'message': 'Erreur interne'}

    def get_status(self, citoyen_id: int) -> Dict[str, Any]:
        entity = self.repository.get_active_by_citoyen(citoyen_id)
        if not entity:
            return {'enrolled': False}
        return {
            'enrolled': True,
            'type': entity.biometric_type.value,
            'created_at': entity.created_at.isoformat() if entity.created_at else None
        }

    def delete(self, citoyen_id: int) -> Dict[str, Any]:
        entity = self.repository.get_active_by_citoyen(citoyen_id)
        if not entity:
            return {'success': False, 'message': 'Aucune donnée active trouvée.'}
        self.repository.delete(entity)
        return {'success': True, 'message': 'Données supprimées avec succès.'}

    # Méthodes privées d'extraction (inchangées)
    def _extract_features(self, img, biometric_type: str):
        if biometric_type == 'face':
            return self._extract_face_features(img)
        elif biometric_type == 'fingerprint':
            return self._extract_fingerprint_features(img)
        elif biometric_type == 'iris':
            return self._extract_iris_features(img)
        return None

    def _extract_face_features(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_roi, (100, 100))
        hist = cv2.calcHist([face_resized], [0], None, [256], [0,256])
        cv2.normalize(hist, hist)
        return hist.flatten().tolist()

    def _extract_fingerprint_features(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        hist = cv2.calcHist([thresh], [0], None, [256], [0,256])
        cv2.normalize(hist, hist)
        return hist.flatten().tolist()

    def _extract_iris_features(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=50, param2=30, minRadius=0, maxRadius=0)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            (x, y, r) = circles[0]
            iris_region = gray[y-r:y+r, x-r:x+r]
            iris_resized = cv2.resize(iris_region, (50, 50))
            hist = cv2.calcHist([iris_resized], [0], None, [256], [0,256])
            cv2.normalize(hist, hist)
            return hist.flatten().tolist()
        return None