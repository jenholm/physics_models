# Inflationary Sector Renormalization

Inflationary Sector Renormalization (ISR) is a toy computational framework for studying whether unobservable inflationary domains can be treated as hidden sectors whose degrees of freedom are integrated out into an effective local measure.

The project does **not** claim to have solved eternal inflation. The serious claim is narrower:

> Treat unobservable inflationary domains as hidden sectors of a shared inflationary field system, integrate them out with a locality-weighted measure, and test whether the resulting effective probabilities become stable under cutoff expansion.

## Central test

The central test is whether a locality-weighted hidden-sector measure is more stable under cutoff expansion than a naive global census measure.

## Bell locality caution

Bell locality is used only as a constraint on measure construction: sectors are weighted by shared causal or field-theoretic ancestry, not by arbitrary global existence. **This is not a local hidden-variable model.**

## What this is

- A toy stochastic inflation simulator (Langevin dynamics on a 1D potential)
- Four probability measures: global census, cutoff-regulated census, locality-weighted ISR, and effective-sector renormalization
- Renormalization stability tests (KL divergence, Wasserstein distance)
- Locality diagnostics inspired by Bell-theorem constraints
- Kernel sensitivity analysis

## What this is not

- This does not prove Bell's theorem.
- This does not solve the measure problem.
- The toy universes are not physical universes.
- "Renormalization" is used in a specific, defined sense: cutoff expansion and probability stability.

## Installation

```bash
cd /home/jenholm/workspace/inflationary-sector-renormalization
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Structure

- `isr/` — core package
- `experiments/` — six experimental scripts
- `configs/` — YAML configurations
- `outputs/` — figures and tables
- `docs/` — theoretical notes and simulation design

## Running experiments

```bash
source .venv/bin/activate
python experiments/01_global_census_baseline.py
python experiments/02_locality_weighted_measure.py
python experiments/03_cutoff_stability.py
python experiments/04_kernel_sensitivity.py
python experiments/05_basin_boundary_test.py
python experiments/06_bell_locality_diagnostic.py
```

- Do not claim Bell proves locality.
- Do not claim ISR solves eternal inflation.
- Do not hard-code the desired result.
- Do not tune the kernel after seeing the answer.
- Do not compare a bad global measure against only one cherry-picked ISR kernel.
- Do not hide failed kernels.
- Do not ignore basin-boundary discontinuities.
- Do not confuse simulation toy universes with physical universes.
- Do not use "renormalization" as decoration. Define the cutoff, the flow, and the stability test.
