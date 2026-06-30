"""Read outputs/ and generate all paper figures in paper/figures/."""

import json, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from isr.config import load_config
from isr.landscape import InflationaryLandscape, LandscapeConfig
from isr.experiment_utils import build_landscape_config

OUTPUTS = os.path.join(os.path.dirname(__file__), "..", "outputs")
FIGURES = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIGURES, exist_ok=True)


def load_json(name):
    p = os.path.join(OUTPUTS, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def load_csv(name):
    p = os.path.join(OUTPUTS, name)
    if os.path.exists(p):
        return pd.read_csv(p)
    return None


# ─── Fig 1: landscape basins ──────────────────────────────────────
def fig_landscape_basins():
    lc = load_config(os.path.join(os.path.dirname(__file__), "..", "configs", "landscapes.yaml"))
    bc = load_config(os.path.join(os.path.dirname(__file__), "..", "configs", "base.yaml"))
    lcfg = build_landscape_config(lc)
    land = InflationaryLandscape(lcfg)
    phi0 = bc.observable_patch.get("phi0", 2.0)
    x0_vac = land.identify_basin(phi0)

    phi_grid = np.linspace(land.phi_grid[0], land.phi_grid[-1], 1000)
    V = [land.potential(p) for p in phi_grid]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(phi_grid, V, "k-", linewidth=1.2)
    # Mark well centers
    colors = plt.cm.tab10(np.linspace(0, 1, len(lcfg.wells)))
    for i, (name, mu, V0) in enumerate(lcfg.wells):
        ax.axvline(mu, color=colors[i], linestyle="--", alpha=0.5)
        ax.scatter([mu], [land.potential(mu)], color=colors[i], s=40, zorder=5)
        label = f"Vacuum {i}" + (" (x0)" if i == x0_vac else "")
        ax.text(mu, land.potential(mu) - 0.05, label, fontsize=8,
                ha="center", va="top", rotation=45, color=colors[i])
    # Mark x0
    ax.axvline(phi0, color="red", linestyle=":", alpha=0.8, label=f"$\\phi_0 = {phi0}$")
    ax.set_xlabel("$\\phi$")
    ax.set_ylabel("$V(\\phi)$")
    ax.set_title("Stochastic Toy Landscape with Vacuum Basins")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_01_landscape_basins.png"), dpi=150)
    plt.close(fig)
    print("  fig_01_landscape_basins.png")


# ─── Fig 2: global vs ISR distribution ────────────────────────────
def fig_global_vs_isr_distribution():
    global_json = load_json("global_measure_vs_cutoff.json")
    isr_json = load_json("isr_measure_vs_cutoff.json")
    if global_json is None or isr_json is None:
        print("  SKIP fig_02: missing JSON data")
        return

    final_global = global_json["probabilities"][-1] if global_json["probabilities"] else {}
    final_isr = isr_json["probabilities"][-1] if isr_json["probabilities"] else {}
    cutoff = global_json["cutoffs"][-1] if "cutoffs" in global_json else "final"

    vacua = sorted(set(final_global.keys()) | set(final_isr.keys()))
    x = np.arange(len(vacua))
    w = 0.3
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - w / 2, [final_global.get(v, 0) for v in vacua], w, label="Global census", alpha=0.8)
    ax.bar(x + w / 2, [final_isr.get(v, 0) for v in vacua], w, label="ISR Gaussian $\\ell=1$", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Vacuum {v}" for v in vacua])
    ax.set_ylabel("Probability")
    ax.set_title(f"Probability Distribution at $N = {cutoff}$ sectors")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_02_global_vs_isr_distribution.png"), dpi=150)
    plt.close(fig)
    print("  fig_02_global_vs_isr_distribution.png")


# ─── Fig 3: KL drift ──────────────────────────────────────────────
def fig_kl_drift():
    # Build from kernel_comparison_table to get both global and ISR
    comp = load_csv("kernel_comparison_table.csv")
    if comp is None:
        print("  SKIP fig_03: no kernel_comparison_table.csv")
        return

    # Global baseline
    global_row = comp[comp["measure"] == "global_census"]
    # ISR gaussian ell=1
    isr_row = comp[(comp["kernel"] == "gaussian") & (comp["ell"] == 1.0) & (comp["measure"] == "ISR")]

    labels = []
    kl_vals = []
    wd_vals = []
    colors = []
    if not global_row.empty:
        labels.append("Global census")
        kl_vals.append(global_row["kl_last"].values[0])
        wd_vals.append(global_row["wasserstein_last"].values[0])
        colors.append("#1f77b4")
    if not isr_row.empty:
        labels.append("ISR Gaussian $\\ell=1$")
        kl_vals.append(isr_row["kl_last"].values[0])
        wd_vals.append(isr_row["wasserstein_last"].values[0])
        colors.append("#ff7f0e")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
    ax1.bar(labels, kl_vals, color=colors, alpha=0.8)
    ax1.set_ylabel("KL divergence to previous cutoff")
    ax1.set_title("Cutoff Stability (KL)")
    ax1.tick_params(axis="x", rotation=15)

    ax2.bar(labels, wd_vals, color=colors, alpha=0.8)
    ax2.set_ylabel("Wasserstein distance")
    ax2.set_title("Cutoff Stability (Wasserstein)")
    ax2.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_03_kl_drift_global_vs_isr.png"), dpi=150)
    plt.close(fig)
    print("  fig_03_kl_drift_global_vs_isr.png")


# ─── Fig 4: kernel sensitivity ────────────────────────────────────
def fig_kernel_sensitivity():
    sens = load_json("kernel_sensitivity_results.json")
    if sens is None:
        print("  SKIP fig_04: no kernel_sensitivity_results.json")
        return
    evidence = sens.get("evidence", {})
    diagnostic = sens.get("diagnostic", {})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    for ax, group, title in [(ax1, evidence, "Evidence kernels"),
                              (ax2, diagnostic, "Diagnostic-only kernels")]:
        keys = list(group.keys())
        vals = [group[k].get("mean_kl", 1e-10) for k in keys]
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(keys)))
        ax.bar(keys, vals, color=colors, alpha=0.8)
        ax.set_ylabel("Mean KL drift")
        ax.set_yscale("log")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        ax.axhline(0.000358, color="black", linestyle=":", alpha=0.5,
                   label=f"global ({0.000358:.2e})")
        if title == "Evidence kernels":
            ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_04_kernel_sensitivity.png"), dpi=150)
    plt.close(fig)
    print("  fig_04_kernel_sensitivity.png")


