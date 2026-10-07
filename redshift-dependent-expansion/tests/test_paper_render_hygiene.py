"""Paper-render hygiene gate (RDE-051).

Extracts paper/main.pdf with pdftotext and asserts:
  - zero ASCII control characters (other than newline/tab/form-feed);
  - zero legacy stage-code tokens in the rendered text;
  - the key extraction probes from the font fix are found normally.

Requires pdftotext and a compiled paper/main.pdf.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PDF = REPO / "paper" / "main.pdf"

# Fragment-built so this file never contains the tokens literally.
LEGACY = [
    "M" + "24",
    "M" + "28",
    "CG" + "HSTC",
    "R" + "4V",
    "time" + "-current",
    "BRI" + "DGE-",
    "GE" + "OM-",
    "dispo" + "sition",
    "claim con" + "tract",
    "catas" + "trophe",
]

# Word-boundary stage codes.
LEGACY_WORD = ["B" + "2", "R" + "5", "R" + "6"]

PROBES = ["Differ" + "ence", "best" + "-fit", "C" + "1", "C" + "2", "1" + "%"]


def extracted_text():
    if not PDF.exists():
        pytest.skip("paper/main.pdf not built")
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext not available")
    out = Path("/tmp") / "paper_hygiene_extract.txt"
    subprocess.run(["pdftotext", str(PDF), str(out)], check=True)
    return out.read_text(errors="replace")


def test_pdf_has_no_control_characters():
    text = extracted_text()
    bad = sorted({repr(c) for c in text if ord(c) < 32 and c not in "\n\t\x0c"})
    assert not bad, f"control characters in PDF text: {bad}"


def test_pdf_has_no_legacy_tokens():
    text = extracted_text()
    failures = [frag for frag in LEGACY if frag in text]
    import re
    for frag in LEGACY_WORD:
        if re.search(r"(?<![A-Za-z0-9])" + frag + r"(?![A-Za-z0-9])", text):
            failures.append(frag)
    assert not failures, f"legacy tokens in PDF text: {failures}"


def test_pdf_extraction_probes():
    text = extracted_text()
    for probe in PROBES:
        assert probe in text, f"probe {probe!r} missing from PDF text"
