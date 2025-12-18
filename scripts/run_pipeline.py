# File: scripts/run_pipeline.py

"""
Run the end-to-end RBYRCT-Houdini data pipeline.

Pipeline:
1) Generate concentric Janus layout CSV
2) (Optional) Export beam paths from Houdini using hython
3) Compute detector endpoints from beam paths
4) Create detector hitmap

Example:
  python scripts/run_pipeline.py --skip-houdini

Full (with Houdini export):
  python scripts/run_pipeline.py \
    --hip houdini/projects/bragg_reflection_demo.hiplc \
    --node /obj/janus_beam_reflection/geo1/OUT_REFLECTION
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("\n▶", " ".join(cmd))
    r = subprocess.run(cmd, check=False)
    if r.returncode != 0:
        raise SystemExit(f"❌ Command failed with exit code {r.returncode}: {' '.join(cmd)}")


def parse_args():
    p = argparse.ArgumentParser(description="Run RBYRCT-Houdini pipeline.")
    p.add_argument("--out-dir", default="data", help="Output directory (default: data)")
    p.add_argument("--skip-houdini", action="store_true", help="Skip hython export step (assumes beam_paths.csv exists)")
    p.add_argument("--hython", default="hython", help="Path to hython executable (default: hython)")
    p.add_argument("--hip", default="houdini/projects/bragg_reflection_demo.hiplc", help="HIP/HIPLC path")
    p.add_argument("--node", default="/obj/janus_beam_reflection/geo1/OUT_REFLECTION", help="SOP node path to export")
    p.add_argument("--z-det", type=float, default=0.0, help="Detector plane z (default: 0)")
    p.add_argument("--width", type=int, default=256, help="Hitmap width")
    p.add_argument("--height", type=int, default=256, help="Hitmap height")
    p.add_argument("--layers", type=int, default=11, help="Layout layers (for generator)")
    p.add_argument("--per-layer", type=int, default=24, help="Spheres per layer (for generator)")
    p.add_argument("--ring-radius", type=float, default=20.0, help="Ring radius (for generator)")
    p.add_argument("--spacing", type=float, default=2.5, help="Layer spacing (for generator)")
    p.add_argument("--step-deg", type=float, default=4.0, help="Layer angle step in degrees")
    return p.parse_args()


def main():
    a = parse_args()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    layout_csv = out_dir / "janus_layers_concentric.csv"
    beam_paths_csv = out_dir / "beam_paths.csv"
    endpoints_csv = out_dir / "ray_endpoints.csv"
    hitmap_csv = out_dir / "hitmap.csv"
    hitmap_meta = out_dir / "hitmap_meta.json"

    # 1) Generate layout CSV
    run([
        sys.executable, "scripts/janus_array_gen.py",
        "--layers", str(a.layers),
        "--per-layer", str(a.per_layer),
        "--ring-radius", str(a.ring_radius),
        "--spacing", str(a.spacing),
        "--step-deg", str(a.step_deg),
        "--out-dir", str(out_dir),
        "--out-name", layout_csv.name,
    ])

    # 2) Export beam paths from Houdini (optional)
    if not a.skip_houdini:
        run([
            a.hython, "scripts/export_beam_paths.py",
            "--hip", a.hip,
            "--node", a.node,
            "--out", str(beam_paths_csv),
        ])
    else:
        if not beam_paths_csv.exists():
            raise SystemExit(f"❌ --skip-houdini set, but missing {beam_paths_csv}")

    # 3) Compute detector endpoints
    cmd = [
        sys.executable, "scripts/make_endpoints_from_paths.py",
        str(beam_paths_csv),
        "--z-det", str(a.z_det),
        "--out", str(endpoints_csv),
        "--write-weight",
    ]
    run(cmd)

    # 4) Create hitmap
    run([
        sys.executable, "scripts/export_detector_hitmap.py",
        str(endpoints_csv),
        "--out", str(hitmap_csv),
        "--meta", str(hitmap_meta),
        "--width", str(a.width),
        "--height", str(a.height),
    ])

    # 5) Validate layout CSV (optional sanity check)
    run([
        sys.executable, "scripts/validate_csv.py",
        str(layout_csv),
        "--layers", str(a.layers),
        "--per-layer", str(a.per_layer),
    ])

    print("\n✅ Pipeline complete. Outputs:")
    print(f"  layout:    {layout_csv}")
    print(f"  paths:     {beam_paths_csv}")
    print(f"  endpoints: {endpoints_csv}")
    print(f"  hitmap:    {hitmap_csv}")
    print(f"  meta:      {hitmap_meta}")


if __name__ == "__main__":
    main()

