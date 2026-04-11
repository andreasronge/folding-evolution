"""Visualization for regime-shift experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .stats import GenerationStats


def plot_regime_shift(
    folding_history: list[GenerationStats],
    direct_history: list[GenerationStats],
    shift_gen: int,
    save_path: str | Path | None = None,
    title: str = "Regime Shift: Folding vs Direct Encoding",
) -> None:
    """Plot 4-curve figure: folding best/mean, direct best/mean.

    Vertical line marks the regime shift.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    f_gens = [s.generation for s in folding_history]
    f_best = [s.best_fitness for s in folding_history]
    f_avg = [s.avg_fitness for s in folding_history]

    d_gens = [s.generation for s in direct_history]
    d_best = [s.best_fitness for s in direct_history]
    d_avg = [s.avg_fitness for s in direct_history]

    ax.plot(f_gens, f_best, "b-", linewidth=2, label="Folding best")
    ax.plot(f_gens, f_avg, "b--", linewidth=1, alpha=0.7, label="Folding mean")
    ax.plot(d_gens, d_best, "r-", linewidth=2, label="Direct best")
    ax.plot(d_gens, d_avg, "r--", linewidth=1, alpha=0.7, label="Direct mean")

    ax.axvline(x=shift_gen, color="gray", linestyle=":", linewidth=2, label="Regime shift")

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title(title)
    ax.legend(loc="lower right")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # Annotate regimes
    ax.text(shift_gen / 2, 1.0, "Regime A", ha="center", fontsize=10, color="gray")
    total = max(f_gens[-1] if f_gens else 0, d_gens[-1] if d_gens else 0)
    ax.text(shift_gen + (total - shift_gen) / 2, 1.0, "Regime B",
            ha="center", fontsize=10, color="gray")

    plt.tight_layout()

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150)
        print(f"Plot saved to {path}")

    plt.close(fig)


def plot_regime_shift_comparison(
    comparison_result: dict,
    save_path: str | Path | None = None,
) -> None:
    """Plot averaged results from run_regime_shift_comparison.

    Averages best/mean fitness across seeds, shows min/max as shaded region.
    """
    folding_runs = comparison_result["folding_runs"]
    direct_runs = comparison_result["direct_runs"]
    shift_gen = comparison_result["shift_gen"]

    # Find common generation count
    n_gens = min(len(r["history"]) for r in folding_runs + direct_runs)

    fig, ax = plt.subplots(figsize=(10, 6))

    for runs, color, label in [
        (folding_runs, "blue", "Folding"),
        (direct_runs, "red", "Direct"),
    ]:
        gens = list(range(n_gens))
        best_per_gen = []
        avg_per_gen = []

        for g in range(n_gens):
            bests = [r["history"][g].best_fitness for r in runs]
            avgs = [r["history"][g].avg_fitness for r in runs]
            best_per_gen.append(bests)
            avg_per_gen.append(avgs)

        mean_best = [sum(b) / len(b) for b in best_per_gen]
        min_best = [min(b) for b in best_per_gen]
        max_best = [max(b) for b in best_per_gen]

        mean_avg = [sum(a) / len(a) for a in avg_per_gen]

        ax.plot(gens, mean_best, color=color, linewidth=2, label=f"{label} best (mean)")
        ax.fill_between(gens, min_best, max_best, color=color, alpha=0.15)
        ax.plot(gens, mean_avg, color=color, linewidth=1, linestyle="--",
                alpha=0.7, label=f"{label} mean (mean)")

    ax.axvline(x=shift_gen, color="gray", linestyle=":", linewidth=2, label="Regime shift")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title(f"Regime Shift Comparison ({comparison_result['n_seeds']} seeds)")
    ax.legend(loc="lower right")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    ax.text(shift_gen / 2, 1.0, "Regime A", ha="center", fontsize=10, color="gray")
    ax.text(shift_gen + (n_gens - shift_gen) / 2, 1.0, "Regime B",
            ha="center", fontsize=10, color="gray")

    plt.tight_layout()

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150)
        print(f"Plot saved to {path}")

    plt.close(fig)
