"""Repo-wide public-repository hygiene gate (RDE-050 + RDE-002).

Scans every public text file (except .git, caches, archives, PDFs and
other binary-large files) and rejects:
  - absolute local paths and the development username;
  - legacy stage codes in prose/source (machine-readable evidence JSON
    may preserve historical keys per the evidence policy);
  - credential-like tokens;
  - stray build artifacts (*.pyc, __pycache__, logs/aux files outside
    the gitignored paper build outputs).

Forbidden patterns are assembled from fragments so this test file
itself never contains them literally. This is a hard release gate.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Strict everywhere (including versioned evidence).
STRICT = [
    "/ho" + "me/",
    "/Us" + "ers/",
    "C:" + "\\Us" + "ers\\",
    "/ro" + "ot/",
    "jen" + "holm",
    "work" + "space/",
    "cg" + "hstc",
    "CG" + "HSTC",
    "M" + "24",
    "M" + "28",
    "R" + "4V",
    "PRIV" + "ATE KEY",
    "api" + "_key",
    "sec" + "ret=",
    "tok" + "en=",
]

# Stage codes: rejected in prose/source, but versioned evidence JSON
# preserves historical machine-readable keys (evidence policy).
STAGE_LITERAL = [
    "BRI" + "DGE-",
    "GE" + "OM-",
    "M" + "24",
    "M" + "28",
]
STAGE_WORD = [
    "B" + "2-",
    "R" + "5",
    "R" + "6",
]

# The canonical repository URL is public by design; strip it before
# checking the username token.
CANONICAL_URL = (
    "http" + "s://git" + "hub.com/jen" + "holm/phy" + "sics_mo" + "dels/tr"
    "ee/main/redshift-dependent-expansion"
)
CANONICAL_BLOB = (
    "http" + "s://git" + "hub.com/jen" + "holm/phy" + "sics_mo" + "dels/bl"
    "ob/main/redshift-dependent-expansion"
)

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
SKIP_SUFFIXES = {".pdf", ".npz", ".png", ".pyc", ".tar", ".gz"}
# Gitignored local outputs of the current paper compile (never committed).
BUILD_OUTPUTS = {
    "paper/main.aux", "paper/main.bbl", "paper/main.blg", "paper/main.log",
    "paper/main.out", "paper/main.fls", "paper/main.fdb_latexmk",
    "paper/main.synctex.gz",
}
TEXT_SUFFIXES = {
    ".py", ".js", ".html", ".css", ".md", ".json", ".txt", ".tex", ".bib",
    ".yaml", ".yml", ".csv", ".cff", ".mk", "",
}


def iter_files():
    for path in sorted(REPO.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if str(rel) in BUILD_OUTPUTS:
            continue
        if path.suffix in SKIP_SUFFIXES or path.name.endswith(".tar.gz"):
            continue
        if path.suffix not in TEXT_SUFFIXES and path.suffix != "":
            continue
        if path.stat().st_size > 2_000_000:
            continue
        yield path


def clean_text(text):
    return text.replace(CANONICAL_URL, "").replace(CANONICAL_BLOB, "")


def test_no_strict_tokens():
    failures = []
    for path in iter_files():
        text = clean_text(path.read_text(errors="replace"))
        low = text.lower()
        for frag in STRICT:
            if frag.lower() in low:
                idx = low.index(frag.lower())
                ctx = text[max(0, idx - 40):idx + len(frag) + 40]
                failures.append(f"{path.relative_to(REPO)}: {ctx!r}")
                break
    assert not failures, "\n".join(failures)


def test_no_stage_codes_outside_evidence():
    word_pats = [
        re.compile(r"(?<![A-Za-z0-9])" + frag + r"(?![A-Za-z0-9])")
        for frag in STAGE_WORD
    ]
    failures = []
    for path in iter_files():
        rel = str(path.relative_to(REPO))
        if rel.startswith("paper/evidence/"):
            continue
        if path.name in ("test_public_repository_hygiene.py",):
            continue  # fragment-built patterns only, never literals
        text = clean_text(path.read_text(errors="replace"))
        hit = None
        for frag in STAGE_LITERAL:
            if frag in text:
                hit = frag
                break
        if hit is None:
            for pat, frag in zip(word_pats, STAGE_WORD):
                if pat.search(text):
                    hit = frag
                    break
        if hit is not None:
            failures.append(f"{rel}: stage code {hit!r}")
    assert not failures, "\n".join(failures)


def test_no_evidence_json_path_leaks():
    """RDE-002: no JSON value under paper/evidence/ carries a local path."""
    needles = [
        "/ho" + "me/", "/Us" + "ers/", "C:" + "\\Us" + "ers\\",
        "jen" + "holm", "work" + "space/", "cg" + "hstc",
    ]
    failures = []

    def walk(value, where):
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, f"{where}.{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f"{where}[{i}]")
        elif isinstance(value, str):
            low = value.lower()
            for frag in needles:
                if frag.lower() in low:
                    failures.append(f"{where}: {value!r}")

    for path in sorted((REPO / "paper" / "evidence").rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            failures.append(f"{path.relative_to(REPO)}: invalid JSON ({exc})")
            continue
        walk(doc, str(path.relative_to(REPO)))
    assert not failures, "\n".join(failures)


def test_no_stray_build_artifacts():
    failures = []
    for path in sorted(REPO.rglob("*")):
        if ".git" in path.parts:
            continue
        rel = str(path.relative_to(REPO))
        if rel in BUILD_OUTPUTS:
            continue
        if path.suffix == ".pyc":
            failures.append(rel)
        elif path.name == "__pycache__" and path.is_dir():
            failures.append(rel + "/")
        elif path.suffix in (".log", ".aux", ".blg", ".out") and path.is_file():
            failures.append(rel)
    assert not failures, "\n".join(failures)
