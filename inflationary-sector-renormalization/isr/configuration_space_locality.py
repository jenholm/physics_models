"""Configuration-space locality diagnostics for ISR.

This module tests whether sectors that are locally adjacent in initial conditions
share correlated effective physics. It does NOT assert Bell-style local hidden variables.

Configuration-space locality is used only as a constraint/prior on measure construction.

Metrics
-------
continuity_success  : near + same basin + small theta distance
basin_exception     : near + different basin  (expected — locality breaks across vacua)
locality_failure    : near + same basin + large theta distance (genuine violation)
"""

import numpy as np
from typing import Optional


def field_distance(x_i: dict, x_j: dict, key: str = "phi") -> float:
    """Distance in field coordinate space."""
    return float(abs(x_i[key] - x_j[key]))


def ancestry_distance(x_i: dict, x_j: dict) -> int:
    """Graph distance through parent sectors (stub: exact if parent info available)."""
    return int(abs(x_i.get("N", 0) - x_j.get("N", 0)))


def effective_physics_distance(theta_i: dict, theta_j: dict) -> float:
    """Distance between effective physics vectors theta."""
    keys = set(theta_i.keys()) & set(theta_j.keys())
    if not keys:
        return 0.0
    vals_i = np.array([theta_i[k] for k in keys], dtype=float)
    vals_j = np.array([theta_j[k] for k in keys], dtype=float)
    return float(np.linalg.norm(vals_i - vals_j))


THETA_EPS = 0.1


def _pair_distance(si: dict, sj: dict, key: str) -> float:
    """Compute declared distance between a pair using the chosen metric."""
    if key == "basin_transition":
        return 0.0 if si["vacuum"] == sj["vacuum"] else 1.0
    return field_distance(si, sj, key=key)


def locality_diagnostics(
    sectors: list[dict],
    distance_threshold: float = 0.5,
    theta_key: str = "theta",
    distance_key: str = "phi",
) -> dict:
    """Evaluate locality continuity and basin-boundary exceptions.

    Parameters
    ----------
    distance_key : str
        Which field to use for the near/far decision.
        One of ``"phi"`` (final), ``"phi_initial"``, or ``"basin_transition"``.

    Returns
    -------
    dict with keys:
      continuity_success, basin_exception, locality_failure,
      near_same_basin_pairs, near_diff_basin_pairs,
      continuity_score, basin_exception_rate, locality_failure_rate
    """
    n = len(sectors)
    if n < 2:
        return {}

    max_pairs = min(50000, n * (n - 1) // 2)
    rng = np.random.default_rng(42)
    indices = rng.choice(n * n, max_pairs, replace=False)
    i_indices = indices // n
    j_indices = indices % n

    near_same_basin = 0
    near_diff_basin = 0
    continuity_success = 0  # near + same basin + small theta distance
    basin_exception = 0     # near + different basin
    locality_failure = 0    # near + same basin + large theta distance

    for i, j in zip(i_indices, j_indices):
        if i == j:
            continue
        si = sectors[i]
        sj = sectors[j]
        d_init = _pair_distance(si, sj, distance_key)
        d_theta = effective_physics_distance(si[theta_key], sj[theta_key])
        same_vacuum = si["vacuum"] == sj["vacuum"]

        if d_init >= distance_threshold:
            continue   # far apart — no constraint

        if same_vacuum:
            near_same_basin += 1
            if d_theta < THETA_EPS:
                continuity_success += 1
            else:
                locality_failure += 1
        else:
            near_diff_basin += 1
            basin_exception += 1

    total_near = near_same_basin + near_diff_basin
    cont_denom = continuity_success + locality_failure

    return {
        "continuity_success": int(continuity_success),
        "basin_exception": int(basin_exception),
        "locality_failure": int(locality_failure),
        "near_same_basin_pairs": int(near_same_basin),
        "near_diff_basin_pairs": int(near_diff_basin),
        "continuity_score": float(continuity_success / cont_denom) if cont_denom > 0 else 0.0,
        "basin_exception_rate": float(basin_exception / total_near) if total_near > 0 else 0.0,
        "locality_failure_rate": float(locality_failure / cont_denom) if cont_denom > 0 else 0.0,
    }
