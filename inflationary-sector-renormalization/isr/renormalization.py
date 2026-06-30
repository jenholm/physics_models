"""Renormalization stability tests for ISR measures."""

import math
import numpy as np
from typing import Optional
from .experiment_utils import DistanceBundle


def compute_kl_divergence(p: dict, q: dict, epsilon: float = 1e-12) -> float:
    """KL(p || q)."""
    all_keys = sorted(set(p.keys()) | set(q.keys()))
    p_sum = 0.0
    q_sum = 0.0
    pairs = []
    for k in all_keys:
        pv = p.get(k)
        if pv is None:
            pv = 0.0
        else:
            pv = float(pv)
        qv = q.get(k)
        if qv is None:
            qv = 0.0
        else:
            qv = float(qv)
        p_sum += pv
        q_sum += qv
        pairs.append((pv, qv))
    p_sum += epsilon * len(all_keys)
    q_sum += epsilon * len(all_keys)
    kl = 0.0
    for pv, qv in pairs:
        pk = (pv + epsilon) / p_sum
        qk = (qv + epsilon) / q_sum
        kl += pk * (math.log(pk) - math.log(qk))
    return float(kl)


def compute_wasserstein_distance(p: dict, q: dict) -> float:
    """1-Wasserstein distance between two discrete distributions over same label space.

    Uses union of support labels (missing labels treated as zero probability).
    """
    keys = sorted(set(p.keys()) | set(q.keys()))
    if not keys:
        return 0.0
    p_vals = np.array([float(p.get(k, 0.0)) for k in keys])
    q_vals = np.array([float(q.get(k, 0.0)) for k in keys])
    p_vals = p_vals / p_vals.sum()
    q_vals = q_vals / q_vals.sum()
    return float(np.sum(np.abs(np.cumsum(p_vals) - np.cumsum(q_vals))))


def cutoff_stability_analysis(
    measure_fn,
    sectors: list[dict],
    x0: dict,
    distances,
    cutoffs: list[int],
    measure_kwargs: dict,
    epsilon: float = 1e-10,
) -> dict:
    """Test measure stability across increasing cutoffs.

    *distances* may be a plain array or a DistanceBundle.
    Slicing [:] on a DistanceBundle returns a sliced copy.
    """
    results = {
        "cutoffs": cutoffs,
        "probabilities": [],
        "kl_divergences": [],
        "wasserstein_distances": [],
    }
    prev_dist = None
    for n in cutoffs:
        kwargs = dict(measure_kwargs)
        kwargs.setdefault("x0", x0)
        kwargs.setdefault("distances", distances[:n])
        dist = measure_fn(sectors[:n], **kwargs)
        results["probabilities"].append(dist)
        if prev_dist is not None:
            kl = compute_kl_divergence(prev_dist, dist, epsilon)
            wd = compute_wasserstein_distance(prev_dist, dist)
            results["kl_divergences"].append(kl)
            results["wasserstein_distances"].append(wd)
        else:
            results["kl_divergences"].append(None)
            results["wasserstein_distances"].append(None)
        prev_dist = dist
    return results
