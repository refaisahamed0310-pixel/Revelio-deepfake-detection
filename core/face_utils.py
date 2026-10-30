"""
core/face_utils.py
──────────────────
Face detection using OpenCV's Haar Cascade classifier.
Detects the primary (largest) face in an image and returns a padded crop.
Falls back to the full image if no face is found.
"""

import cv2
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# OpenCV ships Haar cascades; no separate download needed
_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
_face_cascade: cv2.CascadeClassifier = None


def _get_cascade() -> cv2.CascadeClassifier:
    """Lazy-load and cache the Haar cascade classifier."""
    global _face_cascade
    if _face_cascade is None:
        _face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)
        if _face_cascade.empty():
            logger.error(
                f"Failed to load Haar cascade from: {_CASCADE_PATH}"
            )
    return _face_cascade


def detect_and_crop_face(
    image: np.ndarray,
    padding: float = 0.25,
) -> Tuple[np.ndarray, bool]:
    """
    Detect the largest face in an image and return a padded crop.

    The detector converts to grayscale internally. The returned crop
    is always in the same color space as the input (BGR or RGB).

    Args:
        image:   BGR (or RGB) image array with shape (H, W, 3).
        padding: Fractional padding added around the face bounding box
                 in each direction (default 0.25 = 25 % of face size).

    Returns:
        (cropped_region, face_was_found)
        - cropped_region: The face crop (or full image if no face found).
        - face_was_found: True when at least one face was detected.
    """
    if image is None or image.size == 0:
        return image, False

    cascade = _get_cascade()
    if cascade.empty():
        return image, False

    # Haar cascade needs grayscale
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Equalise histogram to improve detection in varied lighting
    gray_eq = cv2.equalizeHist(gray)

    detections = cascade.detectMultiScale(
        gray_eq,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(48, 48),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    if not isinstance(detections, np.ndarray) or len(detections) == 0:
        logger.debug("No face detected — using full image.")
        return image, False

    # Pick the largest face by area
    detections = sorted(detections, key=lambda f: f[2] * f[3], reverse=True)
    x, y, w, h = detections[0]

    img_h, img_w = image.shape[:2]
    pad_x = int(w * padding)
    pad_y = int(h * padding)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(img_w, x + w + pad_x)
    y2 = min(img_h, y + h + pad_y)

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        return image, False

    logger.debug(f"Face crop: ({x1},{y1}) → ({x2},{y2})  size={crop.shape[:2]}")
    return crop, True
