"""Run all ISR experiments sequentially and print a brief summary."""

import logging
import sys
import time

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("run_all")

EXPERIMENTS = [
    ("01 — Global Census Baseline", "experiments/01_global_census_baseline"),
    ("02 — ISR Locality-Weighted Measure", "experiments/02_locality_weighted_measure"),
    ("03 — Cutoff Stability (with global baseline)", "experiments/03_cutoff_stability"),
    ("04 — Kernel Sensitivity", "experiments/04_kernel_sensitivity"),
    ("05 — Basin Boundary Test", "experiments/05_basin_boundary_test"),
    ("06 — Bell Locality Diagnostic", "experiments/06_bell_locality_diagnostic"),
    ("07 — Effective Action Coefficients", "experiments/07_effective_action_coefficients"),
    ("08 — Stress Test (sigma×seed)", "experiments/08_stress_test"),
]


def main():
    sys.path.insert(0, ".")
    results = {}
    total_start = time.time()

    for label, module_path in EXPERIMENTS:
        mod_name = module_path.replace("/", ".")
        logger.info("Running %s ...", label)
        start = time.time()
        try:
            mod = __import__(mod_name, fromlist=["run"])
            result = mod.run()
            elapsed = time.time() - start
            results[label] = {"status": "OK", "elapsed_s": round(elapsed, 1)}
            logger.info("  Done in %.1fs", elapsed)
        except Exception as e:
            elapsed = time.time() - start
            results[label] = {"status": f"ERROR: {e}", "elapsed_s": round(elapsed, 1)}
            logger.error("  FAILED after %.1fs: %s", elapsed, e)

    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"All experiments completed in {total_elapsed:.1f}s")
    print(f"{'=' * 60}")
    for label, info in results.items():
        print(f"  {label}: {info['status']} ({info['elapsed_s']}s)")
    print()


if __name__ == "__main__":
    main()
