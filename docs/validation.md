# Validation record

Local environment: Python 3.12, NumPy 2.5.3, SciPy 1.18.1 and Matplotlib 3.11.2.

For the default command (six starting positions, μ = 0.0121505856, C = 3.2, duration 120), all six trajectories reached the requested end time without triggering the close-approach guard. The largest absolute Jacobi drift was approximately 6.55 × 10⁻⁹. The six trajectories produced 27, 28, 24, 22, 21 and 21 upward section crossings respectively.

The test suite separately checks equilibrium residuals at three mass ratios, stationary L4 motion, tightened-tolerance convergence, event orientation, forbidden initial conditions and a deliberately triggered close-approach guard. CLI export is also tested.

These are numerical consistency checks. No claim of exact reproduction of a published orbit, measured ephemeris, mission trajectory or formal chaos classification is made.
