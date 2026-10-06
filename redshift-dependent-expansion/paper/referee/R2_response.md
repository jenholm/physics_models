# Response to Referee R2 — point-by-point (R8R2-025)

> Rule (PROJECT.md `COMMON_GEOMETRY_REFEREE2_REVISION`): no item is
> marked resolved merely because text was edited; each row carries a
> file/evidence pointer. R4V/R5/R6 evidence frozen; only re-score of
> frozen folds, a matched constrained bootstrap, explanatory contracts,
> restructuring, and bibliography fixes were performed. No endpoint
> refit, no new model, no data/covariance change, no BBN fit, no
> Lyα-specific parameters, no $z=1.8$ boundary change.

## 0. Overall — architecture and claim semantics, not frozen evidence

**Assessment:** VALID. **Action:** bounded repair cycle R8R2-001..026;
no new cosmological model. **Files:** `PROJECT.md`
(`COMMON_GEOMETRY_REFEREE2_REVISION`), `paper/referee/R2_report.txt`,
this file. **Disposition:** READY_FOR_REVIEW.

## 1. R ≡ Model A identity (H0 72.80 vs 73.21)

**Assessment:** VALID — the most important fix; the H0 complaint is
absolutely valid. **Action:** created the endpoint identity contract;
severed every "Model A behind R" statement; nomenclature updated;
interchangeability validator added. **Files:**
`paper/evidence/endpoint_identity_contract.json`
(R = `runs/cmb_bridge/r3/smooth_lowz_history.npz`, H0 72.80;
historical Model A =
`runs/cmb_reconstruction/frozen/MODEL_A_FINAL.json`, H0 73.21, not the
same endpoint), `paper/tables/nomenclature.tex`,
`tests/test_referee_r2_revision.py::test_R_is_not_Model_A` +
`test_endpoint_identity_h0_values`. **Manuscript location:**
Section 2 opening + nomenclature table. **Disposition:** READY_FOR_REVIEW.

## 2. Model A/B2 archaeology in the main results path

