# Redshift-Dependent Expansion Paper

Manuscript: "Characterizing a Low-Dimensional Redshift-Dependent
Difference Between CMB- and Distance-Compatible Expansion Histories"
(Jake Enholm).

## Scientific scope

The paper characterizes the empirical difference between a
distance-sector expansion history (R) and two Planck-compatible
reference histories (C1, C2) over the constrained domain z <= 1.8,
using a five-coordinate order-3 reconstruction selected by held-out
prediction. No physical mechanism is claimed; the origin remains open.
See [../docs/SCIENTIFIC_SCOPE.md](../docs/SCIENTIFIC_SCOPE.md).

## Build instructions

Requirements: Python 3 with NumPy/Matplotlib/PyYAML/SciPy, pdflatex +
bibtex (TeX Live 2023 or newer).

From the repository root:

```bash
make -C paper registry tables figures validate   # rebuild registry, tables, figures, checks
make -C paper build                              # full manuscript build (registry -> pdf)
make -C paper bundle                             # build + arXiv bundle + bundle check
```

Or step by step with the neutral driver:

```bash
python3 scripts/paper/build_expansion_history_paper.py --release
cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

## Evidence policy

- `paper/evidence/` holds versioned publication evidence only, in
  neutral directories (`endpoints/`, `reconstruction/`,
  `model_selection/`, `reference_sensitivity/`, `likelihood/`).
- `paper/generated/` holds the derived registry, LaTeX macros, and
  provenance manifest. Never hand-copy numbers into the manuscript;
  use the macros in `paper/generated/results_macros.tex`.
- No raw catalog rows, no credentials, no local paths.

## Figure/table regeneration

```bash
python3 scripts/paper/generate_figures.py   # PDFs from versioned CSV tables
python3 scripts/paper/generate_tables.py    # .tex from versioned evidence JSON
```

## arXiv bundle

```bash
python3 scripts/paper/build_arxiv_bundle.py   # collect dependency graph
python3 scripts/paper/check_arxiv_bundle.py   # completeness + hygiene check
```

## Repository URL

Canonical project URL:
`https://github.com/jenholm/physics_models/tree/main/redshift-dependent-expansion`
