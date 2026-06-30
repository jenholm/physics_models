"""Experiment 5: Basin boundary test — where locality breaks.

Explicitly compares same-basin vs different-basin pairs at varying distance thresholds.
Adds theta-distance-to-x0 columns.
"""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.bell_locality import effective_physics_distance
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp05")


def run(output_dir: str = "outputs"):
    ctx = build_simulation_context()
    sectors = ctx["sectors"]
    x0 = ctx["x0"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    save_run_metadata(output_dir, ctx, {"experiment": "05_basin_boundary_test"})

    thresholds = np.linspace(0.1, 3.0, 20)
    threshold_metrics = []

    for thr in thresholds:
        pairs_inside = [s for s in sectors if abs(s["phi"] - ctx["x0"]["phi"]) <= thr]
        if len(pairs_inside) < 10:
            continue

        same_basin = [s for s in pairs_inside if s["vacuum"] == x0["vacuum"]]
        diff_basin = [s for s in pairs_inside if s["vacuum"] != x0["vacuum"]]

        def theta_distance_mean(group):
            if len(group) < 2:
                return 0.0
            dsum = 0.0
            count = 0
            max_pairs = min(2000, len(group) * (len(group) - 1) // 2)
            rng = np.random.default_rng(42)
            n = len(group)
            indices = rng.choice(n * n, max_pairs, replace=False)
            for ii, jj in zip(indices // n, indices % n):
                if ii == jj:
                    continue
                dsum += effective_physics_distance(group[ii]["theta"], group[jj]["theta"])
                count += 1
            return dsum / count if count else 0.0

        def mean_theta_to_x0(group):
            if not group:
                return 0.0
            return float(np.mean([effective_physics_distance(s["theta"], x0["theta"]) for s in group]))

        same_theta_dist = theta_distance_mean(same_basin) if same_basin else 0.0
        diff_theta_dist = theta_distance_mean(diff_basin) if diff_basin else 0.0

        threshold_metrics.append({
            "distance_threshold": float(thr),
            "n_sectors": len(pairs_inside),
            "n_same_basin": len(same_basin),
            "n_diff_basin": len(diff_basin),
            "same_basin_theta_distance": same_theta_dist,
            "diff_basin_theta_distance": diff_theta_dist,
            "same_basin_theta_to_x0": mean_theta_to_x0(same_basin),
            "diff_basin_theta_to_x0": mean_theta_to_x0(diff_basin),
        })

    df = pd.DataFrame(threshold_metrics)
    df.to_csv(output_path / "basin_boundary_metrics.csv", index=False)

    with open(output_path / "basin_boundary_diagnostics.json", "w") as f:
        json.dump({k: v for k, v in df.to_dict(orient="list").items()}, f, indent=2)

    logger.info("Experiment 05 complete — %d thresholds scanned", len(threshold_metrics))
    return df


if __name__ == "__main__":
    run()
