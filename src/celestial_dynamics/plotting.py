from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from .core import potential, lagrange_points

for font_name in ["IBMPlexSans-Regular.ttf", "IBMPlexSans-Medium.ttf"]:
    font_manager.fontManager.addfont(Path(__file__).parent / "fonts" / font_name)

INK, PAPER = "#24283e", "#f4f5f8"
COLOURS = ["#7960af", "#8f79bd", "#aa99ca", "#288f91", "#51a5a2", "#8ac1b7", "#c79159", "#cea97a"]


def geometry(ax, trajectories, mu, c, *, labels=True):
    x, y = np.meshgrid(np.linspace(-1.55, 1.55, 501), np.linspace(-1.2, 1.2, 401))
    v2 = 2*potential(x, y, mu)-c
    ax.contourf(x, y, v2, levels=[-100, 0], colors=["#e5e3ec"], alpha=0.7)
    ax.contour(x, y, v2, levels=[0], colors=["#b7b1c7"], linewidths=0.8)
    for i, orbit in enumerate(trajectories):
        ax.plot(orbit.states[:, 0], orbit.states[:, 1], lw=0.8, alpha=0.82, color=COLOURS[i%len(COLOURS)])
    ax.scatter([-mu, 1-mu], [0, 0], s=[58, 17] if labels else [85, 36], color=INK, zorder=6)
    for name, p in lagrange_points(mu).items():
        ax.scatter(*p, s=13 if labels else 30, facecolors=PAPER, edgecolors="#596375", linewidths=0.6 if labels else 1.1, zorder=5)
        if labels:
            ax.annotate(name, p, xytext=(4, 5), textcoords="offset points", fontsize=7, color="#71788b")
    ax.set(xlim=(-1.4, 1.45), ylim=(-1.15, 1.15), aspect="equal")


def sections(ax, trajectories, *, header=False):
    for i, orbit in enumerate(trajectories):
        if len(orbit.section_states):
            ax.scatter(orbit.section_states[:, 0], orbit.section_states[:, 2],
                       s=24 if header else 10, color=COLOURS[i%len(COLOURS)],
                       edgecolors=INK if header else 'none', linewidths=.3 if header else 0, alpha=1 if header else .9)
    ax.set(xlabel="x", ylabel="vx")


def save_figures(trajectories, mu, c, out):
    out = Path(out)
    plt.rcParams.update({"svg.fonttype": "path", "svg.hashsalt": "celestial-dynamics",
                         "font.family": "IBM Plex Sans", "font.size": 10,
                         "text.color": INK, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    geometry(axes[0], trajectories, mu, c)
    axes[0].set(title="Rotating frame & zero-velocity boundary", xlabel="x", ylabel="y")
    sections(axes[1], trajectories)
    axes[1].set_title("Poincaré section: y = 0, vy > 0")
    for i, orbit in enumerate(trajectories):
        axes[2].semilogy(orbit.times, np.maximum(np.abs(orbit.jacobi_values-orbit.jacobi_values[0]), 1e-16),
                        color=COLOURS[i%len(COLOURS)], lw=0.8)
    axes[2].set(title="Jacobi conservation", xlabel="Dimensionless time", ylabel="|C(t) − C(0)|")
    fig.suptitle(f"Planar circular restricted three-body problem · μ = {mu:.8g} · C = {c:g}")
    for suffix in ["svg", "png"]:
        fig.savefig(out / f"dynamics.{suffix}", dpi=170, metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)

    fig = plt.figure(figsize=(9.6, 6), facecolor=PAPER)
    left = fig.add_axes([0.02, 0.17, 0.59, 0.77])
    geometry(left, trajectories, mu, c, labels=False)
    left.set_axis_off()
    right = fig.add_axes([0.70, 0.34, 0.25, 0.43], facecolor=PAPER)
    sections(right, trajectories, header=True)
    right.set_xticks([])
    right.set_yticks([])
    for spine in right.spines.values():
        spine.set_color("#c9cad5")
    right.set_xlabel("x", size=24)
    right.set_ylabel(r"$\mathregular{v_x}$", size=24, rotation=0, labelpad=16)
    fig.text(.32, .11, "Orbits", ha="center", size=26, color=INK, weight="medium")
    fig.text(.8, .11, "Poincaré section", ha="center", size=23, color=INK, weight="medium")
    fig.savefig(out / "header.svg", facecolor=PAPER, metadata={"Date": None})
    fig.savefig(out / "header.png", facecolor=PAPER, dpi=150)
    plt.close(fig)
    for name in ["dynamics.svg", "header.svg"]:
        svg = out / name
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
