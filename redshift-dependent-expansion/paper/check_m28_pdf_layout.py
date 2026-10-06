"""M28 PDF layout acceptance check (layout/biblio, no science change).

Uses ``pdftotext -layout`` to verify document order and scans the
LaTeX log for float/undefined-reference/overfull-box warnings.

Checks:
  1. References section starts after the last figure/table caption
     and after the appendices.
  2. Log has no undefined references/citations, no missing files,
     no multiply-defined labels.
  3. Log has no float warnings (too many unprocessed, float too
     large, floats kept unprocessed).
  4. Log has no Overfull \\hbox above 2pt tolerance.

Usage:
  python paper/check_m28_pdf_layout.py [--pdf paper/main.pdf]
      [--log paper/main.log] [--tol 2.0]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

OVERFULL_RE = re.compile(r"Overfull \\hbox \(([\d.]+)pt too wide\)")
FLOAT_PATTERNS = [
    "Too many unprocessed floats",
    "Float too large for page",
    "has been moved",
    "remains unprocessed",
    "`h' float specifier changed",
]


def pdftotext_layout(pdf: Path) -> str:
    if shutil.which("pdftotext") is None:
        raise SystemExit("pdftotext not found (install poppler-utils)")
    proc = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise SystemExit(f"pdftotext failed: {proc.stderr[-1000:]}")
    return proc.stdout


def check_order(text: str) -> list[str]:
    errors: list[str] = []
    ref_match = re.search(r"(?m)^\x0c?(References|Bibliography)\s*$", text)
    if not ref_match:
        return ["References/Bibliography heading not found in PDF text"]
    ref_pos = ref_match.start()
    fig_caps = [m.start() for m in re.finditer(r"Figure \d+", text)]
    tab_caps = [m.start() for m in re.finditer(r"Table \d+", text)]
    last_float = max(fig_caps + tab_caps, default=-1)
    if last_float > ref_pos:
        errors.append("figure/table caption found after References start")
    app_match = re.search(
        r"(Appendix|Model-development history|Robustness and M28R1|"
        r"Reproducibility|Likelihood details|Early-window and ruler)",
        text,
    )
    if app_match and app_match.start() > ref_pos:
        errors.append("appendix content found after References start")
    if fig_caps or tab_caps:
        tail = text[ref_pos:ref_pos + 4000]
        if re.search(r"Figure \d+|Table \d+", tail):
            errors.append("float caption inside References tail")
    return errors


def check_log(log: str, tol: float) -> tuple[list[str], dict]:
    errors: list[str] = []
    stats = {"overfull": 0, "float_warnings": 0,
             "undefined": 0, "multi_defined": 0}
    if "There were undefined references" in log:
        errors.append("undefined references remain")
        stats["undefined"] += 1
    if "There were undefined citations" in log:
        errors.append("undefined citations remain")
        stats["undefined"] += 1
    if re.search(r"LaTeX Warning: Citation .* undefined", log):
        errors.append("undefined citation warning")
        stats["undefined"] += 1
    if re.search(r"LaTeX Warning: Reference .* undefined", log):
        errors.append("undefined reference warning")
        stats["undefined"] += 1
    if re.search(r"multiply defined", log, re.IGNORECASE):
        errors.append("multiply-defined label")
        stats["multi_defined"] += 1
    if re.search(r"! LaTeX Error: File `.+' not found", log):
        errors.append("missing figure/file")
    for pat in FLOAT_PATTERNS:
        n = log.count(pat)
        if n:
            stats["float_warnings"] += n
            errors.append(f"float warning: {pat!r} x{n}")
    bad = [float(m.group(1)) for m in OVERFULL_RE.finditer(log)
           if float(m.group(1)) > tol]
    stats["overfull"] = len(bad)
    if bad:
        errors.append(f"overfull hbox above {tol}pt: {len(bad)} "
                      f"(max {max(bad):.2f}pt)")
    return errors, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="paper/main.pdf")
    ap.add_argument("--log", default="paper/main.log")
    ap.add_argument("--tol", type=float, default=2.0)
    args = ap.parse_args()
    pdf, log_path = Path(args.pdf), Path(args.log)
    errors: list[str] = []
    if not pdf.is_file():
        return (print(f"MISSING PDF: {pdf}"), 1)[1]
    text = pdftotext_layout(pdf)
    errors += check_order(text)
    if not log_path.is_file():
        errors.append(f"missing log: {log_path}")
        stats: dict = {}
    else:
        log_errors, stats = check_log(
            log_path.read_text(errors="replace"), args.tol)
        errors += log_errors
    pages = len(re.findall(r"\f", text)) + 1
    print(f"pages(text-ff): {pages}")
    print(f"stats: {stats if log_path.is_file() else {}}")
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: references last, no float/undefined/overfull issues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
