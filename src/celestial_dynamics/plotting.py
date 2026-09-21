from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .core import potential, lagrange_points

INK, PAPER = "#24283e", "#f4f5f8"
COLOURS = ["#7960af", "#8f79bd", "#aa99ca", "#288f91", "#51a5a2", "#8ac1b7", "#c79159", "#cea97a"]


def geometry(ax, trajectories, mu, c, *, labels=True):
    x, y = np.meshgrid(np.linspace(-1.55, 1.55, 501), np.linspace(-1.2, 1.2, 401))
    v2 = 2*potential(x, y, mu)-c
    ax.contourf(x, y, v2, levels=[-100, 0], colors=["#e5e3ec"], alpha=0.7)
    ax.contour(x, y, v2, levels=[0], colors=["#b7b1c7"], linewidths=0.8)
    for i, orbit in enumerate(trajectories):
        ax.plot(orbit.states[:, 0], orbit.states[:, 1], lw=0.55, alpha=0.82, color=COLOURS[i%len(COLOURS)])
    ax.scatter([-mu, 1-mu], [0, 0], s=[58, 17], color=INK, zorder=6)
    for name, p in lagrange_points(mu).items():
        ax.scatter(*p, s=13, facecolors=PAPER, edgecolors="#71788b", linewidths=0.6, zorder=5)
        if labels:
            ax.annotate(name, p, xytext=(4, 5), textcoords="offset points", fontsize=7, color="#71788b")
    ax.set(xlim=(-1.4, 1.45), ylim=(-1.15, 1.15), aspect="equal")


def sections(ax, trajectories):
    for i, orbit in enumerate(trajectories):
        if len(orbit.section_states):
            ax.scatter(orbit.section_states[:, 0], orbit.section_states[:, 2],
                       s=6, color=COLOURS[i%len(COLOURS)], linewidths=0, alpha=0.8)
    ax.set(xlabel="x", ylabel="vx")


def save_figures(trajectories, mu, c, out):
    out = Path(out)
    plt.rcParams.update({"svg.fonttype": "path", "svg.hashsalt": "celestial-dynamics",
                         "font.family": "DejaVu Sans", "font.size": 10,
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
    left = fig.add_axes([0.035, 0.17, 0.58, 0.65])
    geometry(left, trajectories, mu, c)
    left.set_axis_off()
    right = fig.add_axes([0.70, 0.30, 0.25, 0.41], facecolor=PAPER)
    sections(right, trajectories)
    right.tick_params(labelsize=7, colors="#71788b", length=2)
    for spine in right.spines.values():
        spine.set_color("#c9cad5")
    right.set_xlabel("x", size=8)
    right.set_ylabel("vx", size=8)
    right.set_title("y = 0  ·  vy > 0", size=8, color="#71788b", pad=12)
    fig.text(0.055, 0.92, "ORBITAL PHASE SPACE", size=11, color=INK, weight="medium")
    fig.text(0.945, 0.92, "CIRCULAR RESTRICTED THREE-BODY", size=8, color="#777c90", ha="right")
    fig.text(0.055, 0.08, "Rotating-frame trajectories", size=10, color=INK)
    fig.text(0.945, 0.08, "Poincaré section", size=10, color=INK, ha="right")
    fig.savefig(out / "header.svg", facecolor=PAPER, metadata={"Date": None})
    fig.savefig(out / "header.png", facecolor=PAPER, dpi=150)
    plt.close(fig)
    for name in ["dynamics.svg", "header.svg"]:
        svg = out / name
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
