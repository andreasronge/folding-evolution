"""Plasticity-aware analysis for §v2.5-plasticity-1a.

Reads the per-individual plastic metrics persisted into
``final_population.npz`` by ``evolve.py`` (delta_final,
test_fitness_frozen, test_fitness_plastic, train_fitness_frozen,
train_fitness_plastic, has_gt) alongside the genotype array, and
computes the prereg's outcome-grid metrics: R_fit_frozen_999,
R_fit_plastic_999, Baldwin_gap binned by Hamming-to-canonical,
Baldwin_slope + bootstrap 95% CI, and GT_bypass_fraction.

The genotype → active-view → canonical distance pipeline is shared
with ``analyze_retention`` — we import rather than duplicate.

CLI mirrors ``analyze_retention.main``:
    uv run python experiments/chem_tape/analyze_plasticity.py <sweep_name>

Emits ``plasticity.csv`` (per-run rows) and ``plasticity_summary.json``
(per-cell aggregates) in the sweep output dir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

# Re-use canonical/active-view/levenshtein helpers from the retention
# module so the distance definition is consistent across sibling
# analyses (principle 23).
from analyze_retention import (  # type: ignore[import-not-found]
    CANONICAL_AND_BODY_HEX,
    OUTPUT_ROOT,
    extract_active,
    hex_to_tape,
    levenshtein,
)


# --- METRIC_DEFINITIONS (principle 27) ---
#
# Verbatim citations: every entry's value matches the wording the
# §v2.5-plasticity-1a prereg quotes under "METRIC_DEFINITIONS
# additions". Preregs and chronicles should copy/paste from here.
METRIC_DEFINITIONS: dict[str, str] = {
    "F_AND_test": (
        "Fraction of the 20 seeded runs that achieve best-of-run "
        "fitness >= threshold on the held-out test examples (separate "
        "from training examples). Unit: count/20. Binary per-run "
        "measure — used for F-recovery claim only, not for Baldwin "
        "slope regression."
    ),
    "F_AND_train": (
        "Fraction of the 20 seeded runs that achieve best-of-run "
        "fitness >= threshold on training examples. Sanity check — "
        "should remain near 20/20 under seeded init."
    ),
    "test_fitness_frozen": (
        "Per-individual fraction of held-out test examples correctly "
        "classified with delta=0 (frozen, no adaptation). Continuous "
        "scalar in [0, 1]; 16-valued given 75/25 split over 64 "
        "examples (16 test examples). This is the continuous "
        "test-fitness used in the Baldwin slope regression — not the "
        "binary F_AND_test. Emitted per-individual in "
        "final_population.npz."
    ),
    "test_fitness_plastic": (
        "Per-individual fraction of held-out test examples correctly "
        "classified with delta trained on the 48 train examples and "
        "then frozen. Continuous scalar in [0, 1]. Emitted "
        "per-individual in final_population.npz."
    ),
    "delta_convergence": (
        "Per-individual final value of delta after train-phase "
        "adaptation, stored alongside frozen/plastic fitnesses in "
        "final_population.npz. Used to diagnose universal-adapter "
        "signature: if std(delta_final) is small relative to "
        "mean(delta_final) across diverse genotypes, delta converges "
        "to the same value regardless of genotype → universal-adapter "
        "flag independent of F recovery."
    ),
    "GT_bypass_fraction": (
        "Fraction of final-population individuals whose decoded "
        "program contains no GT token. These individuals have "
        "test_fitness_plastic - test_fitness_frozen = 0 trivially "
        "(plasticity cannot act on a program with no GT operation) "
        "and must be excluded from the Baldwin slope regression and "
        "reported separately. Computed by scanning the decoded token "
        "sequence for the GT opcode before any fitness evaluation. "
        "Emitted as a per-cell scalar in the analysis CSV."
    ),
    "R_fit_frozen_999": (
        "Fraction of the final population whose training fitness >= "
        "0.999 under frozen evaluation (plasticity state disabled at "
        "test time). This is the analogue of R_fit_999 under frozen "
        "semantics."
    ),
    "R_fit_plastic_999": (
        "Fraction of the final population whose training fitness >= "
        "0.999 under plastic evaluation (train-phase adaptation, then "
        "test). Captures the within-lifetime adaptation uplift."
    ),
    "Baldwin_gap": (
        "For each non-GT-bypass individual in the final population, "
        "compute test_fitness_plastic - test_fitness_frozen on "
        "held-out test examples. Aggregate as mean of that gap "
        "binned by Hamming-to-canonical-active-view distance (bins "
        "0, 1, 2, 3, >=4). Positive gap means plasticity helps; zero "
        "gap means plasticity does nothing; negative gap means "
        "plasticity hurts. GT-bypass individuals excluded; reported "
        "separately via GT_bypass_fraction."
    ),
    "Baldwin_slope": (
        "Linear regression slope of per-individual "
        "(test_fitness_plastic - test_fitness_frozen) on "
        "hamming_to_canonical, computed on non-GT-bypass individuals "
        "only. If slope is negative (closer genotypes get more "
        "plastic uplift) → Baldwin signature. If slope is zero "
        "(uniform uplift regardless of distance) → universal adapter. "
        "Bootstrap 95% CI on slope using 10 000 resamples."
    ),
    "bootstrap_ci_spec": (
        "Nonparametric bootstrap over per-seed values: 10 000 "
        "resamples with replacement via "
        "numpy.random.default_rng(seed=42); 95% CI is the [2.5%, "
        "97.5%] empirical quantile of the resampled means."
    ),
    # --- §v2.5-plasticity-2a extensions (verbatim from the prereg's
    # "METRIC_DEFINITIONS extensions" block at Plans/prereg_v2-5-plasticity-2a.md) ---
    "max_gap_at_budget_5": (
        "Per-seed maximum of Baldwin_gap across Hamming bins h in {2, 3, >=4} "
        "at plasticity_budget=5. Computed as max over non-excluded bin means "
        "of per-seed Baldwin_gap_h2, Baldwin_gap_h3, Baldwin_gap_h_ge4 for "
        "non-GT-bypass individuals only. Sparse-bin guard (v4): any bin with "
        "fewer than 5 non-GT-bypass individuals in the seed is excluded from "
        "the max (emits nan for that bin). If all three bins are excluded, "
        "per-seed max_gap_at_budget_5 = nan. Broader than §1a's "
        "Baldwin_gap_h_ge4 metric to handle the case where positive plastic "
        "uplift concentrates in h=2 or h=3 rather than h>=4 (expected at "
        "sf=0.0 where the Hamming-to-canonical distribution is shifted "
        "relative to sf=0.01)."
    ),
    "max_gap_at_budget_5_cell_boot_ci": (
        "Seed-level nonparametric bootstrap 95% CI on the per-cell mean of "
        "per-seed max_gap_at_budget_5: 10 000 resamples with replacement over "
        "the 20 per-seed values (excluding seeds where per-seed "
        "max_gap_at_budget_5 is nan due to sparse-bin guard) via "
        "numpy.random.default_rng(seed=42); CI is the [2.5%, 97.5%] empirical "
        "quantile of the resampled means. Matches bootstrap_ci_spec. Returns "
        "nan CI if fewer than 15 non-nan seeds available (row 7 grid-miss "
        "trigger). Distinct from the existing Baldwin_slope_ci95 columns, "
        "which bootstrap intra-population over individuals and cannot support "
        "cell-level row-match clauses."
    ),
    "max_gap_at_budget_5_seed_majority": (
        "Count of seeds (out of 20 in the cell) with per-seed "
        "max_gap_at_budget_5 > 0.10. Part of §v2.5-plasticity-2a's row-3 "
        "dual criterion: cell-bootstrap CI_lo >= 0.10 AND this count >= 10. "
        "Sidesteps v2's incorrect 'CI_lo >= 0.10 implies seed-majority-positive' "
        "equivalence claim — cell-mean CI and per-seed majority are distinct "
        "statistical statements that must both hold for the row."
    ),
    "max_gap_at_budget_5_seed_minority_0_05": (
        "Count of seeds (out of 20 in the cell) with per-seed "
        "max_gap_at_budget_5 > 0.05 (excluding seeds where per-seed "
        "max_gap_at_budget_5 is nan). §v2.5-plasticity-2a's rows 1 and 5 "
        "trigger on this count < 10 (fewer than half the seeds show even "
        "a weak positive uplift at the 0.05 floor). Exactly parallel to "
        "max_gap_at_budget_5_seed_majority but at the tighter tail-absence "
        "threshold of 0.05 rather than the row-3 majority threshold of "
        "0.10. Added in v5 per codex-v4 P2-a to separate row-1/5 absence "
        "semantics from row-3 presence semantics."
    ),
    "top1_winner_hamming": (
        "Per-run active-view Levenshtein distance (cap=4) between the "
        "top-1 winner's tape and the canonical sum_gt_10_AND_max_gt_5 "
        "tape. Winner selection: argmax over the final population's "
        "test_fitness_plastic, tie-broken by train_fitness_plastic, then "
        "by the smallest genotype index (numpy argmax first-max behaviour). "
        "Distance computed as "
        "levenshtein(extract_active(genotypes[winner_idx], alphabet), "
        "extract_active(canonical_tape, alphabet), cap=4); matches the "
        "Baldwin-bin labelling routine verbatim. Emitted as an integer "
        "per-run column in plasticity.csv; values ∈ {0, 1, 2, 3, 4}. "
        "Added in v9 per §25b option (c) / §25c — replaces v6-v8's "
        "three-tier classical_baldwin_gap_max routing clause with a "
        "pre-committed chronicle-time per-seed categorical classification: "
        "top1_winner_hamming <= 1 = classical-Baldwin active seed; >= 2 = "
        "classical-Baldwin inactive seed. Cell-level verdict on row-1-"
        "matching cells is a count over the nominal 20 seeds: "
        "n_classical_active >= 11 = CB dominant; <= 9 = CB non-dominant; "
        "= 10 = split signal. Schema-check guard (v11): if "
        "final_population.npz lacks any of genotypes, test_fitness_plastic, "
        "train_fitness_plastic, or their lengths disagree, emit nan and "
        "route the chronicle-time row-1 verdict to BLOCKED per the "
        "artifact-complete floor."
    ),
    "R_fit_delta_paired_sf0": (
        "Per-seed paired difference R_fit_plastic_999 - R_fit_frozen_999 at "
        "sf=0.0, where R_fit_frozen_999 is taken from the frozen control cell "
        "at the matching seed in the same sweep (NOT from the plastic run's "
        "own final_population frozen evaluation, which would compare plastic "
        "and frozen evaluation on the same evolved population rather than "
        "comparing the plastic cell's final population to the frozen control's "
        "final population). Requires cross-cell merge between the plastic "
        "cells and the frozen control cell on shared seeds 20..39. Used as "
        "§v2.5-plasticity-2a's secondary diagnostic."
    ),
    "initial_population_canonical_count": (
        "Count of individuals in the generation-0 population whose tape "
        "byte-for-byte matches the canonical tape(s) parsed from "
        "cfg.seed_tapes (a hex string; see src/folding_evolution/chem_tape/"
        "config.py:121 — field is 'seed_tapes', NOT 'seed_tapes_hex'). "
        "Parsed via _parse_seed_tapes in evolve.py. Emitted per-run to "
        "history.npz as a scalar at generation-0 population build time. "
        "At sf=0.0 with cfg.seed_tapes == '' (empty string default), the "
        "expected value is 0 for every seed; any nonzero count flags an "
        "infrastructure bug in build_initial_population."
    ),
    # --- §v2.5-plasticity-2c extensions (verbatim from the prereg's
    # "METRIC_DEFINITIONS extensions" block at Plans/prereg_v2-5-plasticity-2c.md) ---
    "top1_winner_overhead": (
        "Per-run integer: active-view length of the top-1 winner's tape minus 12 "
        "(canonical active-view length for sum_gt_10_AND_max_gt_5). Negative if "
        "winner is shorter than canonical. Winner selection: argmax over "
        "test_fitness_plastic, tiebroken by train_fitness_plastic, then by smallest "
        "genotype index (matches top1_winner_hamming selection verbatim). Active "
        "view = tokens with id in {1..19} (v2_probe; excludes NOP=0 and separators "
        "20/21). Added in §v2.5-plasticity-2c; §26-demoted diagnostic, no routing."
    ),
    "top1_winner_plasticity_active_count": (
        "Per-run integer: count of plasticity-active operators {GT (8), IF_GT (17), "
        "THRESHOLD_SLOT (19)} in the top-1 winner's active-view tokens. Conservative "
        "plasticity-active set under rank1_op_threshold. Canonical has "
        "GT*2+IF_GT*1+THRESHOLD_SLOT*0 = 3. Added in §v2.5-plasticity-2c; §26-"
        "demoted diagnostic, no routing."
    ),
    "top1_winner_levenshtein_uncapped": (
        "Per-run integer: full active-view Levenshtein distance (uncapped) from the "
        "top-1 winner's active-view to the canonical sum_gt_10_AND_max_gt_5 active-"
        "view. Replaces the deprecated top1_winner_hamming with cap=4 (which "
        "returned cap+1=5 sentinel on all §v2.5-plasticity-2a + n-exp winners, "
        "destroying distance information). Preserves full distance structure "
        "(observed range 17-26 on §2a n=40). Winner selection identical to "
        "top1_winner_overhead. Added in §v2.5-plasticity-2c; §26-demoted diagnostic."
    ),
    "top1_winner_attractor_category": (
        "Per-run string in {'compositional_AND', 'max>5-only', 'sum>10-only', "
        "'other'}: heuristic classification of the top-1 winner's active-view "
        "structure. compositional_AND: has >=1 of {REDUCE_MAX, CONST_5} AND >=1 of "
        "{SUM} AND >=1 of {GT, IF_GT}. max>5-only: has {REDUCE_MAX, CONST_5, GT} "
        "but no SUM. sum>10-only: has {SUM, GT or IF_GT} but no REDUCE_MAX and no "
        "CONST_5. other: doesn't fit above. Canonical classifies as compositional_"
        "AND. Added in §v2.5-plasticity-2c; §26-demoted diagnostic."
    ),
    "top1_winner_canonical_token_set_size": (
        "Per-run integer in {0..8}: count of canonical active-view operators "
        "{CONST_0, INPUT, REDUCE_MAX, CONST_5, GT, SUM, ADD, IF_GT} present (set "
        "intersection) in top-1 winner's active-view. Higher = more canonical "
        "operators present; does NOT imply canonical structure. Added in §v2.5-"
        "plasticity-2c; §26-demoted diagnostic."
    ),
    "top1_winner_baldwin_gap": (
        "Per-run float: test_fitness_plastic[winner_idx] minus test_fitness_"
        "frozen[winner_idx] on SAME top-1 winner genotype. Positive = plasticity "
        "helps this winner's test-set fitness; negative = plasticity hurts. "
        "Measured on 16 held-out test examples. §2a pooled n=40 budget=5: mean "
        "+0.364, range [-0.125, +0.688]. Added in §v2.5-plasticity-2c; §26-demoted "
        "diagnostic."
    ),
    "f_and_test_plastic_seed_boot_ci": (
        "Per-cell seed-bootstrap 97.5% CI on F_AND_test_plastic fraction. 10 000 "
        "resamples with replacement over 20 per-seed binary indicators (best_"
        "fitness_test_plastic >= 1.0) via numpy.random.default_rng(seed=42); CI = "
        "[1.25%, 98.75%] empirical quantiles of resampled fractions. Matches "
        "bootstrap_ci_spec. For budget=5 pooled cell uses n=40 indicators. "
        "Descriptive (not confirmatory). Added in §v2.5-plasticity-2c."
    ),
    "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5": (
        "Paired-seed bootstrap 97.5% CI on per-seed difference F_AND_test_plastic"
        "[budget=40, seed=s] minus F_AND_test_plastic[budget=5, seed=s] for s in "
        "{20..39}, n=20 paired differences. 10 000 resamples via numpy.random."
        "default_rng(seed=42); CI = [1.25%, 98.75%] empirical quantiles of resampled "
        "paired-difference means. Budget=5 per-seed indicators extracted from "
        "pooled §v2.5-plasticity-2a data (not n-exp) via seed filter. "
        "**Primary confirmatory test for §v2.5-plasticity-2c family 'plasticity-"
        "narrow-plateau' (family size now 2, corrected alpha = 0.025).** H1 "
        "rejection: CI_lo > 0. H-reverse trigger: CI_hi < 0. Added in §v2.5-"
        "plasticity-2c."
    ),
    # --- §v2.5-plasticity-2d extensions (verbatim from the prereg's
    # "METRIC_DEFINITIONS extensions" block at Plans/prereg_v2-5-plasticity-2d.md) ---
    "f_and_test_plastic_seed_boot_ci_98_333": (
        "Per-cell seed-bootstrap 98.333% CI on F_AND_test_plastic fraction. "
        "10 000 resamples with replacement over 20 per-seed binary indicators "
        "(best_fitness_test_plastic >= 1.0) via numpy.random.default_rng(seed=42); "
        "CI = [0.8333%, 99.1667%] empirical quantiles of resampled fractions. "
        "Matches bootstrap_ci_spec at the §v2.5-plasticity-2d family-alpha=0.01667 "
        "discipline (family = 'plasticity-narrow-plateau', size 3 per 22b "
        "commit-time membership). Extends §v2.5-plasticity-2c's "
        "f_and_test_plastic_seed_boot_ci (97.5% CI) to the §2d quantile. "
        "Descriptive (not confirmatory). Added in §v2.5-plasticity-2d."
    ),
    "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40": (
        "Paired-seed bootstrap 98.333% CI on per-seed difference "
        "F_AND_test_plastic[mechanism=rank1_op_threshold, budget=40, seed=s] "
        "minus F_AND_test_plastic[mechanism=random_sample_threshold, budget=40, "
        "seed=s] for s in {20..39}, n=20 paired differences. 10 000 resamples "
        "via numpy.random.default_rng(seed=42); CI = [0.8333%, 99.1667%] "
        "empirical quantiles of resampled paired-difference means. Plastic "
        "budget=40 per-seed indicators extracted from §v2.5-plasticity-2c data "
        "via (mechanism, budget, seed) filter. "
        "**Primary confirmatory test for §v2.5-plasticity-2d family "
        "'plasticity-narrow-plateau' (family size now 3, corrected alpha = "
        "0.01667).** H1 rejection: CI_lo > 0. H-reverse trigger: CI_hi < 0. "
        "Added in §v2.5-plasticity-2d."
    ),
    "delta_final_cell_support_bounds": (
        "Per-cell tuple (min, max, std) of delta_final across 20 seeds. "
        "Mechanism-sanity diagnostic: for plasticity_mechanism="
        "'random_sample_threshold' cells, verifies -budget <= min, max <= "
        "+budget (uniform-continuous support bounds); verifies std >= 0.01 "
        "(non-degenerate rng); verifies 0 < mean(|delta_final|) <= budget "
        "(not all-delta=0). Violation of any sub-check routes Row 6 (SWAMPED) "
        "per Setup Mechanism-sanity pre-check. For plasticity_mechanism="
        "'rank1_op_threshold' cells, support bound is the integer-lattice "
        "+-budget*delta endpoint (same formal bound, different reachability). "
        "Reported per-cell at chronicle time. Added in §v2.5-plasticity-2d."
    ),
    "random_sample_mechanism_draw_spread": (
        "Per-individual tuple (min_draw, max_draw, std_draws, argmax_index) "
        "summarizing the k uniform-continuous draws at a random_sample_"
        "threshold cell. Logged per-individual during adapt_and_evaluate_one_"
        "random_sample as part of the individual's output dict; per-run top-1 "
        "winner aggregation emitted to CSV columns winner_k_draw_min, "
        "winner_k_draw_max, winner_k_draw_std, winner_k_argmax_index. "
        "**MANDATORY at launch per §v2.5-plasticity-2d codex-v1 P1-5 "
        "correction (previously optional-defer; v2 upgrades to launch-"
        "blocking).** Per-individual invariants (any violation on any "
        "individual in any random-sample cell routes to Row 6 SWAMPED): "
        "min_draw >= -budget, max_draw <= +budget, std_draws >= 0.05 * budget, "
        "argmax_index in [0, k-1]. Covers failure modes that cell-level "
        "delta_final cannot see: individual-level collapse where k draws "
        "cluster but argmax produces a different-looking delta_final; "
        "support-bound overshoot from rng-library edge cases. Schema is "
        "(min_draw, max_draw, std_draws, argmax_index) - consistent with "
        "Setup mechanism-sanity pre-check, Guard-6 sub-criterion (c), and "
        "Status-transition checklist item 1(g). Added in §v2.5-plasticity-2d."
    ),
}


# §v2.5-plasticity-2c token-set constants for winner-structural metrics
# (canonical-token-set, plasticity-active-token set, attractor building blocks).
# Ids taken verbatim from src/folding_evolution/chem_tape/alphabet.py.
_CANONICAL_ACTIVE_TOKEN_SET: frozenset[int] = frozenset({
    1,   # INPUT
    2,   # CONST_0
    5,   # SUM
    7,   # ADD
    8,   # GT
    16,  # CONST_5
    17,  # IF_GT
    18,  # REDUCE_MAX
})
_CANONICAL_ACTIVE_LEN: int = 12  # sum_gt_10_AND_max_gt_5 canonical active-view token count
_PLASTICITY_ACTIVE_TOKEN_SET: frozenset[int] = frozenset({
    8,   # GT
    17,  # IF_GT
    19,  # THRESHOLD_SLOT
})
_MAX5_BLOCK_TOKENS: frozenset[int] = frozenset({
    8,   # GT
    16,  # CONST_5
    18,  # REDUCE_MAX
})
_SUM_TOKEN: int = 5
_GT_TOKEN: int = 8
_IF_GT_TOKEN: int = 17


HAMMING_BINS = [0, 1, 2, 3]  # final bin is implicit "≥4"


def hamming_bin_label(d: int) -> str:
    return str(d) if d < 4 else ">=4"


def linreg_slope(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Return (slope, intercept) of the OLS fit of y on x.

    Uses numpy.polyfit to avoid the scipy dependency; equivalent to
    scipy.stats.linregress up to numerical precision on real-valued
    inputs. Returns (nan, nan) when the input has < 2 points or when
    x has zero variance (degenerate regression — no slope is defined).
    """
    if len(x) < 2:
        return float("nan"), float("nan")
    if np.var(x) == 0:
        return float("nan"), float("nan")
    slope, intercept = np.polyfit(x.astype(np.float64), y.astype(np.float64), 1)
    return float(slope), float(intercept)


