"""Referee R3 minor-revision regression tests (R3-029).

Locks the review closeout: stale items stay fixed, valid fixes stay
applied, and declined numerical suggestions (0.14, -6.91, 67.49) can
never overwrite the exact evidence values. PDF-based tests skip when
paper/main.pdf is not built.
"""

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "paper"
PDF = PAPER / "main.pdf"


def registry():
    with open(PAPER / "generated" / "results_registry.json") as fh:
        return json.load(fh)["macros"]


def pdf_text():
    if not PDF.exists() or shutil.which("pdftotext") is None:
        pytest.skip("paper/main.pdf or pdftotext unavailable")
    out = Path("/tmp") / "r3_pdf_text.txt"
    subprocess.run(["pdftotext", str(PDF), str(out)], check=True)
    return out.read_text(errors="replace")


def test_c1_h0_is_67p99_everywhere():
    assert registry()["CmbOneHZero"]["latex"] == "67.99"
    assert "\\newcommand{\\CmbOneHZero}{67.99}" in (
        PAPER / "generated" / "results_macros.tex"
    ).read_text()
    assert "67.99" in pdf_text()


def test_no_67p49_in_source_or_pdf():
    for path in list((PAPER / "sections").glob("*.tex")) + list(
        (PAPER / "appendices").glob("*.tex")
    ) + [PAPER / "main.tex", PAPER / "references.bib"]:
        assert "67.49" not in path.read_text(), path
    assert "67.49" not in pdf_text()


def test_main_sn_equations_have_unique_labels():
    text = (PAPER / "sections" / "03_data_likelihoods.tex").read_text()
    for label in ("eq:r0", "eq:mhat", "eq:chijoint"):
        assert text.count("\\label{%s}" % label) == 1, label
    assert "Eq.~\\eqref{eq:mhat}" in text


def test_appendix_does_not_repeat_profile_equation():
    text = (PAPER / "appendices" / "B_likelihood_details.tex").read_text()
    assert "\\frac{\\mathbf{1}^{T}C^{-1}r_{0}}" not in text
    assert "eq:r0" in text and "eq:chijoint" in text


def test_delta1_delta2_deltaC_equations_exact():
    text = (PAPER / "sections" / "05_reference_sensitivity.tex").read_text()
    assert "\\Delta_{1}(z)=\\ln H_{R}(z)-\\ln H_{C1}(z)," in text
    assert "\\Delta_{2}(z)=\\ln H_{R}(z)-\\ln H_{C2}(z)," in text
    assert "\\Delta_{C}(z)=\\ln H_{C1}(z)-\\ln H_{C2}(z)," in text
    rendered = pdf_text()
    for token in ("1 (z) = ln H", "2 (z) = ln H", "C (z) = ln H"):
        assert token in rendered, token


def test_ln_defined_as_natural_log():
    assert "natural logarithm" in (
        PAPER / "sections" / "05_methods.tex"
    ).read_text()


def test_section_range_is_4_to_6():
    text = (PAPER / "sections" / "03_data_likelihoods.tex").read_text()
    assert "Sections~\\ref{sec:model-selection}--\\ref{sec:results}" in text
    assert "ref{sec:results}--\\ref{sec:reference-sensitivity}" not in text
    rendered = pdf_text()
    assert ("Sections 4\u20136" in rendered) or ("Sections 4-6" in rendered)


def test_no_c1_c2_difference_difference_phrase():
    bad = "difference between C1 and C2 difference"
    for path in list((PAPER / "sections").glob("*.tex")):
        assert bad not in path.read_text(), path
    assert bad not in pdf_text()


def test_m3_gap_rounds_to_0p13():
    with open(REPO / "paper/evidence/model_selection/constrained_cv.json") as fh:
        cv = json.load(fh)
    gap = cv["per_order"]["3"]["combined_constrained"] - cv["best_combined"]
    assert round(gap, 2) == 0.13
    assert registry()["CvConstrMThreeDeltaVsBest"]["latex"] == "0.13"


def test_constrained_desi_delta_rounds_to_minus_6p90():
    with open(REPO / "paper/evidence/reconstruction/null_cv_summary.json") as fh:
        nullcv = json.load(fh)
    bare = sum(
        float(r["held_bare"])
        for r in nullcv["desi_folds"]
        if float(r["block"]) <= 1.8
    )
    m3 = sum(
        float(r["held_m3"])
        for r in nullcv["desi_folds"]
        if float(r["block"]) <= 1.8
    )
    assert round(m3 - bare, 2) == -6.90
    assert registry()["BridgeNullDesiConstr"]["latex"] == "-6.90"


def test_bootstrap_mcse_equals_about_0p026():
    with open(REPO / "paper/evidence/model_selection/bootstrap.json") as fh:
        boot = json.load(fh)
    p, n = boot["frac_select_ge_m3"], boot["nrep"]
    assert round(math.sqrt(p * (1.0 - p) / n), 3) == 0.026
    assert registry()["CvConstrBootMcse"]["latex"] == "0.026"


def test_ruler_clock_wording_is_consistent_with_zero():
    good = "ruler-clock split is consistent with zero"
    bad = "Zero ruler-clock split is allowed"
    abstract = (PAPER / "sections" / "00_abstract.tex").read_text()
    results = (PAPER / "sections" / "06_results.tex").read_text()
    assert good in abstract and good in results
    for path in list((PAPER / "sections").glob("*.tex")):
        assert bad not in path.read_text(), path


def test_row_mask_says_or():
    text = (PAPER / "sections" / "03_data_likelihoods.tex").read_text()
    assert "or the row is a calibrator" in text
    for number in ("1701", "1657", "77", "1580"):
        assert number in text, number


def test_abstract_word_count_under_270():
    words = (PAPER / "sections" / "00_abstract.tex").read_text().split()
    assert len(words) <= 270, len(words)
