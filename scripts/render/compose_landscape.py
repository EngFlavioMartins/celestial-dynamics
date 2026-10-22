"""Add the LaTeX labels (primaries and Lagrange points) to the landscape render.

Usage: python compose_landscape.py <raw png> <output stem>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay import compose  # noqa: E402

raw, stem = Path(sys.argv[1]), Path(sys.argv[2])
pos = json.loads(Path(str(raw) + ".labels.json").read_text())
# offsets [mm] and anchors chosen so labels sit beside their markers without overlapping
place = {"Earth": (0, -9.0, "center"), "Moon": (0, 2.0, "south"), "$L_1$": (-1.4, 0, "east"),
         "$L_2$": (1.4, 0, "west"), "$L_3$": (0, 1.2, "south"), "$L_4$": (0, 1.2, "south"),
         "$L_5$": (0, 1.2, "south")}
notes = [(fx, fy, name, place[name][2], place[name][0], place[name][1]) for name, (fx, fy) in pos.items()]
compose([(raw, None)], stem, notes=notes)
