# Referee response record — minor revision closeout (R3)

This file is a development record for the authors. It is not part of
the manuscript and is not included in the arXiv bundle (the bundle is
built strictly from the `paper/main.tex` dependency graph).

## Item classification

- H0 67.49 — STALE. The current manuscript and PDF already report
  C1 H0 = 67.99 everywhere (Abstract, Introduction, endpoint
  definition, tables, Results, Limitations). Locked by regression test.
- Equation 2–5 labels — STALE. The main-text likelihood block carries
  unique labels for the residual, the estimator, the joint statistic,
  and the subset diagnostics; the cross-reference resolves correctly.
- Equations 7–9 rendering — STALE extraction artifact. The current PDF
  renders all three difference-field definitions with intact symbols,
  minus signs, subscripts, and equation numbers (verified via text
  extraction of the rebuilt PDF).
- Appendix likelihood duplication — VALID. The repeated estimator
  block was removed from the likelihood appendix and replaced with a
  cross-reference to the main-text equations.
- Bootstrap Monte Carlo error — VALID. The registry now exports the
  binomial standard error (0.026 from 250 realizations), stated once
  in Section 4 only.
- Gap 0.13 → 0.14 — DECLINED. Exact evidence gives 0.12756, which
  rounds to 0.13. Now sourced from a generated macro.
- Delta −6.90 → −6.91 — DECLINED. Exact evidence gives −6.90378,
  which rounds to −6.90. The suggested value comes from subtracting
  already-rounded display values. Locked by an exact-arithmetic test.
- "Sections 6–5" — VALID. Fixed to Sections 4–6.
- Duplicated "difference" wording — VALID. Fixed; the section now
  uses the compact en-dash shorthand.
- Ruler-clock wording — VALID. Now "consistent with zero" everywhere.
- Abstract density — VALID. Shortened to 256 words with the requested
  structure (split opening, plain-language sentences kept).
- R-ruler explanation — PARTLY VALID. One operational sentence added;
  no new caveat section.
- Log-scale history figure — DECLINED. The existing difference-field
  panel is more informative; a log-H duplicate adds length without a
  new observable.
- New summary table — DECLINED. Order selection, rulers,
  endpoint construction, and limitations are already tabulated.
- Future-work section — ALREADY SATISFIED. The Discussion names
  chronometers, RSD, weak/CMB lensing, time-delay distances, and
  standard sirens.
- Title suggestion — DISCRETIONARY / NO CHANGE. The current title
  correctly signals an empirical reconstruction paper.

## Numbers locked (no refit, no endpoint change)

C1 H0 = 67.99; selected order 3; raw minimum order 4;
bootstrap P = 0.216 (MCSE 0.026); Jacobian rank 5/5;
epsilon = 0 delta chi-squared = 0.124; constrained domain z <= 1.8;
Lyman-alpha anchor z = 2.33; constrained ratio range about
1.3% to 8.4%.
