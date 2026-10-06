"""Publication-data tests for the redshift-expansion visualization.

Verifies the frozen JSON carries the paper values (invariants), that the
resampling is faithful, that derived fields are internally consistent,
and that the display-exaggeration math separates presentation from data.
"""

import csv
import hashlib
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SIM = REPO / "simulation"
DATA_PATH = SIM / "data" / "publication_simulation_data.json"

C_LIGHT = 299792.458


def load_payload():
    with open(DATA_PATH) as fh:
        return json.load(fh)


def read_csv_rows(rel):
    with open(REPO / rel, newline="") as fh:
        return list(csv.DictReader(fh))


def lin_interp(xp, fp, x):
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


def mulberry32(seed):
    a = seed & 0xFFFFFFFF

    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = (a ^ (a >> 15)) & 0xFFFFFFFF
        t = (t * (1 | a)) & 0xFFFFFFFF
        t = (t + ((t ^ (t >> 7)) * (61 | t))) & 0xFFFFFFFF
        t ^= t >> 14
        return (t & 0xFFFFFFFF) / 4294967296

    return rnd


def test_schema_and_grid():
    d = load_payload()
    for key in ("metadata", "domain", "curves", "peak", "validation",
                "tracers", "display_defaults"):
        assert key in d, f"missing section {key}"
    curves = d["curves"]
    for key in ("z", "H_R", "H_C1", "H_C2", "DM_R", "DM_C1", "DM_C2",
                "delta1", "delta2", "deltaC", "m3"):
        assert key in curves, f"missing curve {key}"
        assert len(curves[key]) == 241, f"{key} has {len(curves[key])} points"
    z = curves["z"]
    assert z[0] == 0.0 and abs(z[-1] - 2.33) < 1e-12
    steps = [b - a for a, b in zip(z, z[1:])]
    assert max(steps) - min(steps) < 1e-12, "grid must be uniform"