**Assessment:** VALID. **Action:** `06B/06C` no longer input from the
main results section; moved nearly intact to
`paper/supplement/predecessor_branch_validation.tex` (input in the
appendix block); main endpoint construction keeps only the short
provenance paragraph (Model A failed Planck; B2 is C1's lineage).
**Evidence:** supplement file; `main.tex` wiring; R8R2 tests.
**Disposition:** READY_FOR_REVIEW.

## 3. R presented as a viable cosmology

**Assessment:** VALID. **Action:** R reclassified as a
phenomenological low-redshift endpoint (`complete_cosmology=false`,
`full_cmb_validated=false`, `bbn_validated=false` in the identity
contract); endpoint construction, limitations, discussion, and
conclusion rewritten: R describes what the fitted distance sector
prefers; Model A was one attempted completion and failed Planck; the
target is R-like low-$z$ behavior with CMB acoustic structure
retained. **Evidence:** `test_R_marked_phenomenological_not_viable_cosmology`.
**Disposition:** READY_FOR_REVIEW.

## 4. r_d = 135.39 Mpc viability buried

**Assessment:** VALID — burying this is unacceptable. **Action:**
contract extended (`rd_ratio_to_C1 = 0.920`, `rd_ratio_to_C2 = 0.920`,
`early_universe_viability`, `full_cmb_status`, `bbn_status`); new
manuscript paragraph states the ~8% smaller ruler is a property of the
phenomenological endpoint, not a demonstrated physical sound horizon,
unvalidated by the compressed prior, with no BBN claim and no BBN fit.
**Files:** `paper/evidence/branch_calibration_contract.json`,
`02_endpoint_construction.tex`. **Evidence:**
`test_rd_135_not_called_CMB_validated`. **Disposition:** READY_FOR_REVIEW.

## 5. C2 weak independence

**Assessment:** VALID. **Action:** subsection retitled to Secondary
Planck-compatible reference C2; "independently constructed branch" →
"separately implemented reference construction"; triangulation language
→ reference-sensitivity/reference-branch robustness; no C3 added.
**Evidence:** `test_C2_is_reference_sensitivity_not_independent_confirmation`.
**Disposition:** READY_FOR_REVIEW.

## 6. Discovery-like claim statuses

**Assessment:** VALID. **Action:** `GEOM-CMB-CONSISTENCY`,
`GEOM-COMMON-MODE`, `GEOM-TRANSFER`, `BRIDGE-TRIANGULATION` moved from
`supported` to `descriptive_robustness` (validator extended);
interpretation changed to "changing between these two
Planck-compatible references changes the inferred difference only
slightly". **Files:** `paper/claims.yaml`,
`scripts/paper/validate_claims.py`. **Disposition:** READY_FOR_REVIEW.

## 7. Lyα fold drives order selection

**Assessment:** VALID. **Action:** no refit;
`scripts/paper/rescore_bridge_cv_constrained.py` re-scores frozen folds
(DESI $z\le1.8$ + SN): m2 = 8213.92, m3 = 8164.28, m4 = 8164.15
(raw minimum, +0.13), m5 = 8186.77, m6 = 8184.00 — the predeclared
smallest-$m$-within-2.0 rule still selects **m3**, independent of the
Lyα catastrophe. **Evidence:**
`runs/cmb_bridge/r8r2/constrained_cv_rescore.json` byte-identical to
`paper/evidence/cmb_bridge_r8r2/constrained_cv_rescore.json`;
`test_constrained_cv_excludes_lya_from_selection`,
`test_constrained_cv_rule_still_selects_m3`. **Disposition:** READY_FOR_REVIEW.

## 8. Lyα kept as failed continuation, not an excuse

**Assessment:** VALID. **Action:** `06D_bridge.tex` rewritten —
constrained selection, then Lyα scored separately where every order
fails; validated domain ends at $z\le1.8$, bounding the claim.
**Evidence:** `test_lya_continuation_failure_retained` + score table
`paper/tables/generated/constrained_cv_rescore.tex`.
**Disposition:** READY_FOR_REVIEW.

## 9. Bootstrap mismatched to selection rule

**Assessment:** VALID. **Action:** added `--score-domain
{full,constrained}` (nothing else changed); ran a new 250-replicate
constrained bootstrap (8 shards, recorded seeds) to
`runs/cmb_bridge/r8r2/selection_bootstrap_constrained.json`
(promoted byte-identical to paper evidence); R5 bootstrap untouched
(verified: still n=250, P=0.148). **Result, reported exactly as
obtained:** selection frequency m2/m3/m4/m5/m6 = 196/26/14/8/6,
**P(select≥m3) = 0.216**, Lyα catastrophe 0.788 recorded separately.
**Evidence:** `test_bootstrap_scoring_matches_selection_domain`.
**Disposition:** READY_FOR_REVIEW.

## 10. Inflated statistical headline

**Assessment:** PARTLY VALID (concern fair; "whole result is null"
conflation declined). **Action:** "establish a branch-robust empirical
background-geometry difference" → "characterize a reproducible
phenomenological difference between the frozen endpoint histories";
added: the bootstrap tests representation complexity, not existence of
the endpoint separation; removed detection/establish/confirmed wording
from headline sections — but did not write that the R–CMB difference
itself has p=0.216, which would be statistically false.
**Disposition:** READY_FOR_REVIEW.

## 11. Rank reads as "five observables"

**Assessment:** VALID. **Action:** generated
`paper/evidence/cmb_bridge_r4v/rank_operator_contract.json` (columns
logK_H/epsilon/c0/c1/c2; 1670 rows; whitening + M-projection operators;
finite-difference policy; S = [602.38, 157.31, 102.07, 32.03, 22.31];
cond ≈27); Methods carries the $J_{ij}$ equation and calls it local
projected Jacobian rank 5/5 fitted coordinates — never five
observables. **Evidence:** `test_rank_contract_has_1670_rows_5_named_columns`,
`test_no_effective_five_observables_phrase`. **Disposition:** READY_FOR_REVIEW.

## 12. Methods about the M28 optimizer, not the bridge

**Assessment:** VALID. **Action:** `05_methods.tex` rewritten around
bridge coordinates, residual vector, SN profile, folds, selection rule,
Jacobian rank, bootstrap, descriptive IC; the 23-vector history moved to
`paper/supplement/predecessor_R_construction.tex`.
**Evidence:** `test_main_methods_contains_no_A_E_or_q_l`.
**Disposition:** READY_FOR_REVIEW.

## 13. Eq.(6) repeated-q10 complaint

**Assessment:** STALE — the defect was not present in the revised
source (unique slots $q_{l0..2}$, $q_{\rho0..2}$); regression test
added. **Evidence:**
`test_predecessor_vector_unique_slots` (23 unique slots).
**Disposition:** READY_FOR_REVIEW.

## 14. Bare null undefined

**Assessment:** VALID. **Action:** `--export-contract` on
`run_cmb_bridge_r5_null_cv.py` →
`paper/evidence/cmb_bridge_r5/null_model_contract.json` (bare LCDM, 0
bridge parameters, $K_H$ fixed, $\epsilon$ n/a, M profiled per
fold-train); 06D states the null explicitly before quoting
$\Delta\chi^2=-76.1$. **Evidence:**
`test_bare_null_contract_present`. **Disposition:** READY_FOR_REVIEW.

## 15. AIC criticism

**Assessment:** PARTLY VALID (mathematically true, not an error).
**Action:** AIC removed from the abstract; k/χ²/Δχ²/AIC/ΔAIC reported
side-by-side ($\Delta{\rm AIC}=-23.96$); "substantial evidence" →
"m3 gives up 8.04 in χ² while using 16 fewer fitted bridge
coordinates; AIC therefore favors the compact representation primarily
through its parsimony penalty"; never a detection or calibrated
probability. **Evidence:** `test_aic_called_descriptive_parsimony`.
**Disposition:** READY_FOR_REVIEW.

## 16. SN 1657-row selection unreproducible

**Assessment:** VALID. **Action:** generated
`paper/evidence/sn_selection_contract.json` from the likelihood module
(raw 1701, exact mask `(zHD > 0.01) | IS_CALIBRATOR`, 1657 selected,
77 calibrators, 1580 Hubble-flow, covariance + ordering hashes); mask
in `03_data_likelihoods.tex`. **Evidence:**
`test_sn_selection_1701_to_1657`. **Disposition:** READY_FOR_REVIEW.

## 17. Distance-duality citation

**Assessment:** VALID. **Action:** foundational citation for
$D_L=(1+z)D_M$ replaced with Etherington (1933, Phil. Mag. 15,
761–773, DOI 10.1080/14786443309462220); Renzi kept for
observational-test context. **Evidence:** `test_etherington_cited`.
**Disposition:** READY_FOR_REVIEW.

## 18. Chen-prior scope warning

**Assessment:** PARTLY VALID (partly already addressed). **Action:**
warning moved into the R-construction opening paragraph and the ruler
table caption: the compressed prior validated only conventional
late-time models and did not validate the $r_d=135.39$ physics; only
historical endpoint discovery used it. No rerun. **Disposition:** READY_FOR_REVIEW.

## 19. Scale-vs-shape obstruction literature

**Assessment:** VALID and genuinely relevant. **Action:** cited Zhou et
al., PRD 114, 063511 (2026), with a short complementary paragraph: R
contains both a large ruler shift and a shape difference; ruler
rescaling alone is not claimed to solve the tension; no agreement
claimed beyond what was compared. **Disposition:** READY_FOR_REVIEW.

## 20. Giant Table 1 cure

**Assessment:** DECLINED (with cleaner alternative). **Action:** Table 1
kept to R/C1/C2/Δs/$K_H$/$c_j$/m3/ε;
comprehensive historical-symbol table added only in the technical
supplement. **Evidence:** `test_main_nomenclature_has_no_M_labels`.
**Disposition:** READY_FOR_REVIEW.

## 21. Validated-range framing

**Assessment:** VALID. **Action:** every headline occurrence carries
$z\le1.8$ or the defined constrained-domain pattern; conclusion states
Lyα continuation fails, bounding the claim. **Disposition:** READY_FOR_REVIEW.

## 22. Closing target overclaims

**Assessment:** VALID. **Action:** closing sentence replaced: "The
resulting target is the low-redshift distance-sector behavior
represented by R over $z\le1.8$, together with the requirement that any
physical completion preserve the observed CMB acoustic structure; R
itself is not asserted to be such a completion."
**Evidence:** `test_final_target_requires_CMB_preservation`.
**Disposition:** READY_FOR_REVIEW.

## 23. Stale copy-edits

**Assessment:** STALE. "Deliberately" is spelled correctly in the
revised source (verified in rendered PDF via `pdftotext`, 1 correct
occurrence, 0 misspellings); the parameter vector is corrected (unique
slots verified in rendered PDF). **Evidence:** this section +
`test_predecessor_vector_unique_slots`. **Disposition:** READY_FOR_REVIEW
("No such typo exists in the revised source; verified in rendered PDF.")

## R8R2A consistency-pass addendum (editorial/plot defects, no new fits)

- **Claim-evidence table regenerated** from active GEOM/BRIDGE claims
  (M28-era rows removed).
- **Registry repaired:** GEOM-SIGNIFICANCE now points at the matched
  constrained bootstrap (P=0.216); BRIDGE-DIMENSION rewritten for
  constrained selection; BRIDGE-RANK rewritten as local projected
  Jacobian rank; allowed-status comment includes
  `descriptive_robustness`.
- **Discussion bootstrap number** unified to `\CvConstrBootProb`
  (0.216); exactly one active complexity-selection probability remains.
- **Figure 2 regenerated:** top panel now plots constrained-domain
  $\Delta\chi^2$ held-out vs the constrained minimum (m3/m4 near-tie
  visible); Lyα stays a separate log-scale bottom panel.
- **Peak-support m3-peak labeling error corrected:** the plotted
  frozen-m3 curve peaks near 0.39, not 0.65 (0.669 was the
  m3-vs-control residual maximum). Manuscript now states R-C1/R-C2 both
  peak near 0.65 while m3 captures the broad trend but not the exact
  peak (`sec:peak-support`; corrected summary JSON).
- **R5/R6 peak bins:** "same region" replaced with "both concentrate
  below $z\sim0.8$, though their peak bins differ" (R5: 0–0.4; R6:
  0.4–0.8).
