import json
import numpy as np
from celestial_dynamics.cli import main


def test_demo_exports(tmp_path):
    main(["--duration", "1", "--samples", "51", "--x", "0.42", "--output", str(tmp_path)])
    report = json.loads((tmp_path / "diagnostics.json").read_text())
    assert report["orbits"][0]["max_jacobi_drift"] < 1e-8
    assert (tmp_path / "header.svg").stat().st_size > 1000
    with np.load(tmp_path / "orbit-00.npz") as data:
        assert data["states"].shape == (51, 4)
