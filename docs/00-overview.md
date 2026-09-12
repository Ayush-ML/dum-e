# Dum-E — Project Overview

## What this is

Dum-E is a software system for a Dum-E-style (Iron Man) assistant robot arm.
The initial build target is a **full simulation** running on a single laptop
with an integrated GPU — no physical hardware is assumed or required to
develop, test, or demo the system. The architecture is designed so that a
real arm can be swapped in later without changes above the hardware
abstraction layer.

## Goals

- Close the full perception → cognition → motion → actuation loop, not just
  script an open-loop demo.
- Give the robot a distinct, expressive personality layer, not just
  functional pick-and-place behavior.
- Run entirely on local, offline inference — no cloud API dependency for
  core functionality (vision, speech, or reasoning).
- Keep the hardware layer swappable from day one, so simulation-to-real
  transition is a config change, not a rewrite.

## Non-goals (for this phase)

- Physical hardware integration (deferred until hardware is acquired).
- Multi-arm or multi-robot coordination.
- Cloud-based reasoning or telemetry.

## High-level architecture

Six layers, top to bottom:

1. **Personality / behavior engine** — mood state, expressive motion shaping
2. **Cognitive / task planning** — behavior tree, goal arbitration, local LLM reasoning
3. **World model / memory** — scene graph, spatial memory, episodic memory
4. **Perception** — vision, depth, hands, speech
5. **Motion planning / control** — inverse kinematics, trajectories, safety limits
6. **Actuation** — PyBullet simulation now, real hardware backend later

See [`01-architecture.md`](./01-architecture.md) for the full breakdown of
each layer, and [`02-project-structure.md`](./02-project-structure.md) for
how this maps onto the actual codebase.

## Key project decisions

See [`03-decisions.md`](./03-decisions.md) for the full decision log,
including hardware assumptions, model choices, and the reasoning behind
each.

## Getting started

See [`04-setup.md`](./04-setup.md) for environment setup, model downloads,
and how to run the simulation.
