# Redshift-Dependent Expansion

## Mission

Characterize the empirical redshift-dependent difference between
distance-sector and Planck-calibrated expansion histories and provide
reproducible tools for testing candidate physical explanations.

## Current scientific result

- R (H0 = 72.80): phenomenological distance-sector endpoint, not a
  complete cosmology.
- C1/C2: Planck-compatible references; C2 is a sensitivity check, not
  independent confirmation.
- Constrained reconstruction domain: z <= 1.8.
- Five-coordinate order-3 representation selected by held-out
  prediction; order-selection bootstrap P = 0.216 (no discovery claim).
- The order-3 reconstruction fails its z = 2.33 Lyman-alpha
  continuation test; physical origin remains open.

## Scope

- Empirical comparison of separately calibrated histories.
- Compact reconstruction of their difference over z <= 1.8.
- Reference-sensitivity checks across two Planck-compatible
  constructions.
- Reproducible evidence, scripts, and visualization.

## Non-goals

- no claim of Hubble-tension resolution
- no claim that R is a complete cosmology
- no claim of independent confirmation from C2
- no inference above z = 1.8 from the compact reconstruction

## Public deliverables

- paper/
- simulation/
- paper/evidence/
- scripts/
- docs/

## Reproducibility rules

- Every number in the manuscript resolves through generated macros to
  versioned publication evidence; never hand-copy numbers.
- Registry/table/figure generation reads only files inside this
  public repository.
- Hash mismatches fail the build.

## Public-repository rules

- no local absolute paths
- no credentials
- no raw private data
- no legacy theory-development archives
- no internal referee reports
- no generated logs/caches
