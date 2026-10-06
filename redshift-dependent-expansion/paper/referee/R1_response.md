# Response to Referee R1 — major revision

> Rule (PROJECT.md `COMMON_GEOMETRY_MAJOR_REVISION`): no item is marked
> resolved merely because text was edited; each row carries a
> file/evidence pointer. R4V/R5/R6 scientific results are frozen; no new
> theory family, no endpoint refit, no new order selection, no
> hidden-sector fitting, no new physical interpretation. The only new
> calculations are the optimizer/gate stability audit (R8-005) and the
> peak-support diagnostic (R8-009).

## 0. Overall assessment

**Referee comment (paraphrase):** the empirical observation is
interesting and worth publishing if presented clearly; objections concern
exposition, nomenclature/provenance clutter, statistical interpretation,
and two technical clarifications.

**Action taken:** full revision restricted to presentation plus two
bounded diagnostics. **Files changed:** `PROJECT.md` (new active
disposition `COMMON_GEOMETRY_MAJOR_REVISION`), `paper/referee/`
(record). **Evidence:** `runs/cmb_bridge/r6/r6_disposition.json`
plus `paper/evidence/cmb_bridge_r{4v,5,6}/` hashes unchanged.
**Disposition:** READY_FOR_REVIEW.

## 1. Manuscript structure (internal research log)

**Action taken:** main paper restructured to Introduction; Data and
endpoint definitions; Empirical reconstruction method; Predictive
model-selection tests; Reference-branch robustness; Results;
Discussion; Limitations; Conclusions. Development history moved to
`paper/supplement/development_provenance.tex` (input after
Appendix G); predecessor detail nested as labeled detail subsections.
**Files changed:** `paper/main.tex`, `paper/sections/01,02,03,05,06,06B,06C,06D,06E_triangulation.tex`,
`paper/supplement/development_provenance.tex`.
**Manuscript location:** Table of contents / section headings.
**Disposition:** READY_FOR_REVIEW.

## 2. Nomenclature table

**Action taken:** created `paper/tables/nomenclature.tex` (R, C1, C2,
$\Delta_1$, $\Delta_2$, $\Delta_C$, m3, $\epsilon$ with Meaning / How
obtained / Used for) with a Historical-development-labels paragraph
(M28 → R, B2 → C1, not scientific variables), input immediately after
the endpoint-definitions opening. **Disposition:** READY_FOR_REVIEW.

## 3. Equation and notation inconsistency

**Action taken:** headline result recast with defined fields
($\Delta_1 \simeq \Delta_2$, $\|\Delta_C\| \ll \|\Delta_{1,2}\|$;
Introduction, endpoint representation, robustness section); generic
`R-C` → 0 hits in build sources (subscripted $R-C_{1,2}$ retained only
inside explicit definitions). **Evidence:** `test_no_undefined_generic_C_difference`,
`test_delta_fields_formally_defined` in
`tests/test_referee_r1_revision.py`. **Disposition:** READY_FOR_REVIEW.

## 4. SN absolute-magnitude profiling mathematics

**Action taken:** joint profile $\hat M = 1^T C^{-1} r_0 / 1^T C^{-1} 1$
stated with "The primary joint likelihood profiles one common $M$";
subset equations $\hat M_{\rm ladder}$, $\hat M_{\rm nonladder}$ added
with "audit diagnostics (diagnostic-only) ... not additive
contributions to the primary joint likelihood."
**Files changed:** `paper/sections/03_data_likelihoods.tex`.
**Evidence:** `test_sn_M_profile_math_explained`,
`test_subset_M_is_diagnostic_only`. **Disposition:** READY_FOR_REVIEW.

## 5. Hard-gate optimizer discontinuity (bounded audit)

