"""ParaView (pvpython) render of the effective-potential landscape with one orbit.

Usage: pvpython render_landscape.py <output png> [width height]
Reads outputs/render/{surface,orbit,zvc,lagrange}.vtp from compute_landscape.py.
Surface: height with Crameri's "oslo", stretched over the plateau around the
Lagrange points (deep wells dark). Orbit: copper tube.
Zero-velocity curve and Lagrange points: neutral grey.
"""
import json
import sys
from pathlib import Path

from paraview.simple import (ColorBy, Elevation, GetActiveViewOrCreate, GetColorTransferFunction, Glyph,
                             SaveScreenshot, Show, Tube, XMLPolyDataReader)

out = Path(sys.argv[1])
width, height = (int(a) for a in (sys.argv[2:4] if len(sys.argv) > 3 else (2400, 1600)))
HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "outputs" / "render"
read = lambda name: XMLPolyDataReader(FileName=[str(DATA / name)])

view = GetActiveViewOrCreate("RenderView")
view.ViewSize = [width, height]
view.OrientationAxesVisibility = 0
view.UseColorPaletteForBackground = 0
view.Background = [1, 1, 1]
view.EnableRayTracing = 1
view.BackEnd = "OSPRay raycaster"
view.SamplesPerPixel = 32
view.AmbientSamples = 8
view.Shadows = 1

surface = read("surface.vtp")
surface.UpdatePipeline()
bounds = surface.GetDataInformation().GetBounds()
elev = Elevation(Input=surface, LowPoint=[0, 0, bounds[4]], HighPoint=[0, 0, bounds[5]])
d = Show(elev, view)
ColorBy(d, ("POINTS", "Elevation"))
lut = GetColorTransferFunction("Elevation")
lut.RGBPoints = json.loads((HERE / "oslo.json").read_text())["oslo"]
lut.ColorSpace = "RGB"
lut.AutomaticRescaleRangeMode = "Never"
lut.RescaleTransferFunction(0.68, 1.12)   # elevation is normalised 0-1 over the surface
d.SetScalarBarVisibility(view, False)
d.Ambient, d.Diffuse, d.Specular, d.SpecularPower = 0.25, 0.75, 0.2, 30

orbit = Tube(Input=read("orbit.vtp"))
orbit.Radius = 0.006
orbit.NumberofSides = 16
d = Show(orbit, view)
d.ColorArrayName = ["POINTS", ""]
d.AmbientColor = d.DiffuseColor = [0.75, 0.38, 0.17]          # site copper
d.Ambient, d.Diffuse, d.Specular, d.SpecularPower = 0.45, 0.6, 0.5, 40

zvc = Tube(Input=read("zvc.vtp"))
zvc.Radius = 0.004
zvc.NumberofSides = 12
d = Show(zvc, view)
d.ColorArrayName = ["POINTS", ""]
d.AmbientColor = d.DiffuseColor = [0.30, 0.33, 0.37]

pts = Glyph(Input=read("lagrange.vtp"), GlyphType="Sphere")
pts.GlyphType.Radius = 0.032
pts.GlyphType.ThetaResolution = 32
pts.GlyphType.PhiResolution = 32
pts.ScaleArray = ["POINTS", "No scale array"]
pts.GlyphMode = "All Points"
pts.ScaleFactor = 1.0
d = Show(pts, view)
d.ColorArrayName = ["POINTS", ""]
d.AmbientColor = d.DiffuseColor = [0.72, 0.74, 0.76]
d.Specular, d.SpecularPower = 0.6, 40

view.CameraPosition = [-1.7, -3.9, 2.25]
view.CameraFocalPoint = [0.05, 0.0, -0.55]
view.CameraViewUp = [0, 0, 1]
view.CameraViewAngle = 30
SaveScreenshot(str(out), view, ImageResolution=[width, height], TransparentBackground=0)
print(out)
