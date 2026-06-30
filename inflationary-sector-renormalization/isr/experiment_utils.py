"""Shared utilities for ISR experiments: simulation setup, distance bundle, metadata."""

import hashlib
import json
import logging
import numpy as np
from pathlib import Path
from typing import Optional

from .config import load_config
from .landscape import InflationaryLandscape, LandscapeConfig
from .stochastic_dynamics import StochasticDynamics

logger = logging.getLogger("isr.exp_utils")


class DistanceBundle:
    """Container for multiple distance metrics between sectors and x0.

    Supports slicing with [:] so that cutoff_stability_analysis
    can pass DistanceBundle objects through unchanged.
    """

    def __init__(self, **arrays):
        self._arrays = arrays

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._arrays[key]
        if isinstance(key, slice):
            return DistanceBundle(**{k: v[key] for k, v in self._arrays.items()})
        if isinstance(key, int):
            return DistanceBundle(**{k: v[key] for k, v in self._arrays.items()})
        raise KeyError(f"DistanceBundle key must be str or slice, got {type(key)}")

    def __getattr__(self, name):
        if name in self._arrays:
            return self._arrays[name]
        raise AttributeError(f"DistanceBundle has no key '{name}'")

    def __len__(self):
        return len(next(iter(self._arrays.values())))

    def __iter__(self):
        return iter(self._arrays)

    def keys(self):
        return self._arrays.keys()

    def values(self):
        return self._arrays.values()

    def items(self):
        return self._arrays.items()


# Map from kernel name to the distance type it should use
DISTANCE_KEY_MAP = {
    "gaussian": "final_phi",
    "exponential": "final_phi",
    "ancestry_proxy": "ancestry",
    "graph": "ancestry",
    "causal_cone": "ancestry",
    "same_basin": "basin_transition",
}


def resolve_distances(distances, kernel_name: str) -> np.ndarray:
    """Extract the right distance array from a DistanceBundle based on kernel name."""
    if isinstance(distances, DistanceBundle):
        key = DISTANCE_KEY_MAP.get(kernel_name, "final_phi")
        return distances[key]
    return distances


def build_landscape_config(land_cfg) -> LandscapeConfig:
    return LandscapeConfig(
        base_type=land_cfg.base_potential.get("type", "quadratic"),
        mass_squared=land_cfg.base_potential.get("mass_squared", 0.1),
        wells=[tuple(w) for w in land_cfg.perturbations.get("wells", [])],
        bumps=[tuple(b) for b in land_cfg.perturbations.get("bumps", [])],
        field_min=land_cfg.field_range.get("min", -8.0),
        field_max=land_cfg.field_range.get("max", 8.0),
    )


def build_sectors_from_trajectories(traj, dynamics, land_cfg) -> list[dict]:
    sectors = []
    for i in range(len(traj["phi_final"])):
        vacuum = int(traj["basin_final"][i])
        sectors.append({
            "phi": float(traj["phi_final"][i]),
            "vacuum": vacuum,
            "N": float(traj["phi_history"].shape[1] * dynamics.dt),
            "theta": _build_theta(vacuum, land_cfg),
            "phi_initial": float(traj["phi_initial"][i]),
        })
    return sectors


def _build_theta(vacuum_id: int, land_cfg) -> dict:
    basins = land_cfg.vacuum_assignment.get("basins", {})
    if vacuum_id in basins:
        raw = dict(basins[vacuum_id])
        return {k: v for k, v in raw.items() if isinstance(v, (int, float))}
    return {"vacuum_id": vacuum_id}


def compute_distance_bundle(sectors: list[dict], x0: dict) -> DistanceBundle:
    phi0 = x0.get("phi", 0.0)
    n0 = x0.get("N", 0)
    x0_vac = x0.get("vacuum", sectors[0]["vacuum"]) if sectors else 0
    return DistanceBundle(
        initial_phi=np.array([abs(s["phi_initial"] - phi0) for s in sectors]),
        final_phi=np.array([abs(s["phi"] - phi0) for s in sectors]),
        ancestry=np.array([abs(s.get("N", 0) - n0) for s in sectors]),
        basin_transition=np.array([0 if s["vacuum"] == x0_vac else 1 for s in sectors], dtype=float),
    )


def _sample_initial_phi(base_cfg, rng, override_kwargs: Optional[dict] = None) -> np.ndarray:
    """Sample initial phi values per configuration, with optional overrides."""
    phi0_mean = base_cfg.observable_patch.get("phi0", 2.0)
    n_traj = (override_kwargs or {}).get("n_trajectories") or base_cfg.simulation.get("n_trajectories", 1000)
    ic = base_cfg.get("initial_conditions", {}) if hasattr(base_cfg, "get") else {}
    default_sigma = ic.get("sigma", 1.5) if isinstance(ic, dict) else 1.5
    sigma = (override_kwargs or {}).get("sigma") or default_sigma
    sampling = ic.get("sampling", "normal") if isinstance(ic, dict) else "normal"

    if sampling == "normal":
        return rng.normal(phi0_mean, sigma, n_traj)
    return np.full(n_traj, phi0_mean)


