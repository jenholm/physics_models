"""Experiment 9: Ell sensitivity scan, randomized null control, convergence rate."""

import json
import logging
import numpy as np
from pathlib import Path
import pandas as pd

from isr.measures import global_census_measure, isr_locality_measure, effective_sector_renormalization
from isr.renormalization import cutoff_stability_analysis
from isr.experiment_utils import build_simulation_context, compute_cutoffs, save_run_metadata, DistanceBundle
from isr.bell_locality import locality_diagnostics
from isr.kernels import KERNEL_REGISTRY

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("exp09")

ELL_VALUES = np.logspace(np.log10(0.05), np.log10(10.0), num=15).round(4).tolist()
EVIDENCE_KERNELS = ["gaussian", "exponential"]


def effective_sample_size(weights):
    w = np.asarray(weights, dtype=np.float64)
    if w.sum() < 1e-12:
        return 0.0
    w_norm = w / w.sum()
    return 1.0 / np.sum(w_norm ** 2)


def run_ell_sweep(sectors, x0, distances, cutoffs, kernel_name, ell_values, base_cfg):
    records = []
    base_kwargs = {"x0": x0, "theta_key": "vacuum"}
    kernel_fn = KERNEL_REGISTRY[kernel_name]
    distance_key = "final_phi"  # used by gaussian/exponential

    for ell in ell_values:
        kwargs = {**base_kwargs, "kernel_name": kernel_name, "ell": ell}
        analysis = cutoff_stability_analysis(
            isr_locality_measure, sectors, x0, distances, cutoffs,
            kwargs, epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
        )
        kl_vals = [v for v in analysis["kl_divergences"] if v is not None]
        wd_vals = [v for v in analysis["wasserstein_distances"] if v is not None]
        kl_last = kl_vals[-1] if kl_vals else None
        wd_last = wd_vals[-1] if wd_vals else None

        wdist = distances[distance_key]
        weights = kernel_fn(wdist, ell)
        n_eff = effective_sample_size(weights)

        diag = locality_diagnostics(
            sectors, distance_threshold=min(float(ell), 5.0),
            distance_key="phi",
        )
        basin_exc_rate = diag.get("basin_exception_rate", np.nan)
        continuity_score = diag.get("continuity_score", np.nan)

        eff = effective_sector_renormalization(sectors, x0, distances, kernel_name, ell)
        lambda_eff = eff.get("Lambda_eff_aggregate", np.nan)

        conv_rate = None
        conv_intercept = None
        if len(kl_vals) >= 3:
            valid_kl = np.array(kl_vals[1:])
            valid_n = np.array(cutoffs[1:1+len(valid_kl)], dtype=float)
            mask = valid_kl > 0
            if mask.sum() >= 3:
                log_n = np.log(valid_n[mask])
                log_kl = np.log(valid_kl[mask])
                slope, intercept = np.polyfit(log_n, log_kl, 1)
                conv_rate = float(slope)
                conv_intercept = float(intercept)

        records.append({
            "kernel": kernel_name,
            "ell": ell,
            "kl_last": float(kl_last) if kl_last is not None else None,
            "wasserstein_last": float(wd_last) if wd_last is not None else None,
            "n_eff": float(n_eff),
            "basin_exception_rate": float(basin_exc_rate),
            "continuity_score": float(continuity_score),
            "lambda_eff": float(lambda_eff),
            "conv_rate": conv_rate,
            "conv_intercept": conv_intercept,
        })
    return pd.DataFrame(records)


