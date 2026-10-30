# REVELIO — AI Media Authentication System

> A professional deepfake detection desktop application built with Python, TensorFlow, OpenCV, and KivyMD.

---

## Overview

VERIDECT is a fully offline AI-powered tool that analyses images and videos to determine whether they are **authentic** or **AI-generated deepfakes**. It is designed for media analysts, cybersecurity professionals, and AI/ML students.

---

## Project Structure

```
veridect/
├── main.py                        ← Entry point (run this)
├── requirements.txt               ← Python dependencies
├── deepfake_detector_finetuned_v3.h5  ← Your trained model (place here)
├── scan_history.json              ← Auto-generated scan history
│
├── core/                          ← Business logic layer
│   ├── __init__.py
│   ├── model_loader.py            ← TF model loading & inference
│   ├── face_utils.py              ← Haar Cascade face detection
│   ├── image_detector.py          ← Image detection pipeline
│   └── video_detector.py          ← Video detection pipeline
│
├── ui/                            ← UI layer
│   ├── __init__.py
│   ├── app.py                     ← KivyMD app class, theme, navigation
│   ├── widgets.py                 ← Custom widgets: ConfidenceArc, VerdictBadge
│   └── screens/
│       ├── __init__.py
│       ├── analyze_screen.py      ← Main detection screen
│       └── history_screen.py      ← Scan history screen
│
└── utils/
    ├── __init__.py
    └── helpers.py                 ← File metadata, history persistence
```

---

## Setup

### 1. Prerequisites

- **Python 3.9+** (3.10 or 3.11 recommended)
- **pip**

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows users:** If you get OpenGL errors, install `kivy[full]` instead of plain `kivy`.

### 3. Place your model

Copy your trained model into the project root:

```
veridect/
└── deepfake_detector_finetuned_v3.h5   ← here
```

If the model file is absent, the app runs in **DEMO mode** — it still functions fully but uses random predictions.

### 4. Launch

```bash
python main.py
```

---

## Model Specification

| Property      | Value                     |
|---------------|---------------------------|
| Architecture  | MobileNetV2-based CNN     |
| Input size    | 160 × 160 RGB             |
| Output        | Probability in `[0.0, 1.0]` |
| Threshold     | `>= 0.6` → **AI GENERATED** |
|               | `< 0.6`  → **REAL**       |

---

## Detection Pipelines

### Image Pipeline
```
Load image (OpenCV)
    │
    ▼
Face Detection (Haar Cascade)
    ├── Face found → crop face region + padding
    └── No face   → use full image
    │
    ▼
Resize to 160×160
Normalize to [0.0, 1.0]
    │
    ▼
Model Inference → probability score
    │
    ▼
probability >= 0.6 → AI GENERATED
probability  < 0.6 → REAL
```

### Video Pipeline
```
Open video (OpenCV VideoCapture)
    │
    ▼
Sample every N frames (configurable, default: 10)
    │
    ▼
Run Image Pipeline on each sampled frame
    │
    ▼
Collect per-frame probability scores
    │
    ▼
Average scores → final probability
    │
    ▼
Apply threshold → final verdict
```

---

## Screens

### ANALYZE Screen
- **Upload zone** — click or browse to select an image or video
- **Preview card** — thumbnail, filename, dimensions, size, duration
- **Settings panel** — face detection toggle, frame interval slider (video)
- **SCAN button** — starts analysis in a background thread
- **Progress bar** — shows real-time progress for video scans
- **Results card** — verdict, confidence bar, raw probability, arc gauge

### HISTORY Screen
- Scrollable table of all past scans
- Colour-coded rows: green (REAL), red (AI GENERATED)
- Columns: filename, verdict, confidence, timestamp
- Clear all history button

---

## Status Indicator

The header shows the current model state:

| Status       | Meaning                              |
|--------------|--------------------------------------|
| 🟡 INITIALIZING | App is starting                    |
| 🟢 MODEL READY  | Model loaded successfully          |
| 🟡 DEMO MODE    | Model file not found — random predictions |
| 🔴 MODEL ERROR  | Model failed to load               |

---

## Customisation

### Change the detection threshold

In `core/model_loader.py`:
```python
FAKE_THRESHOLD = 0.6   # Change to your desired threshold
```

### Use a different model

In `core/model_loader.py`:
```python
MODEL_FILENAME = 'your_model.h5'
```

### Change frame sampling rate

Either use the slider in the UI, or change the default in `core/video_detector.py`:
```python
def detect_video(video_path, frame_interval=10, ...):
```

### Enable MediaPipe face detection (optional)

1. `pip install mediapipe`
2. In `core/face_utils.py`, replace the Haar Cascade detector with the MediaPipe face mesh / detection pipeline. The `detect_and_crop_face()` function signature stays the same.

---

## Architecture Notes

The code is split into three distinct layers with no circular imports:

```
utils/  ──────────────────────────────────────────┐
  helpers.py  (file I/O, metadata, history)        │
                                                   │
core/  ──────────────────────────────────────────  │
  model_loader.py  (TF model, inference)           │
  face_utils.py    (OpenCV face detection)  ←──────┤ no UI imports
  image_detector.py (full image pipeline)          │
  video_detector.py (full video pipeline)          │
                                                   │
ui/  ────────────────────────────────────────────  │
  app.py                                           │
  widgets.py                                       │
  screens/                                    imports core + utils
    analyze_screen.py
    history_screen.py
```

---

## Known Limitations

- Face detection uses OpenCV Haar Cascade which may miss faces at extreme angles. For higher accuracy, replace with MediaPipe or MTCNN.
- Video analysis is single-threaded; for very long videos, increase `frame_interval` or `max_frames`.
- The model accuracy depends entirely on your training data and the provided `.h5` file.

---

## License

For academic / portfolio use. Replace this section with your actual license.
