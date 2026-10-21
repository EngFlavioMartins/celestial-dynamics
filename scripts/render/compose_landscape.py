"""Add the LaTeX labels (primaries and Lagrange points) to the landscape render.

Usage: python compose_landscape.py <raw png> <output stem>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay import HEIGHT_MM, WIDTH_MM, compose  # noqa: E402

raw, stem = Path(sys.argv[1]), Path(sys.argv[2])
pos = json.loads(Path(str(raw) + ".labels.json").read_text())
# offsets [mm] and anchors chosen so labels sit beside their markers without overlapping
place = {"Earth": (0, -3.6, "center"), "Moon": (0, 2.0, "south"), "$L_1$": (-1.4, 0, "east"),
         "$L_2$": (1.4, 0, "west"), "$L_3$": (0, 1.2, "south"), "$L_4$": (0, 1.2, "south"),
         "$L_5$": (0, 1.2, "south")}
labels = []
for name, (fx, fy) in pos.items():
    dx, dy, anchor = place.get(name, (0, 1.0, "south"))
    labels.append((fx * WIDTH_MM + dx, fy * HEIGHT_MM + dy, name, anchor))
compose(raw, stem, labels=labels)
