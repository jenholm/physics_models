"""Public link, URL, and LaTeX dependency tests (RDE-052).

Verifies:
  - the canonical repository URL appears in the root README and the
    paper availability statement, and no legacy project URL remains;
  - every relative markdown link resolves to a file;
  - every local LaTeX \\input/\\includegraphics target exists.

External web availability is never tested (not a release blocker).
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Fragment-built canonical URL (never literal in this file).
CANONICAL = (
    "http" + "s://git" + "hub.com/jen" + "holm/phy" + "sics_mo" + "dels/tr"
    "ee/main/redshift-dependent-expansion"
)
LEGACY_URL_BITS = ["cg" + "hstc", "h0" + "cdr", "M" + "28", "tree/main/cgh"]


def test_canonical_url_present():
    root_readme = (REPO / "README.md").read_text()
    assert CANONICAL in root_readme, "canonical URL missing from root README"
    availability = (REPO / "paper/appendices/E_reproducibility.tex").read_text()
    assert CANONICAL in availability, "canonical URL missing from availability statement"
    paper_readme = (REPO / "paper/README.md").read_text()
    assert CANONICAL in paper_readme, "canonical URL missing from paper README"


def test_no_legacy_urls():
    failures = []
    for path in list(REPO.rglob("*.md")) + list(REPO.rglob("*.tex")) + [
        REPO / "CITATION.cff", REPO / "PROJECT.md",
        REPO / "paper/metadata.yaml",
    ]:
        if ".git" in path.parts or not path.is_file():
            continue
        text = path.read_text(errors="replace")
        for bit in LEGACY_URL_BITS:
            if bit in text:
                failures.append(f"{path.relative_to(REPO)}: {bit!r}")
    assert not failures, "\n".join(failures)


def test_relative_markdown_links_resolve():
    failures = []
    for md in REPO.rglob("*.md"):
        if ".git" in md.parts:
            continue
        for m in re.finditer(r"\[[^\]]*\]\((?!https?://)([^)]+)\)", md.read_text(errors="replace")):
            target = m.group(1).split("#")[0]
            if not target:
                continue
            if not (md.parent / target).exists():
                failures.append(f"{md.relative_to(REPO)}: {target}")
    assert not failures, "\n".join(failures)


def test_latex_inputs_exist():
    failures = []
    paper = REPO / "paper"
    main = (paper / "main.tex").read_text()
    # LaTeX resolves \input relative to the working dir (paper/ here).
    queue = [paper / "main.tex"]
    seen = set()
    while queue:
        src = queue.pop()
        if src in seen:
            continue
        seen.add(src)
        text = src.read_text()
        for m in re.finditer(r"\\input\{([^}]+)\}", text):
            target = paper / (m.group(1) + ".tex")
            if not target.exists():
                failures.append(f"{src.relative_to(REPO)}: {m.group(1)}")
            else:
                queue.append(target)
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
            base = paper / m.group(1)
            if not (base.exists() or base.with_suffix(".pdf").exists()):
                failures.append(f"{src.relative_to(REPO)}: figure {m.group(1)}")
    assert main, "main.tex empty"
    assert not failures, "\n".join(failures)
