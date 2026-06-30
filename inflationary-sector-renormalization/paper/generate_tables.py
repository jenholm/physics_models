"""Read outputs/ and generate LaTeX tables in paper/tables/."""

import json, os, sys
import numpy as np
import pandas as pd

OUTPUTS = os.path.join(os.path.dirname(__file__), "..", "outputs")
TABLES = os.path.join(os.path.dirname(__file__), "tables")
os.makedirs(TABLES, exist_ok=True)


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


# ─── Table 1: main distribution ───────────────────────────────────
def table_main_distribution():
    global_json = load_json("global_measure_vs_cutoff.json")
    isr_json = load_json("isr_measure_vs_cutoff.json")
    if global_json is None or isr_json is None:
        print("  SKIP table_01: missing JSON data")
        return
    p_global = global_json["probabilities"][-1] if global_json["probabilities"] else {}
    p_isr = isr_json["probabilities"][-1] if isr_json["probabilities"] else {}
    vacua = sorted(set(p_global.keys()) | set(p_isr.keys()))

    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Probability distribution over vacuum basins at final cutoff $N=10000$. "
        "ISR uses a Gaussian kernel with $\\ell=1$.}",
        "  \\label{tab:main_distribution}",
        "  \\begin{tabular}{lccc}",
        "    \\toprule",
        "    Vacuum & Global census & ISR Gaussian $\\ell=1$ & Difference \\\\",
        "    \\midrule",
    ]
    for v in vacua:
        g = p_global.get(v, 0)
        i = p_isr.get(v, 0)
        diff = i - g
        lines.append(f"    {v} & {g:.6f} & {i:.6f} & {diff:+.6f} \\\\")
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    path = os.path.join(TABLES, "table_01_main_distribution.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  table_01_main_distribution.tex")


# ─── Table 2: stability metrics ───────────────────────────────────
def table_stability_metrics():
    comp = load_csv("kernel_comparison_table.csv")
    if comp is None:
        print("  SKIP table_02: no kernel_comparison_table.csv")
        return

    # global
    global_row = comp[comp["measure"] == "global_census"]
    # ISR gaussian ell=1
    isr_row = comp[(comp["kernel"] == "gaussian") & (comp["ell"] == 1.0) & (comp["measure"] == "ISR")]

    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Cutoff stability metrics for global census and ISR "
        "(Gaussian $\\ell=1$) at $N=10000$. KL and Wasserstein values measure "
        "divergence from the previous cutoff slice.}",
        "  \\label{tab:stability_metrics}",
        "  \\begin{tabular}{lcc}",
        "    \\toprule",
        "    Metric & Global census & ISR Gaussian $\\ell=1$ \\\\",
        "    \\midrule",
    ]
    if not global_row.empty and not isr_row.empty:
        g_kl = global_row["kl_last"].values[0]
        i_kl = isr_row["kl_last"].values[0]
        g_wd = global_row["wasserstein_last"].values[0]
        i_wd = isr_row["wasserstein_last"].values[0]
        lines.append(f"    Final KL drift & {g_kl:.6f} & {i_kl:.6f} \\\\")
        lines.append(f"    Final Wasserstein & {g_wd:.6f} & {i_wd:.6f} \\\\")
    stability_global = global_row["stability"].values[0] if not global_row.empty else "N/A"
    stability_isr = isr_row["stability"].values[0] if not isr_row.empty else "N/A"
    lines.append(f"    Stability & {stability_global} & {stability_isr} \\\\")
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    path = os.path.join(TABLES, "table_02_stability_metrics.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  table_02_stability_metrics.tex")


# ─── Table 3: kernel roles ────────────────────────────────────────
def table_kernel_roles():
    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Kernel roles, evidence status, and rationale. "
        "Evidence kernels are used in main ISR results; "
        "diagnostic kernels illustrate sensitivity to design choices.}",
        "  \\label{tab:kernel_roles}",
        "  \\begin{tabular}{lllp{5cm}}",
        "    \\toprule",
        "    Kernel & Role & Evidence & Reason \\\\",
        "    \\midrule",
        "    Gaussian & Primary locality kernel & Evidence & "
        "Exponential decay in field-space distance; standard smoothing kernel. \\\\",
        "    Exponential & Robustness kernel & Evidence & "
        "Heavier tail than Gaussian; tests sensitivity to kernel shape. \\\\",
        "    \\texttt{same\\_basin} & Diagnostic & Diagnostic & "
        "Trivially conditions on $x_0$ basin membership; no field-distance resolution. \\\\",
        "    \\texttt{ancestry\\_proxy} & Diagnostic & Diagnostic & "
        "Uses trajectory index as a proxy for branch ancestry; "
        "not a true causal ancestry graph. \\\\",
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    path = os.path.join(TABLES, "table_03_kernel_roles.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  table_03_kernel_roles.tex")


