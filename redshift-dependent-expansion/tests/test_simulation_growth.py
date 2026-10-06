"""Growth and visibility invariants for the redshift-expansion visualization.

Regression coverage for the shell-gating fix: the moving redshift shell is
an emphasis device, never a visibility gate, and the sphere grows
monotonically until it stops at the present-day endpoint.

Python mirrors of the page's pure kinematics live here; companion guards
assert the page source still carries the same constants so the two cannot
drift apart silently.
"""

import json
import math
from pathlib import Path

import test_simulation_data as base

REPO = Path(__file__).resolve().parents[1]
JS_PATH = REPO / "simulation" / "simulation.js"


# ---- Python mirrors of simulation.js pure functions ----

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def a_visual(p):
    return 0.06 + 0.94 * ease_out_cubic(min(max(p, 0.0), 1.0))


def z_scan(p):
    if p < 0.22:
        t = p / 0.22
        t = t * t * (3 - 2 * t)
        return 3.4 + (2.33 - 3.4) * t
    if p < 0.38:
        return 2.33 + (1.8 - 2.33) * (p - 0.22) / 0.16
    return 1.8 * (1 - (p - 0.38) / 0.62)


BASE_POINT = {"early": 0.16, "continuation": 0.30, "constrained": 0.38}
BASE_LINE = {"early": 0.025, "continuation": 0.045, "constrained": 0.065}


def tracer_visual_style(w, regime, peak_boost=1.0):
    point = min(max(BASE_POINT[regime] + 0.58 * w * peak_boost, 0.0), 1.0)
    line = min(max(BASE_LINE[regime] + 0.34 * w, 0.0), 0.55)
    return point, line, 1.35 + 1.8 * w


def tracer_nominal_z(seed, count, z_grid, dm_c1):
    rng = base.mulberry32(seed)
    dm_max = dm_c1[-1]
    out = []
    for _ in range(count):
        u = rng()
        target = u ** (1 / 3) * dm_max
        lo, hi = 0, len(dm_c1) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if dm_c1[mid] <= target:
                lo = mid
            else:
                hi = mid
        frac = (target - dm_c1[lo]) / (dm_c1[hi] - dm_c1[lo])
        out.append(z_grid[lo] + frac * (z_grid[hi] - z_grid[lo]))
    return out


# ---- R2-007: monotonic growth, monotonic scan ----

def test_a_visual_monotonic_and_endpoints():
    a = [a_visual(i / 100) for i in range(101)]
    assert all(b >= v for v, b in zip(a, a[1:]))
    assert abs(a[0] - 0.06) < 1e-12
    assert abs(a[-1] - 1.0) < 1e-12


def test_z_scan_monotonic_nonincreasing():
    z = [z_scan(i / 100) for i in range(101)]
    assert all(b <= v + 1e-12 for v, b in zip(z, z[1:]))
    assert abs(z[0] - 3.4) < 1e-12
    assert abs(z[-1] - 0.0) < 1e-12
    assert abs(z_scan(1.0)) < 1e-12


# ---- R2-008: rendered-envelope invariant at E=8 ----

def test_rendered_envelope_monotonic_E8():
    d = base.load_payload()
    c = d["curves"]
    z_grid = c["z"]
    dm_max = c["DM_C1"][-1]
    zetas = tracer_nominal_z(
        d["tracers"]["seed"], d["tracers"]["count"], z_grid, c["DM_C1"]
    )
    radii = []
    for zi in zetas:
        r_true = base.lin_interp(z_grid, c["DM_R"], zi) / dm_max
        c_true = base.lin_interp(z_grid, c["DM_C1"], zi) / dm_max
        mid = (r_true + c_true) / 2
        gap = r_true - c_true
        radii.append(abs(mid + 4 * gap))
        radii.append(abs(mid - 4 * gap))
    env = [max(radii) * a_visual(i / 100) for i in range(101)]
    assert all(b >= v - 1e-9 for v, b in zip(env, env[1:])), \
        "visual envelope must never shrink as the animation advances"


# ---- R2-009: minimum-visibility regression ----

