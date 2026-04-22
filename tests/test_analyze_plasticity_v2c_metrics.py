"""Tests for §v2.5-plasticity-2c engineering additions to analyze_plasticity.py.

Covers:
- _classify_attractor_category classifier (4 categories; check-order)
- bootstrap_mean_ci_97_5 (97.5% CI variant for §2c family α = 0.025)
- paired_bootstrap_budget40_vs_budget5 (PRIMARY confirmatory test;
  seed-integrity pre-check routing to SWAMPED)
- extract_budget5_indicators_from_csv (Setup § "Shared-seed extraction"
  verbatim)
- _compute_winner_structural_metrics (6 per-run metrics + winner-
  selection parity with _compute_top1_winner_hamming)
"""
from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments" / "chem_tape"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from analyze_plasticity import (  # type: ignore[import-not-found]
    _CANONICAL_ACTIVE_LEN,
    _CANONICAL_ACTIVE_TOKEN_SET,
    _PLASTICITY_ACTIVE_TOKEN_SET,
    _classify_attractor_category,
    _compute_winner_structural_metrics,
    _select_top1_winner_idx,
    bootstrap_mean_ci_97_5,
    extract_budget5_indicators_from_csv,
    paired_bootstrap_budget40_vs_budget5,
)


# --- _classify_attractor_category ---


def test_classifier_compositional_and_minimal():
    # Has REDUCE_MAX + SUM + GT → comp_AND (not max>5-only because has SUM;
    # not sum>10-only because has REDUCE_MAX).
    assert _classify_attractor_category({18, 5, 8}) == "compositional_AND"


def test_classifier_compositional_and_with_const5_but_no_reduce_max():
    # Has CONST_5 + SUM + IF_GT → comp_AND (≥1 of {REDUCE_MAX, CONST_5}).
    assert _classify_attractor_category({16, 5, 17}) == "compositional_AND"


def test_classifier_max5_only_strict_3_tokens_no_sum():
    # Has all three {REDUCE_MAX, CONST_5, GT} and NO SUM → max>5-only.
    assert _classify_attractor_category({18, 16, 8}) == "max>5-only"


def test_classifier_max5_only_with_extra_tokens_no_sum():
    # Strict 3-token set + additional non-SUM tokens → still max>5-only.
    assert _classify_attractor_category({18, 16, 8, 2, 9, 14}) == "max>5-only"


def test_classifier_not_max5_only_when_sum_present():
    # Has strict max set AND SUM → comp_AND (not max>5-only).
    assert _classify_attractor_category({18, 16, 8, 5}) == "compositional_AND"


def test_classifier_sum10_only_no_reduce_max_no_const5():
    # Has SUM + GT, no REDUCE_MAX, no CONST_5 → sum>10-only.
    assert _classify_attractor_category({5, 8}) == "sum>10-only"
    assert _classify_attractor_category({5, 17}) == "sum>10-only"  # IF_GT instead of GT


def test_classifier_not_sum10_only_when_reduce_max_present():
    # SUM + GT + REDUCE_MAX → comp_AND (not sum>10-only because has
    # REDUCE_MAX; comp_AND catches because ≥1 of max-hints is present).
    assert _classify_attractor_category({5, 8, 18}) == "compositional_AND"


def test_classifier_not_sum10_only_when_const5_present():
    # SUM + GT + CONST_5 → comp_AND.
    assert _classify_attractor_category({5, 8, 16}) == "compositional_AND"


def test_classifier_other_missing_all_predicates():
    # No predicates at all → other.
    assert _classify_attractor_category({1, 2, 3, 9, 10}) == "other"


def test_classifier_other_max_hint_without_sum_or_full_maxset():
    # Has CONST_5 but no GT and no SUM → other (not max>5-only because
    # missing GT; not comp_AND because missing SUM).
    assert _classify_attractor_category({16, 2, 9}) == "other"


def test_classifier_other_sum_without_gt_or_if_gt():
    # Has SUM but no GT and no IF_GT → other.
    assert _classify_attractor_category({5, 2, 9}) == "other"


def test_classifier_canonical_body_classifies_as_compositional_and():
    # Canonical sum_gt_10_AND_max_gt_5 active tokens = {CONST_0, INPUT,
    # REDUCE_MAX, CONST_5, GT, SUM, ADD, IF_GT}. Should classify as
    # compositional_AND.
    assert _classify_attractor_category(_CANONICAL_ACTIVE_TOKEN_SET) == "compositional_AND"