def bootstrap_slope_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_boot: int = 10_000,
    rng_seed: int = 42,
) -> tuple[float, float, float]:
    """Return (slope_mean, slope_ci_lo, slope_ci_hi) with n_boot bootstrap
    resamples (with replacement over pairs), 95% CI as [2.5%, 97.5%].

    Matches bootstrap_ci_spec — same rng seed and n_boot as
    analyze_retention so cross-analysis CIs are comparable. Returns
    (nan, nan, nan) when degenerate (< 2 points or zero x-variance).
    """
    if len(x) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(rng_seed)
    n = len(x)
    slopes = np.empty(n_boot, dtype=np.float64)
    x_f = x.astype(np.float64)
    y_f = y.astype(np.float64)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xs = x_f[idx]
        ys = y_f[idx]
        if np.var(xs) == 0:
            slopes[i] = float("nan")
            continue
        s, _ = np.polyfit(xs, ys, 1)
        slopes[i] = s
    valid = slopes[~np.isnan(slopes)]
    if len(valid) == 0:
        return float("nan"), float("nan"), float("nan")
    return (
        float(np.mean(valid)),
        float(np.quantile(valid, 0.025)),
        float(np.quantile(valid, 0.975)),
    )


def _row_common(cfg: dict, result: dict, run_dir: Path) -> dict:
    """Config/result fields present on both plastic and frozen-only rows."""
    return {
        "run_dir": run_dir.name,
        "arm": cfg.get("arm", result.get("arm", "")),
        "seed": int(cfg.get("seed", 0)),
        "seed_fraction": float(cfg.get("seed_fraction", 0.0)),
        "plasticity_budget": int(cfg.get("plasticity_budget", 0)),
        "plasticity_delta": float(cfg.get("plasticity_delta", 0.0)),
        "plasticity_enabled": bool(cfg.get("plasticity_enabled", False)),
        # §v2.5-plasticity-2d: plasticity_mechanism carried on every row
        # (defaults to 'rank1_op_threshold' — matches config default and
        # preserves backward compatibility with pre-§2d §2a/§2c CSVs
        # written before this field existed; those rows will parse as
        # mechanism=rank1_op_threshold when the YAML doesn't set it).
        "plasticity_mechanism": str(
            cfg.get("plasticity_mechanism", "rank1_op_threshold")
        ),
        "best_fitness": float(result.get("best_fitness", float("nan"))),
    }


