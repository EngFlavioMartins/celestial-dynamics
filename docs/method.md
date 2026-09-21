# Model and numerical conventions

The model is the planar circular restricted three-body problem, in a frame rotating with angular speed one. The primary masses are 1−μ and μ, placed at (−μ,0) and (1−μ,0). State ordering is (x,y,vx,vy).

Let r₁² = (x+μ)²+y² and r₂² = (x−1+μ)²+y². The effective potential is

Ω = (x²+y²)/2 + (1−μ)/r₁ + μ/r₂.

The equations are ẍ = 2ẏ + ∂Ω/∂x and ÿ = −2ẋ + ∂Ω/∂y. The Jacobi constant is C = 2Ω − vx² − vy². Regions where 2Ω < C are forbidden; their boundary is the zero-velocity curve.

The separation, total mass, G and angular speed are one. A full primary revolution takes 2π time units. The default μ = 0.0121505856 is illustrative, not a precise epoch-dependent Earth–Moon ephemeris.

## Integration

SciPy's DOP853 uses relative tolerance 10⁻¹⁰, absolute tolerance 10⁻¹² and maximum step 0.04. It is adaptive, **not symplectic**. Every run exports |C(t)−C(0)|; compare tighter tolerances before interpreting sensitive trajectories.

L1–L3 are bracketed roots of the collinear equilibrium equation. L4–L5 are analytic equilateral-triangle solutions.

The Poincaré section records y = 0 with vy > 0, using the integrator's event root finder, not the nearest output frame. The initial point at t = 0 is excluded. Output sampling does not set event precision, although the maximum solver step still limits event resolution.

Integration terminates within 0.001 normalised distance of either primary. This is a numerical singularity guard, not a physical planet radius. The final event state is retained even between output samples.

## Interpretation

Section points from regular trajectories can trace invariant curves; scattered points alone are not proof of chaos. Finite-time drawings do not establish KAM tori, stability regions or a Lyapunov exponent.

The default C = 3.2 closes the Earth–Moon-like inner gateway, keeping the demonstration focused on primary-centred motion. Other settings can produce transit, escape or close approach. The plots mark any guard-triggered stop in the JSON report.

Background: [Martins & Zanotello](https://doi.org/10.1590/1806-9126-rbef-2017-0174). The standard dimensionless equations also appear in [Guzzo & Lega (2013)](https://doi.org/10.1093/mnras/sts225). Implementation uses [SciPy's documented integration/event interface](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).
