# src/shared/utils/image_utils.py
import base64
import cv2
import numpy as np
from django.core.files.base import ContentFile

def base64_to_cv2(base64_str: str):
    
    try:
        if 'base64,' in base64_str:
            base64_str = base64_str.split('base64,')[1]

        img_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # 💥 CHECK CRITIQUE
        if img is None:
            raise ValueError("Image décodée = None (format invalide)")

        return img

    except Exception as e:
        print("❌ ERREUR BASE64 → CV2:", str(e))
        return None

def base64_to_django_file(base64_str: str, filename_prefix: str) -> ContentFile:
    """
    Convertit une chaîne base64 en fichier Django ContentFile.
    Attend un header du type "data:image/jpeg;base64,..."
    """
    format, imgstr = base64_str.split(';base64,')
    ext = format.split('/')[-1]
    data = base64.b64decode(imgstr)
    return ContentFile(data, name=f"{filename_prefix}.{ext}")