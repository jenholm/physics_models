"""Experiment 3: Cutoff stability across increasing cutoffs (including global baseline)."""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.measures import global_census_measure, isr_locality_measure
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp03")

EVIDENCE_KERNELS = ["gaussian", "exponential"]
DIAGNOSTIC_KERNELS = ["ancestry_proxy", "same_basin"]
ALL_KERNELS = EVIDENCE_KERNELS + DIAGNOSTIC_KERNELS


def run(output_dir: str = "outputs"):
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
        "experiment": "03_cutoff_stability",
        "evidence_kernels": EVIDENCE_KERNELS,
        "diagnostic_kernels": DIAGNOSTIC_KERNELS,
        "cutoffs": cutoffs,
    })

    kernel_ell_map = {
        "gaussian": base_cfg.kernels.get("gaussian", {}).get("ell_values", [0.5]),
        "exponential": base_cfg.kernels.get("exponential", {}).get("ell_values", [0.5]),
        "ancestry_proxy": base_cfg.kernels.get("ancestry_proxy", {}).get("ell_values", [2]),
        "same_basin": [1],
    }

    summary = []

    for kernel in ALL_KERNELS:
        kernel_type = "evidence" if kernel in EVIDENCE_KERNELS else "diagnostic"
        ell_values = kernel_ell_map.get(kernel, [0.5])
        for ell in ell_values:
            analysis = cutoff_stability_analysis(
                isr_locality_measure,
                sectors, x0, distances,
                cutoffs,
                {
                    "x0": x0,
                    "kernel_name": kernel,
                    "ell": ell,
                    "theta_key": "vacuum",
                },
                epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
            )
            kl_last = next((v for v in reversed(analysis["kl_divergences"]) if v is not None), None)
            wd_last = next((v for v in reversed(analysis["wasserstein_distances"]) if v is not None), None)
            summary.append({
                "type": kernel_type,
                "kernel": kernel,
                "ell": ell,
                "measure": "ISR",
                "kl_last": kl_last if kl_last is not None else 999.0,
                "wasserstein_last": wd_last if wd_last is not None else 999.0,
                "stability": "good" if (kl_last is not None and kl_last < 0.1) else "poor",
            })

    global_analysis = cutoff_stability_analysis(
        global_census_measure,
        sectors, x0, distances,
        cutoffs,
        {"theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )
    kl_last = next((v for v in reversed(global_analysis["kl_divergences"]) if v is not None), None)
    wd_last = next((v for v in reversed(global_analysis["wasserstein_distances"]) if v is not None), None)
    summary.append({
        "type": "baseline",
        "kernel": "N/A",
        "ell": "N/A",
        "measure": "global_census",
        "kl_last": kl_last if kl_last is not None else 999.0,
        "wasserstein_last": wd_last if wd_last is not None else 999.0,
        "stability": "good" if (kl_last is not None and kl_last < 0.1) else "poor",
    })

    df = pd.DataFrame(summary)
    df.to_csv(output_path / "kernel_comparison_table.csv", index=False)

    with open(output_path / "global_cutoff_stability.json", "w") as f:
        json.dump({
            "cutoffs": global_analysis["cutoffs"],
            "kl_divergences": [None if v is None else float(v) for v in global_analysis["kl_divergences"]],
            "wasserstein_distances": [None if v is None else float(v) for v in global_analysis["wasserstein_distances"]],
        }, f, indent=2)

    logger.info("Experiment 03 complete — cutoffs=%s", cutoffs)
    return df


if __name__ == "__main__":
    run()
