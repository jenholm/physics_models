"""Evidence/figure/table dependency check (RDE-005).

Every retained PDF, table, and evidence file must be reachable from at
least one of:
  - the paper/main.tex dependency tree (\\input/\\includegraphics),
  - paper/claims.yaml evidence lists,
  - the simulation data builder,
  - the current paper build/validation scripts, or
  - paper/generated/provenance.json (the publication evidence record
    written by scripts/paper/build_results_registry.py).

Sidecar .csv/.meta.json files count as reachable with their figure.
"""

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "paper"


def tex_tree_files():
    found = set()
    queue = [PAPER / "main.tex"]
    seen = set()
    while queue:
        src = queue.pop()
        if src in seen or not src.exists():
            continue
        seen.add(src)
        text = src.read_text()
        for m in re.finditer(r"\\input\{([^}]+)\}", text):
            target = PAPER / (m.group(1) + ".tex")
            found.add(target)
            queue.append(target)
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
            base = PAPER / m.group(1)
            found.add(base if base.suffix else base.with_suffix(".pdf"))
    return found


def test_every_artifact_is_reachable():
    reachable = {p.resolve() for p in tex_tree_files()}
    with open(PAPER / "claims.yaml") as fh:
        for claim in yaml.safe_load(fh)["claims"]:
            for ev in claim.get("evidence", []):
                reachable.add((REPO / ev).resolve())
    for script in list((REPO / "scripts").rglob("*.py")):
        for m in re.finditer(r"paper/(?:evidence|figures|tables)/[A-Za-z0-9_./-]+\.\w+", script.read_text()):
            reachable.add((REPO / m.group(0)).resolve())
    with open(PAPER / "generated/provenance.json") as fh:
        for rel in json.load(fh)["evidence_files"]:
            reachable.add((REPO / rel).resolve())
    with open(PAPER / "generated/results_registry.json") as fh:
        for entry in json.load(fh)["macros"].values():
            reachable.add((REPO / entry["source"]).resolve())

    # sidecars travel with their figure
    def anchored(path):
        if path.suffix in (".csv",) or path.name.endswith(".meta.json"):
            stem = path.name.split(".")[0]
            return any(
                (path.parent / (stem + ".pdf")).resolve() in reachable
                for stem in [stem]
            )
        return False

    candidates = (
        list((PAPER / "figures").rglob("*"))
        + list((PAPER / "tables").rglob("*"))
        + list((PAPER / "evidence").rglob("*"))
    )
    failures = []
    for path in sorted(candidates):
        if not path.is_file():
            continue
        if path.resolve() in reachable or anchored(path):
            continue
        failures.append(str(path.relative_to(REPO)))
    assert not failures, "unreachable artifacts:\n" + "\n".join(failures)
