"""Experiment 2: ISR locality-weighted measure and stabilization."""

import json
import logging
import numpy as np
from pathlib import Path

from isr.measures import global_census_measure, isr_locality_measure
from isr.plotting import plot_measure_vs_cutoff, plot_kl_divergence
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp02")


def run(kernel_name: str = "gaussian", ell: float = 1.0, output_dir: str = "outputs"):
    ctx = build_simulation_context()
    base_cfg = ctx["base_cfg"]
    sectors = ctx["sectors"]
    x0 = ctx["x0"]
    distances = ctx["distances"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    raw_cutoffs = base_cfg.renormalization.get("cutoffs", {}).get("n_trajectories",
                                                                   [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000])
    cutoffs = compute_cutoffs(raw_cutoffs, len(sectors))

    save_run_metadata(output_dir, ctx, {
        "experiment": "02_locality_weighted_measure",
        "kernel": kernel_name,
        "ell": ell,
        "cutoffs": cutoffs,
    })

    global_analysis = cutoff_stability_analysis(
        global_census_measure,
        sectors, x0, distances,
        cutoffs,
        {"theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )

    isr_analysis = cutoff_stability_analysis(
        isr_locality_measure,
        sectors, x0, distances,
        cutoffs,
        {
            "x0": x0,
            "kernel_name": kernel_name,
            "ell": ell,
            "theta_key": "vacuum",
        },
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )

    with open(output_path / "isr_measure_vs_cutoff.json", "w") as f:
        json.dump({
            "kernel": kernel_name,
            "ell": ell,
            "cutoffs": isr_analysis["cutoffs"],
            "probabilities": [{str(k): v for k, v in p.items()} for p in isr_analysis["probabilities"]],
            "kl_divergences": [None if v is None else float(v) for v in isr_analysis["kl_divergences"]],
            "wasserstein_distances": [None if v is None else float(v) for v in isr_analysis["wasserstein_distances"]],
        }, f, indent=2)

    plot_measure_vs_cutoff(
        isr_analysis["cutoffs"],
        isr_analysis["probabilities"],
        f"ISR {kernel_name} (ell={ell}) vs Cutoff",
        str(output_path / f"isr_measure_vs_cutoff_{kernel_name}.png"),
    )
    plot_kl_divergence(
        isr_analysis["cutoffs"],
        isr_analysis["kl_divergences"],
        f"KL Divergence to Previous Cutoff (ISR {kernel_name})",
        str(output_path / f"isr_kl_divergence_{kernel_name}.png"),
    )

    logger.info("Experiment 02 complete — kernel=%s ell=%s cutoffs=%s", kernel_name, ell, cutoffs)
    return {"global": global_analysis, "isr": isr_analysis}


if __name__ == "__main__":
    run()
