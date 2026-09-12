# Decision Log

Lightweight ADR-style record of the choices made so far and the reasoning
behind each. Newest entries at the bottom.

---

### D1 — Simulation-first, no hardware assumed

**Decision:** Build and validate the entire stack in simulation (PyBullet)
before any physical hardware is acquired.

**Reasoning:** No hardware currently owned; laptop-only development.
Validating perception, planning, and safety logic in simulation is strictly
cheaper than doing so against real actuators, and the hardware abstraction
layer (see D2) means nothing is lost by starting here.

---

### D2 — Hardware abstraction from day one

**Decision:** All motion/actuation code talks to a single `ActuatorBackend`
interface (`set_joint_targets()`). PyBullet is one implementation; a serial
hardware backend is a second implementation added later.

**Reasoning:** Keeps the simulation-to-hardware transition to "add one new
file" rather than a rewrite of the motion stack.

---

### D3 — PyBullet over MuJoCo or Gazebo/ROS2

**Decision:** PyBullet as the simulator.

**Reasoning:** Pure Python, minimal setup, sufficient physical accuracy for
a single-arm project. MuJoCo is more accurate but has a steeper learning
curve; Gazebo/ROS2 is the "industry standard" but drags in a heavy
dependency stack not justified for a solo laptop project.

---

### D4 — Local-only inference across the stack

**Decision:** No cloud API dependency for vision, speech, or reasoning.
Everything runs on-device.

**Reasoning:** Consistent with an established preference for fully local,
offline-capable systems (also applied to the JARVIS project).

---

### D5 — Perception model choices

- **Object detection:** YOLOv8n, ONNX runtime — reused directly from the
  CleanStreets AI project.
- **Depth estimation:** MiDaS v2.1 small, ONNX export — EfficientNet-Lite3
  encoder, 256×256 input, ~80MB, explicitly CPU/iGPU-friendly. Published
  directly by Intel ISL, no conversion pipeline needed.
- **Hand/gesture detection:** MediaPipe hand landmarks — reused from prior
  holding-detection work, repurposed for gesture commands.

---

### D6 — Speech-to-text: `pywhispercpp`

**Decision:** Use the `pywhispercpp` (absadiki) binding for whisper.cpp
rather than shelling out to a whisper.cpp binary or a different binding.

**Reasoning:** Provides a simple Pythonic API over the full whisper.h
surface, ships a working microphone-based assistant example with
configurable silence threshold, and supports optional OpenBLAS/CUDA build
flags if CPU-only inference proves too slow.

---

### D7 — Compute target: integrated GPU

**Decision:** Confirmed — laptop has an integrated/non-CUDA GPU. All model
and runtime choices are made against this constraint.

**Reasoning:** Rules out CUDA-only tooling; favors Vulkan (cross-vendor) or
CPU fallback throughout the stack.

---

### D8 — Local LLM: llama.cpp + Vulkan, Qwen2.5-3B-Instruct

**Decision:** Run the cognitive reasoning node via llama.cpp's Vulkan
backend, using `Qwen2.5-3B-Instruct` (Q4_K_M GGUF quantization).

**Reasoning:** llama.cpp's Vulkan backend supports AMD, Intel, and NVIDIA
GPUs without requiring CUDA — a documented benchmark showed a 2015-era
integrated GPU running a 1.1B model roughly 33× faster on Vulkan than CPU
alone. A 3B model is small enough to share the iGPU's memory budget with
the rest of the perception pipeline (YOLO, MiDaS, Whisper all running
concurrently) while still giving adequate instruction-following for command
grounding.

**Known risk:** Some recent Intel Lunar Lake / unified-memory-architecture
chips have open driver bugs with llama.cpp's Vulkan backend as of this
writing. If the target iGPU is a newer Intel part and Vulkan acceleration
misbehaves, CPU fallback is a single config flag away.

---

### D9 — Voice activation: double-clap trigger

**Decision:** Voice listening is gated by a detected double-clap, not a
wake word or push-to-talk button.

**Reasoning:** This is an audio transient detection problem, not a speech
problem — a wake-word model would be unnecessary overhead. Implementation:
continuous RMS energy monitoring in small (~20–30ms) windows via
`sounddevice`; a "clap" is a sharp energy spike followed by rapid decay;
two such spikes within a ~600ms window confirm a double-clap and hand off
to the Whisper listener for the actual command capture window.

---

### D10 — Concurrency model: asyncio

**Decision:** The main loop uses asyncio rather than threading.

**Reasoning:** Cleaner cancellation semantics when a new command needs to
interrupt an in-progress task — relevant given perception, speech, and
planning all run concurrently on a single laptop's CPU/GPU budget.

---

### D11 — Reference arm geometry

**Decision:** A generic 5-DOF arm (base rotate, shoulder, elbow, wrist
pitch, gripper) is used as the URDF reference in the absence of specific
target hardware.

**Reasoning:** Reasonable stand-in that keeps the IK and trajectory work
meaningful without hardware commitment; easily swapped for a specific
arm's geometry once hardware is chosen.