# Plastic-specific column keyset — used to pad frozen-only rows so that
# plasticity.csv has a single unified schema (principle 27 / codex-v3
# NEW-P2 schema normalization). Chose the pad-with-None approach over a
# separate plasticity_frozen_controls.csv because downstream paired-delta
# analyses need both kinds visible in one place; documented in the
# §v2.5-plasticity-2a commit message.
_PLASTIC_ONLY_KEYS: tuple[str, ...] = (
    "best_fitness_train_frozen",
    "best_fitness_test_frozen",
    "best_fitness_train_plastic",
    "best_fitness_test_plastic",
    "R_fit_plastic_999",
    "R_fit_delta_999",
    "GT_bypass_fraction",
    "n_non_bypass",
    "Baldwin_slope",
    "Baldwin_slope_bootstrap_mean",
    "Baldwin_slope_ci95_lo",
    "Baldwin_slope_ci95_hi",
    "delta_final_mean",
    "delta_final_std",
    "Baldwin_gap_h0",
    "Baldwin_gap_h1",
    "Baldwin_gap_h2",
    "Baldwin_gap_h3",
    "Baldwin_gap_h_ge4",
    "count_h0",
    "count_h1",
    "count_h2",
    "count_h3",
    "count_h_ge4",
    "delta_mean_h0",
    "delta_std_h0",
    "delta_mean_h1",
    "delta_std_h1",
    "delta_mean_h2",
    "delta_std_h2",
    "delta_mean_h3",
    "delta_std_h3",
    "max_gap_at_budget_5",
    "top1_winner_hamming",
    # §v2.5-plasticity-2c additions (6 new per-run winner-structural metrics):
    "top1_winner_overhead",
    "top1_winner_plasticity_active_count",
    "top1_winner_levenshtein_uncapped",
    "top1_winner_attractor_category",
    "top1_winner_canonical_token_set_size",
    "top1_winner_baldwin_gap",
    # §v2.5-plasticity-2d additions (4 new per-run k-draw winner columns,
    # present only on random_sample_threshold runs; None on rank-1):
    "winner_k_draw_min",
    "winner_k_draw_max",
    "winner_k_draw_std",
    "winner_k_argmax_index",
)


def _analyze_frozen_run(
    run_dir: Path,
    data: "np.lib.npyio.NpzFile",
    cfg: dict,
    result: dict,
) -> dict:
    """Build a per-run row for a frozen-only run (plasticity_enabled=False).

    Emits R_fit_frozen_999 computed from the final-population `fitnesses`
    array (the GA's standard full-task fitness; no train/test split in
    the frozen path). All plastic-specific columns are padded with None
    so plasticity.csv has a unified schema for downstream paired-delta
    merges.
    """
    fitnesses = data["fitnesses"]  # (P,) float32
    row = _row_common(cfg, result, run_dir)
    row["R_fit_frozen_999"] = float(np.mean(fitnesses >= 0.999))
    for k in _PLASTIC_ONLY_KEYS:
        row[k] = None
    return row


def analyze_run(
    run_dir: Path,
    canonical_tape: np.ndarray,
    alphabet: str,
) -> dict | None:
    """Compute per-run metrics. Returns a row dict (plastic or frozen-only
    schema — frozen-only rows pad plastic columns with None) or None when
    the run lacks the required artifacts.
    """
    fp = run_dir / "final_population.npz"
    cfg_path = run_dir / "config.yaml"
    result_path = run_dir / "result.json"
    if not fp.exists() or not cfg_path.exists() or not result_path.exists():
        return None

    data = np.load(fp)
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    result = json.loads(result_path.read_text())

    if "delta_final" not in data.files:
        # §v2.5-plasticity-2a: frozen-only run. Required for paired
        # R_fit_delta_paired_sf0 cross-cell merge (codex-v3 NEW-P2).
        return _analyze_frozen_run(run_dir, data, cfg, result)

    genotypes = data["genotypes"]            # (P, L) uint8
    train_fit_frozen = data["train_fitness_frozen"]   # (P,) float32
    train_fit_plastic = data["train_fitness_plastic"] # (P,) float32
    test_fit_frozen = data["test_fitness_frozen"]     # (P,) float32
    test_fit_plastic = data["test_fitness_plastic"]   # (P,) float32
    delta_final = data["delta_final"]                 # (P,) float32
    has_gt = data["has_gt"].astype(bool)              # (P,) bool

    P = genotypes.shape[0]
    can_active = extract_active(canonical_tape, alphabet)

    # Hamming-to-canonical as active-view Levenshtein (capped at 4 —
    # matches the prereg's {0,1,2,3,≥4} bin structure and avoids
    # computing large edit distances on drifted tapes).
    dist = np.empty(P, dtype=np.int16)
    for i in range(P):
        act = extract_active(genotypes[i], alphabet)
        dist[i] = levenshtein(act, can_active, cap=4)

    delta_fit = test_fit_plastic - test_fit_frozen  # per-individual

    # --- Cell-level scalars ---
    R_fit_frozen_999 = float(np.mean(train_fit_frozen >= 0.999))
    R_fit_plastic_999 = float(np.mean(train_fit_plastic >= 0.999))
    GT_bypass_fraction = float(1.0 - np.mean(has_gt))

    # Restrict Baldwin regression to non-GT-bypass individuals
    # (principle-correct per prereg; GT-bypass is trivially delta_fit=0
    # and would pull the slope toward zero).
    non_bypass = has_gt
    n_non_bypass = int(non_bypass.sum())

    if n_non_bypass >= 2:
        x = dist[non_bypass].astype(np.float64)
        y = delta_fit[non_bypass].astype(np.float64)
        slope, intercept = linreg_slope(x, y)
        slope_boot, slope_ci_lo, slope_ci_hi = bootstrap_slope_ci(x, y)
    else:
        slope = intercept = float("nan")
        slope_boot = slope_ci_lo = slope_ci_hi = float("nan")

    # Baldwin gap binned by Hamming (non-bypass only).
    gap_bins: dict[str, float | None] = {}
    gap_counts: dict[str, int] = {}
    for b in HAMMING_BINS:
        mask = non_bypass & (dist == b)
        gap_bins[f"Baldwin_gap_h{b}"] = (
            float(delta_fit[mask].mean()) if mask.any() else None
        )
        gap_counts[f"count_h{b}"] = int(mask.sum())
    mask_ge4 = non_bypass & (dist >= 4)
    gap_bins["Baldwin_gap_h_ge4"] = (
        float(delta_fit[mask_ge4].mean()) if mask_ge4.any() else None
    )
    gap_counts["count_h_ge4"] = int(mask_ge4.sum())

    # delta_convergence summary per Hamming bin — universal-adapter
    # diagnostic (principle 4 degenerate-success guard).
    delta_stats: dict[str, float | None] = {}
    for b in HAMMING_BINS:
        mask = non_bypass & (dist == b)
        if mask.any():
            delta_stats[f"delta_mean_h{b}"] = float(delta_final[mask].mean())
            delta_stats[f"delta_std_h{b}"] = float(delta_final[mask].std())
        else:
            delta_stats[f"delta_mean_h{b}"] = None
            delta_stats[f"delta_std_h{b}"] = None

    # §v2.5-plasticity-2a max_gap_at_budget_5 per-seed (v4 canonical
    # definition): per-seed max over Baldwin_gap_h{2,3,_ge4} with
    # sparse-bin guard (bin excluded if < 5 non-GT-bypass individuals).
    # Emitted for every plastic budget (the name is the prereg's pinned
    # statistic-axis label; the confirmatory test at summarize-time
    # filters to plasticity_budget == 5). Lower-budget values are
    # descriptive-only and do not enter the FWER family.
    max_gap = _compute_max_gap_at_budget_5(gap_bins, gap_counts)

    # §v2.5-plasticity-2a top1_winner_hamming (v9 per §25b option c;
    # v10 verbatim tiebreak; v11 schema-check guard). Per-run active-view
    # Levenshtein (cap=4) between the final population's top-1 winner
    # (argmax test_fitness_plastic, tiebroken by train_fitness_plastic,
    # then smallest genotype index) and the canonical tape. Schema guard:
    # if required fields are missing or lengths disagree, emit nan —
    # routes the chronicle-time row-1 verdict to BLOCKED per the
    # artifact-complete floor. DEPRECATED in §v2.5-plasticity-2c; retained
    # for backwards compatibility with the §2a chronicle.
    top1_winner_hamming = _compute_top1_winner_hamming(
        data, can_active, alphabet
    )

    # §v2.5-plasticity-2c: 6 new per-run winner-structural metrics (all
    # §26-demoted diagnostics; no routing clauses on them). Computed only
    # when the top-1 winner selection succeeds (schema-complete run); emit
    # None across all 6 columns when schema fails (routes to BLOCKED per
    # the artifact-complete floor, same as top1_winner_hamming).
    winner_idx = _select_top1_winner_idx(data)
    if winner_idx is not None:
        winner_metrics = _compute_winner_structural_metrics(
            data, winner_idx, can_active, alphabet
        )
    else:
        winner_metrics = {
            "top1_winner_overhead": None,
            "top1_winner_plasticity_active_count": None,
            "top1_winner_levenshtein_uncapped": None,
            "top1_winner_attractor_category": None,
            "top1_winner_canonical_token_set_size": None,
            "top1_winner_baldwin_gap": None,
        }

    # §v2.5-plasticity-2d: per-run k-draw winner summary. Present only on
    # random_sample_threshold runs (the four k_draw_* arrays are emitted
    # to final_population.npz only for that mechanism per run.py); None
    # on rank-1 runs so the schema stays uniform across mechanisms.
    if (
        winner_idx is not None
        and "k_draw_min" in data.files
        and "k_draw_max" in data.files
        and "k_draw_std" in data.files
        and "k_argmax_index" in data.files
    ):
        winner_k_draw = {
            "winner_k_draw_min": float(data["k_draw_min"][winner_idx]),
            "winner_k_draw_max": float(data["k_draw_max"][winner_idx]),
            "winner_k_draw_std": float(data["k_draw_std"][winner_idx]),
            "winner_k_argmax_index": int(data["k_argmax_index"][winner_idx]),
        }
    else:
        winner_k_draw = {
            "winner_k_draw_min": None,
            "winner_k_draw_max": None,
            "winner_k_draw_std": None,
            "winner_k_argmax_index": None,
        }

    row = _row_common(cfg, result, run_dir)
    row.update({
        "best_fitness_train_frozen": float(train_fit_frozen.max()),
        "best_fitness_test_frozen": float(test_fit_frozen.max()),
        "best_fitness_train_plastic": float(train_fit_plastic.max()),
        "best_fitness_test_plastic": float(test_fit_plastic.max()),
        "R_fit_frozen_999": R_fit_frozen_999,
        "R_fit_plastic_999": R_fit_plastic_999,
        "R_fit_delta_999": R_fit_plastic_999 - R_fit_frozen_999,
        "GT_bypass_fraction": GT_bypass_fraction,
        "n_non_bypass": n_non_bypass,
        "Baldwin_slope": slope,
        "Baldwin_slope_bootstrap_mean": slope_boot,
        "Baldwin_slope_ci95_lo": slope_ci_lo,
        "Baldwin_slope_ci95_hi": slope_ci_hi,
        "delta_final_mean": float(delta_final.mean()),
        "delta_final_std": float(delta_final.std()),
        **gap_bins,
        **gap_counts,
        **delta_stats,
        "max_gap_at_budget_5": max_gap,
        "top1_winner_hamming": top1_winner_hamming,
        **winner_metrics,  # §v2.5-plasticity-2c: 6 new per-run columns
        **winner_k_draw,   # §v2.5-plasticity-2d: 4 new per-run k-draw columns
    })
    return row


