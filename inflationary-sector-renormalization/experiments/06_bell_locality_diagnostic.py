"""Experiment 6: Bell locality diagnostic.

Tests whether same-ancestry sectors produce correlated effective physics
more often than arbitrary sectors at varying distance thresholds.
Now supports configurable distance_key: phi, phi_initial, basin_transition.
"""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.bell_locality import locality_diagnostics
from isr.experiment_utils import build_simulation_context, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp06")

DISTANCE_KEYS = ["phi", "phi_initial", "basin_transition"]


def run(output_dir: str = "outputs"):
    ctx = build_simulation_context()
    sectors = ctx["sectors"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    save_run_metadata(output_dir, ctx, {
        "experiment": "06_bell_locality_diagnostic",
        "distance_keys": DISTANCE_KEYS,
    })

    all_results = {}
    for dkey in DISTANCE_KEYS:
        results = {}
        for threshold in [0.1, 0.25, 0.5, 1.0, 1.5, 2.0]:
            diag = locality_diagnostics(
                sectors,
                distance_threshold=threshold,
                theta_key="theta",
                distance_key=dkey,
            )
            results[f"thr_{threshold}"] = diag
        all_results[dkey] = results

    with open(output_path / "bell_locality_diagnostics.json", "w") as f:
        json.dump(all_results, f, indent=2)

    rows = []
    for dkey, results in all_results.items():
        for thr_name, d in results.items():
            thr_val = float(thr_name.split("_")[1])
            rows.append({
                "distance_key": dkey,
                "distance_threshold": thr_val,
                "continuity_success": d.get("continuity_success", 0),
                "basin_exception": d.get("basin_exception", 0),
                "locality_failure": d.get("locality_failure", 0),
                "near_same_basin_pairs": d.get("near_same_basin_pairs", 0),
                "near_diff_basin_pairs": d.get("near_diff_basin_pairs", 0),
                "continuity_score": d.get("continuity_score", 0.0),
                "basin_exception_rate": d.get("basin_exception_rate", 0.0),
                "locality_failure_rate": d.get("locality_failure_rate", 0.0),
            })
    df = pd.DataFrame(rows)
    df.to_csv(output_path / "bell_locality_summary.csv", index=False)

    logger.info("Experiment 06 complete — distance_keys=%s", DISTANCE_KEYS)
    return df


if __name__ == "__main__":
    run()
