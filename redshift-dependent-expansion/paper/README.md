# M28 Early-Epoch Paper

Reader-facing manuscript: one early-epoch amplitude added to a
late-time chronogeometric law, fit to the joint DESI DR2 BAO,
Pantheon+SH0ES, and compressed-CMB likelihood.

## Workflow

- Frozen evidence: `paper/evidence/m28_final/` (17 files, hash-bound
  via `provenance_manifest.json`). No frozen-vector, data, or
  likelihood change in prose cycles.
- Registry/macros: `scripts/paper/build_results_registry.py` owns
  `paper/generated/results_macros.tex`,
  `paper/generated/results_registry.json`, `paper/generated/provenance.json`.
  Never hand-copy numbers; use the neutral publication macros in `paper/generated/results_macros.tex`.
- Figures: `scripts/paper/generate_m28_figures.py` writes
  `paper/figures/generated/figure_0{1,2,3,4,5,6}_*.pdf` with sidecar
  CSV + meta.json (source hashes). Fig4 uses full-joint `M_hat_m28`
  parity (every main residual uses one common `M`).
- Tables: `scripts/paper/generate_m28_tables.py` writes
  `paper/tables/generated/m28_*.tex` with CSV + meta.json. T2 uses
  `h r_d [Mpc]` (never km/s/Mpc); T6 lists scientific scope only.
- Driver: `scripts/paper/build_expansion_history_paper.py` replays evidence,
  rebuilds registry/figures/tables, validates claims in release mode,
  compiles with pdflatex+bibtex, builds and checks the arXiv bundle.
- Bundle: `scripts/paper/build_arxiv_bundle.py` collects only the
  dependency graph from `main.tex` (whitelist); legacy figures/tables
  live under `figures/generated_legacy/` and `tables/generated_legacy/`
  and are excluded. Historical evidence is never deleted.

## PAPER-03 rules

- Main sections (`00,01,02,03,05,06,07,08,09`) are reader-facing:
  no `G10`, `M28R1`, `R131`, `M24B`, `M26A`, `rebase`, `winner`,
  `gate`, `ceiling`, `frozen G10`, or `frozen late-time law` outside
  appendices. Internal labels live in Appendix A/D only.
- `PAPER_MODE=release` runs `validate_claims.py` release gates plus
  wrong-`h_rd`-units failure.
- History: `sections/04_history.tex` is a thin redirect to Appendix A;
  full development history lives in `appendices/A_*`; 2025 draft
  preserved under `legacy_2025_draft/`.
