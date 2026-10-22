"""ParaView (pvpython) animation frames: the orbit traced out on the potential landscape.

Usage: pvpython render_animation.py <frame directory> [frames]
Reads outputs/render/{surface,orbit,zvc,lagrange}.vtp from compute_landscape.py and
writes frame_000.png, ... Same scene as the still figure; the amber orbit grows from its
start on the x-axis with a small bright body at its head, while the camera turns slowly.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import onda_style as style  # noqa: E402
from paraview import servermanager as sm  # noqa: E402
from paraview.simple import (Elevation, Glyph, Show, Sphere, TrivialProducer, Tube,  # noqa: E402
                             XMLPolyDataReader)
from vtkmodules.numpy_interface import dataset_adapter as dsa  # noqa: E402
from vtkmodules.vtkCommonCore import vtkPoints  # noqa: E402
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkPolyLine  # noqa: E402

out = Path(sys.argv[1])
frames = int(sys.argv[2]) if len(sys.argv) > 2 else 160
width, height = 1440, 900
DATA = HERE.parents[1] / "outputs" / "render"
read = lambda name: XMLPolyDataReader(FileName=[str(DATA / name)])  # noqa: E731

view = style.setup_view(width, height)
surface = read("surface.vtp")
surface.UpdatePipeline()
zmin, zmax = surface.GetDataInformation().GetBounds()[4:6]
elev = Elevation(Input=surface, LowPoint=[0, 0, zmin], HighPoint=[0, 0, zmax])
lut = style.lut("Elevation", "thesis_blue", 0.55, 1.0, fade_from_black=0.25)
style.mapped(Show(elev, view), "Elevation", lut, roughness=0.45)
lut.RescaleTransferFunction(0.55, 1.0)

zvc = Tube(Input=read("zvc.vtp"))
zvc.Radius = 0.005
zvc.NumberofSides = 12
style.solid(Show(zvc, view), style.LIGHT_GREY, roughness=0.4)
pts = Glyph(Input=read("lagrange.vtp"), GlyphType="Sphere")
pts.GlyphType.Radius = 0.03
pts.GlyphType.ThetaResolution = 32
pts.GlyphType.PhiResolution = 32
pts.ScaleArray = ["POINTS", "No scale array"]
pts.GlyphMode = "All Points"
style.solid(Show(pts, view), style.LIGHT_GREY, roughness=0.3)

def polyline(p):
    points = vtkPoints()
    points.SetNumberOfPoints(len(p))
    for i, q in enumerate(p):
        points.SetPoint(i, *q)
    line = vtkPolyLine()
    line.GetPointIds().SetNumberOfIds(len(p))
    for i in range(len(p)):
        line.GetPointIds().SetId(i, i)
    cells = vtkCellArray()
    cells.InsertNextCell(line)
    pd = vtkPolyData()
    pd.SetPoints(points)
    pd.SetLines(cells)
    return pd


orbit_src = read("orbit.vtp")
orbit_src.UpdatePipeline()
xyz = dsa.WrapDataObject(sm.Fetch(orbit_src)).Points
trace = TrivialProducer()
trace.GetClientSideObject().SetOutput(polyline(np.asarray(xyz[:2])))
tube = Tube(Input=trace)
tube.Radius = 0.007
tube.NumberofSides = 16
style.solid(Show(tube, view), style.colour("thesis_amber", 0.72), roughness=0.35)
body = Sphere(Radius=0.03, ThetaResolution=32, PhiResolution=32)
style.solid(Show(body, view), style.colour("thesis_amber", 0.55), roughness=0.3)


position = np.array([-1.7, -3.9, 2.25])
focal = np.array([0.05, 0.0, -0.55])
out.mkdir(parents=True, exist_ok=True)
ends = np.linspace(2, len(xyz), frames).astype(int)
for k, n in enumerate(ends):
    trace.GetClientSideObject().SetOutput(polyline(np.asarray(xyz[:n])))
    trace.MarkModified(trace)
    body.Center = list(np.asarray(xyz[n - 1]))
    a = np.deg2rad(-12 + 24 * k / max(1, frames - 1))      # slow turn about the vertical axis
    r = position - focal
    view.CameraPosition = list(focal + [r[0] * np.cos(a) - r[1] * np.sin(a), r[0] * np.sin(a) + r[1] * np.cos(a), r[2]])
    view.CameraFocalPoint = list(focal)
    view.CameraViewUp = [0, 0, 1]
    view.CameraViewAngle = 30
    style.save(view, out / f"frame_{k:03d}.png", width, height)
    print(k, end=" ", flush=True)
print()
