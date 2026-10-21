"""Geometry for the website render: effective-potential landscape and one orbit.

Earth-Moon-like mass fraction mu = 0.0121505856 and Jacobi constant C = 3.2,
as in the package defaults. Writes for ParaView:
  surface.vtp  height field z = SCALE * max(-log Omega, FLOOR) over the rotating plane.
               -log Omega is a monotonic display transform of the potential: wells,
               saddles and hills keep their positions, but the deep wells around the
               primaries are compressed (and cut at FLOOR) so that the shallow
               saddles at L1-L3 and hills at L4-L5 stay visible.
  orbit.vtp    the orbit started at x = 0.30 on y = 0 (vy > 0), lifted onto the surface
  zvc.vtp      the zero-velocity curve 2 Omega = C on the surface
  lagrange.vtp the five Lagrange points on the surface
"""
from pathlib import Path

import numpy as np
import pyvista as pv

from celestial_dynamics import integrate
from celestial_dynamics.core import EARTH_MOON_MU as MU, lagrange_points, potential, section_state

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "render"
C, X0, DURATION = 3.2, 0.30, 60.0
FLOOR, SCALE, LIFT = -1.45, 0.75, 0.006
X, Y = np.linspace(-1.35, 1.35, 641), np.linspace(-1.15, 1.15, 561)


def height(x, y):
    return SCALE * np.maximum(-np.log(potential(x, y, MU)), FLOOR)


gx, gy = np.meshgrid(X, Y, indexing="ij")
grid = pv.StructuredGrid(gx, gy, height(gx, gy))
surface = grid.extract_surface(algorithm="dataset_surface").compute_normals(split_vertices=False)

orbit = integrate(section_state(X0, C, MU), duration=DURATION, mu=MU, samples=12001)
xy = orbit.states[:, :2]
print(f"orbit: {len(xy)} samples, max Jacobi drift {orbit.max_jacobi_drift:.1e}")
line = pv.lines_from_points(np.column_stack([xy, height(xy[:, 0], xy[:, 1]) + LIFT]))

flat = pv.StructuredGrid(gx, gy, np.zeros_like(gx))
flat["twice_omega"] = (2 * potential(gx, gy, MU)).ravel(order="F")
zvc = flat.contour([C], scalars="twice_omega")
zvc.points[:, 2] = height(zvc.points[:, 0], zvc.points[:, 1]) + LIFT

L = np.array(list(lagrange_points(MU).values()))[:, :2]
lagrange = pv.PolyData(np.column_stack([L, height(L[:, 0], L[:, 1]) + LIFT]))

OUT.mkdir(parents=True, exist_ok=True)
surface.save(OUT / "surface.vtp")
line.save(OUT / "orbit.vtp")
zvc.save(OUT / "zvc.vtp")
lagrange.save(OUT / "lagrange.vtp")
print("wrote", OUT)
