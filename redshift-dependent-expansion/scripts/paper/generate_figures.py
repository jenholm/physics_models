#!/usr/bin/env python3
"""Regenerate publication figures from versioned evidence tables.

Reads ONLY public CSV tables under paper/figures/generated/ (themselves
derived from versioned publication evidence) and renders the six PDFs
referenced by paper/main.tex with matplotlib. Sidecar meta.json files
record the CSV hash so figures stay bound to their data.
"""

import csv
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figures" / "generated"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(name):
    with open(FIG / name, newline="") as fh:
        return list(csv.DictReader(fh))


def cols(rows, *names):
    return [[float(r[n]) for r in rows] for n in names]


def save(name, fig):
    out = FIG / name
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out.relative_to(REPO)}")


def fig_overview():
    rows = read_csv("overview_fig1_endpoints.csv")
    z, hr, hc1, hc2 = cols(rows, "z", "H_R", "H_C1", "H_C2")
    fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax[0].plot(z, hr, label="R")
    ax[0].plot(z, hc1, label="C1")
    ax[0].plot(z, hc2, label="C2")
    ax[0].set_ylabel("H(z)")
    ax[0].legend()
    ax[0].axvspan(0, 1.8, alpha=0.1)
    ax[1].plot(z, [a - b for a, b in zip(hr, hc1)], label="R-C1")
    ax[1].plot(z, [a - b for a, b in zip(hr, hc2)], label="R-C2")
    ax[1].set_xlabel("z")
    ax[1].set_ylabel("difference")
    ax[1].legend()
    fig.tight_layout()
    save("overview_fig1_endpoints.pdf", fig)


def fig_m3():
    rows = read_csv("bridge_fig2_m3.csv")
    z, hc, hm = cols(rows, "z", "H_control", "H_m3")
    frac = [(b - a) / a for a, b in zip(hc, hm)]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(z, frac)
    ax.set_xlabel("z")
    ax.set_ylabel("(H_m3-H_control)/H_control")
    fig.tight_layout()
    save("bridge_fig2_m3.pdf", fig)


def fig_cv():
    rows = read_csv("bridge_fig3_cv.csv")
    m = [int(r["m"]) for r in rows]
    combined = [float(r["combined_constrained"]) for r in rows]
    lya = [float(r["lya_held"]) for r in rows]
    base = min(combined)
    fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax[0].plot(m, [c - base for c in combined], marker="o")
    ax[0].axhline(2.0, linestyle="--")
    ax[0].set_ylabel("held-out above min")
    ax[1].semilogy(m, lya, marker="o")
    ax[1].set_xlabel("m")
    ax[1].set_ylabel("Ly-alpha continuation")
    fig.tight_layout()
    save("bridge_fig3_cv.pdf", fig)


def fig_epsilon():
    rows = read_csv("bridge_fig4_epsilon.csv")
    e = [float(r["epsilon"]) for r in rows]
    d = [float(r["delta_chi2"]) for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(e, d, marker="o")
    ax.axhline(1.0, linestyle="--")
    ax.axhline(4.0, linestyle="--")
    ax.set_xlabel("epsilon")
    ax.set_ylabel("delta chi2")
    fig.tight_layout()
    save("bridge_fig4_epsilon.pdf", fig)


def fig_triangulation():
    rows = read_csv("bridge_fig5_triangulation.csv")
    z = [float(r["z"]) for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    for key in ("R_minus_C1", "R_minus_C2", "C1_minus_C2", "m3_on_C1"):
        ax.plot(z, [float(r[key]) for r in rows], label=key)
    ax.set_xlabel("z")
    ax.legend()
    fig.tight_layout()
    save("bridge_fig5_triangulation.pdf", fig)


def fig_sn_diagnostics():
    rows = read_csv("figure_A_sn_subset_diagnostics.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    for subset in ("ladder", "nonladder"):
        sel = [r for r in rows if r["subset"] == subset]
        if sel:
            ax.plot([float(r["z_center"]) for r in sel],
                    [float(r["mean_profiled_resid_subset_M"]) for r in sel],
                    marker=".", linestyle="none", label=subset)
    ax.set_xlabel("z")
    ax.legend()
    fig.tight_layout()
    save("figure_A_sn_subset_diagnostics.pdf", fig)


def main():
    for fn in ("overview", "m3", "cv", "epsilon", "triangulation", "sn"):
        {"overview": fig_overview, "m3": fig_m3, "cv": fig_cv,
         "epsilon": fig_epsilon, "triangulation": fig_triangulation,
         "sn": fig_sn_diagnostics}[fn]()
    for meta in sorted(FIG.glob("*.meta.json")):
        csv_name = meta.name.replace(".meta.json", ".csv")
        doc = {"csv_sha256": sha256_of(FIG / csv_name)}
        meta.write_text(__import__("json").dumps(doc, indent=1) + "\n")


if __name__ == "__main__":
    main()