def _compute_max_gap_at_budget_5(
    gap_bins: dict[str, float | None],
    gap_counts: dict[str, int],
    min_count: int = 5,
) -> float:
    """§v2.5-plasticity-2a v4 canonical definition.

    Per-seed max of Baldwin_gap across Hamming bins h ∈ {2, 3, ≥4} with a
    sparse-bin guard: any bin with fewer than `min_count` non-GT-bypass
    individuals is excluded (treated as nan) from the max. Returns nan
    when every bin is excluded; row 7 grid-miss fires at the cell-level
    CI if too many seeds are nan.
    """
    candidates: list[float] = []
    for key, count_key in (
        ("Baldwin_gap_h2", "count_h2"),
        ("Baldwin_gap_h3", "count_h3"),
        ("Baldwin_gap_h_ge4", "count_h_ge4"),
    ):
        v = gap_bins.get(key)
        c = gap_counts.get(count_key, 0)
        if v is None or c < min_count:
            continue
        candidates.append(float(v))
    return max(candidates) if candidates else float("nan")


def _select_top1_winner_idx(data) -> int | None:
    """§v2.5-plasticity-2a v10 verbatim winner selection + v11 schema-check guard.

    Returns the top-1 winner's population index (deterministic tiebreak),
    or None when the schema-check guard fires. A None return routes the
    chronicle-time row-1 verdict to BLOCKED per the artifact-complete floor.

    Winner selection: argmax over ``test_fitness_plastic``, tiebroken by
    ``train_fitness_plastic`` over the argmax set, then by smallest
    genotype index (numpy argmax's first-max behaviour).

    Shared by _compute_top1_winner_hamming (deprecated cap=4 metric) and
    _compute_winner_structural_metrics (§v2.5-plasticity-2c uncapped
    Levenshtein + 5 other winner metrics).
    """
    required = ("genotypes", "test_fitness_plastic", "train_fitness_plastic")
    for name in required:
        if name not in data.files:
            return None

    genotypes = data["genotypes"]
    test_fit_plastic = data["test_fitness_plastic"]
    train_fit_plastic = data["train_fitness_plastic"]

    if not (
        genotypes.shape[0]
        == test_fit_plastic.shape[0]
        == train_fit_plastic.shape[0]
    ):
        return None

    candidates = np.flatnonzero(test_fit_plastic == test_fit_plastic.max())
    return int(candidates[np.argmax(train_fit_plastic[candidates])])


def _compute_top1_winner_hamming(
    data,
    can_active: np.ndarray,
    alphabet: str,
) -> float:
    """§v2.5-plasticity-2a top1_winner_hamming (v9 / v10 / v11).

    DEPRECATED in §v2.5-plasticity-2c (replaced by
    ``top1_winner_levenshtein_uncapped`` — see §v2.5-plasticity-2c prereg
    METRIC_DEFINITIONS extensions). Retained for backwards compatibility
    with the §v2.5-plasticity-2a chronicle's reported numbers (commit
    c08888a); new analyses should use the uncapped metric.

    Schema-check guard: returns nan when ``final_population.npz`` lacks
    the required fields OR their shape[0] values disagree (routes
    chronicle-time row-1 verdict to BLOCKED).

    Distance: ``levenshtein(extract_active(genotypes[winner_idx], alphabet),
    can_active, cap=4)``. Values ∈ {0, 1, 2, 3, 4, 5} for schema-complete
    runs (5 is the cap+1 sentinel for distance > 4).
    """
    winner_idx = _select_top1_winner_idx(data)
    if winner_idx is None:
        return float("nan")

    winner_active = extract_active(data["genotypes"][winner_idx], alphabet)
    return float(levenshtein(winner_active, can_active, cap=4))


def _classify_attractor_category(winner_active_set: set[int]) -> str:
    """§v2.5-plasticity-2c attractor-category classifier — verbatim from the
    §v2.5-plasticity-2c prereg METRIC_DEFINITIONS extensions entry.

    Input: winner's active-view tokens as a set[int]. Output: one of
    {'compositional_AND', 'max>5-only', 'sum>10-only', 'other'}.

    Classification (prereg verbatim):
      - max>5-only: has {REDUCE_MAX, CONST_5, GT} (strict 3-token) AND no SUM.
      - sum>10-only: has {SUM, GT or IF_GT} AND no REDUCE_MAX AND no CONST_5.
      - compositional_AND: has >=1 of {REDUCE_MAX, CONST_5} AND >=1 of {SUM}
        AND >=1 of {GT, IF_GT}.
      - other: none of the above.

    Check order matters (first-match wins): max>5-only → sum>10-only →
    compositional_AND → other. This matches the inspection Section 1.4
    code-order; compositional_AND is the permissive catch for winners that
    have at least one max-hint-token plus the sum-blocks.
    """
    REDUCE_MAX, CONST_5, GT, SUM, IF_GT = 18, 16, 8, 5, 17

    has_reduce_max = REDUCE_MAX in winner_active_set
    has_const_5 = CONST_5 in winner_active_set
    has_gt = GT in winner_active_set
    has_sum = SUM in winner_active_set
    has_if_gt = IF_GT in winner_active_set

    # 1. max>5-only: strict 3-token max set AND no SUM
    if has_reduce_max and has_const_5 and has_gt and not has_sum:
        return "max>5-only"

    # 2. sum>10-only: SUM + (GT or IF_GT) AND no REDUCE_MAX AND no CONST_5
    if has_sum and (has_gt or has_if_gt) and not has_reduce_max and not has_const_5:
        return "sum>10-only"

    # 3. compositional_AND: (REDUCE_MAX or CONST_5) AND SUM AND (GT or IF_GT)
    if (has_reduce_max or has_const_5) and has_sum and (has_gt or has_if_gt):
        return "compositional_AND"

    # 4. other
    return "other"


def _compute_winner_structural_metrics(
    data,
    winner_idx: int,
    can_active: tuple[int, ...],
    alphabet: str,
) -> dict:
    """§v2.5-plasticity-2c per-run winner-structural metrics (6 new columns).

    Computes on the deterministic top-1 winner (see _select_top1_winner_idx):

    - top1_winner_overhead: active_len − 12 (canonical).
    - top1_winner_plasticity_active_count: count of {GT, IF_GT, THRESHOLD_SLOT}.
    - top1_winner_levenshtein_uncapped: full Levenshtein (no cap) to canonical.
    - top1_winner_attractor_category: 'compositional_AND' | 'max>5-only' |
      'sum>10-only' | 'other'.
    - top1_winner_canonical_token_set_size: |{canonical operators} ∩ {winner}|.
    - top1_winner_baldwin_gap: test_fitness_plastic[winner] − test_fitness_frozen[winner].

    Returns dict keyed by METRIC_DEFINITIONS names. Caller verifies the
    winner-idx is not None before calling (use _select_top1_winner_idx).
    """
    genotype = data["genotypes"][winner_idx]
    test_fit_plastic = data["test_fitness_plastic"]
    test_fit_frozen = data["test_fitness_frozen"]

    winner_active = extract_active(genotype, alphabet)  # tuple[int, ...]
    active_len = len(winner_active)
    winner_set = set(winner_active)

    overhead = active_len - _CANONICAL_ACTIVE_LEN
    plactv_count = sum(
        1 for t in winner_active if t in _PLASTICITY_ACTIVE_TOKEN_SET
    )
    lev_uncapped = int(levenshtein(winner_active, can_active))  # cap=None
    category = _classify_attractor_category(winner_set)
    canonical_present = len(_CANONICAL_ACTIVE_TOKEN_SET & winner_set)
    baldwin_gap = float(test_fit_plastic[winner_idx]) - float(
        test_fit_frozen[winner_idx]
    )

    return {
        "top1_winner_overhead": int(overhead),
        "top1_winner_plasticity_active_count": int(plactv_count),
        "top1_winner_levenshtein_uncapped": int(lev_uncapped),
        "top1_winner_attractor_category": category,
        "top1_winner_canonical_token_set_size": int(canonical_present),
        "top1_winner_baldwin_gap": baldwin_gap,
    }


def _cell_key(row: dict) -> tuple:
    """§v2.5-plasticity-2d: grouping tuple extended to include
    `plasticity_mechanism` so §2c plastic cells and §2d random-sample
    cells at the same (arm, plasticity_enabled, plasticity_budget,
    seed_fraction) do NOT collapse into the same cell. Backward-
    compatible: existing pre-§2d rows default plasticity_mechanism to
    'rank1_op_threshold' in `_row_common`, so re-analyzing §2a/§2c
    CSVs under the new cell key reproduces the old cell assignments.
    """
    return (
        row["arm"],
        row["plasticity_enabled"],
        row.get("plasticity_mechanism", "rank1_op_threshold"),
        row["plasticity_budget"],
        row["seed_fraction"],
    )


def bootstrap_mean_ci(
    xs: np.ndarray,
    n_boot: int = 10_000,
    rng_seed: int = 42,
    min_n: int = 15,
) -> tuple[float, float]:
    """§v2.5-plasticity-2a cell-level seed-bootstrap 95% CI on the mean.

    Nan values are dropped before resampling. Returns (nan, nan) when
    fewer than `min_n` non-nan seeds remain — the row 7 grid-miss
    trigger per the prereg's max_gap_at_budget_5_cell_boot_ci definition.
    Matches bootstrap_ci_spec (rng seed 42, 10 000 resamples, [2.5%,
    97.5%] empirical quantile).
    """
    xs = np.asarray(xs, dtype=np.float64)
    xs = xs[~np.isnan(xs)]
    if len(xs) < min_n:
        return float("nan"), float("nan")
    rng = np.random.default_rng(rng_seed)
    boots = rng.choice(xs, size=(n_boot, len(xs)), replace=True).mean(axis=1)
    return float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))


def bootstrap_mean_ci_97_5(
    xs: np.ndarray,
    n_boot: int = 10_000,
    rng_seed: int = 42,
    min_n: int = 15,
) -> tuple[float, float]:
    """§v2.5-plasticity-2c 97.5% CI variant (family α = 0.025 under
    Bonferroni for the plasticity-narrow-plateau family at size 2).

    Returns (CI_lo at 1.25% quantile, CI_hi at 98.75% quantile). Nan
    values dropped before resampling. Returns (nan, nan) if fewer than
    ``min_n`` non-nan seeds remain.

    Used by f_and_test_plastic_seed_boot_ci (per-cell descriptive) and
    as a building block for f_and_test_plastic_paired_boot_ci_budget40_vs_budget5
    (primary confirmatory; see ``paired_bootstrap_budget40_vs_budget5``).
    """
    xs = np.asarray(xs, dtype=np.float64)
    xs = xs[~np.isnan(xs)]
    if len(xs) < min_n:
        return float("nan"), float("nan")
    rng = np.random.default_rng(rng_seed)
    boots = rng.choice(xs, size=(n_boot, len(xs)), replace=True).mean(axis=1)
    return float(np.quantile(boots, 0.0125)), float(np.quantile(boots, 0.9875))


