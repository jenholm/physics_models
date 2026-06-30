"""Experiment 10: Sigma × ell failure boundary — 2D grid stress test."""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.measures import global_census_measure, isr_locality_measure, effective_sector_renormalization
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata
from isr.bell_locality import locality_diagnostics

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp10")

SIGMA_VALUES = [0.5, 1.0, 1.5, 2.0, 3.0]
ELL_VALUES = [0.1, 0.25, 0.5, 1.0, 2.0]
SEEDS = list(range(1, 6))
N_TRAJ = 2000


def run(output_dir: str = "outputs"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cutoffs = compute_cutoffs([100, 250, 500, 1000, 2000], N_TRAJ)
    records = []

    for sigma in SIGMA_VALUES:
        for ell in ELL_VALUES:
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

                global_ana = cutoff_stability_analysis(
                    global_census_measure, sectors, x0, distances, cutoffs,
                    {"theta_key": "vacuum"},
                )
                g_kl = next((v for v in reversed(global_ana["kl_divergences"]) if v is not None), None)

                isr_ana = cutoff_stability_analysis(
                    isr_locality_measure, sectors, x0, distances, cutoffs,
                    {"x0": x0, "kernel_name": "gaussian", "ell": ell, "theta_key": "vacuum"},
                )
                i_kl = next((v for v in reversed(isr_ana["kl_divergences"]) if v is not None), None)

                improvement = (g_kl / i_kl) if (g_kl is not None and i_kl is not None and i_kl > 0) else np.nan
                isr_wins = bool(improvement > 1.0) if not np.isnan(improvement) else False

                eff = effective_sector_renormalization(sectors, x0, distances, "gaussian", ell)
                lambda_eff = eff.get("Lambda_eff_aggregate", np.nan)

                diag = locality_diagnostics(
                    sectors, distance_threshold=min(float(ell), 5.0),
                    distance_key="phi",
                )
                basin_exc_rate = diag.get("basin_exception_rate", np.nan)

                records.append({
                    "sigma": sigma,
                    "ell": ell,
                    "seed": seed,
                    "n_trajectories": N_TRAJ,
                    "n_vacua": diversity.get("n_vacua", 0),
                    "n_sectors": len(sectors),
                    "global_kl": float(g_kl) if g_kl is not None else None,
                    "isr_kl": float(i_kl) if i_kl is not None else None,
                    "improvement_ratio": float(improvement) if not np.isnan(improvement) else None,
                    "isr_wins": isr_wins,
                    "lambda_eff": float(lambda_eff) if not np.isnan(lambda_eff) else None,
                    "basin_exception_rate": float(basin_exc_rate) if not np.isnan(basin_exc_rate) else None,
                    "multi_basin": diversity.get("passed", False),
                })

    df = pd.DataFrame(records)
    df.to_csv(output_path / "sigma_ell_boundary_results.csv", index=False)

    summary = {}
    for sigma in SIGMA_VALUES:
        for ell in ELL_VALUES:
            sub = df[(df["sigma"] == sigma) & (df["ell"] == ell)]
            key = f"sigma={sigma}_ell={ell}"
            wins = sub["isr_wins"].sum()
            total = len(sub)
            summary[key] = {
                "sigma": sigma,
                "ell": ell,
                "mean_global_kl": float(sub["global_kl"].mean()),
                "mean_isr_kl": float(sub["isr_kl"].mean()),
                "mean_improvement": float(sub["improvement_ratio"].mean()),
                "isr_wins": int(wins),
                "total": total,
                "win_rate": float(wins / total) if total > 0 else None,
                "mean_n_vacua": float(sub["n_vacua"].mean()),
                "mean_basin_exception": float(sub["basin_exception_rate"].mean()),
                "mean_lambda_eff": float(sub["lambda_eff"].mean()),
            }

    with open(output_path / "sigma_ell_boundary_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    save_run_metadata(output_dir, ctx, {
        "experiment": "10_sigma_ell_boundary",
        "sigma_values": SIGMA_VALUES,
        "ell_values": ELL_VALUES,
        "seeds": SEEDS,
        "n_trajectories": N_TRAJ,
    })

    logger.info("Experiment 10 complete — %d sigma × %d ell × %d seeds = %d runs",
                len(SIGMA_VALUES), len(ELL_VALUES), len(SEEDS), len(df))
    return df, summary


if __name__ == "__main__":
    run()
