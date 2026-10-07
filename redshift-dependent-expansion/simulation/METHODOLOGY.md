# Methodology

This note describes exactly what the visualization computes. Nothing here
is fitted, inferred, or claimed beyond re-displaying fixed publication
numbers.

## 1. Inputs

`scripts/build_simulation_data.py` reads only publication-grade artifacts
kept with the paper (figure tables of the fixed endpoints, the fixed
difference-field table with the order-3 map column, the constrained
order-selection table, the epsilon profile, the constrained bootstrap and
rescore records, and the endpoint/ruler identity contracts). It resamples
the smooth curves onto 241 uniform points over 0 ≤ z ≤ 2.33 with
piecewise-linear interpolation and writes
`data/publication_simulation_data.json`. Source SHA-256 hashes (relative
publication paths only) are recorded in the JSON metadata. No
observed-catalog rows are embedded anywhere.

## 2. Expansion and distance curves

The JSON carries three fitted endpoint histories `H_R(z)`, `H_C1(z)`,
`H_C2(z)` in km/s/Mpc. Absolute comoving distances are derived from them
by direct numerical integration (cumulative trapezoid rule):

    D_M(z) = integral_0^z c / H(z') dz',   c = 299792.458 km/s

computed on the dense fixed grid and resampled. The difference fields are
recomputed from the resampled endpoints so the file is self-consistent:

    Δ1(z) = ln H_R − ln H_C1
    Δ2(z) = ln H_R − ln H_C2
    ΔC(z) = ln H_C1 − ln H_C2

The dashed gray curve in the second panel is the fixed order-3 map (five
fitted coordinates) applied in the paper; it captures the broad trend but
not the exact ∼0.65 peak. The largest endpoint separation sits in a broad
low/intermediate-redshift region around z ∼ 0.65. That is a description of
the fitted endpoints, not a claim of a physical transition or epoch.

## 3. Synthetic tracers

Tracers are generated at runtime from a fixed seed (560 tracers,
`mulberry32` generator):

- Directions: deterministic Fibonacci sphere lattice (quasi-uniform).
- Radii: uniform in comoving volume,

    D_target = u^(1/3) · D_max,   u ∈ [0, 1),

  with D_max = D_C1(z = 2.33); each target is mapped to a nominal
  redshift z_i by inverting the C1 distance table.
- Paired radii use the real endpoint distances at that redshift:

    r_R  = D_R(z_i) / D_max,      r_C1 = D_C1(z_i) / D_max.

No tracer is, or resembles, an observed galaxy. Only the seed and the
recipe above are stored.

## 4. Display exaggeration (presentation only)

Only the *displayed gap* between the two projections is multiplied. With
exaggeration factor E (default 8, options 1/4/8/12) the pair midpoint is
preserved:

    r_mid   = (r_R + r_C1) / 2
    r_R^disp  = r_mid + (E/2)·(r_R − r_C1)
    r_C1^disp = r_mid − (E/2)·(r_R − r_C1)

E = 1 reproduces the true normalized distances exactly. Graph panels always
use the unexaggerated numbers. The optional C2 marker adds its small
unexaggerated true offset to the displayed C1 position, so it visibly
hugs C1.

In code these are named `trueRadiusR`, `trueRadiusC1`, `displayRadiusR`,
`displayRadiusC1`, and `exaggerationFactor`.

## 5. Sphere, shell, and scan

Tracer coordinates (x, y, z) are rotated with yaw/pitch matrices,
perspective-projected onto a normal 2-D canvas, and depth-sorted before
drawing (no WebGL). The sphere's growth uses a presentation factor

    aVisual = 0.06 + 0.94 · easeOutCubic(animationProgress),

which is a cinematic device, not a cosmological scale factor. The scan
redshift `zScan` falls from an illustrative early state toward 0; each
tracer's brightness follows a radial shell,

    weight = exp(−0.5 · ((z_i − zScan) / shellWidth)²),

so only tracers near the graph cursor light up. The moving redshift shell
controls emphasis only. All synthetic tracers remain present throughout
the visualization; the global `aVisual` factor alone controls the
cinematic growth of the sphere. Three regimes are shown:
z > 2.33 illustration only (no paper inference), 1.8 < z ≤ 2.33
continuation-test region (the compact map fails at the z = 2.33 anchor),
and 0 ≤ z ≤ 1.8 constrained reconstruction domain.

## 6. Validation panel

The third panel plots held-out error above the raw minimum for the
compact-description orders 2–6 on the constrained domain, with a dashed
line at minimum + 2 (the predeclared smallest-order-within-2 rule, which
selects order 3 although order 4 is lower by ∼0.13). Metric cards quote the
fixed publication values: null bootstrap P(select ≥ m=3) = 0.216
(representation complexity, not existence of the separation), projected
Jacobian rank 5/5 with condition number ≈ 27, extra-scaling = 0 allowed at
Δχ² = 0.124, ruler ratio R/C1 ≈ 0.92, and the failed z = 2.33
continuation test.
