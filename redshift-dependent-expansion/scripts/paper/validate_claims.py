#!/usr/bin/env python3
"""Validate publication claims against versioned evidence.

Checks:
  - every evidence path in paper/claims.yaml exists;
  - every claim status is a known value;
  - registry macros match the checked-in results_macros.tex;
  - evidence hashes match paper/generated/provenance.json;
  - in release mode (PAPER_MODE=release), the Abstract/Results/Conclusion
    never present a not_established claim as established fact
    (no discovery, significance, or resolution language).

Exit nonzero on any failure. Reads only public files.
"""

import json
import os
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
KNOWN_STATUSES = {
    "exploratory", "supported", "not_supported", "conditional",
    "not_established", "descriptive_robustness", "supported_negative",
}

# Language that would overstate a not_established claim.
OVERSTATEMENTS = [
    r"resolves the Hubble tension",
    r"resolution of the Hubble tension",
    r"detection significance",
    r"\bsigma\b.{0,20}discovery",
    r"discovery of",
    r"establishes the .* origin",
    r"viable .* completion is (claimed|demonstrated)",
]


def main():
    with open(REPO / "paper/claims.yaml") as fh:
        claims = yaml.safe_load(fh)["claims"]
    errors = []
    for claim in claims:
        if claim["status"] not in KNOWN_STATUSES:
            errors.append(f"unknown status {claim['status']} in {claim['id']}")
        for ev in claim.get("evidence", []):
            if not (REPO / ev).exists():
                errors.append(f"{claim['id']}: missing evidence {ev}")

    with open(REPO / "paper/generated/results_registry.json") as fh:
        registry = json.load(fh)["macros"]
    macro_tex = (REPO / "paper/generated/results_macros.tex").read_text()
    for name, entry in registry.items():
        needle = f"\\newcommand{{\\{name}}}{{{entry['latex']}}}"
        if needle not in macro_tex:
            errors.append(f"macro {name} not in results_macros.tex")

    with open(REPO / "paper/generated/provenance.json") as fh:
        provenance = json.load(fh)["evidence_files"]
    import hashlib
    for rel, recorded in provenance.items():
        data = (REPO / rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != recorded:
            errors.append(f"hash mismatch: {rel}")

    # bibliography audit: every cite key exists, no uncited entries,
    # no duplicate DOI or arXiv identifier.
    tex_all = (REPO / "paper/main.tex").read_text()
    for sub in ("sections", "appendices"):
        for f in (REPO / "paper" / sub).glob("*.tex"):
            tex_all += f.read_text()
    for f in ("tables/endpoint_construction_comparison.tex", "tables/nomenclature.tex"):
        tex_all += (REPO / "paper" / f).read_text()
    cited = set()
    for m in re.finditer(r"\\cite[pt]?\{([^}]+)\}", tex_all):
        cited.update(k.strip() for k in m.group(1).split(","))
    bibtext = (REPO / "paper/references.bib").read_text()
    entries = re.findall(r"@\w+\{([^,]+),", bibtext)
    for key in sorted(cited):
        if key not in entries:
            errors.append(f"cited but missing from references.bib: {key}")
    for key in sorted(set(entries) - cited):
        errors.append(f"uncited bibliography entry (delete it): {key}")
    dois = re.findall(r"doi\s*=\s*\{([^}]+)\}", bibtext)
    for doi in set(dois):
        if dois.count(doi) > 1:
            errors.append(f"duplicate DOI: {doi}")
    eprints = re.findall(r"eprint\s*=\s*\{([^}]+)\}", bibtext)
    for ep in set(eprints):
        if eprints.count(ep) > 1:
            errors.append(f"duplicate arXiv identifier: {ep}")

    if os.environ.get("PAPER_MODE", "draft") == "release":
        prose = ""
        for sec in ("00_abstract", "06_results", "09_conclusion"):
            matches = list((REPO / "paper/sections").glob(f"*{sec[-2:]}*"))
            _ = matches
        for name in ("00_abstract.tex", "06_results.tex", "09_conclusion.tex"):
            prose += (REPO / "paper/sections" / name).read_text() + "\n"
        for pattern in OVERSTATEMENTS:
            if re.search(pattern, prose, re.IGNORECASE):
                errors.append(f"release gate: overstatement '{pattern}' in Abstract/Results/Conclusion")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        sys.exit(1)
    print(f"validate_claims: {len(claims)} claims OK ({os.environ.get('PAPER_MODE', 'draft')} mode)")


if __name__ == "__main__":
    main()
