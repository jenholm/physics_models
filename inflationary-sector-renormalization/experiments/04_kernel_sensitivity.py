"""Experiment 4: Kernel sensitivity analysis."""

import json
import logging
import numpy as np
from pathlib import Path

from isr.measures import isr_locality_measure
from isr.plotting import plot_kernel_comparison_table
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp04")

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
                                                                    [100, 250, 500, 1000, 2500, 5000])
    cutoffs = compute_cutoffs(raw_cutoffs, len(sectors))

    save_run_metadata(output_dir, ctx, {
        "experiment": "04_kernel_sensitivity",
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

    results = {"evidence": {}, "diagnostic": {}}
    for kernel in ALL_KERNELS:
        kernel_type = "evidence" if kernel in EVIDENCE_KERNELS else "diagnostic"
        ell_values = kernel_ell_map.get(kernel, [0.5])
        for ell in ell_values:
            analysis = cutoff_stability_analysis(
                isr_locality_measure,
                sectors, x0, distances,
                cutoffs,
                {"x0": x0, "kernel_name": kernel, "ell": ell, "theta_key": "vacuum"},
                epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
            )
            key = f"{kernel}_ell{ell}"
            results[kernel_type][key] = {
                "kl_values": [float(v) if v is not None else 0.0 for v in analysis["kl_divergences"]],
                "wasserstein_values": [float(v) if v is not None else 0.0 for v in analysis["wasserstein_distances"]],
                "mean_kl": float(np.mean([v for v in analysis["kl_divergences"] if v is not None])) if any(v is not None for v in analysis["kl_divergences"]) else 0.0,
            }

    with open(output_path / "kernel_sensitivity_results.json", "w") as f:
        json.dump(results, f, indent=2)

    plot_kernel_comparison_table(
        results.get("evidence", {}),
        str(output_path / "kernel_sensitivity_heatmap.png"),
        metric="mean_kl",
    )

    logger.info("Experiment 04 complete — cutoffs=%s", cutoffs)
    return results


if __name__ == "__main__":
    run()
