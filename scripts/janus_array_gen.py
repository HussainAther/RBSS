# File: scripts/janus_array_gen.py

"""
Janus Sphere Layer Generator (Concentric Rings)
Generates a concentric ring layout of Janus spheres for Ray-by-Ray CT simulation.

Each layer consists of spheres positioned on a circle around the origin.
Layer deflection increases by step_deg per layer (default 4 degrees).
Outputs to CSV for import into Houdini or other pipelines.

Example:
  python scripts/janus_array_gen.py --layers 11 --per-layer 24 --ring-radius 20 --spacing 2.5 --step-deg 4
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass

import numpy as np


@dataclass
class Config:
    layers: int
    per_layer: int
    ring_radius: float
    spacing: float
    step_deg: float
    out_dir: str
    out_name: str


def parse_args() -> Config:
    p = argparse.ArgumentParser(description="Generate concentric Janus-sphere layout CSV.")
    p.add_argument("--layers", type=int, default=11, help="Number of layers stacked in Z.")
    p.add_argument("--per-layer", type=int, default=24, help="Number of spheres per ring layer.")
    p.add_argument("--ring-radius", type=float, default=20.0, help="Radius of each ring in XY.")
    p.add_argument("--spacing", type=float, default=2.5, help="Z spacing between layers.")
    p.add_argument("--step-deg", type=float, default=4.0, help="Deflection angle increment per layer (deg).")
    p.add_argument("--out-dir", type=str, default="data", help="Output directory.")
    p.add_argument("--out-name", type=str, default="janus_layers_concentric.csv", help="Output CSV filename.")
    a = p.parse_args()

    if a.layers <= 0:
        raise SystemExit("--layers must be > 0")
    if a.per_layer <= 0:
        raise SystemExit("--per-layer must be > 0")
    if a.ring_radius <= 0:
        raise SystemExit("--ring-radius must be > 0")
    if a.spacing <= 0:
        raise SystemExit("--spacing must be > 0")

    return Config(
        layers=a.layers,
        per_layer=a.per_layer,
        ring_radius=a.ring_radius,
        spacing=a.spacing,
        step_deg=a.step_deg,
        out_dir=a.out_dir,
        out_name=a.out_name,
    )


def generate(cfg: Config) -> list[list[float]]:
    rows: list[list[float]] = []
    angle_step = 2 * np.pi / cfg.per_layer

    for i in range(cfg.layers):
        z = i * cfg.spacing
        layer_angle = i * cfg.step_deg  # degrees

        for j in range(cfg.per_layer):
            theta = j * angle_step
            x = cfg.ring_radius * np.cos(theta)
            y = cfg.ring_radius * np.sin(theta)
            rows.append([float(x), float(y), float(z), float(layer_angle)])

    return rows


def write_csv(cfg: Config, rows: list[list[float]]) -> str:
    os.makedirs(cfg.out_dir, exist_ok=True)
    path = os.path.join(cfg.out_dir, cfg.out_name)

    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "z", "layer_angle_deg"])
        w.writerows(rows)

    return path


def main() -> None:
    cfg = parse_args()
    rows = generate(cfg)
    path = write_csv(cfg, rows)

    expected = cfg.layers * cfg.per_layer
    print(f"✅ Wrote {len(rows)} rows (expected {expected}) to: {path}")
    print(f"   layers={cfg.layers}, per_layer={cfg.per_layer}, ring_radius={cfg.ring_radius}, spacing={cfg.spacing}, step_deg={cfg.step_deg}")


if __name__ == "__main__":
    main()

