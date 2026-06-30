"""Experiment 1: Global census baseline — show naive counting is cutoff-sensitive."""

import json
import logging
import numpy as np
from pathlib import Path

from isr.measures import global_census_measure
from isr.plotting import plot_measure_vs_cutoff, plot_kl_divergence
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp01")


def run(output_dir: str = "outputs"):
    ctx = build_simulation_context()
    base_cfg = ctx["base_cfg"]
    sectors = ctx["sectors"]
    x0 = ctx["x0"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    raw_cutoffs = base_cfg.renormalization.get("cutoffs", {}).get("n_trajectories",
                                                                   [100, 250, 500, 1000, 2500, 5000])
    cutoffs = compute_cutoffs(raw_cutoffs, len(sectors))

    save_run_metadata(output_dir, ctx, {"experiment": "01_global_census_baseline", "cutoffs": cutoffs})

    analysis = cutoff_stability_analysis(
        global_census_measure,
        sectors, x0, ctx["distances"],
        cutoffs,
        {"theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )

    with open(output_path / "global_measure_drift.csv", "w") as f:
        f.write("cutoff,kl_divergence,wasserstein_distance\n")
        for n, kl, wd in zip(analysis["cutoffs"], analysis["kl_divergences"], analysis["wasserstein_distances"]):
            f.write(f"{n},{kl if kl is not None else ''},{wd if wd is not None else ''}\n")

    with open(output_path / "global_measure_vs_cutoff.json", "w") as f:
        json.dump({
            "cutoffs": analysis["cutoffs"],
            "probabilities": [{str(k): v for k, v in p.items()} for p in analysis["probabilities"]],
        }, f, indent=2)

    plot_measure_vs_cutoff(
        analysis["cutoffs"],
        analysis["probabilities"],
        "Global Census Measure vs Cutoff",
        str(output_path / "global_measure_vs_cutoff.png"),
    )
    plot_kl_divergence(
        analysis["cutoffs"],
        analysis["kl_divergences"],
        "KL Divergence (Global Census)",
        str(output_path / "global_kl_divergence.png"),
    )

    logger.info("Experiment 01 complete — cutoffs used: %s", cutoffs)
    return analysis


if __name__ == "__main__":
    run()
