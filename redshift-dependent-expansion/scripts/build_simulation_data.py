#!/usr/bin/env python3
"""Build the frozen publication JSON for the redshift-expansion visualization.

Reads ONLY neutral publication artifacts kept alongside the paper
(figure CSV tables and evidence contracts with public-relative names)
and writes a compact derived JSON for the public simulation.

No theory-development files, no raw catalog rows, and no internal
working labels are consumed or embedded here.
"""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Publication artifacts consumed (relative names only).
SRC_ENDPOINTS = "paper/figures/generated/overview_fig1_endpoints.csv"
SRC_DIFFS = "paper/figures/generated/bridge_fig5_triangulation.csv"
SRC_CV = "paper/figures/generated/bridge_fig3_cv.csv"
SRC_EPSILON = "paper/figures/generated/bridge_fig4_epsilon.csv"
SRC_BOOTSTRAP = "paper/evidence/cmb_bridge_r8r2/selection_bootstrap_constrained.json"
SRC_RESCORE = "paper/evidence/cmb_bridge_r8r2/constrained_cv_rescore.json"
SRC_IDENTITY = "paper/evidence/endpoint_identity_contract.json"
SRC_RULERS = "paper/evidence/branch_calibration_contract.json"

OUT_PATH = "simulation/data/publication_simulation_data.json"

N_OUT = 241
Z_MIN = 0.0
Z_MAX = 2.33
Z_CONSTRAINED_MAX = 1.8
Z_LYA = 2.33
C_KM_S = 299792.458

# Synthetic tracer recipe (tracers are generated at runtime in the page
# from this seed; no tracer records are stored).
TRACER_COUNT = 560
TRACER_SEED = 20260233


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with open(REPO_ROOT / path, newline="") as fh:
        return list(csv.DictReader(fh))


def lin_interp(xp, fp, x):
    """Piecewise-linear interpolation on ascending nodes xp."""
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]
    lo, hi = 0, len(xp) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xp[mid] <= x:
            lo = mid
        else:
            hi = mid
    t = (x - xp[lo]) / (xp[hi] - xp[lo])
    return fp[lo] + t * (fp[hi] - fp[lo])


def resample(xp, fp, xs):
    return [lin_interp(xp, fp, x) for x in xs]


def cumulative_trapezoid(z, h):
    """Comoving line-of-sight distance integral of c/H(z) via trapezoids."""
    out = [0.0]
    acc = 0.0
    for i in range(1, len(z)):
        dz = z[i] - z[i - 1]
        acc += 0.5 * (C_KM_S / h[i - 1] + C_KM_S / h[i]) * dz
        out.append(acc)
    return out


