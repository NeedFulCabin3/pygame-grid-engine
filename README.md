# Pygame Grid Engine

> A decoupled 2D arcade loop engine featuring synthetic audio wave generation, strict vector direction validation, and persistent file state.

## Overview

Developing 2D arcade applications often introduces friction around external asset dependencies, unstable input state handling, and bloated multimedia pipelines. `pygame-grid-engine` provides a zero-asset architectural foundation for grid-based mechanics. By generating square-wave audio tones directly in memory using Python standard byte buffers and enforcing deterministic grid-aligned collision passes, this project eliminates external media file asset management while keeping frame timing and input queues cleanly decoupled.

## How It Works

```text
+-------------------------------------------------------------+
|                     Pygame Clock (12 FPS)                   |
+-------------------------------------------------------------+
|
v
+-------------------------------------------------------------+
|                   Input Event Handler                       |
|   (Queues direction vector, validates 180-degree anti-reverse)|
+-------------------------------------------------------------+
|
v
+-------------------------------------------------------------+
|                  Game State & Engine Update                 |
|  - Advance Snake Head Coordinate                            |
|  - Check Grid Boundary & Self Collision Array               |
|  - Process Food Coordinate Match & Tail Growth               |
+-------------------------------------------------------------+
|                                   |
(Collision Fail)                    (Food Eaten)
|                                   |
v                                   v
+--------------------------+       +--------------------------+
| Save High Score via JSON |       | Synth Audio Playback     |
| Render Alpha Modal UI    |       | (Raw Bytearray Buffer)    |
+--------------------------+       +--------------------------+
```

1. **Synthetic Audio Buffer Synthesis**: Sound effects are constructed at runtime inside standard bytearrays. Square waves are calculated using target frequencies, packed into 8-bit signed integer formats, and passed to `pygame.mixer.Sound` directly from raw memory.
2. **Direction Control Mechanics**: Player inputs write to a `next_direction` tuple buffer. The engine verifies that incoming vectors do not equal the inverted active vector `(dx * -1, dy * -1)`, preventing self-collision bugs caused by rapidly tapping opposing keys within a single frame tick.
3. **Discrete Coordinate System**: Entity locations map to integer grid coordinates `(x, y)` rather than continuous pixel floats. Rectangles and collision ellipses scale dynamically during render passes according to `GRID_SIZE`.
4. **Persistent I/O Integrity**: High scores load on initialization and serialize to disk when a game-ending collision triggers. Safe exceptions suppress unhandled standard file I/O crashes on read-only filesystems.

## Key Features

* **Zero Asset Audio Generation**: On-the-fly synthesis of interactive game sound effects using raw PCM byte buffers.
* **Robust Input Guard**: Mathematical inversion check preventing instantaneous backwards movement self-collisions.
* **Deterministic Collision Loop**: Discrete array boundary checking for grid walls and snake segment intersection.
* **Resilient State Persistence**: JSON-backed high score tracker with safe load and fallback state initialization.
* **Clean Screen Rendering**: Native Pygame surface blitting with semi-transparent RGBA overlays during game-over state transitions.

## Tech Stack & Core Dependencies Breakdown

* **Python 3.10+**: Core runtime environment providing structural type hints (`tuple[int, int]`, `list[tuple[int, int]]`).
* **Pygame-ce / Pygame 2.5+**: Primary interface engine utilized for display rendering, event loops, and raw PCM audio array mixing.
* **Standard Library Modules**:
  * `json`: Structured disk serialization for persistent scoring metrics.
  * `random`: Uniform pseudo-random position generation for grid items.
  * `sys` & `os`: System file path resolution and clean process termination.

## Environment & Web-Based Quick Start

### Running in GitHub Codespaces
1. Click the **Code** button on the GitHub repository page.
2. Select the **Codespaces** tab and click **Create codespace on main**.
3. Once the environment initializes, open the integrated terminal and execute:
   ```bash
   pip install pygame
   python main.py
   ```

### Local Virtual Environment Setup

```text
# Clone and enter directory
git clone [https://github.com/your-username/pygame-grid-engine.git](https://github.com/your-username/pygame-grid-engine.git)
cd pygame-grid-engine

# Initialize virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and execute
pip install pygame
python main.py
```

## Repository Structure

```text
pygame-grid-engine/
├── .github/
│   └── workflows/
│       └── ci.yml             # Code quality verification & syntax checks
├── .gitignore                 # Python runtime, Pygame bytecode, & local file ignore rules
├── LICENSE                    # MIT Open-Source License file
├── README.md                  # Comprehensive technical overview & documentation
├── highscore.json             # Local persistent store created at runtime (ignored by git)
└── main.py                    # Core entry point, game loop, rendering engine, and audio synthesis
```

## Roadmap

[ ] Async High Score Persistence: Migrate synchronous JSON operations to asynchronous background threads to avoid blocking the game loop during disk writes.

[ ]Dynamic Frame Interpolation: Decouple game logic updates (tick rate) from rendering refresh rates to allow smooth sub-grid interpolation.

[ ]Structured Sound Synthesizer: Expand the square wave synthesis function to support ADSR (Attack, Decay, Sustain, Release) envelopes and custom waveform tables.