# Redshift-Dependent Expansion

Characterizing the empirical redshift-dependent difference between
distance-sector and Planck-calibrated expansion histories, with
reproducible tools for testing candidate physical explanations.

## Results at a glance

- R: phenomenological distance-sector endpoint, H0 = 72.80
- C1/C2: Planck-compatible references (C2 is a sensitivity check, not independent confirmation)
- constrained reconstruction domain: z <= 1.8
- five-coordinate order-3 representation
- order-selection bootstrap P = 0.216; no discovery claim
- Ly-alpha z = 2.33 continuation fails
- physical origin remains open

## Paper

- [PDF](paper/main.pdf)
- [Source](paper/)
- [Reproducibility](docs/REPRODUCIBILITY.md)

## Interactive visualization

- [Simulation source](simulation/)
- [Methodology](simulation/METHODOLOGY.md)

## Scientific scope

See [docs/SCIENTIFIC_SCOPE.md](docs/SCIENTIFIC_SCOPE.md).

## Repository structure

```text
paper/                 manuscript source, evidence, figures, tables
paper/evidence/        versioned publication evidence (neutral directories)
paper/generated/       registry, macros, provenance (generated, checked in)
scripts/paper/         neutral paper-build scripts
scripts/               simulation data + standalone builders
simulation/            interactive visualization (synthetic tracers only)
tests/                 hygiene, parity, and simulation tests
docs/                  scope, reproducibility, data policy
```

## Citation

See [CITATION.cff](CITATION.cff).

Canonical project URL:
`https://github.com/jenholm/physics_models/tree/main/redshift-dependent-expansion`