def validate_basin_diversity(sectors: list[dict], min_vacua: int = 2) -> dict:
    """Check that at least *min_vacua* distinct vacua appear in sectors.

    Returns a dict with keys: passed, vacua, counts, message.
    """
    from collections import Counter
    counts = Counter(s["vacuum"] for s in sectors)
    vacua = sorted(counts.keys())
    passed = len(vacua) >= min_vacua
    return {
        "passed": passed,
        "n_vacua": len(vacua),
        "vacua": vacua,
        "counts": {int(k): int(v) for k, v in counts.items()},
        "message": f"{len(vacua)} vacua: {dict(counts)} {'(PASS)' if passed else '(FAIL)'}",
    }


def build_simulation_context(
    config_dir: str = "configs",
    require_multi_basin: bool = True,
    **override_kwargs,
) -> dict:
    """Create landscape, dynamics, sectors, x0, and distance bundle from YAML configs.

    Accepts optional keyword overrides:
      sigma, seed, n_trajectories

    If *require_multi_basin* is True and fewer than 2 vacua appear,
    the function logs a warning but does not raise (experiments handle it).

    Returns a dict with keys:
      base_cfg, land_cfg, landscape, dynamics,
      sectors, x0, distances (DistanceBundle), trajectories, diversity
    """
    base_cfg = load_config(f"{config_dir}/base.yaml")
    land_cfg = load_config(f"{config_dir}/landscapes.yaml")
    sim = base_cfg.simulation

    lcfg = build_landscape_config(land_cfg)
    landscape = InflationaryLandscape(lcfg)

    phi0_mean = base_cfg.observable_patch.get("phi0", 2.0)
    seed = override_kwargs.get("seed") or sim.get("seed", 42)
    dynamics = StochasticDynamics(
        landscape,
        h=1.0,
        dt=sim.get("dt", 0.1),
        seed=seed,
    )

    rng = np.random.default_rng(seed)
    phi0_arr = _sample_initial_phi(base_cfg, rng, override_kwargs)
    traj = dynamics.simulate_trajectories(
        phi0_arr,
        n_efolds=sim.get("n_efolds", 80),
    )

    sectors = build_sectors_from_trajectories(traj, dynamics, land_cfg)
    x0_vac = landscape.identify_basin(phi0_mean)
    x0 = {"phi": phi0_mean, "vacuum": x0_vac, "theta": _build_theta(x0_vac, land_cfg)}
    distances = compute_distance_bundle(sectors, x0)
    diversity = validate_basin_diversity(sectors)

    if require_multi_basin and not diversity["passed"]:
        logger.warning("Single-basin run: %s", diversity["message"])

    return {
        "base_cfg": base_cfg,
        "land_cfg": land_cfg,
        "landscape": landscape,
        "dynamics": dynamics,
        "sectors": sectors,
        "x0": x0,
        "distances": distances,
        "trajectories": traj,
        "diversity": diversity,
    }


def compute_cutoffs(raw_cutoffs: list[int], n_sectors: int) -> list[int]:
    """Clamp cutoffs to n_sectors and warn when values are dropped."""
    clamped = [c for c in raw_cutoffs if c <= n_sectors]
    dropped = [c for c in raw_cutoffs if c > n_sectors]
    if dropped:
        logger.warning(
            "Dropped cutoffs exceeding n_sectors=%d: %s",
            n_sectors, dropped,
        )
    if not clamped:
        clamped = [n_sectors]
        logger.warning("All cutoffs dropped; defaulting to [n_sectors=%d]", n_sectors)
    return clamped


def landscape_config_hash(land_cfg) -> str:
    raw = dict(land_cfg._raw)
    return hashlib.md5(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()[:12]


def save_run_metadata(output_dir: str, ctx: dict, extra: Optional[dict] = None) -> Path:
    """Save per-experiment metadata JSON and return the path.

    Includes the experiment name (from *extra*) in the filename so that
    multiple experiments do not overwrite each other's metadata.
    """
    n_traj_override = (extra or {}).get("n_trajectories")
    extra_seed = (extra or {}).get("seed")
    meta = {
        "seed": extra_seed if extra_seed is not None else ctx["base_cfg"].simulation.get("seed", 42),
        "n_trajectories": n_traj_override or ctx["base_cfg"].simulation.get("n_trajectories", 1000),
        "n_efolds": ctx["base_cfg"].simulation.get("n_efolds", 80),
        "landscape_config_hash": landscape_config_hash(ctx["land_cfg"]),
        "phi0": ctx["x0"]["phi"],
    }
    if extra:
        meta.update(extra)
    exp_name = (extra or {}).get("experiment", "unknown")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"run_metadata_{exp_name}.json"
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    return path
