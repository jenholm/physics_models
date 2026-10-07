#!/usr/bin/env python3
"""Rebuild the publication results registry from versioned evidence.

Reads ONLY public files under paper/evidence/ (neutral publication
directories) and writes:
  paper/generated/results_registry.json
  paper/generated/results_macros.tex
  paper/generated/provenance.json

Every macro records its source file, evidence key, value, and the
source-file SHA256 so the paper can never silently drift from the
archived evidence. Scientific parity is enforced by exact-value
assertions on the headline numbers (RDE-054).
"""

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EV = REPO / "paper" / "evidence"
GEN = REPO / "paper" / "generated"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(rel):
    with open(REPO / rel) as fh:
        return json.load(fh)


def fmt(value, ndigits):
    return f"{round(value, ndigits):.{ndigits}f}"


def main():
    # ---- source documents (public publication evidence only) ----
    info = load_json("paper/evidence/reconstruction/information_criteria.json")
    vis = load_json("paper/evidence/reconstruction/visible_map.json")
    rank = load_json("paper/evidence/reconstruction/jacobian_rank.json")
    nullcv = load_json("paper/evidence/reconstruction/null_cv_summary.json")
    rescore = load_json("paper/evidence/model_selection/constrained_cv.json")
    boot = load_json("paper/evidence/model_selection/bootstrap.json")
    agree = load_json("paper/evidence/reference_sensitivity/agreement_metrics.json")
    common = load_json("paper/evidence/reference_sensitivity/common_mode.json")
    scale = load_json("paper/evidence/reference_sensitivity/scale_comparison.json")
    transfer = load_json("paper/evidence/reference_sensitivity/disposition.json")
    zgrid = load_json("paper/evidence/endpoints/endpoint_redshift.json")
    c1 = load_json("paper/evidence/endpoints/endpoint_cmb_1.json")
    c2 = load_json("paper/evidence/endpoints/endpoint_cmb_2.json")

    rows = {r["model"]: r for r in info["rows"]}
    m3 = rows["legendre-m3"]
    ctrl = rows["control21"]

    macros = {}

    def add(name, value, latex, source, key):
        macros[name] = {
            "value": value,
            "latex": latex,
            "source": source,
            "key": key,
            "sha256": sha256_of(REPO / source),
        }

    # --- information criteria (reconstruction coordinates only) ---
    add("BridgeAIC", m3["AIC"], fmt(m3["AIC"], 2),
        "paper/evidence/reconstruction/information_criteria.json", "rows.1.AIC")
    add("BridgeAICCtrl", ctrl["AIC"], fmt(ctrl["AIC"], 2),
        "paper/evidence/reconstruction/information_criteria.json", "rows.5.AIC")
    add("BridgeAICDeltaVsCtrl", m3["AIC"] - ctrl["AIC"],
        fmt(m3["AIC"] - ctrl["AIC"], 2),
        "paper/evidence/reconstruction/information_criteria.json",
        "AIC(legendre-m3)-AIC(control21)")
    add("BridgeKCtrl", ctrl["k_late_map"], str(ctrl["k_late_map"]),
        "paper/evidence/reconstruction/information_criteria.json", "rows.5.k_late_map")
    add("BridgeKmThree", m3["k_late_map"], str(m3["k_late_map"]),
        "paper/evidence/reconstruction/information_criteria.json", "rows.1.k_late_map")

    # --- full-data fit of the selected order-3 reconstruction ---
    add("BridgeChiTwo", vis["full_data_chi2"], fmt(vis["full_data_chi2"], 2),
        "paper/evidence/reconstruction/visible_map.json", "full_data_chi2")
    add("BridgeDeltaCtrl", vis["delta_vs_control"], fmt(vis["delta_vs_control"], 2),
        "paper/evidence/reconstruction/visible_map.json", "delta_vs_control")
    add("BridgeEpsDelta", vis["delta_chi2_eps0"], fmt(vis["delta_chi2_eps0"], 3),
        "paper/evidence/reconstruction/visible_map.json", "delta_chi2_eps0")
    add("BridgeRank", vis["effective_observable_rank"], str(vis["effective_observable_rank"]),
        "paper/evidence/reconstruction/visible_map.json", "effective_observable_rank")
    assert rank["rank"] == 5, "Jacobian rank changed"
    assert len(rank["singular_values"]) == 5, "Jacobian rank changed"

    # --- null-reconstruction comparisons (paired folds) ---
    paired = nullcv["paired_m3_minus_bare"]
    desi_bare = sum(float(r["held_bare"]) for r in nullcv["desi_folds"]
                    if float(r["block"]) <= 1.8)
    desi_m3 = sum(float(r["held_m3"]) for r in nullcv["desi_folds"]
                  if float(r["block"]) <= 1.8)
    add("BridgeNullSn", paired["sn"], fmt(paired["sn"], 1),
        "paper/evidence/reconstruction/null_cv_summary.json", "paired_m3_minus_bare.sn")
    add("BridgeNullDesiConstr", desi_m3 - desi_bare, fmt(desi_m3 - desi_bare, 2),
        "paper/evidence/reconstruction/null_cv_summary.json", "sum(desi_folds, z<=1.8)")
    add("BridgeDesiBareConstr", desi_bare, fmt(desi_bare, 2),
        "paper/evidence/reconstruction/null_cv_summary.json", "sum(desi_folds, z<=1.8)")
    add("BridgeDesiMThreeConstr", desi_m3, fmt(desi_m3, 2),
        "paper/evidence/reconstruction/null_cv_summary.json", "sum(desi_folds, z<=1.8)")

    # --- endpoint Hubble constants (best-fit displays) ---
    add("DistanceHZero", zgrid["H0"], fmt(zgrid["H0"], 2),
        "paper/evidence/endpoints/endpoint_redshift.json", "H0")
    add("CmbOneHZero", c1["H0"], fmt(c1["H0"], 2),
        "paper/evidence/endpoints/endpoint_cmb_1.json", "H0")
    add("CmbTwoHZero", c2["H0"], fmt(c2["H0"], 1),
        "paper/evidence/endpoints/endpoint_cmb_2.json", "H0")

    # --- constrained model selection + bootstrap ---
    per = rescore["per_order"]
    for m in ("2", "3", "4", "5", "6"):
        add(f"CvConstrM{['Two', 'Three', 'Four', 'Five', 'Six'][int(m) - 2]}",
            per[m]["combined_constrained"], fmt(per[m]["combined_constrained"], 2),
            "paper/evidence/model_selection/constrained_cv.json",
            f"per_order.{m}.combined_constrained")
    selected = min(per, key=lambda m: per[m]["combined_constrained"])
    # predeclared rule: smallest order within 2.0 of the raw minimum
    best = min(v["combined_constrained"] for v in per.values())
    candidate = [m for m, v in per.items() if v["combined_constrained"] <= best + 2.0]
    ruled = min(candidate, key=int)
    assert ruled == "3", f"selection rule changed: {ruled}"
    add("CvConstrSelected", 3, "3",
        "paper/evidence/model_selection/constrained_cv.json", "selected_m")
    add("CvConstrBootProb", boot["frac_select_ge_m3"], fmt(boot["frac_select_ge_m3"], 3),
        "paper/evidence/model_selection/bootstrap.json", "frac_select_ge_m3")
    add("CvConstrLyaProb", boot["frac_lya_catastrophe"], fmt(boot["frac_lya_catastrophe"], 3),
        "paper/evidence/model_selection/bootstrap.json", "frac_lya_catastrophe")
    # m3 gap to the raw best (exact evidence difference, two decimals)
    gap = per["3"]["combined_constrained"] - rescore["best_combined"]
    add("CvConstrMThreeDeltaVsBest", gap, fmt(gap, 2),
        "paper/evidence/model_selection/constrained_cv.json",
        "per_order.3.combined_constrained - best_combined")
    # bootstrap Monte Carlo standard error sqrt(p(1-p)/n)
    p = boot["frac_select_ge_m3"]
    n = boot["nrep"]
    mcse = math.sqrt(p * (1.0 - p) / n)
    add("CvConstrBootMcse", mcse, fmt(mcse, 3),
        "paper/evidence/model_selection/bootstrap.json", "sqrt(p(1-p)/n)")

    # --- reference sensitivity (supported domain) ---
    sup = agree["supported"]
    add("GeometryCosineSimilarity", sup["cosine_D1_D2"], fmt(sup["cosine_D1_D2"], 4),
        "paper/evidence/reference_sensitivity/agreement_metrics.json", "supported.cosine_D1_D2")
    add("GeometryPrincipalAngle", sup["principal_angle_deg"], fmt(sup["principal_angle_deg"], 1),
        "paper/evidence/reference_sensitivity/agreement_metrics.json", "supported.principal_angle_deg")
    add("GeometrySvdDominance", sup["svd_dominance_s1_over_s2"], fmt(sup["svd_dominance_s1_over_s2"], 1),
        "paper/evidence/reference_sensitivity/agreement_metrics.json",
        "supported.svd_dominance_s1_over_s2")
    add("GeometryPeakZ", sup["z_of_max_D1"], fmt(sup["z_of_max_D1"], 2),
        "paper/evidence/reference_sensitivity/agreement_metrics.json", "supported.z_of_max_D1")
    fmin = min(row["f_common"] for row in common if row["interval"][1] <= 1.8)
    add("GeometryCommonFractionMin", fmin, fmt(fmin, 3),
        "paper/evidence/reference_sensitivity/common_mode.json", "min f_common, z<=1.8")
    add("GeometryTransferDegradation",
        transfer["checks"]["c_transfer_degradation"]["C1_to_C2"],
        fmt(transfer["checks"]["c_transfer_degradation"]["C1_to_C2"], 3),
        "paper/evidence/reference_sensitivity/disposition.json",
        "checks.c_transfer_degradation.C1_to_C2")
    # interval-specific reference ratios (NOT extrema; see ReferenceRatio* below)
    by_interval = {(r["interval"][0], r["interval"][1]): r for r in scale}
    peak = by_interval[(0.4, 0.8)]["ratio_rms_DC_over_D1"]
    high = by_interval[(1.2, 1.8)]["ratio_rms_DC_over_D1"]
    add("GeometryCmbRatioLow", peak, fmt(peak, 3),
        "paper/evidence/reference_sensitivity/scale_comparison.json",
        "interval[0.4,0.8].ratio_rms_DC_over_D1")
    add("GeometryCmbRatioHigh", high, fmt(high, 3),
        "paper/evidence/reference_sensitivity/scale_comparison.json",
        "interval[1.2,1.8].ratio_rms_DC_over_D1")
    # neutral extrema across the constrained bins (z <= 1.8)
    constrained = [r for r in scale if r["interval"][1] <= 1.8]
    ratios = [r[k] for r in constrained
              for k in ("ratio_rms_DC_over_D1", "ratio_rms_DC_over_D2")]
    rmin, rmax = min(ratios) * 100.0, max(ratios) * 100.0
    add("ReferenceSensitivityRatioMinPct", round(rmin, 1), fmt(rmin, 1),
        "paper/evidence/reference_sensitivity/scale_comparison.json",
        "min DC/D1,DC/D2 over constrained bins, percent")
    add("ReferenceSensitivityRatioMaxPct", round(rmax, 1), fmt(rmax, 1),
        "paper/evidence/reference_sensitivity/scale_comparison.json",
        "max DC/D1,DC/D2 over constrained bins, percent")

    # ---- scientific parity gate (RDE-054): no endpoint or fit reruns ----
    assert macros["DistanceHZero"]["latex"] == "72.80"
    assert macros["CmbOneHZero"]["latex"] == "67.99"
    assert macros["CmbTwoHZero"]["latex"] == "67.4"
    assert macros["CvConstrSelected"]["latex"] == "3"
    assert macros["CvConstrBootProb"]["latex"] == "0.216"
    assert macros["CvConstrMThreeDeltaVsBest"]["latex"] == "0.13"
    assert macros["CvConstrBootMcse"]["latex"] == "0.026"
    assert macros["BridgeRank"]["latex"] == "5"
    assert macros["BridgeEpsDelta"]["latex"] == "0.124"
    assert macros["ReferenceSensitivityRatioMinPct"]["latex"] == "1.3"
    assert macros["ReferenceSensitivityRatioMaxPct"]["latex"] == "8.4"

    GEN.mkdir(parents=True, exist_ok=True)
    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "macros": macros,
    }
    with open(GEN / "results_registry.json", "w") as fh:
        json.dump(registry, fh, indent=1)
        fh.write("\n")

    lines = [
        "% GENERATED FILE -- do not edit by hand.",
        "% Owner: scripts/paper/build_results_registry.py",
        "% Source of truth: paper/evidence/ (versioned publication evidence).",
        "% Publication mode: neutral macros only.",
        "",
    ]
    for name in sorted(macros):
        lines.append(f"\\newcommand{{\\{name}}}{{{macros[name]['latex']}}}")
    with open(GEN / "results_macros.tex", "w") as fh:
        fh.write("\n".join(lines) + "\n")

    evidence_files = sorted(
        str(p.relative_to(REPO)) for p in EV.rglob("*") if p.is_file()
    )
    provenance = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_files": {rel: sha256_of(REPO / rel) for rel in evidence_files},
    }
    with open(GEN / "provenance.json", "w") as fh:
        json.dump(provenance, fh, indent=1)
        fh.write("\n")

    print(f"registry: {len(macros)} macros from versioned publication evidence")


if __name__ == "__main__":
    main()
