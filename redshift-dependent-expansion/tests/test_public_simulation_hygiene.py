"""Public-repository hygiene gate for the visualization.

Recursively rejects internal-development strings, absolute local paths,
stack traces, and credential-like tokens in every file the visualization
ships or builds from. This is a hard release gate: any failure means the
output is not safe to publish.

The forbidden patterns are assembled from fragments so this test file
itself never contains them literally.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Internal labels / paths that must never appear in public output.
FORBIDDEN = [
    "CG" + "HSTC",
    "M" + "24",
    "M" + "28",
    "R" + "4V",
    "R" + "5",
    "R" + "6",
    "BRI" + "DGE-",
    "/ho" + "me/jen" + "holm",
    "sna" + "ke-ey" + "es",
    "PROJ" + "ECT.md",
    "jen" + "holm",
]

# Generic public-content hazards.
HAZARDS = [
    "Tra" + "ceback",
    "api" + "_key",
    "se" + "cret",
    "pass" + "word",
    "file" + "://",
]

SCAN_ROOTS = ["simulation", "scripts", "tests"]
SCAN_SUFFIXES = {".py", ".js", ".html", ".css", ".md", ".json", ".txt"}


def iter_files():
    for root in SCAN_ROOTS:
        base = REPO / root
        if base.is_file():
            yield base
        elif base.is_dir():
            for path in sorted(base.rglob("*")):
                if path.is_file() and path.suffix in SCAN_SUFFIXES:
                    yield path


def test_no_forbidden_strings():
    failures = []
    for path in iter_files():
        text = path.read_text(errors="replace")
        low = text.lower()
        rel = str(path.relative_to(REPO))
        for frag in FORBIDDEN:
            if frag.lower() in low:
                idx = low.index(frag.lower())
                ctx = text[max(0, idx - 40):idx + len(frag) + 40]
                failures.append(f"{rel}: forbidden pattern near ...{ctx!r}...")
                break
    assert not failures, "\n".join(failures)


def test_no_generic_hazards():
    failures = []
    for path in iter_files():
        text = path.read_text(errors="replace")
        low = text.lower()
        rel = str(path.relative_to(REPO))
        for frag in HAZARDS:
            if frag.lower() in low:
                failures.append(f"{rel}: hazard pattern {frag!r}")
    assert not failures, "\n".join(failures)


def test_no_absolute_local_paths():
    import re

    pat = re.compile(r"(?i)(/home/|/Users/|C:\\\\|/root/|/tmp/opencode)")
    failures = []
    for path in iter_files():
        if path.suffix == ".py" and path.name == "test_public_simulation_hygiene.py":
            continue  # patterns here are fragment-built, not literal paths
        text = path.read_text(errors="replace")
        # Allow the p5 CDN URL (https://...) — only flag local-style paths.
        for m in pat.finditer(text):
            failures.append(f"{path.relative_to(REPO)}: {m.group(0)!r}")
    assert not failures, "\n".join(failures)


def test_comments_are_clean():
    """Source comments obey the same rule (covered file-wide above)."""
    for path in iter_files():
        text = path.read_text(errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith(("//", "#", "<!--", "*", "/*")):
                low = line.lower()
                for frag in FORBIDDEN:
                    assert frag.lower() not in low, f"{path.name}:{i}: {line!r}"