def paired_bootstrap_budget40_vs_budget5(
    current_rows: list[dict],
    baseline_budget5_indicators_by_seed: dict[int, int],
    seed_range: tuple[int, int] = (20, 39),
    n_boot: int = 10_000,
    rng_seed: int = 42,
) -> dict:
    """§v2.5-plasticity-2c PRIMARY confirmatory test — paired-bootstrap
    97.5% CI on per-seed F_AND_test_plastic difference budget=40 minus
    budget=5 on shared seeds 20..39 (n=20 paired differences).

    Family: plasticity-narrow-plateau (size 2 after this prereg joins);
    corrected α = 0.05/2 = 0.025. 97.5% two-sided CI ([1.25%, 98.75%]
    quantiles) matches family α via either-side rejection (CI_lo > 0 → H1
    PASS; CI_hi < 0 → H-reverse).

    Inputs:
      current_rows: per-run rows from the §2c sweep (must include
        budget=40 plastic runs with best_fitness_test_plastic + seed).
      baseline_budget5_indicators_by_seed: dict {seed: 0|1} for the 20
        budget=5 seeds, pre-extracted from the §v2.5-plasticity-2a
        plasticity.csv (see Setup § "Shared-seed extraction" in the prereg).
      seed_range: (lo, hi) inclusive — default (20, 39).

    Seed-integrity pre-check (SWAMPED routing):
      Before bootstrapping, verify exactly 20 unique seeds in
      seed_range ∈ each cell. Any missing/duplicated/extra seed →
      swamped = True and CI values = nan.

    Returns dict with keys:
      - f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_lo
      - f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_hi
      - f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_n_paired
      - f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped
        (bool — True if seed-integrity pre-check failed; routes row 6)
      - f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason
        (str — description of anomaly, or empty string on clean pre-check)
    """
    seed_lo, seed_hi = seed_range
    expected_seeds = set(range(seed_lo, seed_hi + 1))

    # Extract budget=40 indicators from current_rows
    b40_by_seed: dict[int, list[int]] = {}  # allow duplicate detection
    for r in current_rows:
        if not r.get("plasticity_enabled"):
            continue
        try:
            if int(r.get("plasticity_budget", 0)) != 40:
                continue
        except (TypeError, ValueError):
            continue
        try:
            seed = int(r.get("seed"))
        except (TypeError, ValueError):
            continue
        tfp = r.get("best_fitness_test_plastic")
        if tfp is None or tfp == "":
            continue
        try:
            indicator = int(float(tfp) >= 1.0 - 1e-9)
        except (TypeError, ValueError):
            continue
        b40_by_seed.setdefault(seed, []).append(indicator)

    # Seed-integrity pre-check on budget=40 cell
    swamped_reasons: list[str] = []
    b40_seen_seeds = set(b40_by_seed.keys())
    for s in b40_by_seed:
        if len(b40_by_seed[s]) > 1:
            swamped_reasons.append(
                f"budget=40 cell: seed {s} duplicated "
                f"({len(b40_by_seed[s])} rows)"
            )
    missing_b40 = expected_seeds - b40_seen_seeds
    if missing_b40:
        swamped_reasons.append(
            f"budget=40 cell: missing seed(s) {sorted(missing_b40)}"
        )
    extra_b40 = b40_seen_seeds - expected_seeds
    if extra_b40:
        swamped_reasons.append(
            f"budget=40 cell: extra seed(s) {sorted(extra_b40)} outside "
            f"[{seed_lo}, {seed_hi}]"
        )

    # Seed-integrity pre-check on budget=5 baseline
    b5_seen_seeds = set(baseline_budget5_indicators_by_seed.keys())
    missing_b5 = expected_seeds - b5_seen_seeds
    if missing_b5:
        swamped_reasons.append(
            f"budget=5 baseline: missing seed(s) {sorted(missing_b5)}"
        )
    extra_b5 = b5_seen_seeds - expected_seeds
    if extra_b5:
        swamped_reasons.append(
            f"budget=5 baseline: extra seed(s) {sorted(extra_b5)} outside "
            f"[{seed_lo}, {seed_hi}]"
        )

    if swamped_reasons:
        return {
            "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_lo": float("nan"),
            "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_hi": float("nan"),
            "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_n_paired": 0,
            "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped": True,
            "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason":
                "; ".join(swamped_reasons),
            "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_point_estimate":
                float("nan"),
        }

    # Build paired-difference vector on seeds 20..39 (deterministic order)
    paired_diffs: list[int] = []
    for s in sorted(expected_seeds):
        b40_ind = b40_by_seed[s][0]
        b5_ind = baseline_budget5_indicators_by_seed[s]
        paired_diffs.append(b40_ind - b5_ind)

    paired_arr = np.asarray(paired_diffs, dtype=np.float64)
    rng = np.random.default_rng(rng_seed)
    boots = rng.choice(
        paired_arr, size=(n_boot, len(paired_arr)), replace=True
    ).mean(axis=1)
    ci_lo = float(np.quantile(boots, 0.0125))
    ci_hi = float(np.quantile(boots, 0.9875))
    point_estimate = float(paired_arr.mean())

    return {
        "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_lo": ci_lo,
        "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_hi": ci_hi,
        "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_n_paired": len(paired_arr),
        "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped": False,
        "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason": "",
        "f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_point_estimate": point_estimate,
    }


def extract_budget5_indicators_from_csv(
    csv_path: Path, seed_range: tuple[int, int] = (20, 39),
) -> dict[int, int]:
    """§v2.5-plasticity-2c Setup § "Shared-seed extraction" step 1-4 (verbatim).

    Loads a sweep's plasticity.csv, filters to plastic budget=5 Arm A rows
    within the seed range, and returns {seed: 0|1} binary indicator dict
    (indicator = ``best_fitness_test_plastic >= 1.0``).

    Only §v2.5-plasticity-2a seeds 20..39 are included by default; the
    seed-integrity pre-check in ``paired_bootstrap_budget40_vs_budget5``
    verifies that exactly 20 seeds are present post-extraction.
    """
    import csv
    seed_lo, seed_hi = seed_range
    indicators: dict[int, int] = {}
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("plasticity_enabled") != "True":
                continue
            if row.get("arm") != "A":
                continue
            try:
                if int(row.get("plasticity_budget", "0")) != 5:
                    continue
                seed = int(row.get("seed"))
            except (TypeError, ValueError):
                continue
            if seed < seed_lo or seed > seed_hi:
                continue
            tfp = row.get("best_fitness_test_plastic")
            if not tfp:
                continue
            try:
                indicators[seed] = int(float(tfp) >= 1.0 - 1e-9)
            except (TypeError, ValueError):
                continue
    return indicators


# ---------------- §v2.5-plasticity-2d CI routines ----------------


def bootstrap_mean_ci_98_333(
    xs: np.ndarray,
    n_boot: int = 10_000,
    rng_seed: int = 42,
    min_n: int = 15,
) -> tuple[float, float]:
    """§v2.5-plasticity-2d 98.333% CI variant (family α = 0.01667 under
    Bonferroni for the plasticity-narrow-plateau family at size 3).

    Returns (CI_lo at 0.8333% quantile, CI_hi at 99.1667% quantile). Nan
    values dropped before resampling. Returns (nan, nan) if fewer than
    ``min_n`` non-nan seeds remain.

    Used by f_and_test_plastic_seed_boot_ci_98_333 (per-cell descriptive)
    and as a building block for f_and_test_plastic_paired_boot_ci_plastic40_
    vs_random40 (primary confirmatory; see ``paired_bootstrap_plastic40_
    vs_random40``).
    """
    xs = np.asarray(xs, dtype=np.float64)
    xs = xs[~np.isnan(xs)]
    if len(xs) < min_n:
        return float("nan"), float("nan")
    rng = np.random.default_rng(rng_seed)
    boots = rng.choice(xs, size=(n_boot, len(xs)), replace=True).mean(axis=1)
    return (
        float(np.quantile(boots, 0.008333)),
        float(np.quantile(boots, 0.991667)),
    )


def extract_plastic_budget40_indicators_from_csv(
    csv_path: Path, seed_range: tuple[int, int] = (20, 39),
) -> dict[int, int | list[int]]:
    """§v2.5-plasticity-2d Setup § "Shared-seed extraction" step 1-4.

    Loads a sweep's plasticity.csv (post-§2c data), filters to
    ``plasticity_enabled=True AND plasticity_mechanism='rank1_op_threshold'
    AND plasticity_budget=40 AND arm='A' AND seed_fraction='0.0'`` rows
    within the seed range, and returns a seed→indicator mapping.

    **Duplicate-seed detection (codex-v4 P1-2 correction):** When a seed
    appears more than once in the filtered rows, the returned value at
    that seed is a ``list[int]`` of every row's indicator rather than a
    scalar ``int``. ``paired_bootstrap_plastic40_vs_random40`` inspects
    the value type at each seed; a list value routes Row 6 SWAMPED with
    a duplicate-baseline-row reason. This prevents silent overwriting of
    duplicate reused-§2c rows, which under the naive dict-assignment
    contract would pass the seed-integrity pre-check even though the
    reused data is corrupt.

    Parallel to ``extract_budget5_indicators_from_csv`` but scoped to the
    plastic budget=40 cell reused from §2c. Missing the
    ``plasticity_mechanism`` column (e.g. in pre-§2d CSV files) is
    treated as the default ``'rank1_op_threshold'`` for backward
    compatibility.

    The seed-integrity pre-check in
    ``paired_bootstrap_plastic40_vs_random40`` verifies that exactly 20
    seeds are present post-extraction AND that no seed has a list value
    (duplicate rows).
    """
    import csv
    seed_lo, seed_hi = seed_range
    raw_by_seed: dict[int, list[int]] = {}
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("plasticity_enabled") != "True":
                continue
            if row.get("arm") != "A":
                continue
            mech = row.get("plasticity_mechanism", "rank1_op_threshold") or "rank1_op_threshold"
            if mech != "rank1_op_threshold":
                continue
            try:
                if int(row.get("plasticity_budget", "0")) != 40:
                    continue
                if float(row.get("seed_fraction", "0") or "0") != 0.0:
                    continue
                seed = int(row.get("seed"))
            except (TypeError, ValueError):
                continue
            if seed < seed_lo or seed > seed_hi:
                continue
            tfp = row.get("best_fitness_test_plastic")
            if not tfp:
                continue
            try:
                raw_by_seed.setdefault(seed, []).append(
                    int(float(tfp) >= 1.0 - 1e-9)
                )
            except (TypeError, ValueError):
                continue
    # Collapse unique-seed entries to scalar int; leave duplicates as
    # list so downstream caller can detect them.
    out: dict[int, int | list[int]] = {}
    for seed, vals in raw_by_seed.items():
        if len(vals) == 1:
            out[seed] = vals[0]
        else:
            out[seed] = vals
    return out


