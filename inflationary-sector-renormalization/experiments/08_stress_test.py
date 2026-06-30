"""Experiment 8: Stress test — ISR vs global stability across sigma × seed grid."""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.measures import global_census_measure, isr_locality_measure, effective_sector_renormalization
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp08")

SIGMA_VALUES = [0.5, 1.0, 1.5, 2.0, 3.0]
SEEDS = list(range(1, 21))
N_TRAJ = 2000


def run(output_dir: str = "outputs"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cutoffs = compute_cutoffs([100, 250, 500, 1000, 2000], N_TRAJ)
    records = []

    for sigma in SIGMA_VALUES:
        logger.info("Stress test: sigma=%s", sigma)
        for seed in SEEDS:
            ctx = build_simulation_context(
                require_multi_basin=False,
                sigma=sigma,
                seed=seed,
                n_trajectories=N_TRAJ,
            )
            sectors = ctx["sectors"]
            x0 = ctx["x0"]
            distances = ctx["distances"]
            diversity = ctx["diversity"]

            # Global census
            global_ana = cutoff_stability_analysis(
                global_census_measure,
                sectors, x0, distances,
                cutoffs,
                {"theta_key": "vacuum"},
            )
            g_kl = next((v for v in reversed(global_ana["kl_divergences"]) if v is not None), None)
            g_wd = next((v for v in reversed(global_ana["wasserstein_distances"]) if v is not None), None)

            # ISR locality
            isr_ana = cutoff_stability_analysis(
                isr_locality_measure,
                sectors, x0, distances,
                cutoffs,
                {"x0": x0, "kernel_name": "gaussian", "ell": 1.0, "theta_key": "vacuum"},
            )
            i_kl = next((v for v in reversed(isr_ana["kl_divergences"]) if v is not None), None)
            i_wd = next((v for v in reversed(isr_ana["wasserstein_distances"]) if v is not None), None)

            eff = effective_sector_renormalization(sectors, x0, distances, "gaussian", 1.0)
            overall_alpha = eff.get("Lambda_eff_aggregate", np.nan)

            improvement = (g_kl / i_kl) if (g_kl is not None and i_kl is not None and i_kl > 0) else np.nan

            records.append({
                "sigma": sigma,
                "seed": seed,
                "n_trajectories": N_TRAJ,
                "n_vacua": diversity.get("n_vacua", 0),
                "n_sectors": len(sectors),
                "global_kl": g_kl if g_kl is not None else 999.0,
                "global_wasserstein": g_wd if g_wd is not None else 999.0,
                "isr_kl": i_kl if i_kl is not None else 999.0,
                "isr_wasserstein": i_wd if i_wd is not None else 999.0,
                "improvement_ratio": improvement,
                "overall_alpha": overall_alpha,
                "multi_basin": diversity.get("passed", False),
            })

    df = pd.DataFrame(records)
    df.to_csv(output_path / "stress_test_results.csv", index=False)

    summary = {}
    for sigma in SIGMA_VALUES:
        sub = df[df["sigma"] == sigma]
        summary[str(sigma)] = {
            "global_mean_kl": float(sub["global_kl"].mean()),
            "global_mean_wasserstein": float(sub["global_wasserstein"].mean()),
            "isr_mean_kl": float(sub["isr_kl"].mean()),
            "isr_mean_wasserstein": float(sub["isr_wasserstein"].mean()),
            "mean_improvement_ratio": float(sub["improvement_ratio"].mean()),
            "mean_alpha": float(sub["overall_alpha"].mean()),
            "multi_basin_frac": float(sub["multi_basin"].mean()),
            "mean_n_vacua": float(sub["n_vacua"].mean()),
        }

    with open(output_path / "stress_test_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    save_run_metadata(output_dir, ctx, {
        "experiment": "08_stress_test",
        "seed": None,
        "seeds": SEEDS,
        "n_trajectories": N_TRAJ,
        "sigma_values": SIGMA_VALUES,
    })

    logger.info("Experiment 08 complete — %d sigma values × %d seeds", len(SIGMA_VALUES), len(SEEDS))
    return df, summary


if __name__ == "__main__":
    run()
