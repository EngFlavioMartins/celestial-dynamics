"""Animation for the README: an orbit traced out on the effective-potential landscape.

Earth-Moon mass fraction, Jacobi constant C = 3.2, the orbit started at x = 0.30 (as the
still figure). Runs compute_landscape.py with this package, renders the frames with
ParaView (render_animation.py) and writes docs/assets/animation.webp.
Run:  python scripts/render/make_animation.py   (needs ParaView; set PVPYTHON if it is not found)
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from gif import crop_union, pvpython, save_gif  # noqa: E402

FRAMES = 160

env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT / "src"), os.environ.get("PYTHONPATH", "")]))
subprocess.run([sys.executable, str(HERE / "compute_landscape.py")], check=True, cwd=ROOT, env=env)
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([pvpython(), str(HERE / "render_animation.py"), tmp, str(FRAMES)], check=True)
    frames = crop_union([Image.open(p) for p in sorted(Path(tmp).glob("frame_*.png"))])
save_gif(frames, ROOT / "docs" / "assets" / "animation.webp", fps=20, width=720, hold=2.0)
