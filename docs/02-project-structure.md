# Project Structure

```
dum-e/
├── README.md
├── pyproject.toml
├── config/
│   ├── robot.yaml                  # arm geometry, joint limits, DOF count
│   ├── perception.yaml             # model paths, camera intrinsics
│   ├── behavior.yaml               # mood decay rates, idle-behavior toggles
│   └── logging.yaml
│
├── urdf/
│   ├── dum_e_arm.urdf              # simulated arm description (5-DOF reference)
│   └── meshes/
│
├── models/                         # gitignored — fetched by scripts/fetch_models.py
│   ├── yolov8n.onnx
│   ├── midas_v21_small_256.onnx
│   ├── whisper-base.en.bin
│   └── qwen2.5-3b-instruct-q4_k_m.gguf
│
├── src/
│   └── dum_e/
│       ├── hal/                    # Hardware Abstraction Layer
│       │   ├── base.py             # ActuatorBackend interface
│       │   ├── sim_backend.py      # PyBullet implementation
│       │   └── serial_backend.py   # real hardware, added later
│       │
│       ├── motion/
│       │   ├── kinematics.py       # IK solver
│       │   ├── trajectory.py       # minimum-jerk / trapezoidal profiles
│       │   └── safety.py           # joint limits, collision checks
│       │
│       ├── perception/
│       │   ├── detector.py         # YOLOv8/ONNX object detection
│       │   ├── depth.py            # MiDaS monocular depth
│       │   ├── hands.py            # MediaPipe hand landmarks / gestures
│       │   ├── camera.py           # frame source, calibration
│       │   └── speech/
│       │       ├── clap_trigger.py # RMS transient detection, double-clap gate
│       │       ├── listener.py     # mic capture, VAD, active post-trigger
│       │       └── transcriber.py  # pywhispercpp binding
│       │
│       ├── world_model/
│       │   ├── scene_graph.py      # persistent object identities
│       │   ├── spatial_memory.py   # object permanence when out of frame
│       │   └── episodic_memory.py  # ChromaDB + local embeddings
│       │
│       ├── planning/
│       │   ├── behavior_tree.py    # task sequencing
│       │   ├── arbitration.py      # priority resolution
│       │   └── llm_reasoner.py     # local llama.cpp (Vulkan) reasoning node
│       │
│       ├── behavior/
│       │   ├── mood.py             # eagerness / confidence / frustration state
│       │   ├── idle.py             # idle-behavior library
│       │   └── expressive_motion.py # mood → trajectory parameter mapping
│       │
│       ├── voice/
│       │   └── command_parser.py   # transcript → intent, feeds planning layer
│       │
│       └── main.py                 # top-level loop wiring all layers together
│
├── scripts/
│   ├── fetch_models.py             # downloads/converts all model weights
│   ├── calibrate_camera.py
│   ├── run_sim.py                  # launch PyBullet + full stack
│   └── run_headless_test.py        # perception-only smoke test, no arm
│
├── tests/
│   ├── test_kinematics.py
│   ├── test_scene_graph.py
│   ├── test_behavior_tree.py
│   └── test_speech_pipeline.py
│
├── notebooks/                      # exploratory only — nothing here feeds src/
│   └── ik_visual_debug.ipynb
│
├── data/
│   ├── episodic_memory/            # ChromaDB persistence directory
│   └── logs/
│
└── docs/                           # this documentation set
```

## Design notes

- **`hal/` is the single most important boundary in the codebase.** Every
  layer above it calls `ActuatorBackend.set_joint_targets()` and nothing
  else — never PyBullet, never a serial port, directly. When real hardware
  arrives, `serial_backend.py` is the only new file required.
- **`perception/speech/` is a subpackage, not a single module**, because
  `clap_trigger.py`, `listener.py`, and `transcriber.py` are three distinct
  concerns with three distinct failure modes and are tested independently.
- **`voice/command_parser.py` lives outside `perception/`** deliberately —
  perception's responsibility ends at "here is a transcript"; turning a
  transcript into actionable intent is a planning concern.
- **`world_model/episodic_memory.py`** is intended to be ported directly
  from the equivalent module in the JARVIS project (ChromaDB + local
  embeddings) rather than reimplemented from scratch.
