"""Locality kernels for weighting sectors."""

from typing import Union
import numpy as np


def gaussian_field_distance(d: np.ndarray, ell: float) -> np.ndarray:
    """K(d) = exp(-d^2 / 2*ell^2)"""
    return np.exp(-d**2 / (2 * ell**2))


def exponential_field_distance(d: np.ndarray, ell: float) -> np.ndarray:
    """K(d) = exp(-d / ell)"""
    return np.exp(-d / ell)


def ancestry_proxy_distance(d: np.ndarray, ell: float) -> np.ndarray:
    """K(d) = exp(-d / ell) using N-distance as a proxy for ancestry depth."""
    return np.exp(-d / ell)


def causal_cone(d: np.ndarray, ell: float) -> np.ndarray:
    """Exponential kernel on e-fold separation."""
    return np.exp(-d / ell)


def same_basin(d: np.ndarray, epsilon: float = 0.1) -> np.ndarray:
    """Binary kernel: 1 if distance < epsilon (same basin), 0 otherwise."""
    return np.where(d < epsilon, 1.0, 0.0)


KERNEL_REGISTRY = {
    "gaussian": gaussian_field_distance,
    "exponential": exponential_field_distance,
    "ancestry_proxy": ancestry_proxy_distance,
    "graph": ancestry_proxy_distance,       # backward-compat alias
    "causal_cone": causal_cone,
    "same_basin": same_basin,
}