def test_source_hashes_reproduce():
    d = load_payload()
    for src in d["metadata"]["sources"]:
        raw = (REPO / src["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == src["sha256"], src["path"]


def test_resampling_fidelity():
    """Resampled H(z) must track the frozen source tables closely."""
    d = load_payload()
    rows = read_csv_rows("paper/figures/generated/overview_fig1_endpoints.csv")
    zs = [float(r["z"]) for r in rows]
    for col, key in (("H_R", "H_R"), ("H_C1", "H_C1"), ("H_C2", "H_C2")):
        src = [float(r[col]) for r in rows]
        got = d["curves"][key]
        worst = 0.0
        for z, g in zip(d["curves"]["z"], got):
            ref = lin_interp(zs, src, z)
            worst = max(worst, abs(g - ref) / ref)
        assert worst < 1e-9, f"{key} resample drift {worst}"
        # Smoothness: no interpolation ringing; second differences stay a
        # small fraction of the local value (linear interpolation of a
        # smooth curve cannot overshoot).
        second = [abs(a - 2 * b + c) / b for a, b, c in zip(got, got[1:], got[2:])]
        assert max(second) < 2e-3, f"{key} ringing {max(second)}"


def test_delta_parity():
    """Difference fields recomputed from H(z) must match the export."""
    d = load_payload()
    c = d["curves"]
    for i in range(len(c["z"])):
        assert abs(c["delta1"][i] - math.log(c["H_R"][i] / c["H_C1"][i])) < 1e-12
        assert abs(c["delta2"][i] - math.log(c["H_R"][i] / c["H_C2"][i])) < 1e-12
        assert abs(c["deltaC"][i] - math.log(c["H_C1"][i] / c["H_C2"][i])) < 1e-12


def test_distance_parity():
    """Exported D_M must equal trapezoid integration of exported H(z)."""
    d = load_payload()
    c = d["curves"]
    z = c["z"]
    for key, hkey in (("DM_R", "H_R"), ("DM_C1", "H_C1"), ("DM_C2", "H_C2")):
        acc = 0.0
        prev = 0.0
        for i in range(1, len(z)):
            dz = z[i] - z[i - 1]
            acc += 0.5 * (C_LIGHT / c[hkey][i - 1] + C_LIGHT / c[hkey][i]) * dz
            rel = abs(c[key][i] - acc) / acc
            assert rel < 2e-3, f"{key}[{i}] drift {rel}"
        assert c[key][0] == 0.0
        assert c[key][-1] > c[key][-2] > 0


def test_no_sign_or_normalization_reversal():
    d = load_payload()
    c = d["curves"]
    # R expands faster than either reference at low redshift.
    assert all(v > 0 for v in c["delta1"][:50])
    assert all(v > 0 for v in c["delta2"][:50])
    # The two references sit close together relative to R.
    assert max(abs(v) for v in c["deltaC"]) < min(c["delta1"]) * 0.15
    # Distances: R closer (smaller ruler), references nearly equal.
    assert c["DM_R"][-1] < c["DM_C1"][-1]
    assert abs(c["DM_C2"][-1] - c["DM_C1"][-1]) / c["DM_C1"][-1] < 0.01


def test_scientific_invariants():
    d = load_payload()
    dom, val, peak = d["domain"], d["validation"], d["peak"]
    assert dom["z_min"] == 0
    assert dom["z_constrained_max"] == 1.8
    assert dom["z_lya"] == 2.33
    assert val["selected_order"] == 3
    assert val["raw_min_order"] == 4
    assert val["cv_orders"] == [2, 3, 4, 5, 6]
    best = min(val["cv_combined_constrained"])
    assert val["cv_combined_constrained"][1] - best < 2.0  # order-3 within 2
    assert val["cv_combined_constrained"][0] - best > 2.0  # order-2 excluded
    assert val["bootstrap_p_select_ge_m3"] == 0.216
    assert val["jacobian_rank"] == 5 and val["jacobian_dimension"] == 5
    assert abs(val["condition_number"] - 27.0) < 0.5
    assert abs(val["epsilon_delta_chi2_zero"] - 0.124) < 0.001
    assert abs(val["rd_ratio_R_over_C1"] - 0.92) < 0.005
    assert val["lya_status"] == "failed_continuation_test"
    assert abs(dom["h0_R"] - 72.80) < 0.01
    assert abs(dom["h0_C1"] - 67.99) < 0.01
    assert abs(dom["h0_C2"] - 67.4) < 0.01
    assert abs(val["rd_R"] - 135.39) < 0.01
    assert abs(val["rd_C1"] - 147.15) < 0.01
    assert abs(peak["z_of_max_delta1"] - 0.65) < 0.02
    assert abs(peak["peak_delta1"] - 0.1207) < 0.002


def test_exaggeration_separates_display_from_data():
    """E=1 reproduces true radii; E only widens the displayed gap."""
    d = load_payload()
    c = d["curves"]
    dm_max = c["DM_C1"][-1]
    z = c["z"]
    for zi in (0.1, 0.65, 1.2, 1.8, 2.33):
        r_true = lin_interp(z, c["DM_R"], zi) / dm_max
        c_true = lin_interp(z, c["DM_C1"], zi) / dm_max
        for e in (1, 4, 8, 12):
            mid = (r_true + c_true) / 2
            gap = r_true - c_true
            r_disp = mid + (e / 2) * gap
            c_disp = mid - (e / 2) * gap
            if e == 1:
                assert abs(r_disp - r_true) < 1e-15
                assert abs(c_disp - c_true) < 1e-15
            assert abs((r_disp + c_disp) / 2 - mid) < 1e-15
            assert abs((r_disp - c_disp) - e * gap) < 1e-15


def test_tracer_recipe_is_deterministic_and_volumetric():
    d = load_payload()
    t = d["tracers"]
    assert t["count"] == 560 and 450 <= t["count"] <= 700
    assert t["direction_method"] == "fibonacci_sphere"
    assert t["radial_method"] == "uniform_in_comoving_volume"

    def build(seed):
        rng = mulberry32(seed)
        n = t["count"]
        out = []
        z = d["curves"]["z"]
        dm = d["curves"]["DM_C1"]
        dm_max = dm[-1]
        for i in range(n):
            y = 1 - 2 * (i + 0.5) / n
            u = rng()
            target = u ** (1 / 3) * dm_max
            lo, hi = 0, len(dm) - 1
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if dm[mid] <= target:
                    lo = mid
                else:
                    hi = mid
            frac = (target - dm[lo]) / (dm[hi] - dm[lo])
            out.append((y, z[lo] + frac * (z[hi] - z[lo]), u))
        return out

    first, second = build(t["seed"]), build(t["seed"])
    assert first == second
    assert all(0.0 <= zi <= 2.33 for _, zi, _ in first)
    # Uniform-in-volume check: mean of u^(1/3) over the sample ~ 3/4.
    mean_cuberoot = sum(u ** (1 / 3) for _, _, u in first) / len(first)
    assert abs(mean_cuberoot - 0.75) < 0.02, mean_cuberoot


def test_frontend_shows_publication_numbers():
    html = (SIM / "index.html").read_text()
    for token in ("0.216", "5/5", "0.124", "0.92", "2.33", "1.8",
                  "synthetic", "×8", "order 3"):
        assert token in html, f"index.html missing {token}"
    assert "real galaxy" not in html.lower()
    assert "real galaxies" not in html.lower()