# --- bootstrap_mean_ci_97_5 ---


def test_bootstrap_97_5_returns_nan_below_min_n():
    xs = np.array([0.0, 1.0, 0.0])
    lo, hi = bootstrap_mean_ci_97_5(xs, min_n=15)
    assert np.isnan(lo) and np.isnan(hi)


def test_bootstrap_97_5_on_all_zeros_gives_zero_ci():
    xs = np.zeros(20, dtype=np.float64)
    lo, hi = bootstrap_mean_ci_97_5(xs, min_n=15)
    assert lo == 0.0 and hi == 0.0


def test_bootstrap_97_5_wider_than_95_pct_ci_on_same_data():
    """97.5% CI (quantiles [1.25%, 98.75%]) must be strictly wider than
    or equal to 95% CI (quantiles [2.5%, 97.5%]) on the same bootstrap.
    Verifies the CI-width operationalization for family α=0.025."""
    from analyze_plasticity import bootstrap_mean_ci  # 95% variant
    xs = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0],
                  dtype=np.float64)
    lo95, hi95 = bootstrap_mean_ci(xs, min_n=15)
    lo97_5, hi97_5 = bootstrap_mean_ci_97_5(xs, min_n=15)
    assert lo97_5 <= lo95
    assert hi97_5 >= hi95


def test_bootstrap_97_5_drops_nans():
    xs = np.array([float("nan"), 0.5, 0.5] + [0.5] * 20)
    lo, hi = bootstrap_mean_ci_97_5(xs, min_n=15)
    # After dropping nan, 22 values all 0.5 → CI = [0.5, 0.5]
    assert abs(lo - 0.5) < 1e-9
    assert abs(hi - 0.5) < 1e-9


# --- paired_bootstrap_budget40_vs_budget5 ---


def _make_rows(budget: int, seed_indicators: dict[int, int]) -> list[dict]:
    return [
        {
            "plasticity_enabled": True,
            "plasticity_budget": budget,
            "seed": seed,
            "best_fitness_test_plastic": str(1.0 if ind else 0.5),
        }
        for seed, ind in seed_indicators.items()
    ]


def test_paired_bootstrap_all_zero_diff_ci_contains_zero():
    """Paired-bootstrap on identical indicators → CI centered on 0."""
    b5 = {i: 1 if i % 2 == 0 else 0 for i in range(20, 40)}
    b40_rows = _make_rows(40, dict(b5))
    result = paired_bootstrap_budget40_vs_budget5(b40_rows, b5)
    assert not result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"]
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_point_estimate"] == 0.0
    lo = result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_lo"]
    hi = result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_hi"]
    assert lo == 0.0 and hi == 0.0  # all diffs are 0 → CI is [0, 0]


def test_paired_bootstrap_all_positive_diff_ci_excludes_zero_positive():
    """All seed differences = +1 → paired CI [+1, +1], excludes 0 positive."""
    b5 = {i: 0 for i in range(20, 40)}
    b40_rows = _make_rows(40, {i: 1 for i in range(20, 40)})
    result = paired_bootstrap_budget40_vs_budget5(b40_rows, b5)
    assert not result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"]
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_point_estimate"] == 1.0
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_lo"] == 1.0
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_hi"] == 1.0


def test_paired_bootstrap_all_negative_diff_ci_excludes_zero_negative():
    """All differences = -1 (budget=40 hurts every seed) → paired CI [-1, -1],
    triggers H-reverse via CI_hi < 0."""
    b5 = {i: 1 for i in range(20, 40)}
    b40_rows = _make_rows(40, {i: 0 for i in range(20, 40)})
    result = paired_bootstrap_budget40_vs_budget5(b40_rows, b5)
    assert not result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"]
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_point_estimate"] == -1.0
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_hi"] == -1.0


