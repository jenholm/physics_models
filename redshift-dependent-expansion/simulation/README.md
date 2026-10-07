# Redshift-Dependent Expansion — interactive visualization

**Same synthetic tracers, different fitted expansion histories.**

This page shows one set of **synthetic galaxy tracers** (not observed
galaxies) projected through two fitted expansion histories from the paper:

- **Blue (R)**: the distance-sector endpoint — what the low-redshift
  distance sector prefers over z ≤ 1.8. A phenomenological endpoint, not a
  complete cosmological model.
- **Red (C1)**: the Planck-compatible reference history.
- **Amber halo (C2, off by default)**: a second Planck-compatible reference
  on the same sky. It sits nearly on top of C1 and only checks reference
  sensitivity — it is not an independent confirmation.
- **White spokes**: the radial gap between the two projections of one
  tracer, multiplied by a display exaggeration (default ×8, badge shown).
  Lengths are not to scale.

> **ILLUSTRATIVE — radial differences exaggerated; not a literal spatial
> model of the Big Bang.** Cosmic expansion is not literally an explosion
> into surrounding space; the growing sphere is a visual metaphor.

## Run it (30 seconds)

```bash
cd simulation
python3 -m http.server 8000
# open http://localhost:8000/
```

No build step, no dependencies besides the p5.js CDN. For a single file
you can copy anywhere:

```bash
python3 scripts/build_standalone_simulation.py
# -> simulation/dist/redshift_expansion_simulation.html
```

## Controls

| Key | Action |
| --- | ------ |
| Space | pause / resume |
| ← / → | step redshift (pauses) |
| R | restart |
| S | save PNG snapshot |
| C | toggle C2 sensitivity reference |
| L | toggle pair lines |
| G | toggle graph dashboard |
| E | cycle exaggeration 1× / 4× / 8× / 12× |
| H | toggle help |
| drag / wheel | rotate sphere / zoom |

Hover any tracer for its nominal redshift, both distances, the active
exaggeration, and the true fractional distance difference.

## What is constrained, and where

- **z ≤ 1.8** (blue-tinted): the constrained reconstruction domain.
- **1.8 < z ≤ 2.33** (amber): continuation-test region. The compact
  order-3 map fails through the z = 2.33 anchor — that point is excluded
  from order selection.
- **z > 2.33**: illustration only; no paper inference.

The bright shell marks the current redshift cursor; the same cursor moves
on the graphs below. Near z ∼ 0.65, the visualization highlights the region where the expansion-rate difference is largest. Spoke length represents an integrated comoving-distance difference, so its maximum need not occur at the same redshift. This page does not claim a physical transition or new physics.

## Data

All numbers come from `data/publication_simulation_data.json`, built by
`scripts/build_simulation_data.py` from fixed publication artifacts only
(241-point resampling over 0 ≤ z ≤ 2.33). No observed-catalog rows are
embedded. See [METHODOLOGY.md](METHODOLOGY.md) for the equations.

Canonical project URL:
`https://github.com/jenholm/physics_models/tree/main/redshift-dependent-expansion`
