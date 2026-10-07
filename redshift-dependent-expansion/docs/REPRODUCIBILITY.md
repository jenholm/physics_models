# Reproducibility

All commands run from the repository root and use only files inside
this public repository.

## Python requirements

Python 3 with NumPy, SciPy, Matplotlib, and PyYAML.

## LaTeX requirements

pdflatex + bibtex (TeX Live 2023 or newer). No latexmk required.

## Paper build

```bash
python3 scripts/paper/build_results_registry.py   # evidence -> registry/macros/provenance
python3 scripts/paper/generate_tables.py          # evidence -> tables
python3 scripts/paper/generate_figures.py        # CSV tables -> figure PDFs
PAPER_MODE=release python3 scripts/paper/validate_claims.py
cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

or via make:

```bash
make -C paper build
```

## Figure regeneration

```bash
python3 scripts/paper/generate_figures.py
```

Figures render from the versioned CSV tables in
`paper/figures/generated/`; sidecar meta.json files record CSV hashes.

## Simulation data regeneration

```bash
python3 scripts/build_simulation_data.py          # evidence + figure tables -> simulation JSON
python3 scripts/build_standalone_simulation.py    # standalone HTML bundle
```

## Simulation standalone build

```bash
cd simulation && python3 -m http.server 8000
# open http://localhost:8000/
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/ -q -p no:cacheprovider
```

## arXiv bundle check

```bash
python3 scripts/paper/build_arxiv_bundle.py
python3 scripts/paper/check_arxiv_bundle.py
```