def test_paired_bootstrap_swamped_on_missing_seed_in_budget40():
    """Budget=40 missing seed 35 → SWAMPED with explicit reason."""
    b5 = {i: 0 for i in range(20, 40)}
    b40 = {i: 1 for i in range(20, 40) if i != 35}  # missing seed 35
    result = paired_bootstrap_budget40_vs_budget5(_make_rows(40, b40), b5)
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"] is True
    reason = result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason"]
    assert "budget=40 cell: missing seed" in reason
    assert "35" in reason
    assert np.isnan(result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_lo"])


def test_paired_bootstrap_swamped_on_duplicated_seed_in_budget40():
    """Budget=40 duplicated seed 25 (2 rows for same seed) → SWAMPED."""
    b5 = {i: 0 for i in range(20, 40)}
    rows = _make_rows(40, {i: 1 for i in range(20, 40)})
    rows.append({  # duplicate seed 25
        "plasticity_enabled": True,
        "plasticity_budget": 40,
        "seed": 25,
        "best_fitness_test_plastic": "0.5",
    })
    result = paired_bootstrap_budget40_vs_budget5(rows, b5)
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"] is True
    assert "seed 25 duplicated" in result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason"]


def test_paired_bootstrap_swamped_on_extra_seed_in_budget40():
    """Budget=40 includes seed 50 (outside {20..39}) → SWAMPED."""
    b5 = {i: 0 for i in range(20, 40)}
    b40 = {i: 1 for i in range(20, 40)}
    b40[50] = 1  # extra seed outside range
    result = paired_bootstrap_budget40_vs_budget5(_make_rows(40, b40), b5)
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"] is True
    assert "extra seed" in result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason"]


def test_paired_bootstrap_swamped_on_missing_seed_in_budget5_baseline():
    """Budget=5 baseline missing seed 30 → SWAMPED."""
    b5 = {i: 0 for i in range(20, 40) if i != 30}  # missing seed 30
    b40 = {i: 1 for i in range(20, 40)}
    result = paired_bootstrap_budget40_vs_budget5(_make_rows(40, b40), b5)
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"] is True
    reason = result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped_reason"]
    assert "budget=5 baseline: missing seed" in reason and "30" in reason


def test_paired_bootstrap_ignores_non_budget40_rows():
    """Rows at budgets other than 40 are ignored; only budget=40 paired."""
    b5 = {i: 0 for i in range(20, 40)}
    rows = _make_rows(40, {i: 1 for i in range(20, 40)})
    # Add distractor rows at other budgets
    rows.extend(_make_rows(10, {i: 0 for i in range(20, 40)}))
    rows.extend(_make_rows(20, {i: 1 for i in range(20, 40)}))
    result = paired_bootstrap_budget40_vs_budget5(rows, b5)
    # Should use only budget=40 rows for pairing
    assert not result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_swamped"]
    assert result["f_and_test_plastic_paired_boot_ci_budget40_vs_budget5_point_estimate"] == 1.0


# --- extract_budget5_indicators_from_csv ---


def test_extract_budget5_indicators_roundtrip():
    """Write a plasticity.csv with mixed rows, extract, verify filter +
    binary indicator computation."""
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "plasticity.csv"
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "arm", "seed", "plasticity_enabled", "plasticity_budget",
                "best_fitness_test_plastic",
            ])
            w.writeheader()
            # Target rows (Arm A, plastic, budget=5, seeds 20..39) — 20 seeds
            for seed in range(20, 40):
                w.writerow({
                    "arm": "A",
                    "seed": seed,
                    "plasticity_enabled": "True",
                    "plasticity_budget": "5",
                    # Alternating solver/non-solver
                    "best_fitness_test_plastic": "1.0" if seed % 2 == 0 else "0.95",
                })
            # Distractor rows (different budget, different arm, different seed range)
            w.writerow({
                "arm": "A", "seed": "40", "plasticity_enabled": "True",
                "plasticity_budget": "5", "best_fitness_test_plastic": "1.0",
            })  # seed 40 — outside range
            w.writerow({
                "arm": "A", "seed": "21", "plasticity_enabled": "True",
                "plasticity_budget": "10", "best_fitness_test_plastic": "1.0",
            })  # budget=10 — wrong budget
            w.writerow({
                "arm": "BP_TOPK", "seed": "22", "plasticity_enabled": "True",
                "plasticity_budget": "5", "best_fitness_test_plastic": "1.0",
            })  # wrong arm
            w.writerow({
                "arm": "A", "seed": "23", "plasticity_enabled": "False",
                "plasticity_budget": "5", "best_fitness_test_plastic": "1.0",
            })  # frozen

        indicators = extract_budget5_indicators_from_csv(csv_path, seed_range=(20, 39))

    # Exactly 20 seeds (20..39) with alternating 1/0 indicators
    assert len(indicators) == 20
    assert set(indicators.keys()) == set(range(20, 40))
    for seed in range(20, 40):
        expected = 1 if seed % 2 == 0 else 0
        assert indicators[seed] == expected, f"seed {seed}: expected {expected}, got {indicators[seed]}"


# --- _compute_winner_structural_metrics ---


