# RBYRCT-Houdini Pipeline Usage

This document describes how to run the end-to-end RBYRCT-Houdini simulation pipeline.

## Overview

The pipeline consists of:

1. Generating a concentric Janus-sphere layout
2. (Optional) Exporting beam paths from Houdini
3. Computing detector endpoints
4. Generating a synthetic detector hitmap

All steps can be run with a single command.

---

## Requirements

- Python 3.9+
- Houdini Indie or Apprentice (for hython export)
- Houdini project file (`.hiplc`)

---

## One-Command Pipeline

Run everything (including Houdini export):

```bash
python scripts/run_pipeline.py \
  --hip houdini/projects/bragg_reflection_demo.hiplc \
  --node /obj/janus_beam_reflection/geo1/OUT_REFLECTION
````

---

## Skip Houdini (Use Existing Beam Paths)

If `data/beam_paths.csv` already exists:

```bash
python scripts/run_pipeline.py --skip-houdini
```

---

## Output Files

All outputs are written to the `data/` directory:

| File                          | Description              |
| ----------------------------- | ------------------------ |
| `janus_layers_concentric.csv` | Janus layout geometry    |
| `beam_paths.csv`              | Exported ray paths       |
| `ray_endpoints.csv`           | Detector intersections   |
| `hitmap.csv`                  | 2D detector hitmap       |
| `hitmap_meta.json`            | Hitmap bounds + metadata |

---

## Notes

* The pipeline is designed for **simulation and planning**, not validated dose calculation.
* Geometry, steering logic, and feedback loops are implemented procedurally.
* Monte Carlo or hardware validation can be integrated downstream.

---

## Troubleshooting

* Ensure `hython` is on your PATH
* Verify node path exists in the `.hiplc` file
* Use `validate_csv.py` to check intermediate outputs