**Action taken:** no refit. New audit
`scripts/paper/audit_gate_optimizer_stability.py`: frozen-optimum
replay + 24 starts (interior / perturbations / near-gate) under the
hard gate + local-attractor cloud + smooth-softplus-penalty diagnostic
(which may not replace the frozen solution).
**Evidence:** `paper/evidence/optimizer_gate_stability/{starts.csv,local_attractor.csv,hard_gate_summary.json,smooth_penalty_check.json,disposition.json}`
with disposition `FROZEN_OPTIMUM_GATE_ROBUST`, including the documented
finding that distant single-start SLSQP is trapped by sentinel plateaus
(the frozen result stands on its global-search provenance).
**Disposition:** READY_FOR_REVIEW (escalation path predeclared if a
better feasible point had appeared; none did).

## 6. Similarity p-value (2.2) — no manufactured statistic

**Answer:** We agree that the distinction between order-selection
significance and reference-branch similarity required clarification.
Because C1 and C2 share Planck information and both difference fields
contain the same R endpoint, the similarity metrics are not independent
random draws and we do not assign them a naive p-value. We have
reframed R6 as a reference-branch robustness test and now state this
explicitly.

**Action taken:** new subsection "Statistical status of the
reference-branch robustness test"; "triangulation confirms" →
"reference-branch robustness test shows" throughout.
**Files changed:** `paper/sections/06E_triangulation.tex`,
`paper/sections/00_abstract.tex`. **Disposition:** READY_FOR_REVIEW.

## 7. Meaning of "independently constructed"

**Action taken:** created
`paper/tables/endpoint_construction_comparison.tex` (observations,
Boltzmann code, likelihood, parameterization, primordial spectrum,
optimizer, extraction, H0, $\Omega_m$, $r_d$, $r_s$ for C1 vs C2) plus
the precise sentence "C1 and C2 are independently constructed in
pipeline/model space, not statistically independent in data space; both
use Planck information." "Independent CMB measurements /
observations / confirmation" removed (validator-enforced).
**Evidence:** `test_r6_not_called_independent_confirmation`,
`test_shared_planck_information_disclosed`. **Disposition:** READY_FOR_REVIEW.

## 8. Branch $r_d$/$r_s$ calibration contract

**Action taken:** created
`paper/evidence/branch_calibration_contract.json` (R: $r_d=135.39$
pinned, $r_s$ explicitly not used; C1: $r_d=147.15$, $r_s=144.50$
CAMB-recomputed; C2: $r_d=147.11$, $r_s=144.45$ CAMB-recomputed; R's
ruler differs by construction) with manuscript
Table~\ref{tab:calibration} and branch-specific BAO forward model
$D_M/r_d, D_H/r_d, D_V/r_d$; legacy "at $A_E=0$ ratios are unity"
mechanism moved to Appendix B (appendix-only, not needed to reproduce
R). **Evidence:** `test_branch_rd_contract_complete`.
**Disposition:** READY_FOR_REVIEW.

## 9–10. $z \approx 0.65$ peak: leverage diagnostic + language

**Action taken:** no refit. New diagnostic
`scripts/paper/analyze_peak_support.py` (SN count/inverse-variance
densities, DESI information density + blocks, $|\Delta_{\rm common}|$,
frozen R5 attribution, frozen m3 peak comparison).
**Evidence:** `paper/evidence/peak_support/{sn_density.csv,sn_weight_density.csv,bao_support.csv,common_deformation.csv,peak_support_summary.json,figure_peak_vs_data_support.pdf}`,
disposition `PEAK_NOT_EXPLAINED_BY_SIMPLE_DATA_DENSITY` (peak at
$z=0.651$ coincides with no simple density maximum; frozen m3 peaks at
the same location). Manuscript states the fitted difference reaches its
largest amplitude near $z\approx0.65$ but, carrying substantial
observational leverage there, the peak is not interpreted as a
fundamental physical scale; origin unresolved
(Sections 5–6, `sec:peak-support`). **Disposition:** READY_FOR_REVIEW.