class _FakeNpz:
    """Minimal npz-like object for unit testing (dict lookup)."""
    def __init__(self, data: dict):
        self.data = data
        self.files = list(data.keys())

    def __getitem__(self, key):
        return self.data[key]


def test_select_top1_winner_idx_basic():
    # Winner = index 2 (tfp=0.9 is highest)
    g = np.array([[1, 0], [0, 1], [1, 1], [2, 2]], dtype=np.uint8)
    tfp = np.array([0.5, 0.8, 0.9, 0.7], dtype=np.float32)
    trfp = np.array([0.5, 0.8, 0.9, 0.7], dtype=np.float32)
    data = _FakeNpz({"genotypes": g, "test_fitness_plastic": tfp,
                     "train_fitness_plastic": trfp})
    assert _select_top1_winner_idx(data) == 2


def test_select_top1_winner_idx_tiebreak_by_train():
    # Two candidates tied at max tfp = 0.9; winner = one with higher train.
    g = np.array([[1, 0], [0, 1], [2, 2], [3, 3]], dtype=np.uint8)
    tfp = np.array([0.5, 0.9, 0.9, 0.9], dtype=np.float32)
    trfp = np.array([0.5, 0.7, 0.9, 0.8], dtype=np.float32)  # idx 2 has max train
    data = _FakeNpz({"genotypes": g, "test_fitness_plastic": tfp,
                     "train_fitness_plastic": trfp})
    assert _select_top1_winner_idx(data) == 2


def test_select_top1_winner_idx_tiebreak_by_smallest_idx_when_all_tied():
    # All tied on tfp AND train → smallest index wins.
    g = np.array([[1, 0], [0, 1], [2, 2], [3, 3]], dtype=np.uint8)
    tfp = np.array([0.9, 0.9, 0.9, 0.9], dtype=np.float32)
    trfp = np.array([0.9, 0.9, 0.9, 0.9], dtype=np.float32)
    data = _FakeNpz({"genotypes": g, "test_fitness_plastic": tfp,
                     "train_fitness_plastic": trfp})
    assert _select_top1_winner_idx(data) == 0


def test_select_top1_winner_idx_returns_none_on_missing_field():
    # Missing test_fitness_plastic → None
    data = _FakeNpz({"genotypes": np.zeros((4, 2), dtype=np.uint8),
                     "train_fitness_plastic": np.zeros(4, dtype=np.float32)})
    assert _select_top1_winner_idx(data) is None


def test_select_top1_winner_idx_returns_none_on_shape_mismatch():
    g = np.zeros((4, 2), dtype=np.uint8)
    tfp = np.zeros(3, dtype=np.float32)  # wrong length
    trfp = np.zeros(4, dtype=np.float32)
    data = _FakeNpz({"genotypes": g, "test_fitness_plastic": tfp,
                     "train_fitness_plastic": trfp})
    assert _select_top1_winner_idx(data) is None


def test_compute_winner_structural_metrics_canonical_shape():
    """Winner genotype = canonical 32-token tape → all metrics match canonical."""
    canonical_tokens = [2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17] + [0] * 20  # len 32
    g = np.array([canonical_tokens, [1] * 32], dtype=np.uint8)
    tfp = np.array([1.0, 0.5], dtype=np.float32)
    trfp = np.array([1.0, 0.5], dtype=np.float32)
    tff = np.array([0.5, 0.3], dtype=np.float32)  # frozen eval
    data = _FakeNpz({
        "genotypes": g, "test_fitness_plastic": tfp,
        "train_fitness_plastic": trfp, "test_fitness_frozen": tff,
    })
    winner_idx = 0

    # Canonical active = [2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17], len=12
    can_active = (2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17)

    metrics = _compute_winner_structural_metrics(data, winner_idx, can_active, "v2_probe")

    assert metrics["top1_winner_overhead"] == 0  # active_len == canonical_len
    assert metrics["top1_winner_levenshtein_uncapped"] == 0
    assert metrics["top1_winner_attractor_category"] == "compositional_AND"
    assert metrics["top1_winner_canonical_token_set_size"] == 8  # all 8 canonical tokens present
    # Plasticity-active tokens in canonical: GT×2 + IF_GT×1 + THRESHOLD_SLOT×0 = 3
    assert metrics["top1_winner_plasticity_active_count"] == 3
    assert abs(metrics["top1_winner_baldwin_gap"] - 0.5) < 1e-6  # tfp 1.0 - tff 0.5
