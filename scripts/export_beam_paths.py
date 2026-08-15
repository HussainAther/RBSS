# File: scripts/export_beam_paths.py

"""
Export beam path points from a Houdini node to CSV.

Usage (recommended with hython):
  hython scripts/export_beam_paths.py \
    --hip houdini/projects/bragg_reflection_demo.hiplc \
    --node /obj/janus_beam_reflection/geo1/OUT_REFLECTION \
    --out data/beam_paths.csv

Exports per-point:
- x,y,z from P
- nx,ny,nz from N (if present)
- r,g,b from Cd (if present)
- intensity (optional): derived from |Cd| or from a named attribute via --int-attr

Notes:
- This script is designed for Houdini Indie/Apprentice workflows.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

import hou


def parse_args():
    p = argparse.ArgumentParser(description="Export Houdini node point attributes to CSV.")
    p.add_argument("--hip", required=True, help="Path to .hip/.hiplc file")
    p.add_argument("--node", required=True, help="Houdini node path to export (SOP node output)")
    p.add_argument("--out", default="data/beam_paths.csv", help="Output CSV path")
    p.add_argument(
        "--int-attr",
        default="",
        help="Optional float point attribute name to export as intensity. If omitted, uses |Cd| if Cd exists.",
    )
    return p.parse_args()


def get_point_attrib(geo: hou.Geometry, name: str):
    attrib = geo.findPointAttrib(name)
    return attrib


def main():
    args = parse_args()

    if not os.path.exists(args.hip):
        raise SystemExit(f"❌ HIP file not found: {args.hip}")

    # Load hip
    hou.hipFile.load(args.hip)

    node = hou.node(args.node)
    if node is None:
        raise SystemExit(f"❌ Node not found: {args.node}")

    geo = node.geometry()
    pts = geo.points()
    if not pts:
        raise SystemExit("❌ No points found on node geometry.")

    # Attributes
    hasN = get_point_attrib(geo, "N") is not None
    hasCd = get_point_attrib(geo, "Cd") is not None
    int_attrib = get_point_attrib(geo, args.int_attr) if args.int_attr else None

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    headers = ["x", "y", "z"]
    if hasN:
        headers += ["nx", "ny", "nz"]
    if hasCd:
        headers += ["r", "g", "b"]
    headers += ["intensity"]

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)

        for p in pts:
            P = p.position()
            row = [float(P[0]), float(P[1]), float(P[2])]

            if hasN:
                N = p.attribValue("N")
                row += [float(N[0]), float(N[1]), float(N[2])]

            intensity = 1.0

            if hasCd:
                Cd = p.attribValue("Cd")
                row += [float(Cd[0]), float(Cd[1]), float(Cd[2])]
                # default intensity from magnitude of Cd
                intensity = float((Cd[0] ** 2 + Cd[1] ** 2 + Cd[2] ** 2) ** 0.5)

            if int_attrib is not None:
                intensity = float(p.attribValue(args.int_attr))

            row += [intensity]
            w.writerow(row)

    print(f"✅ Exported {len(pts)} points from {args.node}")
    print(f"✅ Wrote CSV: {args.out}")


if __name__ == "__main__":
    # Must be run under hython (Houdini Python)
    try:
        import hou  # noqa: F401
    except Exception:
        raise SystemExit("❌ This script must be run with hython (Houdini's Python).")
    main()