def test_off_shell_tracers_stay_visible():
    for boost in (1.0, 2.5):
        p_con, _, _ = tracer_visual_style(0.0, "constrained", boost)
        assert p_con >= 0.30, (boost, p_con)
        p_mid, _, _ = tracer_visual_style(0.0, "continuation", boost)
        assert p_mid >= 0.22, (boost, p_mid)
        p_shell, _, _ = tracer_visual_style(1.0, "constrained", boost)
        assert p_shell > p_con, (boost, p_shell, p_con)


def test_lines_stay_subdued_but_persistent():
    _, line_off, _ = tracer_visual_style(0.0, "constrained")
    _, line_on, _ = tracer_visual_style(1.0, "constrained")
    assert 0.0 < line_off < line_on <= 0.55


# ---- Mirror-drift guards: page source must carry the same constants ----

def test_js_matches_growth_mirror():
    js = JS_PATH.read_text()
    for snippet in (
        "0.06 + 0.94 * easeOutCubic",
        "lerp(3.4, 2.33",
        "lerp(2.33, 1.8",
        "1.8 * (1 - (p - 0.38) / 0.62)",
        "0.58 * shellWeightValue",
        "0.34 * shellWeightValue",
        "1.35 + 1.8 * shellWeightValue",
        "state.animationProgress = 1;",
        "state.endHoldElapsed = 0.0;",
        "Present-day endpoint — restarting shortly.",
    ):
        assert snippet in js, f"simulation.js missing {snippet!r}"
    for gone in (
        "animationProgress -= 1",
        "0.06 + 0.94 * wgt",
        "30 + 225 * alpha",
        "14 + 150 * alpha",
        "animationProgress = 1;\n        state.playing = false",
    ):
        assert gone not in js, f"simulation.js still contains {gone!r}"


# ---- R3-011: startup regression ----

def test_animation_starts_at_beginning():
    js = JS_PATH.read_text()
    for snippet in (
        "animationProgress: 0.0,",
        "zScan: 3.4,",
        "aVisual: 0.06,",
        "playing: true,",
        "endHoldElapsed: 0.0,",
        "endHoldSeconds: 1.75,",
        "function resetAnimation() {",
        "state.zScan = zScanOf(0.0);",
        "state.aVisual = aVisualOf(0.0);",
    ):
        assert snippet in js, f"simulation.js missing {snippet!r}"
    # resetAnimation drives both page init and the R key.
    assert js.count("resetAnimation();") >= 2


def test_a_visual_strictly_increases_by_quarter():
    a = [a_visual(p) for p in (0, 0.25, 0.50, 0.75, 1.0)]
    assert a[0] < a[1] < a[2] < a[3] < a[4]


# ---- R3-012: automatic-loop behavior (mirrored step logic) ----

def test_auto_loop_holds_then_resets_without_pausing():
    dt, rate, hold_seconds = 0.016, 0.045, 1.75
    p, hold, playing = 0.0, 0.0, True
    previous = 0.0
    clamped_time = 0.0
    for _ in range(20000):
        assert p >= previous - 1e-12, "progress must never run backward"
        previous = p
        if playing:
            p += dt * rate
            if p >= 1:
                p = 1.0
                hold += dt
                clamped_time += dt
                if hold >= hold_seconds:
                    p, hold = 0.0, 0.0
                    playing = True
                    break
            else:
                hold = 0.0
    else:
        raise AssertionError("loop never completed")
    assert previous == 1.0, "cycle must reach the present-day endpoint"
    assert 1.75 <= clamped_time <= 1.75 + dt, clamped_time
    assert p == 0.0, "cycle must reset to the beginning"
    assert playing, "no permanent pause at p=1"


def test_auto_loop_hold_duration():
    dt, rate, hold_seconds = 0.016, 0.045, 1.75
    p, hold = 0.0, 0.0
    held_time = 0.0
    while True:
        p += dt * rate
        if p >= 1:
            p = 1.0
            hold += dt
            held_time += dt
            if hold >= hold_seconds:
                break
        if held_time > 10:
            raise AssertionError("loop never reset")
    assert 1.75 <= held_time <= 1.75 + dt, held_time


def test_loop_snippets_present():
    js = JS_PATH.read_text()
    assert "endHoldElapsed >= state.endHoldSeconds" in js
    assert "resetAnimation();" in js


def test_methodology_documents_emphasis_only_shell():
    text = (REPO / "simulation" / "METHODOLOGY.md").read_text()
    flat = " ".join(text.split())
    assert "shell controls emphasis only" in flat
    assert "aVisual" in flat
