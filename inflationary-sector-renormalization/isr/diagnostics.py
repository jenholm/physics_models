"""Diagnostic utilities for ISR analysis."""

import numpy as np
from collections import defaultdict


def coefficient_drift(theta_history: list[dict]) -> dict:
    """Track drift of effective parameters over cutoffs."""
    if len(theta_history) < 2:
        return {}
    params = set()
    for d in theta_history:
        params.update(d.keys())
    drift = {}
    for param in params:
        vals = [d.get(param, np.nan) for d in theta_history]
        diffs = np.abs(np.diff(vals))
        drift[param] = {
            "mean_drift": float(np.nanmean(diffs)),
            "max_drift": float(np.nanmax(diffs)),
            "std_drift": float(np.nanstd(diffs)),
        }
    return drift


def basin_boundary_instability(sectors: list[dict], distances: np.ndarray) -> dict:
    """Score instability near basin boundaries."""
    boundary_sectors = [
        i for i, s in enumerate(sectors) if s["vacuum"] != sectors[0]["vacuum"]
    ]
    if not boundary_sectors:
        return {"instability_score": 0.0}
    # Distance of boundary sectors to patch
    patch_dist = distances[0]
    boundary_dists = distances[boundary_sectors]
    return {
        "instability_score": float(np.mean(boundary_dists)),
        "n_boundary_sectors": len(boundary_sectors),
        "mean_boundary_distance": float(np.mean(boundary_dists)),
    }