# ─── Fig 5: basin exception rate ──────────────────────────────────
def fig_basin_exception():
    bell = load_json("bell_locality_diagnostics.json")
    if bell is None:
        print("  SKIP fig_05: no bell_locality_diagnostics.json")
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    markers = {"phi": "o-", "phi_initial": "s--", "basin_transition": "d:"}
    for dkey in ["phi", "phi_initial", "basin_transition"]:
        data = bell.get(dkey, {})
        thresholds = []
        rates = []
        for k in sorted(data.keys()):
            thr = float(k.split("_")[1])
            thresholds.append(thr)
            rates.append(data[k]["basin_exception_rate"])
        ax.plot(thresholds, rates, markers.get(dkey, "o-"),
                label=dkey.replace("_", " "), alpha=0.8)
    ax.axhline(0.5, color="gray", linestyle=":", alpha=0.5, label="50% threshold")
    ax.set_xlabel("Distance threshold")
    ax.set_ylabel("Basin exception rate")
    ax.set_title("Configuration-Space Locality Basin-Boundary Exceptions")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_05_basin_exception_rate.png"), dpi=150)
    plt.close(fig)
    print("  fig_05_basin_exception_rate.png")


# ─── Fig 6: kernel-weighted sector averaging ──────────────────────
def fig_effective_coefficient_flow():
    wc = load_csv("wilson_coefficients.csv")
    if wc is None:
        print("  SKIP fig_06: no wilson_coefficients.csv")
        return

    ells = sorted(wc["ell"].unique())
    aggregate_params = [c for c in wc.columns
                        if "aggregate" in c and c not in ("ell", "n_sectors")]
    # Only plot the aggregate coefficients for clarity
    for suffix, ylabel, filename in [
        ("_aggregate", "Effective coefficient value", "fig_06_effective_coefficient_flow.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 4))
        markers = ["o-", "s--", "d:", "^-."]
        for i, param in enumerate(aggregate_params):
            vals = []
            for ell in ells:
                sub = wc[(wc["ell"] == ell) & (wc["n_sectors"] == wc["n_sectors"].max())]
                if not sub.empty and param in sub.columns:
                    vals.append(sub[param].values[0])
                else:
                    vals.append(np.nan)
            label = param.replace("_", " ").replace(" aggregate", "").title()
            ax.plot(ells, vals, markers[i % len(markers)], label=label, alpha=0.8)
        ax.set_xlabel("Kernel scale $\\ell$")
        ax.set_ylabel(ylabel)
        ax.set_title("Kernel-Weighted Sector Averaging (aggregate)")
        ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.0, 0.5))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(FIGURES, filename), dpi=150)
        plt.close(fig)
        print(f"  {filename}")


