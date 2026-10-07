"""Unit locks for the core reconstruction mathematics (RDE-019).

Verifies, against versioned publication evidence (no refits):
  - the profiled-nuisance estimator M-hat and joint chi-squared form;
  - the logarithmic difference-field definitions;
  - the common/disagreement decomposition identity;
  - the common-mode fraction formula and its headline value.
"""

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
EV = REPO / "paper" / "evidence"


def m_hat(r0, cinv):
    ones = np.ones_like(r0)
    return float(ones @ cinv @ r0 / (ones @ cinv @ ones))


def chi2_joint(r0, cinv):
    m = m_hat(r0, cinv)
    resid = r0 - m * np.ones_like(r0)
    return float(resid @ cinv @ resid)


def test_m_hat_closed_form():
    rng = np.random.default_rng(0)
    n = 12
    a = rng.normal(size=(n, n))
    cov = a @ a.T + n * np.eye(n)
    cinv = np.linalg.inv(cov)
    r0 = rng.normal(size=n)
    got = m_hat(r0, cinv)
    # brute-force optimum of (r0 - m 1)^T C^-1 (r0 - m 1)
    ms = np.linspace(got - 1, got + 1, 10001)
    brute = ms[np.argmin([float((r0 - m) @ cinv @ (r0 - m)) for m in ms])]
    assert abs(got - brute) < 1e-3
    assert chi2_joint(r0, cinv) <= float(r0 @ cinv @ r0)


def test_difference_field_definitions():
    hr = np.array([72.8, 73.0, 73.2])
    hc1 = np.array([68.0, 68.1, 68.2])
    hc2 = np.array([67.4, 67.5, 67.6])
    d1 = np.log(hr) - np.log(hc1)
    d2 = np.log(hr) - np.log(hc2)
    dc = np.log(hc1) - np.log(hc2)
    np.testing.assert_allclose(dc, d2 - d1, rtol=1e-12)
    # symmetric decomposition identity
    common = (d1 + d2) / 2
    dis = (d1 - d2) / 2
    np.testing.assert_allclose(common + dis, d1, rtol=1e-12)
    np.testing.assert_allclose(common - dis, d2, rtol=1e-12)


def f_common(rms_dis, rms_common):
    return 1.0 - (rms_dis / rms_common) ** 2


def test_common_mode_formula_on_evidence():
    with open(EV / "reference_sensitivity/common_mode.json") as fh:
        rows = json.load(fh)
    for row in rows:
        if row["interval"][1] > 1.8:
            continue
        expect = f_common(row["rms_disagreement"], row["rms_common"])
        assert abs(expect - row["f_common"]) < 1e-9
    fmin = min(r["f_common"] for r in rows if r["interval"][1] <= 1.8)
    assert abs(fmin - 0.9983825364249921) < 1e-12
    assert f"{fmin:.3f}" == "0.998"


def test_headline_parity_values():
    with open(EV / "model_selection/bootstrap.json") as fh:
        boot = json.load(fh)
    assert boot["frac_select_ge_m3"] == 0.216
    assert boot["nrep"] == 250
    with open(EV / "reconstruction/jacobian_rank.json") as fh:
        rank = json.load(fh)
    assert rank["rank"] == 5
    with open(EV / "model_selection/constrained_cv.json") as fh:
        rescore = json.load(fh)
    assert abs(rescore["per_order"]["3"]["combined_constrained"]
               - rescore["per_order"]["4"]["combined_constrained"] - 0.13) < 0.02
