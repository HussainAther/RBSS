# File: scripts/export_detector_hitmap.py

"""
Export a synthetic detector hitmap from ray endpoints.

Input CSV format (minimum):
  x,y          (endpoints in detector plane coordinates)
Optional:
  w            (weight / intensity per ray)

Outputs:
- hitmap CSV with rows of integer counts (or weighted sums)
- metadata JSON (optional) describing bounds and resolution

Example:
  python scripts/export_detector_hitmap.py data/ray_endpoints.csv --out data/hitmap.csv --width 256 --height 256 --bounds -50 50 -50 50

If bounds are not provided, they are inferred from the data (with small padding).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass

import numpy as np


@dataclass
class Bounds:
    xmin: float
    xmax: float
    ymin: float
    ymax: float


def parse_args():
    p = argparse.ArgumentParser(description="Export detector hitmap from ray endpoints CSV.")
    p.add_argument("endpoints_csv", type=str, help="Input CSV with columns: x,y[,w]")
    p.add_argument("--out", type=str, default="data/hitmap.csv", help="Output hitmap CSV path")
    p.add_argument("--meta", type=str, default="data/hitmap_meta.json", help="Output metadata JSON path")
    p.add_argument("--width", type=int, default=256, help="Hitmap width (pixels)")
    p.add_argument("--height", type=int, default=256, help="Hitmap height (pixels)")
    p.add_argument(
        "--bounds",
        type=float,
        nargs=4,
        default=None,
        metavar=("XMIN", "XMAX", "YMIN", "YMAX"),
        help="Explicit bounds for binning. If omitted, inferred from data.",
    )
    p.add_argument("--weight-col", type=str, default="w", help="Weight column name if present (default: w).")
    p.add_argument("--x-col", type=str, default="x", help="X column name (default: x).")
    p.add_argument("--y-col", type=str, default="y", help="Y column name (default: y).")
    p.add_argument("--pad-frac", type=float, default=0.02, help="Padding fraction when inferring bounds.")
    return p.parse_args()


def load_points(path: str, x_col: str, y_col: str, w_col: str):
    xs, ys, ws = [], [], []
    with open(path, "r", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise SystemExit("❌ Input CSV missing headers.")
        for row in r:
            xs.append(float(row[x_col]))
            ys.append(float(row[y_col]))
            if w_col in row and row[w_col] not in (None, ""):
                ws.append(float(row[w_col]))
            else:
                ws.append(1.0)
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32), np.array(ws, dtype=np.float32)


def infer_bounds(xs: np.ndarray, ys: np.ndarray, pad_frac: float) -> Bounds:
    xmin, xmax = float(xs.min()), float(xs.max())
    ymin, ymax = float(ys.min()), float(ys.max())

    dx = max(1e-6, xmax - xmin)
    dy = max(1e-6, ymax - ymin)

    xmin -= dx * pad_frac
    xmax += dx * pad_frac
    ymin -= dy * pad_frac
    ymax += dy * pad_frac

    return Bounds(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)


def bin_points(xs: np.ndarray, ys: np.ndarray, ws: np.ndarray, b: Bounds, width: int, height: int) -> np.ndarray:
    # Normalize into [0,1]
    nx = (xs - b.xmin) / (b.xmax - b.xmin)
    ny = (ys - b.ymin) / (b.ymax - b.ymin)

    # Convert to pixel indices
    ix = np.floor(nx * (width - 1)).astype(np.int32)
    iy = np.floor(ny * (height - 1)).astype(np.int32)

    # Clip to bounds
    ix = np.clip(ix, 0, width - 1)
    iy = np.clip(iy, 0, height - 1)

    hitmap = np.zeros((height, width), dtype=np.float32)

    # Accumulate weights
    for x, y, w in zip(ix, iy, ws):
        hitmap[y, x] += float(w)

    return hitmap


def write_hitmap_csv(hitmap: np.ndarray, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        for row in hitmap.tolist():
            w.writerow(row)


def write_meta(meta_path: str, bounds: Bounds, width: int, height: int, n_points: int) -> None:
    os.makedirs(os.path.dirname(meta_path) or ".", exist_ok=True)
    meta = {
        "width": width,
        "height": height,
        "n_points": n_points,
        "bounds": {"xmin": bounds.xmin, "xmax": bounds.xmax, "ymin": bounds.ymin, "ymax": bounds.ymax},
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def main() -> None:
    args = parse_args()
    xs, ys, ws = load_points(args.endpoints_csv, args.x_col, args.y_col, args.weight_col)

    if args.bounds is None:
        b = infer_bounds(xs, ys, args.pad_frac)
    else:
        b = Bounds(xmin=args.bounds[0], xmax=args.bounds[1], ymin=args.bounds[2], ymax=args.bounds[3])

    hitmap = bin_points(xs, ys, ws, b, args.width, args.height)

    write_hitmap_csv(hitmap, args.out)
    write_meta(args.meta, b, args.width, args.height, int(xs.shape[0]))

    print(f"✅ Wrote hitmap: {args.out}")
    print(f"✅ Wrote meta:   {args.meta}")
    print(f"   points={xs.shape[0]}, width={args.width}, height={args.height}")
    print(f"   bounds: x[{b.xmin:.3f},{b.xmax:.3f}] y[{b.ymin:.3f},{b.ymax:.3f}]")


if __name__ == "__main__":
    main()

