#!/usr/bin/env python3
"""Build M28 validation summary tables/figs from runs/m28_validation/."""
from __future__ import annotations

import json
import pathlib
import shutil

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "runs" / "m28_validation"
EV = PROJECT_ROOT / "paper" / "evidence" / "m28_validation"
TAB = PROJECT_ROOT / "paper" / "tables" / "generated"


def _load(name: str, default=None):
    p = SRC / name
    return json.loads(p.read_text()) if p.is_file() else default


def main() -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    SRC.mkdir(parents=True, exist_ok=True)
    EV.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    hand = _load("VALIDATION_HANDOFF.json", {})
    decomp = _load("joint_decomposition.json", {})
    desi = _load("desi_covariance_audit.json", {})
    cmb = _load("cmb_compact_export.json", {})
    cal = _load("calibrator_audit.json", {})
    du = _load("duality_check.json", {})
    emb = _load("embedding_check.json", {})

    rows = [
        ("decomposition", str(decomp.get("chi2_joint", "")),
         "joint=cond+condl both orderings"),
        ("desi_chi2", str(round(float(desi.get("chi2_desi", 0)), 4)), "sum w^2"),
        ("cmb_chi2", str(round(float(cmb.get("chi2_cmb", 0)), 6)), "compact 3-pt"),
        ("calibrator", str(cal.get("disposition", "")), "numeric audit"),
        ("duality_maxerr", str(du.get("max_err", "")), "D_A/D_L identities"),
        ("embedding_fd_p99", str(emb.get("fd_p99", "")), "lnA parity"),
    ]
    # Recurse into nested validation dirs (preflight/profiles/epoch/width/
    # gate/marker/convergence): count files + surface disposition/status keys.
    for sub in ("preflight", "profiles", "epoch", "width", "gate", "marker",
                "convergence"):
        d = SRC / sub
        if not d.is_dir():
            rows.append((f"{sub}_dir", "absent", "nested dir not run"))
            continue
        files = sorted(d.rglob("*.json"))
        rows.append((f"{sub}_dir", str(len(files)), "nested json count"))
        for f in files[:8]:
            try:
                doc = json.loads(f.read_text())
            except ValueError:
                continue
            rel = str(f.relative_to(SRC))
            if isinstance(doc, dict):
                for key in ("status", "disposition", "passes",
                            "c0_continuous", "c1_continuous"):
                    if key in doc:
                        rows.append((rel, str(doc[key]), f"nested {key}"))
                        break
    tex = ("\\begin{tabular}{lll}\n\\hline\narea & value & note \\\\\n\\hline\n"
           + "\n".join(f"{a} & {v} & {n} \\\\" for a, v, n in rows)
           + "\n\\hline\n\\end{tabular}\n")
    (TAB / "m28_validation_summary.tex").write_text(tex)
    (TAB / "m28_validation_summary.csv").write_text(
        "area,value,note\n" + "\n".join(f"{a},{v},{n}" for a, v, n in rows) + "\n")

    if desi:
        resid = desi["residual"]
        fig, ax = plt.subplots(figsize=(7.2, 3.7))
        ax.bar(range(len(resid)), resid)
        ax.set_xlabel("DESI index")
        ax.set_ylabel("residual (obs - pred)")
        ax.set_title("M28 DESI residuals (diagnostic)")
        fig.tight_layout()
        fig.savefig(SRC / "fig_desi_residuals.png", dpi=150)
        plt.close(fig)
    if decomp:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(["chiN2", "chiL|N2"],
               [decomp["forward"]["chi2_N"], decomp["forward"]["chi2_L_given_N"]])
        ax.set_ylabel("chi2")
        ax.set_title("M28 joint conditional decomposition")
        fig.tight_layout()
        fig.savefig(SRC / "fig_decomposition.png", dpi=150)
        plt.close(fig)

    for f in sorted(SRC.rglob("*.json")):
        rel = f.relative_to(SRC)
        dest = EV / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, dest)
    for f in sorted(SRC.rglob("*.png")):
        rel = f.relative_to(SRC)
        dest = EV / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, dest)
    print(f"summary -> {TAB/'m28_validation_summary.tex'}; "
          f"evidence -> {EV} ({len(list(EV.glob('*')))} files)")
    print(f"handoff status: {hand.get('status', 'NO_HANDOFF_YET')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
