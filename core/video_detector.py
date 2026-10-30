"""
core/video_detector.py
──────────────────────
Video deepfake detection using user's provided logic.
"""

import cv2
import numpy as np
import tensorflow as tf
import random
import core.model_loader as ml


# -------- SETTINGS --------
IMG_SIZE = 224
FRAMES_TO_TEST = 20
THRESHOLD = 0.18


def detect_video(video_path, use_face_detection=False, **kwargs):
    result = {
        'probability': 0.0,
        'verdict': 'UNKNOWN',
        'confidence': 0.0,
        'frames_analyzed': 0,
        'error': None
    }

    if ml._video_model is None:
        result['error'] = f"Model {ml.VIDEO_MODEL_FILENAME} not loaded. Please check model_path in core/model_loader.py"
        return result

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        result['error'] = "Cannot open video"
        return result

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        result['error'] = "No frames in video"
        return result

    # Set a static seed based on total frames so the same video always extracts the exact same frames
    random.seed(total_frames)
    frame_ids = sorted(
        random.sample(range(total_frames), min(FRAMES_TO_TEST, total_frames))
    )
    # Reset seed to avoid impacting other parts of the application
    random.seed()

    predictions = []
    idx = 0

    # Initialize the cascade dynamically only if face detection is needed
    if use_face_detection:
        from core.face_utils import detect_and_crop_face

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        if idx in frame_ids:

            if use_face_detection:
                face_crop, face_found = detect_and_crop_face(frame)
                if face_found:
                    frame = face_crop

            frame = cv2.resize(frame,(IMG_SIZE,IMG_SIZE))
            frame = np.expand_dims(frame,axis=0)

            pred = ml._video_model.predict(frame, verbose=0)[0][0]
            predictions.append(pred)

            # Update progress in the UI if callback is provided
            progress_callback = kwargs.get('progress_callback')
            if progress_callback:
                progress_callback(len(predictions) / min(FRAMES_TO_TEST, total_frames), f"Analyzing frame {len(predictions)}")

        idx += 1

    cap.release()

    if len(predictions) == 0:
        print("⚠ No frames processed")
        result['error'] = "⚠ No frames processed"
        return result

    avg_pred = float(np.mean(predictions))

    print("Frame Predictions:", [round(float(p),4) for p in predictions])
    print(f"Average Score: {avg_pred:.2f}")

    # -------- CLASSIFICATION --------
    if avg_pred > THRESHOLD:

        label = "REAL"  # Kept as REAL for UI compatibility
        confidence = avg_pred * 100

    else:

        label = "AI GENERATED" # Kept as AI GENERATED for UI compatibility
        confidence = (1 - avg_pred) * 100

    print("Result:", label)
    print(f"Confidence: {confidence:.2f}%")

    # Adapt results for the UI
    result['probability'] = avg_pred
    result['verdict'] = label
    result['confidence'] = confidence / 100.0  # UI expects value between 0.0 and 1.0
    result['frames_analyzed'] = len(predictions)

    return result
