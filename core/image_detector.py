import numpy as np
import cv2
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image as PILImage

from . import model_loader as ml
from .face_utils import detect_and_crop_face
from utils.helpers import load_image

IMG_SIZE = (224, 224)

def detect_image(image_path: str, use_face_detection: bool = True, model=None) -> dict:
    """
    Run deepfake detection using ensemble models.
    """
    result = {
        'probability': 0.0,
        'verdict': 'UNKNOWN',
        'confidence': 0.0,
        'face_detected': False,
        'width': 0,
        'height': 0,
        'error': None
    }

    try:
        # Pre-load models if needed
        ml.load_models()
        
        # Robust load for Windows Unicode support
        bgr = load_image(image_path)
        if bgr is None:
            result['error'] = f"Cannot read image: {image_path}"
            return result
            
        result['height'], result['width'] = bgr.shape[:2]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        # Handle face detection if requested
        if use_face_detection:
            crop_bgr, face_found = detect_and_crop_face(bgr)
            result['face_detected'] = face_found
            if face_found:
                rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)

        # -------- PREPROCESS IMAGE (USER LOGIC) --------
        # We use PIL from array to match load_img's behavior while supporting Unicode paths
        img = image.load_img(image_path, target_size=IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # -------- PREDICTIONS (USER LOGIC) --------
        preds = []
        if ml._model1 is not None:
            preds.append(ml._model1.predict(img_array, verbose=0)[0][0])
        if ml._model2 is not None:
            preds.append(ml._model2.predict(img_array, verbose=0)[0][0])
        
        if not preds:
            result['error'] = "No models available"
            return result
            
        final_pred = float(sum(preds) / len(preds))
        result['probability'] = final_pred

        # -------- CLASSIFICATION --------
        if final_pred >= 0.6:
            result['verdict'] = 'REAL'
            result['confidence'] = final_pred
        else:
            result['verdict'] = 'AI GENERATED'
            result['confidence'] = float(1.0 - final_pred)

    except Exception as e:
        result['error'] = str(e)

    return result