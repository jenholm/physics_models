#!/usr/bin/env python3
"""Full public-paper driver: evidence -> registry -> figures -> tables.

Runs the neutral publication pipeline end to end:
  1. build_results_registry.py (evidence -> registry/macros/provenance)
  2. generate_tables.py
  3. generate_figures.py
  4. validate_claims.py (honors PAPER_MODE; use --release for gates)

Compiling LaTeX, building the simulation JSON, and bundling arXiv are
left to `make build` / `make bundle` so each stage stays inspectable.

Usage: python scripts/paper/build_expansion_history_paper.py [--release]
"""

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAPER_SCRIPTS = REPO / "scripts" / "paper"


def run(name, env=None):
    print(f"--- {name} ---")
    result = subprocess.run(
        [sys.executable, str(PAPER_SCRIPTS / name)],
        cwd=REPO, env=env or os.environ.copy(),
    )
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    release = "--release" in sys.argv
    run("build_results_registry.py")
    run("generate_tables.py")
    run("generate_figures.py")
    env = os.environ.copy()
    env["PAPER_MODE"] = "release" if release else env.get("PAPER_MODE", "draft")
    run("validate_claims.py", env=env)
    print("driver done (registry -> tables -> figures -> validate)")


if __name__ == "__main__":
    main()