def main():
    import math

    end_rows = read_csv(SRC_ENDPOINTS)
    z_src = [float(r["z"]) for r in end_rows]
    h_r_src = [float(r["H_R"]) for r in end_rows]
    h_c1_src = [float(r["H_C1"]) for r in end_rows]
    h_c2_src = [float(r["H_C2"]) for r in end_rows]

    diff_rows = read_csv(SRC_DIFFS)
    z_d = [float(r["z"]) for r in diff_rows]
    m3_src = [float(r["m3_on_C1"]) for r in diff_rows]

    cv_rows = read_csv(SRC_CV)
    cv_rows.sort(key=lambda r: int(r["m"]))
    cv_orders = [int(r["m"]) for r in cv_rows]
    cv_combined = [float(r["combined_constrained"]) for r in cv_rows]
    cv_desi = [float(r["desi_constrained_held"]) for r in cv_rows]
    cv_sn = [float(r["sn_held"]) for r in cv_rows]
    cv_delta = [float(r["delta_vs_min"]) for r in cv_rows]
    cv_lya = [float(r["lya_held"]) for r in cv_rows]

    eps_rows = read_csv(SRC_EPSILON)
    eps_zero = None
    for r in eps_rows:
        if float(r["epsilon"]) == 0.0:
            eps_zero = float(r["delta_chi2"])
    if eps_zero is None:
        raise ValueError("epsilon=0 row missing from epsilon profile table")

    with open(REPO_ROOT / SRC_BOOTSTRAP) as fh:
        boot = json.load(fh)
    with open(REPO_ROOT / SRC_RESCORE) as fh:
        rescore = json.load(fh)
    with open(REPO_ROOT / SRC_IDENTITY) as fh:
        identity = json.load(fh)
    with open(REPO_ROOT / SRC_RULERS) as fh:
        rulers = json.load(fh)

    # Uniform output grid.
    z_out = [Z_MIN + (Z_MAX - Z_MIN) * i / (N_OUT - 1) for i in range(N_OUT)]

    h_r = resample(z_src, h_r_src, z_out)
    h_c1 = resample(z_src, h_c1_src, z_out)
    h_c2 = resample(z_src, h_c2_src, z_out)

    # Absolute comoving distances come from the frozen H(z) curves by direct
    # numerical integration (cumulative trapezoid on the dense source grid,
    # then resampled to the output grid).
    dm_r = resample(z_src, cumulative_trapezoid(z_src, h_r_src), z_out)
    dm_c1 = resample(z_src, cumulative_trapezoid(z_src, h_c1_src), z_out)
    dm_c2 = resample(z_src, cumulative_trapezoid(z_src, h_c2_src), z_out)

    # Difference fields recomputed from the resampled endpoints so the JSON
    # is internally consistent by construction.
    delta1 = [math.log(a / b) for a, b in zip(h_r, h_c1)]
    delta2 = [math.log(a / b) for a, b in zip(h_r, h_c2)]
    delta_c = [math.log(a / b) for a, b in zip(h_c1, h_c2)]
    m3 = resample(z_d, m3_src, z_out)

    i1 = max(range(len(z_out)), key=lambda i: delta1[i])
    i2 = max(range(len(z_out)), key=lambda i: delta2[i])

    best = min(cv_combined)
    raw_min_order = cv_orders[cv_combined.index(best)]
    # Predeclared parsimony rule: smallest order within 2.0 of the minimum.
    selected_order = min(
        o for o, v in zip(cv_orders, cv_combined) if v <= best + 2.0
    )

    payload = {
        "metadata": {
            "title": "Redshift-dependent expansion: frozen publication numbers",
            "version": 1,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "grid": {
                "n": N_OUT,
                "z_min": Z_MIN,
                "z_max": Z_MAX,
                "method": "piecewise-linear resampling of frozen curves",
            },
            "sources": [
                {"path": p, "sha256": sha256_of(REPO_ROOT / p)}
                for p in [
                    SRC_ENDPOINTS,
                    SRC_DIFFS,
                    SRC_CV,
                    SRC_EPSILON,
                    SRC_BOOTSTRAP,
                    SRC_RESCORE,
                    SRC_IDENTITY,
                    SRC_RULERS,
                ]
            ],
            "provenance_notes": [
                "H_R/H_C1/H_C2 resampled from the frozen endpoint figure table.",
                "Comoving distances integrated from frozen H(z) with c/H trapezoids.",
                "Difference fields recomputed from resampled H(z); see tests.",
                "Order-3 map column resampled from the frozen triangulation table.",
                "Projected Jacobian rank and condition number are the values "
                "printed in the manuscript methods section for the frozen "
                "order-3 audit (rank 5 of 5 fitted coordinates).",
            ],
        },
        "domain": {
            "z_min": Z_MIN,
            "z_constrained_max": Z_CONSTRAINED_MAX,
            "z_lya": Z_LYA,
            "h0_R": identity["R"]["H0"],
            "h0_C1": identity["C1"]["H0"],
            "h0_C2": identity["C2"]["H0"],
        },
        "curves": {
            "z": z_out,
            "H_R": h_r,
            "H_C1": h_c1,
            "H_C2": h_c2,
            "DM_R": dm_r,
            "DM_C1": dm_c1,
            "DM_C2": dm_c2,
            "delta1": delta1,
            "delta2": delta2,
            "deltaC": delta_c,
            "m3": m3,
        },
        "peak": {
            "z_of_max_delta1": z_out[i1],
            "peak_delta1": delta1[i1],
            "z_of_max_delta2": z_out[i2],
            "peak_delta2": delta2[i2],
        },
        "validation": {
            "cv_orders": cv_orders,
            "cv_combined_constrained": cv_combined,
            "cv_desi_constrained": cv_desi,
            "cv_sn": cv_sn,
            "cv_delta_vs_min": cv_delta,
            "cv_lya_held": cv_lya,
            "selected_order": selected_order,
            "raw_min_order": raw_min_order,
            "parsimony_threshold": 2.0,
            "bootstrap_p_select_ge_m3": boot["frac_select_ge_m3"],
            "bootstrap_lya_catastrophe_frac": boot["frac_lya_catastrophe"],
            "bootstrap_nrep": boot["nrep"],
            "jacobian_rank": 5,
            "jacobian_dimension": 5,
            "condition_number": 27.0,
            "condition_note": "manuscript value rounded from 27.0021",
            "singular_values": [
                602.3765781514629,
                157.31382890246925,
                102.06996475760742,
                32.03324959162922,
                22.30849662630157,
            ],
            "epsilon_delta_chi2_zero": eps_zero,
            "rd_R": rulers["R"]["rd_value"],
            "rd_C1": rulers["C1"]["rd_value"],
            "rd_C2": rulers["C2"]["rd_value"],
            "rd_ratio_R_over_C1": rulers["rd_ratio_to_C1"],
            "lya_status": "failed_continuation_test",
        },
        "tracers": {
            "count": TRACER_COUNT,
            "seed": TRACER_SEED,
            "direction_method": "fibonacci_sphere",
            "radial_method": "uniform_in_comoving_volume",
            "prng": "mulberry32",
        },
        "display_defaults": {
            "exaggeration": 8,
            "exaggeration_options": [1, 4, 8, 12],
            "shell_width": 0.08,
        },
    }

    # Cross-check the rescore record agrees with the figure table.
    for o in cv_orders:
        a = rescore["per_order"][str(o)]["combined_constrained"]
        b = cv_combined[cv_orders.index(o)]
        if abs(a - b) > 1e-6:
            raise ValueError(f"CV mismatch at order {o}: {a} vs {b}")
    if rescore["rule"].find("2.0") < 0:
        raise ValueError("parsimony rule text changed; review selection")
    if boot["frac_select_ge_m3"] != 0.216:
        raise ValueError("bootstrap fraction changed; review selection")

    out = REPO_ROOT / OUT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"wrote {OUT_PATH} ({N_OUT} grid points)")


if __name__ == "__main__":
    main()
