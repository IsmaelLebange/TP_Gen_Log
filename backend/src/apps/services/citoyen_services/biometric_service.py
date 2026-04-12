import cv2
import numpy as np
import pickle
import logging
from typing import Dict, Any, List, Optional
from src.apps.interfaces.citoyen_interfaces.biometric_repository_interface import BiometricRepositoryInterface
from src.domain.entities.biometric import BiometricEntity
from src.domain.value_objects.biometrics import BiometricType, BiometricTemplate
from src.domain.exceptions.biometric_exceptions import (
    BiometricExtractionError,
    BiometricNotFoundError,
    BiometricAlreadyExistsError
)
from src.shared.utils.image_utils import base64_to_cv2

logger = logging.getLogger(__name__)

class BiometricService:
    def __init__(self, repository: BiometricRepositoryInterface):
        self.repository = repository

    def enroll(self, citoyen_id: int, biometric_type: str, image_base64: str) -> Dict[str, Any]:
        
        try:
            existing = self.repository.get_active_by_citoyen(citoyen_id)
            if existing and existing.biometric_type.value == biometric_type:
                raise BiometricAlreadyExistsError("Une donnée biométrique active existe déjà pour ce type.")
            img = base64_to_cv2(image_base64)
            features = self._extract_features(img, biometric_type)
            
            if features is None:
                raise BiometricExtractionError("Impossible d'extraire les caractéristiques.")
            
            entity = BiometricEntity(
                citoyen_id=citoyen_id,
                biometric_type=BiometricType.from_string(biometric_type),
                image_base64=image_base64,  # on garde l'image brute pour le traitement, mais pas pour la sortie
                template=BiometricTemplate(features=features),  # garde pour l'entité
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

            # Récupérer les features stockées (sous forme de liste ou de descripteurs)
            stored_features = entity.template.features
            stored_descriptors = self._deserialize_features(stored_features, entity.biometric_type.value)
            new_descriptors = self._deserialize_features(new_features, entity.biometric_type.value)

            if entity.biometric_type.value == 'fingerprint':
                # Matching avec BFMatcher (distance de Hamming)
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches = bf.match(stored_descriptors, new_descriptors)
                # Trier par distance
                matches = sorted(matches, key=lambda x: x.distance)
                # Garder les bons matches (distance < 50)
                good_matches = [m for m in matches if m.distance < 50]
                if len(stored_descriptors) == 0:
                    score = 0
                else:
                    score = (len(good_matches) / len(stored_descriptors)) * 100
                match = score > 20   # seuil à ajuster
                confidence = score
                distance = 100 - score
            else:
                # Pour face et iris, distance euclidienne sur les histograms
                stored = np.array(stored_features)
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
        except (BiometricNotFoundError, BiometricExtractionError) as e:
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

    def get_active_types(self, citoyen_id: int) -> List[str]:
        """Retourne la liste des types biométriques actifs pour un citoyen."""
        entities = self.repository.list_active_by_citoyen(citoyen_id)  # à ajouter dans l'interface
        return [e.biometric_type.value for e in entities]

    def delete(self, citoyen_id: int) -> Dict[str, Any]:
        entity = self.repository.get_active_by_citoyen(citoyen_id)
        if not entity:
            return {'success': False, 'message': 'Aucune donnée active trouvée.'}
        self.repository.delete(entity)
        return {'success': True, 'message': 'Données supprimées avec succès.'}

    # --- Méthodes privées d'extraction ---
    def _extract_features(self, img, biometric_type: str):
        biometric_type = biometric_type.value if hasattr(biometric_type, 'value') else biometric_type
        print(f"🔍 Extraction des caractéristiques pour type: {biometric_type}")  # Debug du type biométrique"""
        print("Extractiion biometric_type:", biometric_type)
        if biometric_type == 'face':
            print("🔍 Extraction des caractéristiques faciales...")
            return self._extract_face_features(img)
        elif biometric_type == 'fingerprint':
            return self._extract_fingerprint_features_orb(img)
        elif biometric_type == 'iris':
            return self._extract_iris_features(img)
        return None

    def _extract_face_features(self, img):
        print(f"🔍 Début extraction visage, image shape: {img.shape if img is not None else 'None'}")
        try:
            logger.info("📸 Début extraction visage")

            # 1. Vérif image brute
            if img is None:
                logger.error("❌ Image reçue = None")
                return None

            logger.info(f"🧠 Shape image: {img.shape}")

            # DEBUG : sauvegarde image brute
            cv2.imwrite("debug_1_input.jpg", img)

            # 2. Conversion gris
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            logger.info("🎯 Conversion en niveaux de gris OK")

            cv2.imwrite("debug_2_gray.jpg", gray)

            # 3. Amélioration contraste
            gray = cv2.equalizeHist(gray)
            logger.info("✨ Histogram equalization appliqué")

            cv2.imwrite("debug_3_equalized.jpg", gray)

            # 4. Resize si nécessaire
            h, w = gray.shape
            logger.info(f"📏 Taille avant resize: {w}x{h}")

            if w < 200 or h < 200:
                gray = cv2.resize(gray, (400, 400))
                logger.warning("⚠️ Image trop petite → redimensionnée en 400x400")

            cv2.imwrite("debug_4_resized.jpg", gray)

            # 5. Multi-cascade
            cascades_paths = [
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
                cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml',
                cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'
            ]

            faces = []

            for i, path in enumerate(cascades_paths):
                logger.info(f"🔍 Test cascade {i+1}: {path}")

                face_cascade = cv2.CascadeClassifier(path)

                detected = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=4,
                    minSize=(80, 80)
                )

                logger.info(f"👉 Visages détectés: {len(detected)}")

                if len(detected) > 0:
                    faces = detected
                    logger.info(f"✅ Cascade {i+1} a trouvé un visage")
                    break

            # ❌ Aucun visage
            if len(faces) == 0:
                logger.error("❌ Aucun visage détecté après toutes les cascades")

                # DEBUG VISUEL
                cv2.imwrite("debug_FAIL_no_face.jpg", gray)

                return None

            # 6. Prendre le plus grand visage
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            (x, y, w, h) = faces[0]

            logger.info(f"📦 Visage sélectionné: x={x}, y={y}, w={w}, h={h}")

            # Dessiner rectangle debug
            debug_img = img.copy()
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0,255,0), 2)
            cv2.imwrite("debug_5_face_detected.jpg", debug_img)

            face_roi = gray[y:y+h, x:x+w]

            cv2.imwrite("debug_6_face_roi.jpg", face_roi)

            # 7. Resize final
            face_resized = cv2.resize(face_roi, (100, 100))
            cv2.imwrite("debug_7_face_resized.jpg", face_resized)

            # 8. Histogramme
            hist = cv2.calcHist([face_resized], [0], None, [256], [0, 256])
            cv2.normalize(hist, hist)

            logger.info("✅ Extraction features OK")

            return hist.flatten().tolist()

        except Exception as e:
            logger.exception("💥 Erreur extraction visage")
            return None

    def _extract_fingerprint_features_orb(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create(nfeatures=500)
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        if descriptors is None:
            return None
        # Les descripteurs ORB sont des matrices de uint8. On les convertit en liste de listes pour stockage.
        return descriptors.tolist()  # sera pickle.dumps plus tard

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

    def _deserialize_features(self, features, biometric_type: str):
        """Convertit les features stockées (liste) en format utilisable par OpenCV."""
        if biometric_type == 'fingerprint':
            # features est une liste de listes (descripteurs)
            return np.array(features, dtype=np.uint8)
        else:
            # pour face/iris, c'est une liste plate (histogramme)
            return np.array(features)
        
    def add_photo(self, citoyen_id: int, image_base64: str) -> Dict[str, Any]:
        # Désactiver toute photo active existante du même type
        existing = self.repository.get_active_by_citoyen(citoyen_id)
        if existing and existing.biometric_type.value == 'face':
            self.repository.delete(existing)  # soft delete : is_active=False
        return self.enroll(citoyen_id, 'face', image_base64)