# Setup

## Prerequisites

- Python (version pinned in `.python-version`)
- A Vulkan-capable driver for the integrated GPU (required for accelerated
  local LLM inference — see D8 in `03-decisions.md`)
- `ffmpeg` (required by `pywhispercpp` for non-WAV audio handling)

## Environment

```bash
# from the project root
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
```

Dependencies of note (final list lives in `pyproject.toml`):

- `pybullet` — simulation and IK
- `onnxruntime` — YOLOv8 and MiDaS inference
- `mediapipe` — hand landmark detection
- `pywhispercpp` — local speech-to-text
- `sounddevice` — microphone capture, clap-trigger energy monitoring
- `chromadb` — episodic memory store
- `llama-cpp-python` (Vulkan build) or a local `llama.cpp` server binary —
  reasoning node backend

## Fetching models

```bash
python scripts/fetch_models.py
```

Downloads and places the following into `models/` (gitignored):

| File | Purpose |
|---|---|
| `yolov8n.onnx` | Object detection |
| `midas_v21_small_256.onnx` | Monocular depth estimation |
| `whisper-base.en.bin` | Speech-to-text |
| `qwen2.5-3b-instruct-q4_k_m.gguf` | Local reasoning node |

## Running the simulation

```bash
python scripts/run_sim.py
```

Launches PyBullet with the arm loaded from `urdf/dum_e_arm.urdf`, starts
the perception pipeline against the default webcam, and brings up the
double-clap listener.

## Running a perception-only smoke test

Useful for validating the camera, detector, and depth pipeline without
touching the simulator:

```bash
python scripts/run_headless_test.py
```

## Configuration

Runtime behavior is controlled by the YAML files in `config/`:

- `robot.yaml` — arm geometry, joint limits, DOF count
- `perception.yaml` — model paths, camera intrinsics
- `behavior.yaml` — mood decay rates, idle-behavior toggles
- `logging.yaml` — log verbosity and output targets

## Tests

```bash
pytest tests/
```
