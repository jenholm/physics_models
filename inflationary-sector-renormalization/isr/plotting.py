"""Plotting utilities for ISR outputs."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional


def ensure_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def plot_measure_vs_cutoff(
    cutoffs: list[int],
    probabilities: list[dict],
    title: str,
    filename: str,
    measure_label: str = "Measure",
    figsize: tuple = (8, 5),
):
    ensure_dir(filename)
    fig, ax = plt.subplots(figsize=figsize)
    # Stack probabilities by class
    classes = sorted({k for p in probabilities for k in p.keys()})
    class_arrays = {cls: [] for cls in classes}
    for p in probabilities:
        for cls in classes:
            class_arrays[cls].append(p.get(cls, 1e-12))
    bottom = np.zeros(len(cutoffs))
    for cls in classes:
        vals = np.array(class_arrays[cls])
        ax.bar(cutoffs, vals, bottom=bottom, label=str(cls), width=0.6 * np.diff(cutoffs + [cutoffs[-1] + (cutoffs[-1] - cutoffs[-2])])[0])
        bottom += vals
    ax.set_xlabel("Cutoff (number of sectors)")
    ax.set_ylabel("Probability")
    ax.set_title(title)
    ax.legend(title="Vacuum", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_ylim(0, 1.0)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_kl_divergence(
    cutoffs: list[int],
    kl_values: list[float],
    title: str,
    filename: str,
    figsize: tuple = (8, 4),
):
    ensure_dir(filename)
    fig, ax = plt.subplots(figsize=figsize)
    vals = [v if v is not None else 0.0 for v in kl_values]
    ax.plot(cutoffs, vals, marker="o", linestyle="-")
    ax.set_xlabel("Cutoff (number of sectors)")
    ax.set_ylabel("KL divergence to previous cutoff")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_kernel_comparison_table(
    results: dict,
    filename: str,
    metric: str = "mean_drift",
    figsize: tuple = (10, 4),
):
    ensure_dir(filename)
    fig, ax = plt.subplots(figsize=figsize)
    kernels = list(results.keys())
    values = [results[k].get(metric, 0.0) for k in kernels]
    ax.bar(kernels, values)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(f"Kernel Comparison ({metric})")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_stress_improvement(
    df_path: str,
    filename: str,
    figsize: tuple = (8, 5),
):
    """Bar chart of ISR improvement ratio (global_KL / ISR_KL) by sigma,
    with individual seed points overlaid."""
    import pandas as pd
    df = pd.read_csv(df_path)
    fig, ax = plt.subplots(figsize=figsize)
    sigmas = sorted(df["sigma"].unique())
    positions = []
    labels = []
    for i, s in enumerate(sigmas):
        sub = df[df["sigma"] == s]
        ratio = sub["improvement_ratio"].dropna()
        pos = i + 1
        positions.append(pos)
        labels.append(str(s))
        bp = ax.boxplot(ratio.values, positions=[pos], widths=0.5,
                        patch_artist=True,
                        boxprops=dict(facecolor="lightblue", alpha=0.6),
                        medianprops=dict(color="blue"))
        # overlay individual seeds
        ax.scatter(np.full_like(ratio, pos), ratio, alpha=0.5, color="navy", s=20)
    ax.axhline(1.0, color="red", linestyle="--", alpha=0.7, label="ISR = Global (ratio=1)")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Initial-condition spread sigma")
    ax.set_ylabel("Improvement ratio (global_KL / ISR_KL)")
    ax.set_title("ISR Stability Improvement Over Global Census")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
