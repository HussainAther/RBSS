## Vision: RBYRCT Beam Steering Studio (RBSS)

RBYRCT-Houdini is the foundation for **RBYRCT Beam Steering Studio (RBSS)** — a purpose-built simulation, planning, and control platform for **electronically steerable X-ray beams**.

Unlike conventional CT (fan/cone beam), RBYRCT is **ray-by-ray**: the system can actively steer a micro-beam, estimate uncertainty, and **stop early** once targets are detected to minimize dose.

### What RBSS will do
- **Simulate beam steering** through layered Janus reflectors (Bragg-angle steering)
- **Plan steering sequences** under dose and angle constraints (beam “flight plan”)
- **Run an adaptive feedback loop** that corrects misalignment and drift
- **Export datasets** (beam paths, detector hitmaps) for ML and reconstruction experiments
- Provide a path from **simulation → prototype hardware control** via a clean command format

### Near-term milestones
- Houdini demo scene (`.hiplc`) showing layered steering + attenuation
- CSV-driven geometry generation and import workflow
- VEX/Python core for Bragg steering and efficiency modeling
- Synthetic detector hitmap exporter for ML/reconstruction

## ▶️ Pipeline Quickstart

Run the full pipeline (layout → Houdini export → endpoints → hitmap):

```bash
python scripts/run_pipeline.py \
  --hip houdini/projects/bragg_reflection_demo.hiplc \
  --node /obj/janus_beam_reflection/geo1/OUT_REFLECTION
```
