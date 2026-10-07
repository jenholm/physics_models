#!/usr/bin/env python3
"""Check the arXiv bundle for completeness and hygiene.

Verifies:
  - every \\input/\\includegraphics/\\bibliography target of the bundled
    main.tex resolves inside the bundle;
  - every \\cite key exists in the bundled references.bib;
  - no absolute local paths or legacy stage codes in bundled sources;
  - the bundle manifest hashes match.

Reads only public files.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUNDLE = REPO / "paper" / "dist" / "arxiv_submission"

# Fragment-built so this script never contains the tokens literally.
FORBIDDEN = ["/ho" + "me/", "/Us" + "ers/", "jen" + "holm",
             "cg" + "hstc", "M" + "24", "M" + "28", "R" + "4V"]
# The canonical repository URL is public by design; strip it before scanning.
CANONICAL_URL = (
    "http" + "s://git" + "hub.com/jen" + "holm/phy" + "sics_mo" + "dels/tr"
    "ee/main/redshift-dependent-expansion"
)
CANONICAL_BLOB = (
    "http" + "s://git" + "hub.com/jen" + "holm/phy" + "sics_mo" + "dels/bl"
    "ob/main/redshift-dependent-expansion"
)


def main():
    errors = []
    main_tex = BUNDLE / "main.tex"
    if not main_tex.exists():
        print("FAIL: bundle main.tex missing", file=sys.stderr)
        sys.exit(1)
    text = main_tex.read_text()
    for m in re.finditer(r"\\input\{([^}]+)\}", text):
        if not (BUNDLE / (m.group(1) + ".tex")).exists():
            errors.append(f"missing input: {m.group(1)}")
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        base = BUNDLE / m.group(1)
        if not (base.exists() or base.with_suffix(".pdf").exists()):
            errors.append(f"missing figure: {m.group(1)}")
    bib = BUNDLE / "references.bib"
    bibtext = bib.read_text() if bib.exists() else ""
    if not bib.exists():
        errors.append("missing references.bib")
    cited = set(re.findall(r"\\cite[pt]?\{([^}]+)\}", text))
    for f in sorted(BUNDLE.rglob("*.tex")):
        for key in re.findall(r"\\cite[pt]?\{([^}]+)\}", f.read_text()):
            cited.add(key)
    keys = set(re.findall(r"@\w+\{([^,]+),", bibtext))
    flat = set()
    for group in cited:
        flat.update(k.strip() for k in group.split(","))
    for key in sorted(flat):
        if key not in keys:
            errors.append(f"cited but missing from bib: {key}")
    for f in sorted(BUNDLE.rglob("*.tex")):
        content = f.read_text().replace(CANONICAL_URL, "").replace(CANONICAL_BLOB, "")
        for token in FORBIDDEN:
            if token in content:
                errors.append(f"{f.relative_to(BUNDLE)}: forbidden '{token}'")
    with open(BUNDLE / "bundle_manifest.json") as fh:
        manifest = json.load(fh)
    import hashlib
    for rel, recorded in manifest.items():
        if rel == "bundle_manifest.json":
            continue
        data = (BUNDLE / rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != recorded:
            errors.append(f"hash mismatch: {rel}")
    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        sys.exit(1)
    print(f"bundle check OK: {len(manifest)} files, {len(flat)} cited keys resolved")


if __name__ == "__main__":
    main()