def paired_bootstrap_plastic40_vs_random40(
    current_rows: list[dict],
    baseline_plastic40_indicators_by_seed: dict[int, int],
    seed_range: tuple[int, int] = (20, 39),
    n_boot: int = 10_000,
    rng_seed: int = 42,
) -> dict:
    """§v2.5-plasticity-2d PRIMARY confirmatory test — paired-bootstrap
    98.333% CI on per-seed F_AND_test_plastic difference
    ``plastic[mechanism=rank1_op_threshold, budget=40]`` minus
    ``random[mechanism=random_sample_threshold, budget=40]`` on shared
    seeds 20..39 (n=20 paired differences).

    Family: plasticity-narrow-plateau (size 3 after this prereg joins);
    corrected α = 0.05/3 ≈ 0.01667. 98.333% two-sided CI ([0.8333%,
    99.1667%] quantiles) matches family α via either-side rejection
    (CI_lo > 0 → Row 1 PASS-POSITIVE; CI_hi < 0 → Row 5 REVERSE).

    Inputs:
      current_rows: per-run rows from the §2d sweep. Must include
        random-sample budget=40 plastic runs with
        ``best_fitness_test_plastic``, ``plasticity_mechanism``,
        ``plasticity_budget``, and ``seed`` fields.
      baseline_plastic40_indicators_by_seed: dict ``{seed: 0|1}`` for the
        20 plastic budget=40 seeds, pre-extracted from the
        §v2.5-plasticity-2c plasticity.csv (see Setup § "Shared-seed
        extraction" in the §2d prereg).
      seed_range: (lo, hi) inclusive — default (20, 39).

    Seed-integrity pre-check (Row 6 SWAMPED routing): before
    bootstrapping, verify exactly 20 unique seeds in ``seed_range`` on
    each cell. Any missing/duplicated/extra seed → ``swamped = True``
    and CI values = nan.

    Returns dict with keys (parallel to
    ``paired_bootstrap_budget40_vs_budget5`` §2c contract):
      - f_and_test_plastic_paired_boot_ci_plastic40_vs_random40_lo
      - f_and_test_plastic_paired_boot_ci_plastic40_vs_random40_hi
      - f_and_test_plastic_paired_boot_ci_plastic40_vs_random40_n_paired
      - f_and_test_plastic_paired_boot_ci_plastic40_vs_random40_swamped
      - f_and_test_plastic_paired_boot_ci_plastic40_vs_random40_swamped_reason
      - f_and_test_plastic_paired_boot_ci_plastic40_vs_random40_point_estimate
    """
    seed_lo, seed_hi = seed_range
    expected_seeds = set(range(seed_lo, seed_hi + 1))

    # Extract random-sample budget=40 indicators from current_rows
    rnd40_by_seed: dict[int, list[int]] = {}
    for r in current_rows:
        if not r.get("plasticity_enabled"):
            continue
        mech = r.get("plasticity_mechanism", "rank1_op_threshold")
        if mech != "random_sample_threshold":
            continue
        try:
            if int(r.get("plasticity_budget", 0)) != 40:
                continue
        except (TypeError, ValueError):
            continue
        try:
            seed = int(r.get("seed"))
        except (TypeError, ValueError):
            continue
        tfp = r.get("best_fitness_test_plastic")
        if tfp is None or tfp == "":
            continue
        try:
            indicator = int(float(tfp) >= 1.0 - 1e-9)
        except (TypeError, ValueError):
            continue
        rnd40_by_seed.setdefault(seed, []).append(indicator)

    # Seed-integrity pre-check on random-sample budget=40 cell
    swamped_reasons: list[str] = []
    rnd40_seen_seeds = set(rnd40_by_seed.keys())
    for s in rnd40_by_seed:
        if len(rnd40_by_seed[s]) > 1:
            swamped_reasons.append(
                f"random-sample budget=40 cell: seed {s} duplicated "
                f"({len(rnd40_by_seed[s])} rows)"
            )
    missing_rnd40 = expected_seeds - rnd40_seen_seeds
    if missing_rnd40:
        swamped_reasons.append(
            f"random-sample budget=40 cell: missing seed(s) "
            f"{sorted(missing_rnd40)}"
        )
    extra_rnd40 = rnd40_seen_seeds - expected_seeds
    if extra_rnd40:
        swamped_reasons.append(
            f"random-sample budget=40 cell: extra seed(s) "
            f"{sorted(extra_rnd40)} outside [{seed_lo}, {seed_hi}]"
        )

    # Seed-integrity pre-check on plastic budget=40 baseline
    pl40_seen_seeds = set(baseline_plastic40_indicators_by_seed.keys())
    missing_pl40 = expected_seeds - pl40_seen_seeds
    if missing_pl40:
        swamped_reasons.append(
            f"plastic budget=40 baseline: missing seed(s) "
            f"{sorted(missing_pl40)}"
        )
    extra_pl40 = pl40_seen_seeds - expected_seeds
    if extra_pl40:
        swamped_reasons.append(
            f"plastic budget=40 baseline: extra seed(s) "
            f"{sorted(extra_pl40)} outside [{seed_lo}, {seed_hi}]"
        )
    # §v2.5-plasticity-2d codex-v4 P1-2 correction: detect duplicate
    # seeds in the baseline (extracted as list-valued entries by
    # ``extract_plastic_budget40_indicators_from_csv``).
    duplicated_pl40: list[int] = []
    for s, v in baseline_plastic40_indicators_by_seed.items():
        if isinstance(v, list):
            duplicated_pl40.append(s)
    if duplicated_pl40:
        swamped_reasons.append(
            f"plastic budget=40 baseline: duplicated seed(s) "
            f"{sorted(duplicated_pl40)} (multiple rows per seed in "
            f"baseline CSV)"
        )

    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    if swamped_reasons:
        return {
            f"{key_prefix}_lo": float("nan"),
            f"{key_prefix}_hi": float("nan"),
            f"{key_prefix}_n_paired": 0,
            f"{key_prefix}_swamped": True,
            f"{key_prefix}_swamped_reason": "; ".join(swamped_reasons),
            f"{key_prefix}_point_estimate": float("nan"),
        }

    # Build paired-difference vector: plastic − random (matches H1 direction)
    paired_diffs: list[int] = []
    for s in sorted(expected_seeds):
        pl_ind = baseline_plastic40_indicators_by_seed[s]
        rnd_ind = rnd40_by_seed[s][0]
        paired_diffs.append(pl_ind - rnd_ind)

    paired_arr = np.asarray(paired_diffs, dtype=np.float64)
    rng = np.random.default_rng(rng_seed)
    boots = rng.choice(
        paired_arr, size=(n_boot, len(paired_arr)), replace=True
    ).mean(axis=1)
    ci_lo = float(np.quantile(boots, 0.008333))
    ci_hi = float(np.quantile(boots, 0.991667))
    point_estimate = float(paired_arr.mean())

    return {
        f"{key_prefix}_lo": ci_lo,
        f"{key_prefix}_hi": ci_hi,
        f"{key_prefix}_n_paired": len(paired_arr),
        f"{key_prefix}_swamped": False,
        f"{key_prefix}_swamped_reason": "",
        f"{key_prefix}_point_estimate": point_estimate,
    }


def _build_frozen_rfit_lookup(rows: list[dict]) -> dict[tuple, float]:
    """§v2.5-plasticity-2a R_fit_delta_paired_sf0 cross-cell merge table.

    Indexes frozen-control runs (plasticity_enabled=False, sf=0.0) by
    (arm, seed) so plastic cells can look up the matched frozen seed's
    R_fit_frozen_999 without re-walking every row. Only sf=0.0 frozen
    runs are indexed — the secondary diagnostic is defined at sf=0.0
    only per the prereg's wording.
    """
    lookup: dict[tuple, float] = {}
    for r in rows:
        if r.get("plasticity_enabled"):
            continue
        if float(r.get("seed_fraction", -1.0)) != 0.0:
            continue
        rfit = r.get("R_fit_frozen_999")
        if rfit is None:
            continue
        lookup[(r["arm"], int(r["seed"]))] = float(rfit)
    return lookup


