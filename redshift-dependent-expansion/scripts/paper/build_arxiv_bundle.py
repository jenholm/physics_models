#!/usr/bin/env python3
"""Build a self-contained arXiv bundle from the paper dependency graph.

Parses paper/main.tex for \\input/\\includegraphics/\\bibliography targets,
copies exactly those files plus main.tex and references.bib into
paper/dist/arxiv_submission/, and writes a manifest with SHA256 hashes.
Reads only public files; never reaches outside the repository.
"""

import hashlib
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "paper"
BUNDLE = PAPER / "dist" / "arxiv_submission"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_deps():
    deps = set()
    sources = [PAPER / "main.tex"]
    seen = set()
    while sources:
        src = sources.pop()
        if src in seen:
            continue
        seen.add(src)
        text = src.read_text()
        for m in re.finditer(r"\\input\{([^}]+)\}", text):
            target = PAPER / (m.group(1) + ".tex")
            if not target.exists():
                target = src.parent / (m.group(1) + ".tex")
            target = target.resolve()
            deps.add(target)
            sources.append(target)
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
            base = PAPER / m.group(1)
            for cand in (base, base.with_suffix(".pdf")):
                if cand.exists():
                    deps.add(cand.resolve())
        m = re.search(r"\\bibliography\{([^}]+)\}", text)
        if m:
            deps.add((PAPER / (m.group(1) + ".bib")).resolve())
    return deps


def main():
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    deps = collect_deps()
    deps.add((PAPER / "main.tex").resolve())
    manifest = {}
    for dep in sorted(deps):
        rel = dep.relative_to(PAPER)
        dest = BUNDLE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dep, dest)
        manifest[str(rel)] = sha256_of(dest)
    # pre-generated bibliography for arXiv
    bbl = PAPER / "main.bbl"
    if bbl.exists():
        dest = BUNDLE / "main.bbl"
        shutil.copy2(bbl, dest)
        manifest["main.bbl"] = sha256_of(dest)
    with open(BUNDLE / "bundle_manifest.json", "w") as fh:
        __import__("json").dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"bundle: {len(manifest)} files -> {BUNDLE.relative_to(REPO)}")


if __name__ == "__main__":
    main()
