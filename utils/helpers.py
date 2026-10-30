

import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Constants
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm'}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'scan_history.json'
)
MAX_HISTORY_ENTRIES = 30


#File type helpers 

def get_file_type(path: str) -> Optional[str]:
    """
    Returns 'image', 'video', or None if the file type is unsupported.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in VIDEO_EXTENSIONS:
        return 'video'
    return None


def load_image(path: str) -> Optional[np.ndarray]:
    """
    Robust image loader that handles Unicode file paths on Windows.
    Returns BGR image array or None if loading fails.
    """
    import cv2
    try:
        if not os.path.exists(path):
            return None
        # Use np.fromfile to read file content, then cv2.imdecode
        # This bypasses the C++ imread path which has unicode issues on Windows
        data = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception as exc:
        logger.warning(f"load_image failed for '{path}': {exc}")
        return None


def is_supported_file(path: str) -> bool:
    """Returns True if the file has a supported media extension."""
    return get_file_type(path) is not None


def format_file_size(bytes_size: int) -> str:
    """
    Format a byte count as a human-readable string.
    Examples: '2.4 MB', '847 KB', '12 B'
    """
    for unit in ('B', 'KB', 'MB', 'GB'):
        if bytes_size < 1024:
            if unit == 'B':
                return f"{bytes_size} {unit}"
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def get_file_metadata(path: str) -> dict:
    """
    Extract basic metadata from a media file.

    Returns a dict with:
      - 'filename'   (str)
      - 'extension'  (str)
      - 'size_bytes' (int)
      - 'size_str'   (str)  human-readable size
      - 'type'       (str)  'image' or 'video'
      - 'width'      (int)  0 if unavailable
      - 'height'     (int)  0 if unavailable
      - 'fps'        (float) video only, else 0.0
      - 'duration'   (float) seconds, video only, else 0.0
    """
    meta = {
        'filename': os.path.basename(path),
        'extension': os.path.splitext(path)[1].upper().lstrip('.'),
        'size_bytes': 0,
        'size_str': 'Unknown',
        'type': get_file_type(path) or 'unknown',
        'width': 0,
        'height': 0,
        'fps': 0.0,
        'duration': 0.0,
    }

    try:
        meta['size_bytes'] = os.path.getsize(path)
        meta['size_str'] = format_file_size(meta['size_bytes'])
    except OSError:
        pass

    try:
        import cv2
        if meta['type'] == 'image':
            img = load_image(path)
            if img is not None:
                meta['height'], meta['width'] = img.shape[:2]

        elif meta['type'] == 'video':
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                meta['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                meta['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                meta['fps'] = cap.get(cv2.CAP_PROP_FPS) or 0.0
                total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if meta['fps'] > 0:
                    meta['duration'] = total / meta['fps']
                cap.release()
    except Exception as exc:
        logger.warning(f"Metadata extraction failed: {exc}")

    return meta


def format_duration(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# Scan history

def load_history() -> list:
    """Load scan history from the JSON file. Returns [] on error."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as exc:
        logger.warning(f"Failed to load history: {exc}")
        return []


def save_history(entries: list) -> None:
    """Persist the history list to JSON."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(entries[-MAX_HISTORY_ENTRIES:], f, indent=2, default=str)
    except Exception as exc:
        logger.warning(f"Failed to save history: {exc}")


def append_history_entry(
    file_path: str,
    result: dict,
    media_type: str,
) -> None:
    """
    Append a completed scan result to the persistent history.

    Args:
        file_path:  Full path to the analyzed file.
        result:     Detection result dict from detect_image / detect_video.
        media_type: 'image' or 'video'.
    """
    entries = load_history()

    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'filename': os.path.basename(file_path),
        'filepath': file_path,
        'type': media_type,
        'verdict': result.get('verdict', 'UNKNOWN'),
        'probability': round(result.get('probability', 0.0), 4),
        'confidence': round(result.get('confidence', 0.0), 4),
        'face_detected': result.get('face_detected', False),
        'frames_analyzed': result.get('frames_analyzed', 1),
    }

    entries.append(entry)
    save_history(entries)


def clear_history() -> None:
    """Delete all scan history entries."""
    save_history([])