# ─── Table 4: stress summary ──────────────────────────────────────
def table_stress_summary():
    ss = load_json("stress_test_summary.json")
    if ss is None:
        print("  SKIP table_04: no stress_test_summary.json")
        return
    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Stress test summary by $\\sigma$. "
        "Each row aggregates 20 random seeds with $N=2000$ trajectories per run.}",
        "  \\label{tab:stress_summary}",
        "  \\begin{tabular}{lcccccc}",
        "    \\toprule",
        "    $\\sigma$ & Global mean KL & ISR mean KL & Median improv. & "
        "ISR wins / total & Mean $n_{\\rm vacua}$ \\\\",
        "    \\midrule",
    ]
    raw = load_csv("stress_test_results.csv")
    for sigma_str in sorted(ss.keys(), key=float):
        info = ss[sigma_str]
        wins = 0
        total = 0
        median_ratio = 0.0
        if raw is not None:
            sub = raw[raw["sigma"] == float(sigma_str)]["improvement_ratio"].dropna()
            wins = int((sub > 1.0).sum())
            total = len(sub)
            median_ratio = float(sub.median())
        lines.append(
            f"    {sigma_str} & {info['global_mean_kl']:.4f} & {info['isr_mean_kl']:.4f} & "
            f"{median_ratio:.1f}$\\times$ & "
            f"{wins}/{total} & {info['mean_n_vacua']:.1f} \\\\"
        )
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    path = os.path.join(TABLES, "table_04_stress_summary_by_sigma.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  table_04_stress_summary_by_sigma.tex")


# ─── Table 5: failure cases ───────────────────────────────────────
def table_failure_cases():
    df = load_csv("stress_test_results.csv")
    if df is None:
        print("  SKIP table_05: no stress_test_results.csv")
        return
    failures = df[df["improvement_ratio"] < 1.0].sort_values("improvement_ratio")
    if failures.empty:
        print("  SKIP table_05: no failures found")
        return
    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Failure cases: ISR underperforms global census. "
        "Both cases occur at $\\sigma=3.0$, the broadest initial-condition spread.}",
        "  \\label{tab:failure_cases}",
        "  \\begin{tabular}{lccccc}",
        "    \\toprule",
        "    $\\sigma$ & Seed & ISR KL & Global KL & Ratio & Possible cause \\\\",
        "    \\midrule",
    ]
    for _, row in failures.iterrows():
        cause = "Broad initial spread samples vacua far from $x_0$; kernel overlap is thin."
        lines.append(
            f"    {row['sigma']} & {int(row['seed'])} & {row['isr_kl']:.4f} & "
            f"{row['global_kl']:.4f} & {row['improvement_ratio']:.2f} & {cause} \\\\"
        )
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    path = os.path.join(TABLES, "table_05_failure_cases.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  table_05_failure_cases.tex")


# ─── Table 6: effective coefficients ──────────────────────────────
def table_effective_coefficients():
    wc = load_csv("kernel_weighted_sector_averaging.csv")
    if wc is None:
        print("  SKIP table_06: no kernel_weighted_sector_averaging.csv")
        return
    ells = sorted(wc["ell"].unique())
    params = [c for c in wc.columns if c not in ("ell", "n_sectors") and "aggregate" in c]

    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Kernel-weighted sector averaging across kernel scale $\\ell$ at final cutoff $N=10000$. "
        "As $\\ell$ increases, unobserved-sector mixing shifts aggregate toy coefficients away from the "
        "pure $x_0$ basin values.}",
        "  \\label{tab:effective_coefficients}",
        "  \\begin{tabular}{l" + "c" * len(params) + "c}",
        "    \\toprule",
        "    $\\ell$ & " + " & ".join(p.replace("_aggregate", "").replace("_", "\\_").title() for p in params) + " & Interpretation \\\\",
        "    \\midrule",
    ]
    for ell in ells:
        sub = wc[(wc["ell"] == ell) & (wc["n_sectors"] == wc["n_sectors"].max())]
        if sub.empty:
            continue
        row = sub.iloc[0]
        vals = [f"{row[p]:.4f}" for p in params]
        if ell < 0.3:
            interp = "Near-pure $x_0$ basin"
        elif ell < 0.8:
            interp = "Moderate mixing"
        else:
            interp = "Strong unobserved-sector mixing"
        line = f"    {ell} & " + " & ".join(vals) + f" & {interp} \\\\"
        lines.append(line)
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    path = os.path.join(TABLES, "table_06_effective_coefficients.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  table_06_effective_coefficients.tex")


if __name__ == "__main__":
    print("Generating tables...")
    table_main_distribution()
    table_stability_metrics()
    table_kernel_roles()
    table_stress_summary()
    table_failure_cases()
    table_effective_coefficients()
    print("All tables generated.")
