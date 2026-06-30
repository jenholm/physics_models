# Inflationary Sector Renormalization

A toy computational framework for testing configuration-space locality-weighted measures in stochastic inflationary sector ensembles.

## Scientific status

ISR is currently a proof-of-principle toy framework. Its results demonstrate numerical behavior in a simplified stochastic landscape and should not be interpreted as a physical solution to the eternal-inflation measure problem.

## What this is

- A toy model.
- A reproducible simulation.
- A finite trajectory-sampling cutoff study.

## What this is not

- Not a solution to the eternal-inflation measure problem.
- Not a physical proof of other universes.
- Not a replacement for spacetime-volume measures.

## Quick start

```bash
git clone https://github.com/jenholm/physics_models.git
cd physics_models/inflationary-sector-renormalization
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m compileall isr experiments
python experiments/run_all.py
```

## Paper

`paper/inflationary-sector-renormalization.pdf`

## Repository layout

```
configs/   — YAML configurations
isr/       — core package
experiments/ — experimental scripts
outputs/   — figures and tables
paper/     — LaTeX source and PDF
docs/      — theoretical notes
```