def summarize(rows: list[dict]) -> dict:
    cells: dict[tuple, list[dict]] = {}
    for r in rows:
        cells.setdefault(_cell_key(r), []).append(r)

    frozen_lookup = _build_frozen_rfit_lookup(rows)

    summary = []
    for key, members in sorted(cells.items()):
        # §v2.5-plasticity-2d: 5-tuple key now includes plasticity_mechanism.
        arm, pl_enabled, pl_mechanism, pl_budget, sf = key
        # Per-cell means of scalar run-level metrics.
        def _mean(colname: str) -> float | None:
            vals = [m[colname] for m in members if m.get(colname) is not None
                    and not (isinstance(m[colname], float) and np.isnan(m[colname]))]
            return float(np.mean(vals)) if vals else None

        # §v2.5-plasticity-2a: cell-level seed-bootstrap CI + seed-majority
        # count on max_gap_at_budget_5. Per the prereg's statistical-test
        # block, this is meaningful only at the plastic budget=5 cell —
        # the single confirmatory axis. Emitted at every plastic cell for
        # descriptive monotonicity checks; the row-3 / row-1 / row-5 gates
        # at chronicle time consume only the budget=5 value.
        max_gap_vals = np.array(
            [m.get("max_gap_at_budget_5") for m in members
             if m.get("max_gap_at_budget_5") is not None],
            dtype=np.float64,
        )
        if pl_enabled and max_gap_vals.size > 0:
            max_gap_mean = (
                float(np.nanmean(max_gap_vals))
                if np.any(~np.isnan(max_gap_vals)) else None
            )
            max_gap_ci_lo, max_gap_ci_hi = bootstrap_mean_ci(max_gap_vals)
            max_gap_seed_majority = int(
                np.sum((max_gap_vals > 0.10) & (~np.isnan(max_gap_vals)))
            )
            max_gap_seed_minority_0_05 = int(
                np.sum((max_gap_vals > 0.05) & (~np.isnan(max_gap_vals)))
            )
            max_gap_n_non_nan = int(np.sum(~np.isnan(max_gap_vals)))
        else:
            max_gap_mean = None
            max_gap_ci_lo = max_gap_ci_hi = float("nan")
            max_gap_seed_majority = 0
            max_gap_seed_minority_0_05 = 0
            max_gap_n_non_nan = 0

        # §v2.5-plasticity-2a top1_winner_hamming cell-level counts (v9
        # chronicle-time classical-Baldwin disambiguation discipline).
        # Categorical classification is per-seed: hamming <= 1 = CB-active,
        # >= 2 = CB-inactive. Cell-level verdict is a count over the
        # row-1-matching cell's nominal 20 seeds. Nan entries (schema-
        # incomplete runs) are counted separately — any nan routes the
        # chronicle-time row-1 verdict to BLOCKED per the artifact-complete
        # floor, regardless of the other counts.
        t1wh_vals = [
            m.get("top1_winner_hamming") for m in members
            if m.get("top1_winner_hamming") is not None
        ]
        if pl_enabled and t1wh_vals:
            t1wh_arr = np.array(t1wh_vals, dtype=np.float64)
            t1wh_n_nan = int(np.sum(np.isnan(t1wh_arr)))
            non_nan = t1wh_arr[~np.isnan(t1wh_arr)]
            t1wh_n_cb_active = int(np.sum(non_nan <= 1))
            t1wh_n_cb_inactive = int(np.sum(non_nan >= 2))
        else:
            t1wh_n_nan = 0
            t1wh_n_cb_active = 0
            t1wh_n_cb_inactive = 0

        # §v2.5-plasticity-2a: paired R_fit_plastic_999 − R_fit_frozen_999
        # at sf=0.0, joined across the plastic cell and the sf=0.0 frozen
        # control cell on (arm, seed). Secondary diagnostic — not in any
        # FWER family. The plastic cell's R_fit_plastic_999 is computed
        # from train_fit_plastic (48-example train subset); the frozen
        # cell's R_fit_frozen_999 is computed from the full-task
        # `fitnesses` array (frozen runs carry no train/test split).
        # The asymmetric denominator is noted; the metric retains its
        # diagnostic intent (did the plastic-evolved population land in
        # a different fitness distribution than the frozen-evolved one).
        paired_deltas: list[float] = []
        if pl_enabled and float(sf) == 0.0:
            for m in members:
                rp = m.get("R_fit_plastic_999")
                if rp is None:
                    continue
                key_ms = (m["arm"], int(m["seed"]))
                if key_ms not in frozen_lookup:
                    continue
                paired_deltas.append(float(rp) - frozen_lookup[key_ms])
        R_fit_delta_paired_sf0_mean = (
            float(np.mean(paired_deltas)) if paired_deltas else None
        )

        # §v2.5-plasticity-2c: F_AND_test_plastic count/fraction/CI per
        # plastic cell (primary observable per the §2c prereg). For frozen
        # cells, "solver" is defined via the best_fitness column (frozen
        # runs carry no train/test split). For plastic cells, use
        # best_fitness_test_plastic (plastic eval on 16 test examples).
        # CI width is 97.5% (quantiles [1.25%, 98.75%]) to match the
        # §2c family-α = 0.025 Bonferroni correction.
        f_indicators: list[int] = []
        if pl_enabled:
            for m in members:
                tfp = m.get("best_fitness_test_plastic")
                if tfp is None:
                    continue
                try:
                    f_indicators.append(int(float(tfp) >= 1.0 - 1e-9))
                except (TypeError, ValueError):
                    continue
        else:
            # Frozen cell: use best_fitness as the F_AND_test_plastic
            # analogue (no plastic eval available).
            for m in members:
                bf = m.get("best_fitness")
                if bf is None:
                    continue
                try:
                    f_indicators.append(int(float(bf) >= 1.0 - 1e-9))
                except (TypeError, ValueError):
                    continue

        f_count = sum(f_indicators)
        f_n = len(f_indicators)
        f_fraction = float(f_count) / f_n if f_n > 0 else None
        # 97.5% seed-bootstrap CI on F_AND_test_plastic fraction. min_n=15
        # kept consistent with the project's bootstrap convention; §2c
        # cells have n=20 (or n=40 pooled at budget=5), well above the
        # floor.
        if f_n >= 15:
            f_ci_arr = np.asarray(f_indicators, dtype=np.float64)
            f_ci_lo, f_ci_hi = bootstrap_mean_ci_97_5(f_ci_arr, min_n=15)
            # §v2.5-plasticity-2d: also emit the 98.333% CI (family-α=0.01667
            # Bonferroni for the plasticity-narrow-plateau family at size 3).
            # Used by chronicle-time row-clause evaluation on random-sample
            # and rank-1 cells under the §2d discipline.
            f_ci_lo_98, f_ci_hi_98 = bootstrap_mean_ci_98_333(f_ci_arr, min_n=15)
        else:
            f_ci_lo = f_ci_hi = float("nan")
            f_ci_lo_98 = f_ci_hi_98 = float("nan")

        # §v2.5-plasticity-2d: per-cell delta_final support-bound aggregates
        # (Guard-6 / Row 6 SWAMPED mechanism-sanity pre-check). Emitted on
        # every cell; for rank-1 cells these are the integer-lattice
        # ±budget*delta endpoints (same formal bound as random-sample's
        # continuous support).
        df_vals: list[float] = []
        for m in members:
            v = m.get("delta_final_mean")
            if v is None:
                continue
            if isinstance(v, float) and np.isnan(v):
                continue
            try:
                df_vals.append(float(v))
            except (TypeError, ValueError):
                continue
        df_min = float(min(df_vals)) if df_vals else float("nan")
        df_max = float(max(df_vals)) if df_vals else float("nan")
        df_std = (
            float(np.std(np.asarray(df_vals, dtype=np.float64)))
            if df_vals else float("nan")
        )
        df_abs_mean = (
            float(np.mean(np.abs(np.asarray(df_vals, dtype=np.float64))))
            if df_vals else float("nan")
        )

        # §v2.5-plasticity-2d: per-cell k-draw winner summary (random-sample
        # mechanism only). Aggregates the top-1 winner's k-draw statistics
        # across seeds. Used at chronicle time as Guard-6 sub-criterion (c)
        # input. Also drives the per-cell mechanism-sanity pre-check: any
        # cell whose top-1 winners' k-draws violate support-bounds or
        # collapse in variance routes Row 6 SWAMPED.
        def _col_float_nonnan(colname: str) -> list[float]:
            out: list[float] = []
            for m in members:
                v = m.get(colname)
                if v is None or v == "":
                    continue
                if isinstance(v, float) and np.isnan(v):
                    continue
                try:
                    out.append(float(v))
                except (TypeError, ValueError):
                    continue
            return out

        kd_min_vals = _col_float_nonnan("winner_k_draw_min")
        kd_max_vals = _col_float_nonnan("winner_k_draw_max")
        kd_std_vals = _col_float_nonnan("winner_k_draw_std")
        # §v2.5-plasticity-2d codex-v5 P1-1: aggregate argmax_index
        # across seeds (integer). If any seed's argmax_index is outside
        # [0, budget-1], routes Row 6 SWAMPED via swamped_k_draw.
        kd_argmax_vals: list[int] = []
        for m in members:
            v = m.get("winner_k_argmax_index")
            if v is None or v == "":
                continue
            try:
                kd_argmax_vals.append(int(v))
            except (TypeError, ValueError):
                continue
        winner_kd_min_min = float(min(kd_min_vals)) if kd_min_vals else None
        winner_kd_max_max = float(max(kd_max_vals)) if kd_max_vals else None
        winner_kd_std_min = float(min(kd_std_vals)) if kd_std_vals else None
        winner_kd_std_mean = (
            float(np.mean(kd_std_vals)) if kd_std_vals else None
        )
        winner_kd_argmax_min = (
            int(min(kd_argmax_vals)) if kd_argmax_vals else None
        )
        winner_kd_argmax_max = (
            int(max(kd_argmax_vals)) if kd_argmax_vals else None
        )
        # Guard-6 (c) cell-level SWAMPED trigger. Only meaningful on
        # random-sample cells; emitted on all cells for schema uniformity.
        is_random_sample = pl_mechanism == "random_sample_threshold"
        swamped_k_draw = False
        swamped_k_draw_reasons: list[str] = []
        if is_random_sample:
            budget_f = float(pl_budget)
            # codex-v5 P1-2 + codex-v6 P1-1: random-sample cell with NO
            # k-draw data on ANY of the 4 mandatory columns is itself a
            # SWAMPED trigger — infrastructure failed to emit the
            # mandatory per-individual k-draw 4-tuple. Without this,
            # a broken NPZ/CSV path silently passes Guard-6(c). The
            # 4-tuple schema (min_draw, max_draw, std_draws,
            # argmax_index) is enforced as all-or-none across each of
            # the four per-run columns.
            n_members = len(members)
            column_counts = {
                "winner_k_draw_min": len(kd_min_vals),
                "winner_k_draw_max": len(kd_max_vals),
                "winner_k_draw_std": len(kd_std_vals),
                "winner_k_argmax_index": len(kd_argmax_vals),
            }
            missing_fully = [
                col for col, c in column_counts.items() if c == 0
            ]
            if n_members > 0 and missing_fully:
                swamped_k_draw_reasons.append(
                    f"random_sample_threshold cell at budget={pl_budget} "
                    f"has {n_members} members but NO values for column(s) "
                    f"{sorted(missing_fully)} — mandatory k-draw 4-tuple "
                    f"logging appears broken. Check final_population.npz "
                    f"emission in run.py and _cell_key extraction in "
                    f"analyze_plasticity.py."
                )
            partial = [
                col for col, c in column_counts.items()
                if 0 < c < n_members
            ]
            if n_members > 0 and partial:
                parts = ", ".join(
                    f"{col}={column_counts[col]}/{n_members}" for col in sorted(partial)
                )
                swamped_k_draw_reasons.append(
                    f"random_sample_threshold cell at budget={pl_budget}: "
                    f"partial k-draw logging failure — {parts}."
                )
            if kd_min_vals:
                # Per-cell support-bound check: min across seeds of per-run
                # min_draw must be >= -budget; max across seeds of per-run
                # max_draw must be <= +budget. Any violation → SWAMPED.
                if winner_kd_min_min is not None and winner_kd_min_min < -budget_f - 1e-9:
                    swamped_k_draw_reasons.append(
                        f"winner_k_draw_min={winner_kd_min_min:.4f} < -budget={-budget_f}"
                    )
                if winner_kd_max_max is not None and winner_kd_max_max > budget_f + 1e-9:
                    swamped_k_draw_reasons.append(
                        f"winner_k_draw_max={winner_kd_max_max:.4f} > +budget={budget_f}"
                    )
                # std-collapse check: any seed's per-run std < 0.05*budget → flag.
                std_floor = 0.05 * budget_f
                if (
                    winner_kd_std_min is not None
                    and winner_kd_std_min < std_floor - 1e-9
                ):
                    swamped_k_draw_reasons.append(
                        f"min(winner_k_draw_std)={winner_kd_std_min:.4f} < "
                        f"0.05*budget={std_floor}"
                    )
            # codex-v5 P1-1 argmax_index bound check: every seed's
            # winner_k_argmax_index must be in [0, budget-1].
            if kd_argmax_vals:
                argmax_lo_violation = winner_kd_argmax_min is not None and winner_kd_argmax_min < 0
                argmax_hi_violation = (
                    winner_kd_argmax_max is not None
                    and pl_budget > 0
                    and winner_kd_argmax_max > pl_budget - 1
                )
                if argmax_lo_violation:
                    swamped_k_draw_reasons.append(
                        f"winner_k_argmax_index min={winner_kd_argmax_min} < 0"
                    )
                if argmax_hi_violation:
                    swamped_k_draw_reasons.append(
                        f"winner_k_argmax_index max={winner_kd_argmax_max} "
                        f"> budget-1={pl_budget - 1}"
                    )
            swamped_k_draw = bool(swamped_k_draw_reasons)

        # §v2.5-plasticity-2c: per-cell medians of the 6 §26-demoted
        # winner-structural diagnostics. Computed only on plastic cells
        # (frozen-only runs lack the winner metrics). Reported descriptively;
        # NO routing clauses on these axes per the §2c prereg.
        def _median_of(colname: str) -> float | None:
            vals = []
            for m in members:
                v = m.get(colname)
                if v is None or v == "":
                    continue
                if isinstance(v, float) and np.isnan(v):
                    continue
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    continue
            return float(np.median(vals)) if vals else None

        top1_winner_attractor_counts: dict[str, int] = {
            "compositional_AND": 0,
            "max>5-only": 0,
            "sum>10-only": 0,
            "other": 0,
        }
        if pl_enabled:
            for m in members:
                cat = m.get("top1_winner_attractor_category")
                if cat in top1_winner_attractor_counts:
                    top1_winner_attractor_counts[cat] += 1

        summary.append({
            "arm": arm,
            "plasticity_enabled": pl_enabled,
            "plasticity_mechanism": pl_mechanism,
            "plasticity_budget": pl_budget,
            "seed_fraction": sf,
            "n_seeds": len(members),
            "R_fit_frozen_999_mean": _mean("R_fit_frozen_999"),
            "R_fit_plastic_999_mean": _mean("R_fit_plastic_999"),
            "R_fit_delta_999_mean": _mean("R_fit_delta_999"),
            "GT_bypass_fraction_mean": _mean("GT_bypass_fraction"),
            "Baldwin_slope_mean": _mean("Baldwin_slope"),
            "Baldwin_slope_ci95_lo_mean": _mean("Baldwin_slope_ci95_lo"),
            "Baldwin_slope_ci95_hi_mean": _mean("Baldwin_slope_ci95_hi"),
            "delta_final_mean_mean": _mean("delta_final_mean"),
            "delta_final_std_mean": _mean("delta_final_std"),
            "Baldwin_gap_h0_mean": _mean("Baldwin_gap_h0"),
            "Baldwin_gap_h1_mean": _mean("Baldwin_gap_h1"),
            "Baldwin_gap_h2_mean": _mean("Baldwin_gap_h2"),
            "Baldwin_gap_h3_mean": _mean("Baldwin_gap_h3"),
            "Baldwin_gap_h_ge4_mean": _mean("Baldwin_gap_h_ge4"),
            "max_gap_at_budget_5_mean": max_gap_mean,
            "max_gap_at_budget_5_cell_boot_ci_lo": max_gap_ci_lo,
            "max_gap_at_budget_5_cell_boot_ci_hi": max_gap_ci_hi,
            "max_gap_at_budget_5_seed_majority": max_gap_seed_majority,
            "max_gap_at_budget_5_seed_minority_0_05": max_gap_seed_minority_0_05,
            "max_gap_at_budget_5_n_non_nan_seeds": max_gap_n_non_nan,
            "top1_winner_hamming_n_cb_active": t1wh_n_cb_active,
            "top1_winner_hamming_n_cb_inactive": t1wh_n_cb_inactive,
            "top1_winner_hamming_n_nan": t1wh_n_nan,
            "R_fit_delta_paired_sf0_mean": R_fit_delta_paired_sf0_mean,
            "R_fit_delta_paired_sf0_n_pairs": len(paired_deltas),
            # §v2.5-plasticity-2c additions — primary observable + 6 §26-demoted diagnostics
            "f_and_test_plastic_count": f_count,
            "f_and_test_plastic_n": f_n,
            "f_and_test_plastic_fraction": f_fraction,
            "f_and_test_plastic_seed_boot_ci_lo": f_ci_lo,
            "f_and_test_plastic_seed_boot_ci_hi": f_ci_hi,
            "top1_winner_overhead_median": _median_of("top1_winner_overhead"),
            "top1_winner_plasticity_active_count_median": _median_of("top1_winner_plasticity_active_count"),
            "top1_winner_levenshtein_uncapped_median": _median_of("top1_winner_levenshtein_uncapped"),
            "top1_winner_canonical_token_set_size_median": _median_of("top1_winner_canonical_token_set_size"),
            "top1_winner_baldwin_gap_median": _median_of("top1_winner_baldwin_gap"),
            "top1_winner_attractor_counts": top1_winner_attractor_counts,
            # §v2.5-plasticity-2d: 98.333% seed-bootstrap CI on F_AND_test_plastic
            # (Bonferroni family α=0.01667 discipline for plasticity-narrow-
            # plateau size 3). Emitted alongside the §2c 97.5% CI so the
            # chronicle can grep the §2d-scoped family-α for routing.
            "f_and_test_plastic_seed_boot_ci_98_333_lo": f_ci_lo_98,
            "f_and_test_plastic_seed_boot_ci_98_333_hi": f_ci_hi_98,
            # §v2.5-plasticity-2d: per-cell delta_final support-bound
            # aggregates (Guard-6 / Row 6 SWAMPED mechanism-sanity
            # pre-check input).
            "delta_final_cell_support_bounds_min": df_min,
            "delta_final_cell_support_bounds_max": df_max,
            "delta_final_cell_support_bounds_std": df_std,
            "delta_final_cell_abs_mean": df_abs_mean,
            # §v2.5-plasticity-2d: per-cell top-1 winner k-draw
            # aggregates. None on rank-1 cells where the k-draw columns
            # are absent (random-sample mechanism only).
            "winner_k_draw_min_min": winner_kd_min_min,
            "winner_k_draw_max_max": winner_kd_max_max,
            "winner_k_draw_std_min": winner_kd_std_min,
            "winner_k_draw_std_mean": winner_kd_std_mean,
            # codex-v5 P1-1: argmax_index aggregation (completes the
            # METRIC_DEFINITIONS 4-tuple schema for
            # random_sample_mechanism_draw_spread).
            "winner_k_argmax_index_min": winner_kd_argmax_min,
            "winner_k_argmax_index_max": winner_kd_argmax_max,
            "winner_k_draw_swamped": swamped_k_draw,
            "winner_k_draw_swamped_reason": (
                "; ".join(swamped_k_draw_reasons) if swamped_k_draw_reasons else ""
            ),
        })
    return {
        "per_cell": summary,
        # Report both §2c's α=0.05 (97.5% CI) and §2d's family-α=0.01667
        # (98.333% CI) bootstrap specs. Downstream chronicles grep the
        # one matching their §26-demotion discipline.
        "bootstrap_spec": {"n_boot": 10_000, "alpha": 0.05, "rng_seed": 42},
        "bootstrap_spec_v2d": {
            "n_boot": 10_000, "alpha": 0.01667, "rng_seed": 42,
            "family": "plasticity-narrow-plateau", "family_size": 3,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", help="sweep name under experiments/chem_tape/output/ "
                                   "(or an absolute path)")
    ap.add_argument("--canonical-hex", default=CANONICAL_AND_BODY_HEX)
    ap.add_argument("--alphabet", default="v2_probe")
    ap.add_argument("--out", type=Path, default=None)
    # §v2.5-plasticity-2d: optional paths for the §2c plastic baseline
    # plasticity.csv (used by the primary paired-bootstrap confirmatory
    # test plastic@40 vs random@40). When present, the analyzer runs
    # `paired_bootstrap_plastic40_vs_random40` after `summarize()` and
    # appends the result to the summary JSON under the key
    # `paired_bootstrap_plastic40_vs_random40`.
    ap.add_argument(
        "--paired-plastic40-baseline-csv",
        type=Path, default=None,
        help="Path to §v2.5-plasticity-2c plasticity.csv providing the "
             "plastic budget=40 seeds-20..39 baseline indicators for the "
             "§2d primary confirmatory test. Triggers the paired-bootstrap "
             "plastic@40 vs random@40 CI routine when present.",
    )
    args = ap.parse_args()

    sweep_arg = Path(args.sweep)
    sw_dir = sweep_arg if sweep_arg.is_absolute() else OUTPUT_ROOT / args.sweep
    if not sw_dir.exists():
        print(f"sweep dir missing: {sw_dir}", file=sys.stderr)
        return 2

    canonical = hex_to_tape(args.canonical_hex)
    rows: list[dict] = []
    missing = 0
    n_plastic = n_frozen = 0
    for d in sorted(sw_dir.iterdir()):
        if not d.is_dir():
            continue
        r = analyze_run(d, canonical, args.alphabet)
        if r is None:
            # Missing config/result/npz — not a frozen-only run (those
            # now produce a schema-normalized row per v2.5-plasticity-2a).
            missing += 1
            continue
        if r.get("plasticity_enabled"):
            n_plastic += 1
        else:
            n_frozen += 1
        rows.append(r)

    print(f"analyzed {len(rows)} run(s); "
          f"{n_plastic} plastic, {n_frozen} frozen-only "
          f"(schema-normalized); {missing} missing artifacts")

    out_dir = args.out or sw_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "plasticity.csv"
    summary_path = out_dir / "plasticity_summary.json"

    if rows:
        # Union keyset across all rows — plastic and frozen-only schemas
        # mix here, and the frozen rows pad plastic-specific columns with
        # None. Preserves first-seen order so CSVs stay diff-friendly
        # across sweep types (codex-v3 NEW-P2 CSV schema normalization).
        csv_keys: list[str] = []
        seen: set[str] = set()
        for r in rows:
            for k in r.keys():
                if k in seen:
                    continue
                if isinstance(r[k], (dict, list)):
                    continue
                csv_keys.append(k)
                seen.add(k)
        with csv_path.open("w") as f:
            f.write(",".join(csv_keys) + "\n")
            for r in rows:
                f.write(",".join(
                    "" if r.get(k) is None else str(r[k])
                    for k in csv_keys
                ) + "\n")
    summary = summarize(rows)

    # §v2.5-plasticity-2d PRIMARY confirmatory test: paired-bootstrap
    # 98.333% CI on F_AND_test_plastic difference plastic@40 minus
    # random@40 on shared seeds 20..39. Runs when the caller provides
    # the §2c plasticity.csv as the baseline source. Silent no-op
    # otherwise (pre-§2d sweeps don't need the paired routing).
    if args.paired_plastic40_baseline_csv is not None:
        if not args.paired_plastic40_baseline_csv.exists():
            print(
                f"--paired-plastic40-baseline-csv path does not exist: "
                f"{args.paired_plastic40_baseline_csv}",
                file=sys.stderr,
            )
            return 2
        baseline_pl40 = extract_plastic_budget40_indicators_from_csv(
            args.paired_plastic40_baseline_csv
        )
        paired_result = paired_bootstrap_plastic40_vs_random40(
            rows, baseline_pl40
        )
        paired_result["baseline_csv"] = str(
            args.paired_plastic40_baseline_csv
        )
        paired_result["baseline_n_seeds"] = len(baseline_pl40)
        summary["paired_bootstrap_plastic40_vs_random40"] = paired_result
        key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
        swamped = paired_result.get(f"{key_prefix}_swamped", False)
        ci_lo = paired_result.get(f"{key_prefix}_lo")
        ci_hi = paired_result.get(f"{key_prefix}_hi")
        pt = paired_result.get(f"{key_prefix}_point_estimate")
        if swamped:
            print(
                f"\n§v2.5-plasticity-2d primary confirmatory: SWAMPED — "
                f"{paired_result.get(f'{key_prefix}_swamped_reason')}"
            )
        else:
            print(
                f"\n§v2.5-plasticity-2d primary confirmatory "
                f"(plastic@40 − random@40, shared seeds 20..39, 98.333% "
                f"CI): point_est={pt:+.4f}  "
                f"CI=[{ci_lo:+.4f}, {ci_hi:+.4f}]  "
                f"n_paired={paired_result.get(f'{key_prefix}_n_paired')}"
            )

    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"  per-run CSV: {csv_path}")
    print(f"  summary JSON: {summary_path}")
    print()
    for cell in summary.get("per_cell", []):
        rf = cell.get("R_fit_frozen_999_mean")
        rp = cell.get("R_fit_plastic_999_mean")
        bs = cell.get("Baldwin_slope_mean")
        bs_lo = cell.get("Baldwin_slope_ci95_lo_mean")
        bs_hi = cell.get("Baldwin_slope_ci95_hi_mean")
        gt_fr = cell.get("GT_bypass_fraction_mean")
        mg = cell.get("max_gap_at_budget_5_mean")
        mg_lo = cell.get("max_gap_at_budget_5_cell_boot_ci_lo")
        mg_hi = cell.get("max_gap_at_budget_5_cell_boot_ci_hi")
        mg_maj = cell.get("max_gap_at_budget_5_seed_majority")
        mg_n = cell.get("max_gap_at_budget_5_n_non_nan_seeds")
        rpd = cell.get("R_fit_delta_paired_sf0_mean")
        rpd_n = cell.get("R_fit_delta_paired_sf0_n_pairs")
        rf_s = f"{rf:.3f}" if rf is not None else "-"
        rp_s = f"{rp:.3f}" if rp is not None else "-"
        bs_s = f"{bs:+.4f}" if bs is not None else "-"
        ci_s = (f"[{bs_lo:+.4f},{bs_hi:+.4f}]"
                if bs_lo is not None and bs_hi is not None else "[-, -]")
        gt_s = f"{gt_fr:.2f}" if gt_fr is not None else "-"
        mg_s = f"{mg:+.4f}" if mg is not None else "-"
        mg_ci_s = (f"[{mg_lo:+.4f},{mg_hi:+.4f}]"
                   if mg_lo is not None and not np.isnan(mg_lo)
                   and mg_hi is not None and not np.isnan(mg_hi)
                   else "[-, -]")
        mg_maj_s = (f"{mg_maj}/{mg_n}"
                    if mg_maj is not None and mg_n is not None else "-")
        rpd_s = (f"{rpd:+.3f} (n={rpd_n})"
                 if rpd is not None else "-")
        print(
            f"  arm={cell['arm']:<8s} pl={int(cell['plasticity_enabled'])} "
            f"budget={cell['plasticity_budget']} "
            f"sf={cell['seed_fraction']:.3f}  n={cell['n_seeds']:>2}  "
            f"R_fit_frozen={rf_s}  R_fit_plastic={rp_s}  "
            f"Baldwin_slope={bs_s} CI95={ci_s}  "
            f"max_gap@5={mg_s} CI={mg_ci_s} maj={mg_maj_s}  "
            f"R_fit_delta_paired_sf0={rpd_s}  "
            f"GT_bypass={gt_s}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
