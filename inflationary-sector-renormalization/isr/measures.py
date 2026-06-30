"""Probabilistic measures for inflationary sector renormalization."""

import numpy as np
from collections import defaultdict, Counter
from typing import Optional
from .kernels import KERNEL_REGISTRY
from .experiment_utils import resolve_distances


def global_census_measure(sectors: list[dict], theta_key: str = "vacuum", **kwargs) -> dict:
    """Measure 1: naive global census (bad baseline)."""
    counts = Counter([s[theta_key] for s in sectors])
    total = len(sectors)
    return {k: v / total for k, v in counts.items()}


def cutoff_census_measure(sectors: list[dict], n_max: int, theta_key: str = "vacuum", **kwargs) -> dict:
    """Measure 2: cutoff-regulated census."""
    subset = sectors[:n_max]
    counts = Counter([s[theta_key] for s in subset])
    return {k: v / n_max for k, v in counts.items()}


def isr_locality_measure(
    sectors: list[dict],
    x0: dict,
    distances,
    kernel_name: str,
    ell: float,
    theta_key: str = "vacuum",
) -> dict:
    """Measure 3: locality-weighted measure.
    P_ISR(theta | x0) = sum_i K[d(x_i, x0)] * I(theta_i == theta) / sum_i K[d(x_i, x0)]
    """
    kernel_fn = KERNEL_REGISTRY[kernel_name]
    wdist = resolve_distances(distances, kernel_name)
    weights = kernel_fn(wdist, ell)
    total_weight = weights.sum()
    if total_weight < 1e-12:
        counts = Counter([s[theta_key] for s in sectors])
        total = len(sectors)
        return {k: v / total for k, v in counts.items()}
    weight_sum = defaultdict(float)
    for s, w in zip(sectors, weights):
        weight_sum[s[theta_key]] += w
    return {k: v / total_weight for k, v in weight_sum.items()}


def effective_sector_renormalization(
    sectors: list[dict],
    x0: dict,
    distances,
    kernel_name: str,
    ell: float,
    theta_key: str = "vacuum",
) -> dict:
    """Measure 4: integrate hidden sectors into effective coefficients.

    Returns per-vacuum coefficients *and* aggregate (total weighted mean
    across all vacua) for each parameter.
    """
    kernel_fn = KERNEL_REGISTRY[kernel_name]
    wdist = resolve_distances(distances, kernel_name)
    weights = kernel_fn(wdist, ell)
    total_weight = weights.sum()
    if total_weight < 1e-12:
        return {}
    theta_sums = defaultdict(lambda: defaultdict(float))
    for s, w in zip(sectors, weights):
        if s["theta"]:
            for k, v in s["theta"].items():
                theta_sums[k][s[theta_key]] += w * v
    eff = {}
    for param, vd in theta_sums.items():
        param_total = sum(vd.values())
        # per-vacuum coefficients
        for key, val in vd.items():
            eff[f"{param}_vac{key}"] = val / total_weight
        # aggregate (overall weighted mean across vacua)
        eff[f"{param}_aggregate"] = param_total / total_weight
    return eff
