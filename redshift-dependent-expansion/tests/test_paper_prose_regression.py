"""Direct-prose regression tests (R2-039) and evidence-link tests (R2-040).

R2-039: the deleted defensive/project phrases must not return to the
reader-facing manuscript source (sections, appendices, main.tex,
nomenclature/comparison tables, generated claim table).

R2-040: the neutral endpoint evidence files exist, and every
github.com blob URL in the manuscript maps to an existing local path
beneath redshift-dependent-expansion/.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "paper"

# Fragment-built so this file never contains the banned phrases literally.
BANNED = [
    "Indepen" + "dent study",
    "not pres" + "ented as a complete cosmological model",
    "not a vi" + "able cosmology",
    "order selection alone is not ev" + "idence",
    "not ev" + "idence of a discovery",
    "dyna" + "mical origin",
    "reso" + "lve the Hubble tension",
    "phys" + "ical origin remains",
    "funda" + "mental expansion law",
    "funda" + "mental physical scale",
    "Nei" + "ther branch fits everything",
    "no ten" + "sion resolution",
    "We cl" + "aim no resolution",
    "We cl" + "aim no modified gravity",
    "We cl" + "aim no proof",
    "ruler resca" + "ling alone solves",
    "What is not estab" + "lished",
    "time" + "-current",
    "Model " + "A",
    "BRID" + "GE-",
    "GE" + "OM-",
    "sec:not-estab" + "lished",
]

PROSE_ROOTS = ["sections", "appendices"]


def prose_files():
    for root in PROSE_ROOTS:
        for path in sorted((PAPER / root).glob("*.tex")):
            yield path
    yield PAPER / "main.tex"
    yield PAPER / "tables" / "nomenclature.tex"
    yield PAPER / "tables" / "endpoint_construction_comparison.tex"
    yield PAPER / "tables" / "generated" / "claim_evidence.tex"


def test_no_banned_phrases():
    failures = []
    for path in prose_files():
        text = path.read_text()
        for frag in BANNED:
            if frag in text:
                failures.append(f"{path.relative_to(REPO)}: {frag!r}")
                break
    assert not failures, "\n".join(failures)


def test_no_bare_double_dash_constructions():
    text = ""
    for path in prose_files():
        text += path.read_text() + "\n"
    for bad in ("C1--C2", "R--CMB", "CMB--CMB", "1--8"):
        assert bad not in text, f"awkward construction remains: {bad}"


def test_endpoint_evidence_files_exist():
    for rel in (
        "paper/evidence/endpoints/endpoint_redshift.json",
        "paper/evidence/endpoints/endpoint_cmb_1.json",
        "paper/evidence/endpoints/endpoint_cmb_2.json",
        "paper/evidence/endpoints/domain_split.json",
        "paper/evidence/reference_sensitivity/scale_comparison.json",
        "paper/evidence/reference_sensitivity/agreement_metrics.json",
        "paper/evidence/model_selection/constrained_cv.json",
        "paper/evidence/model_selection/bootstrap.json",
    ):
        assert (REPO / rel).exists(), f"missing: {rel}"


def test_github_urls_map_to_local_files():
    failures = []
    seen = set()
    for path in prose_files():
        for m in re.finditer(r"github\.com/\S+", path.read_text()):
            url = m.group(0).rstrip("}.,;)")
            if url in seen:
                continue
            seen.add(url)
            if url.endswith("tree/main/redshift-dependent-expansion"):
                continue  # repository root maps to REPO itself
            assert "blob/main/redshift-dependent-expansion/" in url, url
            local = url.split("blob/main/redshift-dependent-expansion/", 1)[1]
            if not (REPO / local).exists():
                failures.append(f"{path.name}: {url} -> missing {local}")
    assert seen, "no GitHub URLs found in manuscript"
    assert not failures, "\n".join(failures)
