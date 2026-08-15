# File: scripts/make_endpoints_from_paths.py

"""
Create detector endpoints from exported beam paths.

Input: CSV with columns x,y,z and optionally nx,ny,nz and intensity.
Output: endpoints CSV with x,y and optional w.

Two modes:
1) If direction (nx,ny,nz) exists:
   Intersect ray from (x,y,z) along (nx,ny,nz) with detector plane z = z_det.
2) If direction does not exist:
   Treat (x,y) as already being on detector plane and pass through.

Example:
  python scripts/make_endpoints_from_paths.py data/beam_paths.csv --z-det 0 --out data/ray_endpoints.csv
"""

from __future__ import annotations

import argparse
import csv
import os


def parse_args():
    p = argparse.ArgumentParser(description="Compute detector endpoints from beam path CSV.")
    p.add_argument("beam_paths_csv", help="Input beam paths CSV")
    p.add_argument("--z-det", type=float, default=0.0, help="Detector plane z value")
    p.add_argument("--out", type=str, default="data/ray_endpoints.csv", help="Output endpoints CSV")
    p.add_argument("--write-weight", action="store_true", help="Include weight column w (uses intensity if present)")
    return p.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.beam_paths_csv):
        raise SystemExit(f"❌ Not found: {args.beam_paths_csv}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(args.beam_paths_csv, "r", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise SystemExit("❌ Missing CSV headers.")

        fields = set(r.fieldnames)
        has_dir = {"nx", "ny", "nz"}.issubset(fields)
        has_intensity = "intensity" in fields

        out_headers = ["x", "y"]
        if args.write_weight:
            out_headers.append("w")

        rows_out = 0
        with open(args.out, "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(out_headers)

            for row in r:
                x = float(row["x"])
                y = float(row["y"])
                z = float(row["z"])

                weight = float(row["intensity"]) if (args.write_weight and has_intensity) else 1.0

                if has_dir:
                    nx = float(row["nx"])
                    ny = float(row["ny"])
                    nz = float(row["nz"])

                    # Avoid divide-by-zero if nz ~ 0 (ray parallel to detector plane)
                    if abs(nz) < 1e-9:
                        # skip or pass-through; here we skip
                        continue

                    t = (args.z_det - z) / nz
                    xd = x + t * nx
                    yd = y + t * ny
                else:
                    # Assume already on plane
                    xd, yd = x, y

                if args.write_weight:
                    w.writerow([xd, yd, weight])
                else:
                    w.writerow([xd, yd])

                rows_out += 1

    print(f"✅ Wrote {rows_out} endpoints to {args.out}")
    print(f"   used_direction={has_dir}, z_det={args.z_det}, weight={'on' if args.write_weight else 'off'}")


if __name__ == "__main__":
    main()

