"""Planar circular restricted three-body problem (PCR3BP).

Distance between primaries, total mass, G and angular speed are one.
The primaries are at (-mu, 0) and (1-mu, 0). State order: x,y,vx,vy.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

EARTH_MOON_MU = 0.0121505856  # Illustrative mass fraction, not an ephemeris.


def check_mu(mu):
    if not np.isfinite(mu) or not 0 < mu <= 0.5:
        raise ValueError("mu must be finite and satisfy 0 < mu <= 0.5")


def potential(x, y, mu=EARTH_MOON_MU):
    """Effective potential Ω; singular at either point-mass primary."""
    check_mu(mu)
    r1, r2 = np.hypot(np.asarray(x)+mu, y), np.hypot(np.asarray(x)-1+mu, y)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (np.asarray(x)**2 + np.asarray(y)**2)/2 + (1-mu)/r1 + mu/r2


def rhs(t, state, mu=EARTH_MOON_MU):
    """Rotating-frame equations, including both Coriolis terms."""
    check_mu(mu)
    x, y, vx, vy = state
    r1, r2 = np.hypot(x+mu, y), np.hypot(x-1+mu, y)
    if min(r1, r2) <= np.finfo(float).tiny:
        raise ValueError("equations are singular at a primary")
    gx = x - (1-mu)*(x+mu)/r1**3 - mu*(x-1+mu)/r2**3
    gy = y - (1-mu)*y/r1**3 - mu*y/r2**3
    return np.array([vx, vy, 2*vy+gx, -2*vx+gy])


def jacobi(states, mu=EARTH_MOON_MU):
    """C = 2Ω − vx² − vy²; accepts (...,4) arrays."""
    s = np.asarray(states, dtype=float)
    return 2*potential(s[..., 0], s[..., 1], mu) - np.sum(s[..., 2:4]**2, axis=-1)


def lagrange_points(mu=EARTH_MOON_MU):
    """Find L1–L3 by bracketed roots, L4–L5 analytically."""
    check_mu(mu)
    delta = min(1e-8, mu*1e-3)
    def gradient(x):
        return rhs(0, [x, 0, 0, 0], mu)[2]
    l1 = brentq(gradient, -mu+delta, 1-mu-delta, xtol=1e-13)
    l2 = brentq(gradient, 1-mu+delta, 3, xtol=1e-13)
    l3 = brentq(gradient, -3, -mu-delta, xtol=1e-13)
    return {"L1": np.array([l1, 0.]), "L2": np.array([l2, 0.]),
            "L3": np.array([l3, 0.]), "L4": np.array([0.5-mu, np.sqrt(3)/2]),
            "L5": np.array([0.5-mu, -np.sqrt(3)/2])}


def section_state(x, c, mu=EARTH_MOON_MU, vx=0.0):
    """State at y=0 with vy>0 and a specified Jacobi constant."""
    if not np.isfinite([x, c, vx]).all():
        raise ValueError("section inputs must be finite")
    vy2 = 2*potential(x, 0, mu) - c - vx*vx
    if not np.isfinite(vy2) or vy2 <= 0:
        raise ValueError("section initial condition is singular, tangent, or forbidden at this C")
    return np.array([x, 0, vx, np.sqrt(vy2)])


@dataclass
class Trajectory:
    times: np.ndarray
    states: np.ndarray
    section_times: np.ndarray
    section_states: np.ndarray
    jacobi_values: np.ndarray
    terminated: bool
    message: str

    @property
    def max_jacobi_drift(self):
        return float(np.max(np.abs(self.jacobi_values-self.jacobi_values[0])))


def integrate(initial, duration=80.0, mu=EARTH_MOON_MU, *, samples=4001,
              rtol=1e-10, atol=1e-12, max_step=0.04, collision_radius=1e-3):
    """DOP853 integration with upward y=0 events and terminal close-approach guards.

    The guard radius is a numerical cutoff, not a physical planetary radius.
    This adaptive integrator is not symplectic; monitor the returned C drift.
    """
    check_mu(mu)
    initial = np.asarray(initial, dtype=float)
    if initial.shape != (4,) or not np.isfinite(initial).all():
        raise ValueError("initial must be four finite values: x, y, vx, vy")
    if not np.isfinite([duration, max_step, collision_radius, rtol, atol]).all() or min(duration, max_step, collision_radius, rtol, atol) <= 0:
        raise ValueError("duration, max_step, collision_radius and tolerances must be finite and positive")
    if not isinstance(samples, (int, np.integer)) or samples < 2:
        raise ValueError("samples must be an integer >= 2")
    def primary_distance(t, s):
        return np.hypot(s[0]+mu, s[1])-collision_radius
    def secondary_distance(t, s):
        return np.hypot(s[0]-1+mu, s[1])-collision_radius
    def section(t, s):
        return s[1]
    section.direction, section.terminal = 1, False
    for event in [primary_distance, secondary_distance]:
        event.direction, event.terminal = -1, True
        if event(0, initial) <= 0:
            raise ValueError("initial state lies inside the close-approach guard")
    sol = solve_ivp(lambda t, y: rhs(t, y, mu), (0, duration), initial,
                    method="DOP853", t_eval=np.linspace(0, duration, samples),
                    events=[section, primary_distance, secondary_distance],
                    rtol=rtol, atol=atol, max_step=max_step)
    if not sol.success:
        raise RuntimeError(sol.message)
    times, states = sol.t, sol.y.T
    # Keep the terminal event itself, even when it lies between requested samples.
    if sol.status == 1:
        for event_times, event_states in zip(sol.t_events[1:], sol.y_events[1:]):
            if len(event_times) and event_times[-1] > times[-1]:
                times = np.append(times, event_times[-1])
                states = np.vstack((states, event_states[-1]))
    keep = sol.t_events[0] > 1e-9  # exclude the seeded section at t=0
    crossings = sol.y_events[0].reshape(-1, 4)[keep]
    return Trajectory(times, states, sol.t_events[0][keep], crossings,
                      jacobi(states, mu), sol.status == 1, sol.message)
