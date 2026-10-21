"""ParaView (pvpython) render of the effective-potential landscape, OpenONDA style.

Usage: pvpython render_landscape.py <output png> [width height]
Reads outputs/render/{surface,orbit,zvc,lagrange}.vtp from compute_landscape.py
and writes <output>.labels.json with the image positions of the primaries and
the Lagrange points for compose_landscape.py.

Black background. The surface is shaded with thesis_blue by height, so the
wells fade into the black; the orbit is thesis_amber; the zero-velocity curve
and the Lagrange points are light grey.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import onda_style as style  # noqa: E402
from paraview.simple import Elevation, Glyph, Show, Tube, XMLPolyDataReader  # noqa: E402

out = Path(sys.argv[1])
width, height = (int(a) for a in (sys.argv[2:4] if len(sys.argv) > 3 else (2400, 1500)))
DATA = HERE.parents[1] / "outputs" / "render"
MU = 0.0121505856
read = lambda name: XMLPolyDataReader(FileName=[str(DATA / name)])

view = style.setup_view(width, height)
surface = read("surface.vtp")
surface.UpdatePipeline()
zmin, zmax = surface.GetDataInformation().GetBounds()[4:6]
elev = Elevation(Input=surface, LowPoint=[0, 0, zmin], HighPoint=[0, 0, zmax])
lut = style.lut("Elevation", "thesis_blue", 0.55, 1.0, fade_from_black=0.25)
d = Show(elev, view)
style.mapped(d, "Elevation", lut, roughness=0.45)
lut.RescaleTransferFunction(0.55, 1.0)            # elevation is normalised 0-1 over the surface

orbit = Tube(Input=read("orbit.vtp"))
orbit.Radius = 0.007
orbit.NumberofSides = 16
style.solid(Show(orbit, view), style.colour("thesis_amber", 0.72), roughness=0.35)
zvc = Tube(Input=read("zvc.vtp"))
zvc.Radius = 0.005
zvc.NumberofSides = 12
style.solid(Show(zvc, view), style.LIGHT_GREY, roughness=0.4)
lagrange = read("lagrange.vtp")
pts = Glyph(Input=lagrange, GlyphType="Sphere")
pts.GlyphType.Radius = 0.03
pts.GlyphType.ThetaResolution = 32
pts.GlyphType.PhiResolution = 32
pts.ScaleArray = ["POINTS", "No scale array"]
pts.ScaleFactor = 1.0
pts.GlyphMode = "All Points"
style.solid(Show(pts, view), style.LIGHT_GREY, roughness=0.3)

view.CameraPosition = [-1.7, -3.9, 2.25]
view.CameraFocalPoint = [0.05, 0.0, -0.55]
view.CameraViewUp = [0, 0, 1]
view.CameraViewAngle = 30
style.save(view, out, width, height)

# image positions (fractions from the lower-left corner) for the LaTeX labels
from paraview import servermanager as sm  # noqa: E402
lagrange.UpdatePipeline()
L = sm.Fetch(lagrange).GetPoints()
plateau = L.GetPoint(0)[2]
anchors = {f"$L_{k + 1}$": L.GetPoint(k) for k in range(5)}
anchors["Earth"] = (-MU, 0.0, plateau)
anchors["Moon"] = (1 - MU, 0.0, plateau)
ren = view.GetRenderer()
labels = {}
for name, (x, y, z) in anchors.items():
    ren.SetWorldPoint(x, y, z, 1.0)
    ren.WorldToDisplay()
    px, py, _ = ren.GetDisplayPoint()
    labels[name] = [px / width, py / height]
Path(str(out) + ".labels.json").write_text(json.dumps(labels, indent=1))
print(out)
