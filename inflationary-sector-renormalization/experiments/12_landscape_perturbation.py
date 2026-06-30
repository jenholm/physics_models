"""Experiment 12: Landscape perturbation robustness.

Shift all well centers mu -> mu + 0.5 and repeat Experiments 1 and 2
at sigma in {1.5, 3.0}, 5 seeds per cell.  Verifies that ISR improvement
is not an artifact of the specific well placement.
"""

import json
import logging
import numpy as np
from pathlib import Path

from isr.measures import global_census_measure, isr_locality_measure
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata
from isr.config import load_config
from isr.landscape import InflationaryLandscape, LandscapeConfig
from isr.stochastic_dynamics import StochasticDynamics
from isr.experiment_utils import (
    build_sectors_from_trajectories, compute_distance_bundle,
    validate_basin_diversity, landscape_config_hash,
)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp12")


def _build_perturbed_landscape_config(base_cfg, shift=0.5):
    """Return a LandscapeConfig with all well centers shifted by +shift."""
    land_cfg = load_config("configs/landscapes.yaml")
    wells = land_cfg.perturbations.get("wells", [])
    shifted_wells = []
    for w in wells:
        amp, mu, sigma_w = w[0], w[1], w[2]
        shifted_wells.append([amp, mu + shift, sigma_w])
    return LandscapeConfig(
        base_type=land_cfg.base_potential.get("type", "quadratic"),
        mass_squared=land_cfg.base_potential.get("mass_squared", 0.1),
        wells=[tuple(w) for w in shifted_wells],
        bumps=[tuple(b) for b in land_cfg.perturbations.get("bumps", [])],
        field_min=land_cfg.field_range.get("min", -8.0),
        field_max=land_cfg.field_range.get("max", 8.0),
    )


def _build_theta(vacuum_id, land_cfg):
    basins = land_cfg.vacuum_assignment.get("basins", {})
    if vacuum_id in basins:
        raw = dict(basins[vacuum_id])
        return {k: v for k, v in raw.items() if isinstance(v, (int, float))}
    return {"vacuum_id": vacuum_id}


def _run_pair(sigma, seed, shift, output_dir, n_traj=2000):
    """Run global census and ISR on perturbed (shift=0.5) or original (shift=0)
    landscape.  Returns improvement_ratio = global_KL / ISR_KL."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    base_cfg = load_config("configs/base.yaml")
    land_cfg_raw = load_config("configs/landscapes.yaml")

    if shift != 0:
        lcfg = _build_perturbed_landscape_config(base_cfg, shift)
    else:
        from isr.experiment_utils import build_landscape_config
        lcfg = build_landscape_config(land_cfg_raw)

    landscape = InflationaryLandscape(lcfg)
    dynamics = StochasticDynamics(landscape, h=1.0, dt=base_cfg.simulation.get("dt", 0.1), seed=seed)

    rng = np.random.default_rng(seed)
    phi0_mean = base_cfg.observable_patch.get("phi0", 2.0)
    phi0_arr = rng.normal(phi0_mean, sigma, n_traj)
    traj = dynamics.simulate_trajectories(phi0_arr, n_efolds=base_cfg.simulation.get("n_efolds", 80))

    sectors = build_sectors_from_trajectories(traj, dynamics, land_cfg_raw)
    x0_vac = landscape.identify_basin(phi0_mean)
    x0 = {"phi": phi0_mean, "vacuum": x0_vac, "theta": _build_theta(x0_vac, land_cfg_raw)}
    distances = compute_distance_bundle(sectors, x0)

    cutoffs = compute_cutoffs([100, 250, 500, 1000, n_traj], len(sectors))

    global_analysis = cutoff_stability_analysis(
        global_census_measure, sectors, x0, distances, cutoffs,
        {"theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )
    isr_analysis = cutoff_stability_analysis(
        isr_locality_measure, sectors, x0, distances, cutoffs,
        {"x0": x0, "kernel_name": "gaussian", "ell": 1.0, "theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )

    g_kl = next((v for v in reversed(global_analysis["kl_divergences"]) if v is not None), None)
    i_kl = next((v for v in reversed(isr_analysis["kl_divergences"]) if v is not None), None)

    improvement = float(g_kl / i_kl) if (g_kl is not None and i_kl is not None and i_kl > 0) else None

    return {
        "sigma": sigma,
        "seed": seed,
        "shift": shift,
        "n_vacua": len(set(s["vacuum"] for s in sectors)),
        "global_kl": float(g_kl) if g_kl is not None else None,
        "isr_kl": float(i_kl) if i_kl is not None else None,
        "improvement_ratio": improvement,
    }


def run(output_dir: str = "outputs"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    SIGMAS = [1.5, 3.0]
    SEEDS = list(range(1, 6))
    N_TRAJ = 2000
    records = []

    for sigma in SIGMAS:
        for seed in SEEDS:
            records.append(_run_pair(sigma, seed, shift=0.5, output_dir=output_dir, n_traj=N_TRAJ))

    df = records

    with open(output_path / "landscape_perturbation_results.json", "w") as f:
        json.dump({f"perturbed_sigma{s}": r for s, r in zip(
            [f"{r['sigma']}_seed{r['seed']}" for r in df], df)}, f, indent=2)

    summary = {}
    for sigma in SIGMAS:
        ratios = [r["improvement_ratio"] for r in df if r["sigma"] == sigma and r["improvement_ratio"] is not None]
        if ratios:
            summary[f"perturbed_sigma{sigma}"] = {
                "mean": float(np.mean(ratios)),
                "std": float(np.std(ratios)),
                "min": float(min(ratios)),
                "max": float(max(ratios)),
                "n_seeds": len(ratios),
            }

    with open(output_path / "landscape_perturbation_5seed.json", "w") as f:
        json.dump(summary, f, indent=2)

    save_run_metadata(output_dir, {}, {
        "experiment": "12_landscape_perturbation",
        "sigma_values": SIGMAS,
        "seeds": SEEDS,
        "n_trajectories": N_TRAJ,
        "shift": 0.5,
    })

    logger.info("Experiment 12 complete — %d sigma×seed cells", len(df))
    return df, summary


if __name__ == "__main__":
    run()
