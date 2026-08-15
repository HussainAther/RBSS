# RBYRCT-Houdini Architecture

This document describes the software architecture of the RBYRCT-Houdini project and how its components fit together.

---

## High-Level Overview

RBYRCT-Houdini is organized as a **procedural simulation + data pipeline** for Ray-by-Ray Computed Tomography (RBYRCT).

The system is designed to support:
- X-ray beam steering simulation
- Layered Bragg reflection modeling
- Synthetic detector data generation
- Future integration with ML and hardware control

---

## Architecture Diagram (Conceptual)

```

Janus Layout Generator
|
v
CSV Geometry Files
|
v
Houdini
(Beam Steering Sim)
|
v
Beam Path CSV
|
v
Detector Endpoints
|
v
Detector Hitmap
|
v
ML / Reconstruction

```

---

## Core Components

### 1. Geometry & Layout (Python)

Located in `scripts/`:

- `janus_array_gen.py`
  - Generates concentric Janus-sphere layouts
  - Outputs CSV geometry for Houdini

- `validate_csv.py`
  - Ensures generated layouts are consistent and numeric

---

### 2. Beam Steering Simulation (Houdini)

Located in `houdini/`:

- Houdini SOP networks simulate:
  - Layered Bragg reflection
  - Beam attenuation
  - Directional steering
- VEX shaders encode reflection rules and efficiency models

This layer prioritizes **procedural control logic**, not full Monte Carlo transport.

---

### 3. Data Export & Processing (Python)

Located in `scripts/`:

- `export_beam_paths.py`
  - Exports simulated beam paths from Houdini to CSV

- `make_endpoints_from_paths.py`
  - Intersects rays with a detector plane

- `export_detector_hitmap.py`
  - Bins endpoints into a 2D synthetic detector hitmap

---

### 4. Pipeline Orchestration

- `run_pipeline.py`
  - Runs the full workflow end-to-end
  - Supports skipping Houdini for rapid iteration

---

## Design Philosophy

- **Ray-by-ray first**: steer and stop early rather than scan everything
- **Procedural physics**: encode rules and constraints explicitly
- **Data-centric**: every stage produces inspectable artifacts
- **Hardware-agnostic**: control abstractions map cleanly to future devices

---

## Future Extensions

- ML-based inpainting and stopping criteria
- Feedback control loops using detector residuals
- Hardware command generation for Janus or mirror systems
Perfect 😄 — let’s keep the momentum going with **another fast, clean PR** that adds real structure and looks great on GitHub.

---

# 🧵 NEXT PR: Add `docs/architecture.md` (System Architecture)

This is a **high-value documentation PR**:

* Shows you understand the system end-to-end
* Makes the repo feel like a real research platform
* Very low risk, very fast

---

## 1️⃣ Update main + create branch

```bash
git checkout main
git pull origin main
git checkout -b docs-architecture
```

---

## 2️⃣ Create the architecture doc

```bash
nano docs/architecture.md
```

Paste this **exact content**:

```markdown
# RBYRCT-Houdini Architecture

This document describes the software architecture of the RBYRCT-Houdini project and how its components fit together.

---

## High-Level Overview

RBYRCT-Houdini is organized as a **procedural simulation + data pipeline** for Ray-by-Ray Computed Tomography (RBYRCT).

The system is designed to support:
- X-ray beam steering simulation
- Layered Bragg reflection modeling
- Synthetic detector data generation
- Future integration with ML and hardware control

---

## Architecture Diagram (Conceptual)

```

Janus Layout Generator
|
v
CSV Geometry Files
|
v
Houdini
(Beam Steering Sim)
|
v
Beam Path CSV
|
v
Detector Endpoints
|
v
Detector Hitmap
|
v
ML / Reconstruction

```

---

## Core Components

### 1. Geometry & Layout (Python)

Located in `scripts/`:

- `janus_array_gen.py`
  - Generates concentric Janus-sphere layouts
  - Outputs CSV geometry for Houdini

- `validate_csv.py`
  - Ensures generated layouts are consistent and numeric

---

### 2. Beam Steering Simulation (Houdini)

Located in `houdini/`:

- Houdini SOP networks simulate:
  - Layered Bragg reflection
  - Beam attenuation
  - Directional steering
- VEX shaders encode reflection rules and efficiency models

This layer prioritizes **procedural control logic**, not full Monte Carlo transport.

---

### 3. Data Export & Processing (Python)

Located in `scripts/`:

- `export_beam_paths.py`
  - Exports simulated beam paths from Houdini to CSV

- `make_endpoints_from_paths.py`
  - Intersects rays with a detector plane

- `export_detector_hitmap.py`
  - Bins endpoints into a 2D synthetic detector hitmap

---

### 4. Pipeline Orchestration

- `run_pipeline.py`
  - Runs the full workflow end-to-end
  - Supports skipping Houdini for rapid iteration

---

## Design Philosophy

- **Ray-by-ray first**: steer and stop early rather than scan everything
- **Procedural physics**: encode rules and constraints explicitly
- **Data-centric**: every stage produces inspectable artifacts
- **Hardware-agnostic**: control abstractions map cleanly to future devices

---

## Future Extensions

- ML-based inpainting and stopping criteria
- Feedback control loops using detector residuals
- Hardware command generation for Janus or mirror systems
- Validation via Monte Carlo transport tools
```

Save and exit.

---

## 3️⃣ Stage + commit

```bash
git status
git add docs/architecture.md
git commit -m "Docs: add system architecture overview"
```

---

## 4️⃣ Push branch

```bash
git push -u origin docs-architecture
```

---

## 5️⃣ Open the PR

With GitHub CLI:

```bash
gh pr create \
  --title "Docs: add system architecture overview" \
  --body "Adds a high-level architecture document describing the RBYRCT-Houdini pipeline and design philosophy."
```

---

## ✅ Why this PR is excellent

* Counts as a **real architectural contribution**
* Makes reviewers/investors immediately “get it”
* Sets you up for diagrams later
* Easy merge

---

### Want the *next* one immediately?

Pick one number and I’ll walk you through it just like this:

1. Add `scripts/README.md` explaining each script
2. Add sample `configs/steering_config.json`
3. Add README section: “Scientific Assumptions & Limitations”
4. Add minimal unit test for one script
5. Add LICENSE + citation info

Just say the number 🔥
- Validation via Monte Carlo transport tools