def run_randomized_null(sectors, x0, distances, cutoffs, kernel_name, ell_values, base_cfg):
    records = []
    kernel_fn = KERNEL_REGISTRY[kernel_name]
    distance_key = "final_phi"
    rng = np.random.default_rng(42)

    for ell in ell_values:
        wdist = distances[distance_key].copy()
        rng.shuffle(wdist)
        shuffled_d = DistanceBundle(
            initial_phi=rng.permutation(distances["initial_phi"]),
            final_phi=wdist,
            ancestry=rng.permutation(distances["ancestry"]),
            basin_transition=rng.permutation(distances["basin_transition"]),
        )
        kwargs = {"x0": x0, "kernel_name": kernel_name, "ell": ell, "theta_key": "vacuum"}
        analysis = cutoff_stability_analysis(
            isr_locality_measure, sectors, x0, shuffled_d, cutoffs,
            kwargs, epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
        )
        kl_vals = [v for v in analysis["kl_divergences"] if v is not None]
        kl_last = kl_vals[-1] if kl_vals else None

        weights = kernel_fn(wdist, ell)
        n_eff = effective_sample_size(weights)

        records.append({
            "kernel": kernel_name,
            "ell": ell,
            "type": "shuffled_null",
            "kl_last": float(kl_last) if kl_last is not None else None,
            "n_eff": float(n_eff),
        })
    return pd.DataFrame(records)


def run(output_dir: str = "outputs"):
    ctx = build_simulation_context()
    base_cfg = ctx["base_cfg"]
    sectors = ctx["sectors"]
    x0 = ctx["x0"]
    distances = ctx["distances"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    raw_cutoffs = base_cfg.renormalization.get("cutoffs", {}).get("n_trajectories", [])
    cutoffs = compute_cutoffs(raw_cutoffs, len(sectors))

    save_run_metadata(output_dir, ctx, {
        "experiment": "09_ell_sensitivity",
        "ell_values": ELL_VALUES,
        "cutoffs": cutoffs,
    })

    # Global baseline
    global_analysis = cutoff_stability_analysis(
        global_census_measure, sectors, x0, distances, cutoffs,
        {"theta_key": "vacuum"},
        epsilon=base_cfg.metrics.get("kl_epsilon", 1e-12),
    )
    g_kl_vals = [v for v in global_analysis["kl_divergences"] if v is not None]
    g_wd_vals = [v for v in global_analysis["wasserstein_distances"] if v is not None]
    global_kl_last = g_kl_vals[-1] if g_kl_vals else None
    global_wd_last = g_wd_vals[-1] if g_wd_vals else None

    # Ell sweep over evidence kernels
    all_dfs = []
    for kernel_name in EVIDENCE_KERNELS:
        logger.info("Ell sweep: kernel=%s", kernel_name)
        df = run_ell_sweep(sectors, x0, distances, cutoffs, kernel_name, ELL_VALUES, base_cfg)
        all_dfs.append(df)

    # Randomized null control (gaussian only, subset of ell values)
    null_ells = [e for e in ELL_VALUES if e >= 0.1]
    logger.info("Null control: gaussian kernel, %d ell values", len(null_ells))
    df_null = run_randomized_null(sectors, x0, distances, cutoffs, "gaussian", null_ells, base_cfg)
    all_dfs.append(df_null)

    # Combine and save
    result = pd.concat(all_dfs, ignore_index=True)
    result.to_csv(output_path / "ell_sensitivity_results.csv", index=False)

    # Convergence rate for global census
    global_slope = None
    if len(g_kl_vals) >= 3:
        valid_kl = np.array(g_kl_vals[1:])
        valid_n = np.array(cutoffs[1:1+len(valid_kl)], dtype=float)
        mask = valid_kl > 0
        if mask.sum() >= 3:
            log_n = np.log(valid_n[mask])
            log_kl = np.log(valid_kl[mask])
            global_slope, _ = np.polyfit(log_n, log_kl, 1)

    summary = {
        "n_trajectories": len(sectors),
        "n_vacua": ctx["diversity"]["n_vacua"],
        "global_kl_last": float(global_kl_last) if global_kl_last is not None else None,
        "global_wasserstein_last": float(global_wd_last) if global_wd_last is not None else None,
        "global_conv_rate": float(global_slope) if global_slope is not None else None,
        "ell_values": ELL_VALUES,
        "evidence_kernels": EVIDENCE_KERNELS,
    }

    with open(output_path / "ell_sensitivity_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("Experiment 09 complete — %d ell values, %d kernels, null control",
                len(ELL_VALUES), len(EVIDENCE_KERNELS))
    return result, summary


if __name__ == "__main__":
    run()
