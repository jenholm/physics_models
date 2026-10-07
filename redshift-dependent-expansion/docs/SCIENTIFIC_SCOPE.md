# Scientific scope

## What R, C1, C2 are

- **R** is a phenomenological distance-sector endpoint: the expansion
  history the low-redshift distance data (DESI DR2 BAO plus
  Pantheon+SH0ES supernovae) prefer, with H0 = 72.80. It is not a
  complete cosmological model: no validated recombination, BBN, or
  perturbation completion is provided for R.
- **C1** is a Planck-compatible reference history (H0 = 67.99),
  calibrated to the full Planck TT/TE/EE spectra.
- **C2** is a second, separately implemented Planck-compatible
  reference (H0 = 67.4). It shares the same Planck sky as C1, so it is
  a sensitivity check on the reference construction, not an
  independent confirmation of anything.

## What the order-3 reconstruction means

Over the constrained domain (z <= 1.8), the logarithmic differences
between R and each reference are described by a compact
five-coordinate order-3 representation (an overall amplitude, a
reciprocity parameter, and three shape coefficients). It is an
empirical summary of the measured separation, not a physical law, and
it does not extend to higher redshift.

## What P = 0.216 means and does not mean

Constrained-domain held-out prediction selects order 3 under the
predeclared smallest-order-within-2 rule (order 4 is lower by only
0.13). A matched null bootstrap gives P(select >= m=3) = 0.216. This
tests the complexity of the selected representation, not the
existence of the numerical separation between the fixed endpoint
histories. Order selection alone is not evidence of a discovery, and
no statistical significance is claimed.

## Why C2 is sensitivity, not confirmation

C1 and C2 use the same Planck data with different construction
pipelines. The fact that the R-versus-CMB difference looks the same
against either reference shows the result is insensitive to the
tested reference-construction choices. Because both references share
the Planck sky, this cannot count as independent confirmation.

## Why z <= 1.8 is the constrained domain

Order selection uses supernova and DESI folds at z <= 1.8. The
z = 2.33 Lyman-alpha anchor is scored separately as an
out-of-domain continuation test and never participates in selection.

## Why Lyman-alpha is a failed extrapolation test

The order-3 reconstruction fails its z = 2.33 Lyman-alpha
continuation test: the compact low-redshift map does not extrapolate
to the high-redshift anchor. This bounds the claim (domain ends at
z <= 1.8) rather than rescuing the model.

## No physical mechanism is claimed

No dynamics, no metric theory, no recombination physics, and no
Hubble-tension resolution are established here. The paper
characterizes a reproducible phenomenological difference and provides
the tools to test candidate explanations against independent
observables.
