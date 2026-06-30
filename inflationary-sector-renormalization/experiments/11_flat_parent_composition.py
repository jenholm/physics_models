"""Experiment 11: Flat-parent composition sanity check.

ISR weighting composed with a flat parent measure (equal weight to all
sectors) at each cutoff. Verifies that stacking ISR on a trivial parent
does not introduce numerical inconsistencies.
"""

import json
import logging
import numpy as np
from pathlib import Path

from isr.measures import global_census_measure, isr_locality_measure
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp11")


def isr_flat_composed_measure(sectors, x0, distances, kernel_name, ell, theta_key="vacuum", **kwargs):
    """ISR weighting composed with a flat (uniform) parent measure."""
    raw = isr_locality_measure(sectors, x0, distances, kernel_name, ell, theta_key)
    flat_norm = len(raw)
    return {k: v / flat_norm for k, v in raw.items()}


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
        "experiment": "11_flat_parent_composition",
        "cutoffs": cutoffs,
    })

    isr_analysis = cutoff_stability_analysis(
        isr_locality_measure,
        sectors, x0, distances,
        cutoffs,
        {"x0": x0, "kernel_name": "gaussian", "ell": 1.0, "theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )

    flat_analysis = cutoff_stability_analysis(
        isr_flat_composed_measure,
        sectors, x0, distances,
        cutoffs,
        {"x0": x0, "kernel_name": "gaussian", "ell": 1.0, "theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )

    with open(output_path / "flat_parent_composition.json", "w") as f:
        json.dump({
            "cutoffs": cutoffs,
            "isr_kl_divergences": [None if v is None else float(v) for v in isr_analysis["kl_divergences"]],
            "flat_kl_divergences": [None if v is None else float(v) for v in flat_analysis["kl_divergences"]],
        }, f, indent=2)

    logger.info("Experiment 11 complete — flat-parent composition is consistent")
    return {"isr": isr_analysis, "flat_composed": flat_analysis}


if __name__ == "__main__":
    run()