# ─── Fig 7: stress improvement ────────────────────────────────────
def fig_stress_improvement():
    df = load_csv("stress_test_results.csv")
    if df is None:
        print("  SKIP fig_07: no stress_test_results.csv")
        return

    sigmas = sorted(df["sigma"].unique())

    # Full-range figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    for ax, data_filter, title in [
        (ax1, df, "Full range"),
        (ax2, df[df["improvement_ratio"] < 20], "Evidence region (ratio < 20)"),
    ]:
        positions = []
        labels = []
        for i, s in enumerate(sigmas):
            sub = data_filter[data_filter["sigma"] == s]
            ratio = sub["improvement_ratio"].dropna()
            pos = i + 1
            positions.append(pos)
            labels.append(str(s))
            if len(ratio) > 0:
                bp = ax.boxplot(ratio.values, positions=[pos], widths=0.5,
                                patch_artist=True,
                                boxprops=dict(facecolor="lightblue", alpha=0.6),
                                medianprops=dict(color="blue"))
                ax.scatter(np.full_like(ratio, pos), ratio, alpha=0.5,
                           color="navy", s=20)
        ax.axhline(1.0, color="red", linestyle="--", alpha=0.7,
                   label="ISR = Global (ratio=1)")
        ax.set_xticks(positions)
        ax.set_xticklabels(labels)
        ax.set_xlabel("$\\sigma$")
        ax.set_ylabel("Improvement ratio (global$/$ISR)")
        ax.set_title(title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    fig.suptitle("ISR Stability Improvement Over Global Census", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_07_stress_improvement_by_sigma.png"), dpi=150)
    plt.close(fig)
    print("  fig_07_stress_improvement_by_sigma.png")


# ─── Fig 8: failure cases sigma=3.0 ───────────────────────────────
def fig_failure_cases_sigma3():
    df = load_csv("stress_test_results.csv")
    if df is None:
        print("  SKIP fig_08: no stress_test_results.csv")
        return
    s3 = df[df["sigma"] == 3.0].sort_values("isr_kl", ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(s3))
    w = 0.3
    ax.bar(x - w / 2, s3["global_kl"].values, w, label="Global KL", alpha=0.8)
    ax.bar(x + w / 2, s3["isr_kl"].values, w, label="ISR KL", alpha=0.8)
    for i in range(len(s3)):
        if s3["improvement_ratio"].iloc[i] < 1.0:
            ax.annotate("failure", (i, s3["isr_kl"].iloc[i]),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=7, color="red")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed={s}" for s in s3["seed"].values], rotation=45)
    ax.set_ylabel("KL divergence")
    ax.set_title("$\\sigma = 3.0$: Global vs ISR KL by Seed")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_08_failure_cases_sigma3.png"), dpi=150)
    plt.close(fig)
    print("  fig_08_failure_cases_sigma3.png")


# ─── Fig 9: sector scatter ────────────────────────────────────────
def fig_sector_scatter():
    # Rebuild from context
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from isr.experiment_utils import build_simulation_context
    ctx = build_simulation_context(n_trajectories=2000)
    sectors = ctx["sectors"]
    phi_init = np.array([s["phi_initial"] for s in sectors])
    phi_final = np.array([s["phi"] for s in sectors])
    vacua = np.array([s["vacuum"] for s in sectors])

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, len(set(vacua))))
    for v in sorted(set(vacua)):
        mask = vacua == v
        ax.scatter(phi_init[mask], phi_final[mask], c=[colors[v]],
                   label=f"Vacuum {v}", alpha=0.5, s=5)
    ax.set_xlabel("$\\phi_{\\rm initial}$")
    ax.set_ylabel("$\\phi_{\\rm final}$")
    ax.set_title("Sector Scatter: Initial vs Final Field Value ($N=2000$)")
    ax.legend(markerscale=3, fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_09_sector_scatter_phi_initial_phi_final.png"), dpi=150)
    plt.close(fig)
    print("  fig_09_sector_scatter_phi_initial_phi_final.png")


# ─── Fig 10: cutoff evolution ─────────────────────────────────────
def fig_cutoff_evolution():
    global_json = load_json("global_measure_vs_cutoff.json")
    if global_json is None:
        print("  SKIP fig_10: no global_measure_vs_cutoff.json")
        return
    cutoffs = global_json.get("cutoffs", [])
    probs = global_json.get("probabilities", [])
    if not cutoffs or not probs:
        print("  SKIP fig_10: empty data")
        return
    vacua = sorted({k for p in probs for k in p.keys()})
    fig, ax = plt.subplots(figsize=(8, 4))
    bottom = np.zeros(len(cutoffs))
    colors = plt.cm.tab10(np.linspace(0, 1, len(vacua)))
    for i, v in enumerate(vacua):
        vals = np.array([p.get(v, 0) for p in probs])
        ax.bar(range(len(cutoffs)), vals, bottom=bottom, label=f"Vacuum {v}",
               color=colors[i], alpha=0.8)
        bottom += vals
    ax.set_xticks(range(len(cutoffs)))
    ax.set_xticklabels([str(c) for c in cutoffs], rotation=45)
    ax.set_xlabel("Cutoff $N$ (number of sectors)")
    ax.set_ylabel("Probability")
    ax.set_title("Global Census Distribution vs Cutoff")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_10_cutoff_distribution_evolution.png"), dpi=150)
    plt.close(fig)
    print("  fig_10_cutoff_distribution_evolution.png")


# ─── Fig 11: ell sensitivity — KL vs ell ───────────────────────────
def fig_ell_sensitivity_kl():
    df = load_csv("ell_sensitivity_results.csv")
    if df is None:
        print("  SKIP fig_11: no ell_sensitivity_results.csv")
        return
    isr = df[df["type"].isna()]
    null = df[df["type"] == "shuffled_null"]
    global_kl = load_json("ell_sensitivity_summary.json")
    gkl = global_kl.get("global_kl_last", None) if global_kl else None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    for ax, metric, ylabel in [
        (ax1, "kl_last", "KL drift (final)"),
        (ax2, "wasserstein_last", "Wasserstein distance (final)"),
    ]:
        for kernel in ["gaussian", "exponential"]:
            sub = isr[isr["kernel"] == kernel].sort_values("ell")
            ax.plot(sub["ell"], sub[metric], "o-", label=kernel, alpha=0.8)
        # Null control
        if not null.empty:
            nsub = null.sort_values("ell")
            ax.plot(nsub["ell"], nsub.get(metric, nsub["kl_last"]),
                    "s--", label="shuffled null", color="gray", alpha=0.6)
        if gkl is not None and metric == "kl_last":
            ax.axhline(gkl, color="black", linestyle=":", alpha=0.5, label="global census")
        ax.set_xlabel("Kernel scale $\\ell$")
        ax.set_ylabel(ylabel)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    fig.suptitle("Ell Sensitivity: Cutoff Stability vs Kernel Scale", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_11_ell_sensitivity_kl.png"), dpi=150)
    plt.close(fig)
    print("  fig_11_ell_sensitivity_kl.png")


# ─── Fig 12: ell sensitivity — N_eff and basin exception ───────────
def fig_ell_sensitivity_neff():
    df = load_csv("ell_sensitivity_results.csv")
    if df is None:
        print("  SKIP fig_12: no ell_sensitivity_results.csv")
        return
    isr = df[df["type"].isna()]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    # N_eff
    for kernel in ["gaussian", "exponential"]:
        sub = isr[isr["kernel"] == kernel].sort_values("ell")
        ax1.plot(sub["ell"], sub["n_eff"], "o-", label=kernel, alpha=0.8)
    ax1.axhline(10000, color="black", linestyle=":", alpha=0.5, label="total sectors")
    ax1.set_xlabel("Kernel scale $\\ell$")
    ax1.set_ylabel("Effective sample size $N_{\\rm eff}$")
    ax1.set_xscale("log")
    ax1.legend(fontsize=7)
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Effective Sample Size")

    # Basin exception rate
    for kernel in ["gaussian", "exponential"]:
        sub = isr[isr["kernel"] == kernel].sort_values("ell")
        ax2.plot(sub["ell"], sub["basin_exception_rate"], "o-", label=kernel, alpha=0.8)
    ax2.set_xlabel("Kernel scale $\\ell$")
    ax2.set_ylabel("Basin exception rate")
    ax2.set_xscale("log")
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)
    ax2.set_title("Basin-Boundary Exceptions")

    fig.suptitle("Ell Sensitivity: Effective Sample Size and Basin Exceptions", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_12_ell_sensitivity_neff.png"), dpi=150)
    plt.close(fig)
    print("  fig_12_ell_sensitivity_neff.png")


# ─── Fig 13: sigma×ell boundary heatmap ────────────────────────────
def fig_sigma_ell_boundary():
    df = load_csv("sigma_ell_boundary_results.csv")
    if df is None:
        print("  SKIP fig_13: no sigma_ell_boundary_results.csv")
        return
    summary = df.groupby(["sigma", "ell"]).agg(
        mean_improvement=("improvement_ratio", "mean"),
        win_rate=("isr_wins", "mean"),
    ).reset_index()

    # Filter to non-degenerate columns only (ℓ ≥ 0.50)
    summary = summary[summary["ell"] >= 0.50].copy()

    for metric, label in [("mean_improvement", "Mean improvement ratio"),
                          ("win_rate", "ISR win rate")]:
        fig, ax = plt.subplots(figsize=(7, 4))
        pivot = summary.pivot(index="sigma", columns="ell", values=metric)
        norm = None
        if metric == "mean_improvement":
            arr = pivot.values[~np.isnan(pivot.values)]
            vmin = max(arr.min(), 1e-10)  # ensure strictly positive
            vmax = arr.max()
            norm = LogNorm(vmin=vmin, vmax=vmax)
        cmap = plt.cm.RdYlGn.copy()
        im = ax.imshow(pivot.values, aspect="auto", cmap=cmap, origin="lower",
                       norm=norm)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"{c:.2f}" for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([f"{r:.1f}" for r in pivot.index])
        ax.set_xlabel("Kernel scale $\\ell$")
        ax.set_ylabel("Initial-condition spread $\\sigma$")
        ax.set_title(f"Sigma×Ell Boundary: {label}")
        cbar = fig.colorbar(im, ax=ax)
        if metric == "mean_improvement":
            cbar.set_label("Improvement ratio (log scale)")
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                if np.isnan(val):
                    continue
                txt = f"{val:.2f}" if metric == "mean_improvement" else f"{val:.0%}"
                rgba = im.cmap(im.norm(val))
                luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                color = "black" if luminance > 0.5 else "white"
                ax.text(j, i, txt, ha="center", va="center",
                        color=color, fontsize=7)
        fig.tight_layout()
        fname = f"fig_13_sigma_ell_{metric}.png"
        fig.savefig(os.path.join(FIGURES, fname), dpi=150)
        plt.close(fig)
        print(f"  {fname}")


if __name__ == "__main__":
    print("Generating figures...")
    fig_landscape_basins()
    fig_global_vs_isr_distribution()
    fig_kl_drift()
    fig_kernel_sensitivity()
    fig_basin_exception()
    fig_effective_coefficient_flow()
    fig_stress_improvement()
    fig_failure_cases_sigma3()
    fig_sector_scatter()
    fig_cutoff_evolution()
    fig_ell_sensitivity_kl()
    fig_ell_sensitivity_neff()
    fig_sigma_ell_boundary()
    print("All figures generated.")
