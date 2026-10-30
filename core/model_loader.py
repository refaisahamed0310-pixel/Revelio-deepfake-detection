"""
core/model_loader.py
─────────────────────
Handles loading and caching the deepfake ensemble models using user's provided logic.
"""

import os
import logging
from tensorflow.keras.models import load_model as tf_load_model

logger = logging.getLogger(__name__)

# Constants
MODEL1_FILENAME = 'deepfake_efficientnetb0_best1.h5'
MODEL2_FILENAME = 'deepfake_efficientnetb0_final1.h5'
VIDEO_MODEL_FILENAME = 'deepfake_video_model_v2.h5'

# Global cache
_model1 = None
_model2 = None
_video_model = None
_model_status = 'unloaded'

def get_model_status() -> str:
    return _model_status

def load_models():
    """Load both ensemble models into global cache."""
    global _model1, _model2, _video_model, _model_status
    
    if _model_status != 'unloaded':
        return

    # Resolve paths relative to project root
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p1 = os.path.join(root, MODEL1_FILENAME)
    p2 = os.path.join(root, MODEL2_FILENAME)
    pv = os.path.join(root, VIDEO_MODEL_FILENAME)

    try:
        if os.path.exists(pv):
            _video_model = tf_load_model(pv, compile=False)
            
        if os.path.exists(p1) and os.path.exists(p2):
            logger.info("Models loaded successfully")
            _model1 = tf_load_model(p1, compile=False)
            _model2 = tf_load_model(p2, compile=False)
            _model_status = 'both'
        elif os.path.exists(p1):
            _model1 = tf_load_model(p1, compile=False)
            _model_status = 'model1'
        elif os.path.exists(p2):
            _model2 = tf_load_model(p2, compile=False)
            _model_status = 'model2'
        else:
            _model_status = 'demo'
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        _model_status = 'failed'

def load_model(path: str = None):
    """Alias for load_models."""
    load_models()
    return None
