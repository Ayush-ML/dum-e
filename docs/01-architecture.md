# Architecture

Dum-E is built as six layers, each with a narrow, well-defined
responsibility. Data flows top-to-bottom as commands/intent, and
bottom-to-top as sensor feedback, forming a continuous closed loop.

```
┌─────────────────────────────────────┐
│   Personality / behavior engine      │
├─────────────────────────────────────┤
│   Cognitive / task planning          │
├─────────────────────────────────────┤
│   World model / memory               │
├─────────────────────────────────────┤
│   Perception                         │
├─────────────────────────────────────┤
│   Motion planning / control          │
├─────────────────────────────────────┤
│   Actuation (sim / hardware)         │
└─────────────────────────────────────┘
        ↑ continuous sensor feedback ↑
```

---

## 1. Personality / behavior engine

Responsible for making the robot feel like Dum-E rather than a generic
pick-and-place arm.

- **Mood state** — continuous variables (`eagerness`, `confidence`,
  `frustration`) that decay over time and update based on task outcomes.
  Success raises `eagerness`; rejection or a dropped object lowers
  `confidence`.
- **Expressive motion shaping** — mood variables modulate the trajectory
  generator's velocity profile, overshoot, and settling time. High
  eagerness produces a faster approach with a slight overshoot-correct;
  low confidence produces slower, more hesitant motion.
- **Idle-behavior library** — when no task is active, the robot performs
  small idle actions (a slow sweep, a tilt toward detected motion) rather
  than freezing.

## 2. Cognitive / task planning

- **Behavior tree** for task sequencing — chosen over a flat finite state
  machine for composability and cleaner interrupt handling as capabilities
  are added.
- **Local LLM reasoning node** — grounds open-ended natural-language
  commands ("grab the thing near the mug") that a rigid command grammar
  cannot handle. Runs entirely locally (see `03-decisions.md`).
- **Goal arbitration** — explicit priority resolution between an active
  human command and autonomous idle/helpful behavior.

## 3. World model / memory

- **Scene graph** — persistent object identities across frames (not just
  per-frame detections), so an object retains its identity through
  occlusion.
- **Spatial memory** — object permanence for items currently outside the
  camera's field of view.
- **Episodic memory** — a local vector store (ChromaDB + a local embedding
  model) logging past interactions ("fetched the red tool at 14:32, was
  rejected") so behavior can reference history rather than starting cold
  each session.

## 4. Perception

- **Object detection** — YOLOv8, ONNX runtime.
- **Depth estimation** — MiDaS v2.1 small (ONNX), monocular, CPU/iGPU-friendly.
- **Hand/gesture detection** — MediaPipe hand landmarks, used for gesture
  commands (pointing, "come here", "stop").
- **Speech**:
  - `clap_trigger.py` — RMS-based audio transient detection; gates
    listening on a detected double-clap rather than a wake word or
    push-to-talk.
  - `listener.py` — microphone capture and silence detection, active only
    after a confirmed trigger.
  - `transcriber.py` — local speech-to-text via `pywhispercpp`.

## 5. Motion planning / control

- **Inverse kinematics** — `pybullet.calculateInverseKinematics()` against
  the simulated arm's URDF.
- **Trajectory generation** — minimum-jerk profiles, parameterized by the
  personality layer's mood variables.
- **Safety limiting** — joint limit checks and collision checks against
  known object positions from the world model. Implemented and tested in
  simulation now so the logic is already correct before it matters on real
  hardware.

## 6. Actuation

- **Simulation backend** — PyBullet, the only backend currently
  implemented.
- **Hardware abstraction** — all layers above this one talk to a single
  `ActuatorBackend` interface (`set_joint_targets()`), never to PyBullet or
  a serial port directly. Adding real hardware later means implementing one
  new backend class; nothing above this layer changes.

---

## Why this counts as "advanced"

The differentiator is the feedback loop, not any single layer. Perception
continuously updates the world model, which continuously informs planning,
which continuously reshapes behavior. An open-loop script with a
personality skin on top is not sufficient to meet this bar — the loop must
actually close.
