#!/usr/bin/env python3
"""Regenerate publication tables from versioned evidence.

Reads ONLY public files under paper/evidence/ and writes:
  paper/tables/generated/constrained_cv_rescore.tex
  paper/tables/generated/claim_evidence.tex
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TAB = REPO / "paper" / "tables" / "generated"


def main():
    with open(REPO / "paper/evidence/model_selection/constrained_cv.json") as fh:
        rescore = json.load(fh)
    per = rescore["per_order"]
    lines = [
        "\\begin{tabular}{rrrrr}",
        "\\toprule",
        "$m$ & SN held-out & DESI $z\\le1.8$ held-out & combined (selection) & DESI Ly$\\alpha$ (continuation) \\\\",
        "\\midrule",
    ]
    for m in ("2", "3", "4", "5", "6"):
        v = per[m]
        star = " $\\star$" if m == "3" else ""
        lines.append(
            f"{m}{star} & {v['sn_held']:.1f} & {v['desi_constrained_held']:.3f} "
            f"& {v['combined_constrained']:.3f} & {v['desi_lya_held']:.1f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}"]
    TAB.mkdir(parents=True, exist_ok=True)
    with open(TAB / "constrained_cv_rescore.tex", "w") as fh:
        fh.write("\n".join(lines) + "\n")

    rows = [
        ("Endpoint separation (R vs C1/C2, $z\\le1.8$)",
         "fixed difference fields, scale comparison", "supported"),
        ("C1/C2 reference sensitivity",
         "changing references moves the difference only slightly", "descriptive"),
        ("Shared common-mode description",
         "common-mode fraction $\\ge0.998$ per interval, no $p$-value", "descriptive"),
        ("Compact order-3 representation",
         "constrained CV selects $m{=}3$; Jacobian rank 5/5 fitted coordinates", "supported"),
        ("Order-selection significance",
         "matched null bootstrap $P{=}0.216$; complexity only", "not established"),
        ("Ly$\\alpha$ continuation",
         "order-3 reconstruction fails its $z{=}2.33$ continuation test; domain ends at $1.8$",
         "not established"),
        ("Physical dynamics of the difference", "no dynamical completion", "not established"),
        ("Nonreciprocal calibration",
         "$\\Delta\\chi^{2}(\\epsilon{=}0)=0.124$", "no evidence"),
    ]
    lines = [
        "{\\small",
        "\\begin{tabular}{p{0.30\\linewidth}p{0.44\\linewidth}l}",
        "\\toprule",
        "Claim & Evidence & Status \\\\",
        "\\midrule",
    ]
    for claim, ev, status in rows:
        lines.append(f"{claim} & {ev} & {status} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}}"]
    with open(TAB / "claim_evidence.tex", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote constrained_cv_rescore.tex, claim_evidence.tex")


if __name__ == "__main__":
    main()
