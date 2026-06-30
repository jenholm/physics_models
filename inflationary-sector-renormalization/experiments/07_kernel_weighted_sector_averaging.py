"""Experiment 7: Kernel-weighted sector averaging — hidden sectors as integrated-out degrees of freedom."""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.measures import effective_sector_renormalization
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp07")


def run(output_dir: str = "outputs"):
    ctx = build_simulation_context()
    base_cfg = ctx["base_cfg"]
    sectors = ctx["sectors"]
    x0 = ctx["x0"]
    distances = ctx["distances"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    kernel = base_cfg.kernels.get("gaussian", {})
    ell_values = kernel.get("ell_values", [0.5, 1.0, 2.0])
    raw_cutoffs = base_cfg.renormalization.get("cutoffs", {}).get("n_trajectories",
                                                                   [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000])
    cutoffs = compute_cutoffs(raw_cutoffs, len(sectors))

    save_run_metadata(output_dir, ctx, {
        "experiment": "07_kernel_weighted_sector_averaging",
        "kernel": "gaussian",
        "ell_values": ell_values,
        "cutoffs": cutoffs,
    })

    results = {}
    for ell in ell_values:
        eff_history = []
        for n in cutoffs:
            eff = effective_sector_renormalization(
                sectors[:n], x0, distances[:n],
                kernel_name="gaussian", ell=ell, theta_key="vacuum",
            )
            entry = dict(eff)
            entry["n_sectors"] = n
            eff_history.append(entry)
        results[f"ell_{ell}"] = eff_history

    with open(output_path / "kernel_weighted_sector_averaging.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    rows = []
    for ell_key, history in results.items():
        ell = float(ell_key.split("_")[1])
        for entry in history:
            row = {"ell": ell, "n_sectors": entry.get("n_sectors", 0)}
            for param, val in entry.items():
                if param == "n_sectors":
                    continue
                row[param] = val
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(output_path / "kernel_weighted_sector_averaging.csv", index=False)

    logger.info("Experiment 07 complete — ell_values=%s cutoffs=%s", ell_values, cutoffs)
    return results


if __name__ == "__main__":
    run()