## 11. "Telescope stays fixed" metaphor

**Action taken:** replaced everywhere with "Observed values,
uncertainties, and covariance matrices are held fixed across model
comparisons." **Evidence:** `test_no_telescope_metaphor` (0 hits).
**Disposition:** READY_FOR_REVIEW.

## 12. Copy-edit pass

**Action taken:** aspell TeX-mode sweep (no genuine typos; cited
examples absent), hyphenation normalization (CMB-compatible,
distance-compatible, low-/high-redshift, best-fit, held-out).
**Evidence:** `paper/evidence/copyedit_report.md`.
**Disposition:** READY_FOR_REVIEW.

## 13. Table 8 statuses

**Action taken:** verified no sentence-fragment status entries remain in
the manuscript (sector contract lives in evidence JSON; prose uses
complete grammatical entries). **Evidence:**
`test_table_statuses_are_grammatical` (new in R8-020 file — see
`test_peak_not_called_physical_transition` cohort; fragment scan over
`paper/sections` and generated tables). **Disposition:** READY_FOR_REVIEW.

## 14. Defensive historical language

**Action taken:** $\epsilon=-0.0149$ rewritten as calm closure-diagnostic
prose compatible with $\epsilon=0$; "different universes" →
"quantitatively different expansion histories"; "not presented as one"
instances removed where debugging-toned (two appropriate "must not be
confused/conflated" disambiguations retained).
**Disposition:** READY_FOR_REVIEW.

## 15. Predecessor-results contamination

**Action taken:** Results section rewritten as synthesis over R/C1/C2/m3
only; predecessor publication-vector tables removed from the main text
(canonical Model A table moved appendix-only to Appendix B with label
preserved for existing references); branch-detail subsections carry
explicit R/C1 reading guides.
**Disposition:** READY_FOR_REVIEW.

## 16. Reference audit

**Action taken:** added the missing SH0ES Cepheid-calibration reference
(Riess et al. 2019, ApJ 876, 85) cited alongside Riess et al. 2022 at
the calibrator contract; CAMB citations attached to Boltzmann-ruler
statements (Lewis et al. 2000; CLASS Blas et al. 2011 already cited at
the validation description); compressed prior (Chen et al. 2019) now
explicitly framed as an exploratory predecessor approximation, not a
substitute for C1/C2 full-CMB validation. ACT not mentioned — no action.
**Files changed:** `paper/references.bib`,
`paper/sections/02,03_data_likelihoods.tex`.
**Disposition:** READY_FOR_REVIEW.

## 17. Title

**Action taken:** retitled to "Characterizing a Low-Dimensional
Redshift-Dependent Difference Between CMB- and Distance-Compatible
Expansion Histories" in `main.tex` (title + pdftitle),
`metadata.yaml`, and the framing test expectation.
**Evidence:** `test_title_is_characterization_not_geometry_detection`.
**Disposition:** READY_FOR_REVIEW.

## 18. Interpretive sentence placement

**Action taken:** end-of-Introduction now carries "The principal result
of this work is therefore not a specific dynamical model, but an
empirically defined expansion-history target that candidate explanations
of the CMB–distance discrepancy can be tested against," with the
shortened form retained in the Conclusion.
**Disposition:** READY_FOR_REVIEW.

## 20–22. Tests, reader check, acceptance

**Evidence:** `tests/test_referee_r1_revision.py` (17 tests, all green);
`test_paper_geometry_pivot.py` title expectation updated; R4V/R5/R6 +
claim-gating + provenance suites green (frozen evidence byte-untouched);
claims + referee-attack validators PASS; clean `pdflatex` with zero
undefined references; flat arXiv bundle check passed; fresh-reader
protocol 8/8 PASS from the paper alone.
**Final disposition:** `COMMON_GEOMETRY_MAJOR_REVISION_COMPLETE`.
**Disposition:** READY_FOR_REVIEW.
