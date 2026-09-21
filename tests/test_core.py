import numpy as np
import pytest
from celestial_dynamics.core import integrate, jacobi, lagrange_points, rhs, section_state


@pytest.mark.parametrize("mu", [0.001, 0.0121505856, 0.5])
def test_lagrange_equilibria(mu):
    points = lagrange_points(mu)
    for point in points.values():
        np.testing.assert_allclose(rhs(0, [*point, 0, 0], mu), 0, atol=2e-11)
    assert points["L3"][0] < -mu < points["L1"][0] < 1-mu < points["L2"][0]


def test_l4_remains_at_equilibrium():
    p = lagrange_points()["L4"]
    orbit = integrate([*p, 0, 0], 10, samples=101)
    np.testing.assert_allclose(orbit.states, np.tile([*p, 0, 0], (101, 1)), atol=1e-11)
    assert orbit.max_jacobi_drift < 1e-12


def test_jacobi_section_and_convergence():
    initial = section_state(0.42, 3.15)
    assert jacobi(initial) == pytest.approx(3.15, abs=1e-14)
    a = integrate(initial, 15, samples=601)
    b = integrate(initial, 15, samples=601, rtol=1e-12, atol=1e-14, max_step=0.02)
    assert a.max_jacobi_drift < 5e-8
    np.testing.assert_allclose(a.states, b.states, atol=3e-7, rtol=0)
    assert len(a.section_times) >= 2
    assert np.all(a.section_times > 0)
    assert np.max(np.abs(a.section_states[:, 1])) < 1e-12
    assert np.all(a.section_states[:, 3] > 0)


def test_close_approach_guard_stops_integration():
    mu = 0.0121505856
    orbit = integrate([-mu+0.05, 0, -1, 0], 1, samples=101, collision_radius=0.02, max_step=0.001)
    assert orbit.terminated and orbit.times[-1] < 1
    assert np.hypot(orbit.states[-1, 0]+mu, orbit.states[-1, 1]) == pytest.approx(0.02, abs=1e-9)


def test_forbidden_and_invalid_initial_conditions():
    with pytest.raises(ValueError, match="forbidden"):
        section_state(0.5, 100)
    for mu in [0, -1, 0.9, np.nan]:
        with pytest.raises(ValueError):
            lagrange_points(mu)
    with pytest.raises(ValueError, match="guard"):
        integrate([-0.0121505856, 0, 0, 0])
    with pytest.raises(ValueError):
        integrate([0.4, 0, 0, np.nan])