- **C2 wording:** "pipeline-independent", "independently constructed",
  "independent ΛCDM/Planck pipeline" all replaced with separately
  implemented / secondary-reference language.
- **C1 parameterization:** frozen stage-0 background reference (no
  running assigned to C1 itself); running kept in B2 historical lineage.
- **Limitations trimmed** to this paper's scope; archaeology moved to
  the supplement.
- **$f_{\rm common}$ defined** as
  $1-\mathrm{RMS}^2(\Delta_{\rm disagreement})/
  \mathrm{RMS}^2(\Delta_{\rm common})$.
- **§4 sentence** replaced with "reference-sensitivity analysis is a
  separate robustness check, not a significance test."
- **Tables 1/3 reflowed** (`tabularx`/`p{}`/`\small`); overfull-box gate
  added.
- **References:** `DESIDR2w0wa` duplicate deleted (cite `DESIDR2`);
  Zhou author list corrected; Chen-prior scope confirmed
  (ΛCDM/$w$CDM/CPL only); Etherington retained.
- **Absolute statements softened** (headline-values hashing;
  bootstrap stopping-tolerance note).
- **New Figure 1** (frozen-endpoint overview) generated from R6
  evidence; plain-language paragraph added after the headline equations
  with a shortened form at the end of the abstract.
