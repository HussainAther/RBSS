# File: scripts/validate_csv.py

"""
Validate a Janus layout CSV.

Checks:
- file exists
- headers include x,y,z,layer_angle_deg
- values are numeric
- optional: row count matches layers*per_layer (if provided)

Example:
  python scripts/validate_csv.py data/janus_layers_concentric.csv --layers 11 --per-layer 24
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import Iterable


REQUIRED_HEADERS = ("x", "y", "z", "layer_angle_deg")


def parse_args():
    p = argparse.ArgumentParser(description="Validate a Janus layout CSV.")
    p.add_argument("csv_path", type=str, help="Path to CSV (e.g., data/janus_layers_concentric.csv)")
    p.add_argument("--layers", type=int, default=None, help="Expected number of layers (optional).")
    p.add_argument("--per-layer", type=int, default=None, help="Expected spheres per layer (optional).")
    return p.parse_args()


def fail(msg: str) -> None:
    raise SystemExit(f"❌ {msg}")


def to_float(row: dict, key: str) -> float:
    try:
        return float(row[key])
    except Exception:
        fail(f"Non-numeric value for '{key}': {row.get(key)}")


def main() -> None:
    args = parse_args()

    if not os.path.exists(args.csv_path):
        fail(f"CSV does not exist: {args.csv_path}")

    with open(args.csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            fail("CSV has no header row.")
        fieldnames = tuple(reader.fieldnames)

        for h in REQUIRED_HEADERS:
            if h not in fieldnames:
                fail(f"Missing required header '{h}'. Found: {fieldnames}")

        n = 0
        angles = set()
        for row in reader:
            _ = to_float(row, "x")
            _ = to_float(row, "y")
            _ = to_float(row, "z")
            ang = to_float(row, "layer_angle_deg")
            angles.add(ang)
            n += 1

    if args.layers is not None and args.per_layer is not None:
        expected = args.layers * args.per_layer
        if n != expected:
            fail(f"Row count mismatch: got {n}, expected {expected} (layers*per_layer).")

    print(f"✅ CSV OK: {args.csv_path}")
    print(f"   rows={n}, unique_layer_angles={len(angles)}")
    if args.layers is not None and args.per_layer is not None:
        print(f"   expected_rows={args.layers * args.per_layer}")


if __name__ == "__main__":
    main()

