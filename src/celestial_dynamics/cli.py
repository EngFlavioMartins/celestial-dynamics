import argparse
import json
from pathlib import Path
import numpy as np
from .core import EARTH_MOON_MU, integrate, lagrange_points, section_state
from .plotting import save_figures


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute planar CR3BP orbits, Poincaré sections and Jacobi diagnostics.")
    parser.add_argument("--mu", type=float, default=EARTH_MOON_MU)
    parser.add_argument("--jacobi", type=float, default=3.2)
    parser.add_argument("--duration", type=float, default=120.0)
    parser.add_argument("--samples", type=int, default=8001)
    parser.add_argument("--x", type=float, nargs="+", default=[0.24, 0.30, 0.36, 0.42, 0.48, 0.54])
    parser.add_argument("--rtol", type=float, default=1e-10)
    parser.add_argument("--output", type=Path, default=Path("outputs/demo"))
    args = parser.parse_args(argv)
    try:
        initials = [section_state(x, args.jacobi, args.mu) for x in args.x]
        trajectories = [integrate(s, args.duration, args.mu, samples=args.samples, rtol=args.rtol)
                        for s in initials]
    except ValueError as error:
        parser.error(str(error))
    args.output.mkdir(parents=True, exist_ok=True)
    for i, orbit in enumerate(trajectories):
        np.savez_compressed(args.output / f"orbit-{i:02}.npz", times=orbit.times,
            states=orbit.states, jacobi=orbit.jacobi_values, section_times=orbit.section_times,
            section_states=orbit.section_states)
    report = {"mu": args.mu, "jacobi": args.jacobi, "duration": args.duration,
              "initial_states": [s.tolist() for s in initials],
              "rtol": args.rtol, "atol": 1e-12, "max_step": 0.04, "collision_radius": 0.001,
              "lagrange_points": {k: v.tolist() for k, v in lagrange_points(args.mu).items()},
              "orbits": [{"max_jacobi_drift": o.max_jacobi_drift,
                          "upward_crossings": len(o.section_times), "close_approach_stop": o.terminated,
                          "final_time": float(o.times[-1])} for o in trajectories]}
    (args.output / "diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
    save_figures(trajectories, args.mu, args.jacobi, args.output)
    print(json.dumps(report, indent=2))
    print(f"Figures and arrays written to {args.output.resolve()}")


if __name__ == "__main__":
    main()
