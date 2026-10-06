# Copy-edit report (R8-012)

Date: 2026-10-05. Scope: `paper/sections/*.tex`, `paper/appendices/*.tex`,
`paper/tables/*.tex`, `paper/main.tex`, `paper/references.bib`.

## Method

- `aspell --mode=tex list` over all section/appendix sources: no genuine
  typos found (hits are acronyms: CMB, DESI, TT/TE/EE, SLSQP, CAMB, npz,
  macro names). The referee's cited examples ("It's provenance", "It is
  low-redshift predictions", "cat astrophically") do not occur in the
  current sources; "catastrophically" is spelled correctly (2x,
  06D_bridge).
- Regex sweep for the defensive set (`not a measurement`, `we do not
  claim`, `we never`, `must not`, `not presented as`): three instances
  rewritten to calm journal prose (06D epsilon closure diagnostic;
  08 "different universes" and "not presented as one"). Retained two
  appropriate instances ("must not be confused/conflated" for the two
  CMB uses — legitimate disambiguation, not debugging language).
- Metaphor sweep: `telescope stays` → 0 hits in build sources
  (only a stale generated copy under `paper/dist/`, regenerated on build).
- `different universes` → 0 hits in build sources.

## Categories

- grammar: headline equations recast with defined fields
  ($\Delta_1 \simeq \Delta_2$, $\|\Delta_C\| \ll \|\Delta_{1,2}\|$);
  Table 8-style status fragments: none present as fragments (the sector
  contract lives in evidence JSON; manuscript prose uses complete
  sentences; verified by `test_table_statuses_are_grammatical`).
- typos: none found by aspell beyond jargon.
- hyphenation: normalized set verified present and consistent —
  CMB-compatible, distance-compatible, low-redshift, high-redshift,
  best-fit (noun adjuncts), held-out. No random `Distance-Compatible`
  capitalization in prose (one subsection heading uses title case,
  correct for headings).
- notation: $R-C_1 \simeq R-C_2$ / $C_1-C_2 \ll R-C$ replaced by
  $\Delta$-field definitions; generic `R-C` → 0 hits in build sources.
- sentence fragments: none introduced; 06_results rewritten as complete
  summary prose.
- legacy terminology: M24/M26A/M28/R131/G10/R4V/R5/R6 removed from
  narrative body (retained only in mapping notes, provenance appendix,
  and the development-provenance supplement); `triangulation confirms`
  → `reference-branch robustness test shows`.

## Disposition

COPYEDIT_COMPLETE. Remaining risk: none blocking evaluation.
