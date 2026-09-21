from types import SimpleNamespace
import matplotlib.pyplot as plt
import numpy as np
from celestial_dynamics.plotting import sections, geometry


def test_header_points_remain_readable():
    orbit = SimpleNamespace(section_states=np.array([[.2,0,.3,1],[.3,0,.4,1]]))
    fig, ax = plt.subplots()
    sections(ax, [orbit], header=True)
    assert min(ax.collections[0].get_sizes()) >= 24
    assert ax.collections[0].get_alpha() == 1
    assert min(ax.collections[0].get_linewidths()) > 0
    plt.close(fig)


def test_header_primary_and_equilibrium_markers():
    fig, ax = plt.subplots()
    geometry(ax, [], .0121505856, 3.2, labels=False)
    # Contours have no scatter sizes; only marker collections participate.
    markers = [c for c in ax.collections if hasattr(c, 'get_sizes') and len(c.get_sizes())]
    assert markers
    assert all(min(c.get_sizes()) >= 30 for c in markers)
    plt.close(fig)
