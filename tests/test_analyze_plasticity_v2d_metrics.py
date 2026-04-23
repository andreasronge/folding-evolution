"""Tests for §v2.5-plasticity-2d engineering additions to analyze_plasticity.py.

Covers:
- bootstrap_mean_ci_98_333 (98.333% CI variant for §2d family α = 0.01667)
- paired_bootstrap_plastic40_vs_random40 (PRIMARY confirmatory test;
  seed-integrity pre-check routing to Row 6 SWAMPED)
- extract_plastic_budget40_indicators_from_csv (Setup § "Shared-seed
  extraction" step 1-4 verbatim)
- _cell_key extension including plasticity_mechanism (backward-compat
  with pre-§2d CSVs + explicit separation of rank-1 vs random-sample
  cells at the same budget)
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
    _cell_key,
    bootstrap_mean_ci_98_333,
    extract_plastic_budget40_indicators_from_csv,
    paired_bootstrap_plastic40_vs_random40,
    summarize,
)


# --- bootstrap_mean_ci_98_333 ---


def test_bootstrap_98_333_on_all_zeros_gives_zero_ci():
    xs = np.zeros(20, dtype=np.float64)
    lo, hi = bootstrap_mean_ci_98_333(xs)
    assert lo == 0.0
    assert hi == 0.0


def test_bootstrap_98_333_wider_than_97_5_pct_ci_on_same_data():
    """98.333% CI must be strictly wider than 97.5% CI on the same data
    (tighter quantiles → wider bounds on the bootstrap distribution)."""
    from analyze_plasticity import bootstrap_mean_ci_97_5  # type: ignore[import-not-found]
    rng = np.random.default_rng(123)
    xs = rng.normal(0.5, 1.0, size=50)
    lo_97, hi_97 = bootstrap_mean_ci_97_5(xs)
    lo_98, hi_98 = bootstrap_mean_ci_98_333(xs)
    # 98.333% CI quantiles [0.833%, 99.167%] are STRICTLY outside
    # 97.5% CI quantiles [1.25%, 98.75%] → lo_98 ≤ lo_97 ≤ hi_97 ≤ hi_98
    # with at least one strict inequality in practice on continuous data.
    assert lo_98 <= lo_97
    assert hi_98 >= hi_97
    # On 50 normal samples the quantile difference is non-trivial.
    assert (hi_98 - lo_98) > (hi_97 - lo_97)


def test_bootstrap_98_333_drops_nans():
    xs = np.array([0.5, float("nan"), 0.7, float("nan"), 0.3] + [0.5] * 15)
    lo, hi = bootstrap_mean_ci_98_333(xs)
    assert not np.isnan(lo)
    assert not np.isnan(hi)
    # With mostly 0.5 values, CI should be tight around 0.5.
    assert 0.3 < lo < 0.6
    assert 0.4 < hi < 0.7


def test_bootstrap_98_333_too_few_non_nan_returns_nan():
    xs = np.array([0.5, 0.5, 0.5] + [float("nan")] * 17)
    lo, hi = bootstrap_mean_ci_98_333(xs, min_n=15)
    assert np.isnan(lo)
    assert np.isnan(hi)


# --- paired_bootstrap_plastic40_vs_random40 ---


def _make_row(seed: int, mechanism: str, budget: int, tfp: float) -> dict:
    return {
        "arm": "A",
        "seed": seed,
        "plasticity_enabled": True,
        "plasticity_mechanism": mechanism,
        "plasticity_budget": budget,
        "seed_fraction": 0.0,
        "best_fitness_test_plastic": tfp,
    }


def test_paired_bootstrap_v2d_all_zero_diff_ci_contains_zero():
    # All 20 seeds: plastic and random both solve → diff = 0 everywhere.
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 1.0) for s in range(20, 40)
    ]
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is False
    assert result[f"{key_prefix}_n_paired"] == 20
    assert result[f"{key_prefix}_lo"] == 0.0
    assert result[f"{key_prefix}_hi"] == 0.0
    assert result[f"{key_prefix}_point_estimate"] == 0.0


def test_paired_bootstrap_v2d_plastic_wins_ci_excludes_zero_positive():
    # Plastic solves all 20; random solves none → diff = 1 everywhere.
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.0) for s in range(20, 40)
    ]
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is False
    assert result[f"{key_prefix}_lo"] > 0  # CI excludes 0 positive → Row 1 PASS
    assert result[f"{key_prefix}_point_estimate"] == 1.0


def test_paired_bootstrap_v2d_random_wins_ci_excludes_zero_negative():
    # Plastic solves none; random solves all 20 → diff = -1 everywhere.
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 1.0) for s in range(20, 40)
    ]
    baseline_pl40 = {s: 0 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is False
    assert result[f"{key_prefix}_hi"] < 0  # CI excludes 0 negative → Row 5 REVERSE
    assert result[f"{key_prefix}_point_estimate"] == -1.0


def test_paired_bootstrap_v2d_swamped_on_missing_seed_in_random40():
    # Only 19 random-sample rows (missing seed 39) → SWAMPED.
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 39)
    ]
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is True
    assert "39" in result[f"{key_prefix}_swamped_reason"]
    assert np.isnan(result[f"{key_prefix}_lo"])
    assert np.isnan(result[f"{key_prefix}_hi"])


def test_paired_bootstrap_v2d_swamped_on_duplicated_seed_in_random40():
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ]
    # Add a duplicate row for seed 22.
    current_rows.append(_make_row(22, "random_sample_threshold", 40, 1.0))
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is True
    assert "duplicated" in result[f"{key_prefix}_swamped_reason"]
    assert "22" in result[f"{key_prefix}_swamped_reason"]


def test_paired_bootstrap_v2d_swamped_on_extra_seed_in_random40():
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ]
    # Add a row for seed 99 (outside range).
    current_rows.append(_make_row(99, "random_sample_threshold", 40, 1.0))
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is True
    assert "extra" in result[f"{key_prefix}_swamped_reason"]
    assert "99" in result[f"{key_prefix}_swamped_reason"]


def test_paired_bootstrap_v2d_swamped_on_missing_seed_in_plastic_baseline():
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ]
    # Baseline missing seed 30.
    baseline_pl40 = {s: 1 for s in range(20, 40) if s != 30}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is True
    assert "30" in result[f"{key_prefix}_swamped_reason"]
    assert "plastic" in result[f"{key_prefix}_swamped_reason"]


def test_paired_bootstrap_v2d_ignores_rank1_rows_in_current_sweep():
    """rank1_op_threshold rows in the current §2d sweep must be ignored
    (the routine is scoped to random_sample_threshold for the new cell).
    This prevents accidental double-counting if the §2d sweep output
    somehow includes rank-1 rows.
    """
    # 20 random rows + 20 rank-1 rows in the same current_rows list.
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ] + [
        _make_row(s, "rank1_op_threshold", 40, 1.0) for s in range(20, 40)
    ]
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    # Should NOT fire SWAMPED on "duplicated seeds" — the rank-1 rows
    # are filtered out before counting.
    assert result[f"{key_prefix}_swamped"] is False
    assert result[f"{key_prefix}_n_paired"] == 20


def test_paired_bootstrap_v2d_ignores_non_budget40_random_rows():
    """random_sample rows at supporting budgets {5, 10, 20} must NOT
    contribute to the primary confirmatory test (budget=40 only).
    """
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ] + [
        # Supporting budgets — should be ignored.
        _make_row(s, "random_sample_threshold", 10, 1.0) for s in range(20, 40)
    ] + [
        _make_row(s, "random_sample_threshold", 20, 1.0) for s in range(20, 40)
    ]
    baseline_pl40 = {s: 1 for s in range(20, 40)}
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is False
    assert result[f"{key_prefix}_n_paired"] == 20


# --- extract_plastic_budget40_indicators_from_csv ---


def test_extract_plastic40_indicators_roundtrip():
    """Write a minimal plasticity.csv with mixed rank-1 / random-sample
    / non-budget-40 / non-seed-range rows and verify the extractor
    returns exactly the plastic budget=40 seeds-20..39 indicators.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".csv", mode="w", delete=False
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "arm", "seed", "plasticity_enabled", "plasticity_mechanism",
                "plasticity_budget", "seed_fraction",
                "best_fitness_test_plastic",
            ],
        )
        writer.writeheader()
        # 20 plastic budget=40 rank-1 rows at seeds 20..39 — these are
        # what the extractor should return.
        for s in range(20, 40):
            writer.writerow({
                "arm": "A", "seed": str(s),
                "plasticity_enabled": "True",
                "plasticity_mechanism": "rank1_op_threshold",
                "plasticity_budget": "40", "seed_fraction": "0.0",
                "best_fitness_test_plastic": "1.0" if s % 2 == 0 else "0.5",
            })
        # Non-rank-1 at budget=40 (would collide without mechanism filter).
        for s in range(20, 25):
            writer.writerow({
                "arm": "A", "seed": str(s),
                "plasticity_enabled": "True",
                "plasticity_mechanism": "random_sample_threshold",
                "plasticity_budget": "40", "seed_fraction": "0.0",
                "best_fitness_test_plastic": "1.0",
            })
        # rank-1 at supporting budgets (should be ignored).
        for s in range(20, 40):
            writer.writerow({
                "arm": "A", "seed": str(s),
                "plasticity_enabled": "True",
                "plasticity_mechanism": "rank1_op_threshold",
                "plasticity_budget": "10", "seed_fraction": "0.0",
                "best_fitness_test_plastic": "1.0",
            })
        # rank-1 budget=40 BUT seed outside 20..39 (should be ignored).
        writer.writerow({
            "arm": "A", "seed": "5",
            "plasticity_enabled": "True",
            "plasticity_mechanism": "rank1_op_threshold",
            "plasticity_budget": "40", "seed_fraction": "0.0",
            "best_fitness_test_plastic": "1.0",
        })
        csv_path = Path(f.name)

    try:
        indicators = extract_plastic_budget40_indicators_from_csv(csv_path)
        assert len(indicators) == 20
        assert set(indicators.keys()) == set(range(20, 40))
        # Even seeds solve (indicator=1), odd seeds don't (indicator=0).
        for s in range(20, 40):
            assert indicators[s] == (1 if s % 2 == 0 else 0)
    finally:
        csv_path.unlink(missing_ok=True)


def test_extract_plastic40_indicators_flags_duplicate_seeds():
    """Codex-v4 P1-2 correction: duplicate-row detection in the plastic
    budget=40 baseline. A seed appearing in two filtered rows must be
    returned as a list[int] (rather than silently overwritten) so the
    paired-bootstrap routine can route Row 6 SWAMPED.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".csv", mode="w", delete=False
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "arm", "seed", "plasticity_enabled", "plasticity_mechanism",
                "plasticity_budget", "seed_fraction",
                "best_fitness_test_plastic",
            ],
        )
        writer.writeheader()
        # Seed 25 appears twice (simulating duplicate §2c data).
        for s in [20, 21, 22, 23, 24, 25, 25, 26, 27, 28, 29,
                  30, 31, 32, 33, 34, 35, 36, 37, 38, 39]:
            writer.writerow({
                "arm": "A", "seed": str(s),
                "plasticity_enabled": "True",
                "plasticity_mechanism": "rank1_op_threshold",
                "plasticity_budget": "40", "seed_fraction": "0.0",
                "best_fitness_test_plastic": "1.0",
            })
        csv_path = Path(f.name)

    try:
        indicators = extract_plastic_budget40_indicators_from_csv(csv_path)
        # Seed 25 is duplicated → list[int] value
        assert isinstance(indicators[25], list)
        assert indicators[25] == [1, 1]
        # Other seeds are singleton → scalar int
        for s in [20, 21, 22, 23, 24, 26, 27, 28, 29,
                  30, 31, 32, 33, 34, 35, 36, 37, 38, 39]:
            assert indicators[s] == 1
    finally:
        csv_path.unlink(missing_ok=True)


def test_paired_bootstrap_v2d_swamped_on_duplicated_baseline_seed():
    """Codex-v4 P1-2 correction: duplicate seed in the plastic baseline
    must route Row 6 SWAMPED, not silently pass the pre-check.
    """
    current_rows = [
        _make_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ]
    # Baseline with seed 30 duplicated (list value).
    baseline_pl40 = {s: 1 for s in range(20, 40) if s != 30}
    baseline_pl40[30] = [1, 0]  # duplicate → list
    result = paired_bootstrap_plastic40_vs_random40(
        current_rows, baseline_pl40
    )
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    assert result[f"{key_prefix}_swamped"] is True
    assert "30" in result[f"{key_prefix}_swamped_reason"]
    assert "duplicated" in result[f"{key_prefix}_swamped_reason"]


def test_extract_plastic40_indicators_backward_compat_no_mechanism_column():
    """Pre-§2d plasticity.csv files have no plasticity_mechanism column.
    The extractor must treat missing-column as the default
    rank1_op_threshold for backward compatibility with §2a/§2c CSVs.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".csv", mode="w", delete=False
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "arm", "seed", "plasticity_enabled",
                "plasticity_budget", "seed_fraction",
                "best_fitness_test_plastic",
            ],  # NO plasticity_mechanism column
        )
        writer.writeheader()
        for s in range(20, 40):
            writer.writerow({
                "arm": "A", "seed": str(s),
                "plasticity_enabled": "True",
                "plasticity_budget": "40", "seed_fraction": "0.0",
                "best_fitness_test_plastic": "1.0",
            })
        csv_path = Path(f.name)

    try:
        indicators = extract_plastic_budget40_indicators_from_csv(csv_path)
        assert len(indicators) == 20
        assert all(v == 1 for v in indicators.values())
    finally:
        csv_path.unlink(missing_ok=True)


# --- _cell_key extension (codex-v1 engineering item 1(c)) ---


def test_cell_key_separates_mechanism_at_same_budget():
    """§v2.5-plasticity-2d: rank-1 and random-sample cells at the same
    (arm, enabled, budget, sf) MUST produce distinct cell keys so
    per-cell summaries don't collapse them.
    """
    rank1_row = {
        "arm": "A", "plasticity_enabled": True,
        "plasticity_mechanism": "rank1_op_threshold",
        "plasticity_budget": 40, "seed_fraction": 0.0,
    }
    random_row = {
        "arm": "A", "plasticity_enabled": True,
        "plasticity_mechanism": "random_sample_threshold",
        "plasticity_budget": 40, "seed_fraction": 0.0,
    }
    assert _cell_key(rank1_row) != _cell_key(random_row), (
        "§2d cell-key did not separate rank-1 and random-sample at "
        "matched budget → per-cell summaries would collapse cross-"
        "mechanism data."
    )


def test_cell_key_backward_compat_missing_mechanism_defaults_to_rank1():
    """Rows without plasticity_mechanism column (pre-§2d CSVs) must
    default to rank1_op_threshold under the extended cell-key. Verifies
    the .get(…, 'rank1_op_threshold') default.
    """
    old_row = {
        "arm": "A", "plasticity_enabled": True,
        "plasticity_budget": 40, "seed_fraction": 0.0,
        # no plasticity_mechanism key
    }
    rank1_row = {
        "arm": "A", "plasticity_enabled": True,
        "plasticity_mechanism": "rank1_op_threshold",
        "plasticity_budget": 40, "seed_fraction": 0.0,
    }
    assert _cell_key(old_row) == _cell_key(rank1_row), (
        "Pre-§2d row (no plasticity_mechanism column) did NOT collapse "
        "to rank-1 cell under extended cell-key → backward-compat "
        "broken."
    )


def test_cell_key_separates_supporting_budgets_within_mechanism():
    """Extended cell-key must still separate different budgets within
    the same mechanism (basic invariant preserved from v1 cell-key).
    """
    b10 = {
        "arm": "A", "plasticity_enabled": True,
        "plasticity_mechanism": "random_sample_threshold",
        "plasticity_budget": 10, "seed_fraction": 0.0,
    }
    b40 = {
        "arm": "A", "plasticity_enabled": True,
        "plasticity_mechanism": "random_sample_threshold",
        "plasticity_budget": 40, "seed_fraction": 0.0,
    }
    assert _cell_key(b10) != _cell_key(b40)


# --- summarize() integration: cell separation + §2d column emission
# (codex-v4 P2-2) ---


def _make_full_row(
    seed: int, mechanism: str, budget: int, tfp: float,
    **overrides,
) -> dict:
    """Builder for rows consumed by summarize(). Includes the minimal
    field set the analyzer reads out of the per-run CSV."""
    base = {
        "run_dir": f"run_{seed}_{mechanism}_{budget}",
        "arm": "A",
        "seed": seed,
        "seed_fraction": 0.0,
        "plasticity_enabled": True,
        "plasticity_mechanism": mechanism,
        "plasticity_budget": budget,
        "plasticity_delta": 1.0,
        "best_fitness": tfp,
        "best_fitness_test_plastic": tfp,
        "best_fitness_train_plastic": tfp,
        "best_fitness_test_frozen": 0.5,
        "best_fitness_train_frozen": 0.5,
        "R_fit_frozen_999": 0.0,
        "R_fit_plastic_999": 0.0,
        "R_fit_delta_999": 0.0,
        "GT_bypass_fraction": 0.0,
        "n_non_bypass": 500,
        "Baldwin_slope": 0.0,
        "Baldwin_slope_ci95_lo": 0.0,
        "Baldwin_slope_ci95_hi": 0.0,
        "Baldwin_slope_bootstrap_mean": 0.0,
        "delta_final_mean": 0.0,
        "delta_final_std": 1.0,
        "max_gap_at_budget_5": float("nan"),
        "top1_winner_hamming": 4,
        "top1_winner_overhead": 4,
        "top1_winner_plasticity_active_count": 3,
        "top1_winner_levenshtein_uncapped": 20,
        "top1_winner_attractor_category": "compositional_AND",
        "top1_winner_canonical_token_set_size": 7,
        "top1_winner_baldwin_gap": 0.0,
    }
    # Hamming-bin counts/gap fields (required by _mean lookups).
    for k in ("Baldwin_gap_h0", "Baldwin_gap_h1", "Baldwin_gap_h2",
             "Baldwin_gap_h3", "Baldwin_gap_h_ge4"):
        base[k] = 0.0
    for k in ("count_h0", "count_h1", "count_h2", "count_h3", "count_h_ge4"):
        base[k] = 10
    for k in ("delta_mean_h0", "delta_mean_h1", "delta_mean_h2",
             "delta_mean_h3", "delta_std_h0", "delta_std_h1",
             "delta_std_h2", "delta_std_h3"):
        base[k] = 0.0
    base.update(overrides)
    return base


def test_summarize_separates_rank1_and_random_cells_at_matched_budget():
    """codex-v4 P2-2: integration test — mixed rank-1 + random-sample
    rows at matched budget=40 must produce 2 distinct per-cell summary
    entries, not collapse into one. Verifies that _cell_key extension
    is actually respected by summarize() end-to-end.
    """
    rows_rank1 = [
        _make_full_row(s, "rank1_op_threshold", 40, 0.6)
        for s in range(20, 40)
    ]
    rows_random = [
        _make_full_row(s, "random_sample_threshold", 40, 0.4,
                       delta_final_mean=2.0,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.0, winner_k_argmax_index=3)
        for s in range(20, 40)
    ]
    result = summarize(rows_rank1 + rows_random)
    per_cell = result["per_cell"]
    # Exactly 2 cells (one per mechanism).
    assert len(per_cell) == 2
    mechanisms = {c["plasticity_mechanism"] for c in per_cell}
    assert mechanisms == {"rank1_op_threshold", "random_sample_threshold"}
    # Each cell has n_seeds=20 (no collapse).
    for c in per_cell:
        assert c["n_seeds"] == 20
    # Random-sample cell has winner_k_draw_* populated; rank-1 cell has
    # None (random-sample emits k-draw columns, rank-1 doesn't).
    rank1_cell = next(c for c in per_cell if c["plasticity_mechanism"] == "rank1_op_threshold")
    random_cell = next(c for c in per_cell if c["plasticity_mechanism"] == "random_sample_threshold")
    assert random_cell["winner_k_draw_min_min"] == -4.5
    assert random_cell["winner_k_draw_max_max"] == 4.5
    assert rank1_cell["winner_k_draw_min_min"] is None
    assert rank1_cell["winner_k_draw_max_max"] is None


def test_summarize_emits_98_333_ci_on_f_and_test():
    """codex-v4 P1-1: summarize() must emit the 98.333% CI alongside the
    §2c 97.5% CI so the chronicle can grep the §2d family-α discipline.
    """
    rows = [
        _make_full_row(s, "random_sample_threshold", 40,
                       0.5 if s % 2 == 0 else 0.3)
        for s in range(20, 40)
    ]
    result = summarize(rows)
    per_cell = result["per_cell"]
    assert len(per_cell) == 1
    cell = per_cell[0]
    # Both CIs are emitted.
    assert "f_and_test_plastic_seed_boot_ci_lo" in cell
    assert "f_and_test_plastic_seed_boot_ci_hi" in cell
    assert "f_and_test_plastic_seed_boot_ci_98_333_lo" in cell
    assert "f_and_test_plastic_seed_boot_ci_98_333_hi" in cell
    # 98.333% CI is wider (quantiles further from 50%).
    c97_lo = cell["f_and_test_plastic_seed_boot_ci_lo"]
    c97_hi = cell["f_and_test_plastic_seed_boot_ci_hi"]
    c98_lo = cell["f_and_test_plastic_seed_boot_ci_98_333_lo"]
    c98_hi = cell["f_and_test_plastic_seed_boot_ci_98_333_hi"]
    assert c98_lo <= c97_lo + 1e-9
    assert c98_hi >= c97_hi - 1e-9


def test_summarize_emits_bootstrap_spec_v2d():
    """Top-level summary dict must include bootstrap_spec_v2d naming the
    plasticity-narrow-plateau family at size 3 with α=0.01667.
    """
    rows = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5)
        for s in range(20, 40)
    ]
    result = summarize(rows)
    assert "bootstrap_spec_v2d" in result
    spec = result["bootstrap_spec_v2d"]
    assert spec["alpha"] == pytest.approx(0.01667, rel=1e-3)
    assert spec["family"] == "plasticity-narrow-plateau"
    assert spec["family_size"] == 3


def test_summarize_flags_random_sample_swamped_on_support_violation():
    """codex-v4 P2-3: Guard-6 (c) is enforced at the summary level. A
    random-sample cell whose winner_k_draw_min < -budget on any seed
    must emit `winner_k_draw_swamped=True` with a matching reason.
    """
    # Inject one seed whose winner_k_draw_min violates support bound.
    rows = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.0, winner_k_argmax_index=3)
        for s in range(20, 39)
    ]
    rows.append(_make_full_row(
        39, "random_sample_threshold", 40, 0.5,
        winner_k_draw_min=-50.0,  # VIOLATION: below -budget=-40
        winner_k_draw_max=4.5,
        winner_k_draw_std=2.0, winner_k_argmax_index=3,
    ))
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_draw_swamped"] is True
    assert "< -budget" in cell["winner_k_draw_swamped_reason"]


def test_summarize_flags_random_sample_swamped_on_std_collapse():
    """Guard-6 (c) std-threshold: seed with std_draws < 0.05*budget
    triggers SWAMPED at the cell level. For budget=40, floor = 2.0.
    """
    rows = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.5, winner_k_argmax_index=3)
        for s in range(20, 39)
    ]
    # Inject one seed with collapsed std.
    rows.append(_make_full_row(
        39, "random_sample_threshold", 40, 0.5,
        winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
        winner_k_draw_std=0.5,  # VIOLATION: < 0.05 * 40 = 2.0
        winner_k_argmax_index=3,
    ))
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_draw_swamped"] is True
    assert "std" in cell["winner_k_draw_swamped_reason"]


def test_summarize_rank1_cell_no_k_draw_swamped():
    """rank-1 cells never receive the k-draw SWAMPED flag even if the
    columns are missing (they don't apply to that mechanism).
    """
    rows = [_make_full_row(s, "rank1_op_threshold", 40, 0.5)
            for s in range(20, 40)]
    result = summarize(rows)
    cell = result["per_cell"][0]
    # swamped=False because k-draw columns are absent for rank-1.
    assert cell["winner_k_draw_swamped"] is False


# --- §v2.5-plasticity-2d sweep YAML hash-dedup (codex-v4 P2-4) ---


def test_v2d_sweep_yaml_hashes_disjoint_from_v2c():
    """§v2.5-plasticity-2d Status-transition checklist item 3: verify
    that the new sweep YAML's config hashes do NOT collide with any §2c
    config hash. random_sample_threshold is a non-default mechanism, so
    cfg.hash() must include it and produce hashes disjoint from the
    §2c (rank1_op_threshold) cells. Prevents sweep.py from silently
    short-circuiting against existing §2c cached outputs.
    """
    import sys
    import yaml
    from pathlib import Path

    # expand_grid lives in experiments/chem_tape/sweep.py
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent.parent / "experiments" / "chem_tape"),
    )
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent.parent / "src"),
    )
    from sweep import expand_grid  # type: ignore[import-not-found]

    repo_root = Path(__file__).resolve().parent.parent
    v2c_yaml = repo_root / "experiments" / "chem_tape" / "sweeps" / "v2" / "v2_5_plasticity_2c.yaml"
    v2d_yaml = repo_root / "experiments" / "chem_tape" / "sweeps" / "v2" / "v2_5_plasticity_2d.yaml"

    v2c_spec = yaml.safe_load(v2c_yaml.read_text())
    v2d_spec = yaml.safe_load(v2d_yaml.read_text())

    v2c_hashes = {cfg.hash() for cfg in expand_grid(v2c_spec)}
    v2d_hashes = {cfg.hash() for cfg in expand_grid(v2d_spec)}

    # §2d sweep must have 80 distinct configs (4 budgets × 20 seeds).
    assert len(v2d_hashes) == 80

    # Critical invariant: NO overlap with §2c hashes.
    overlap = v2c_hashes & v2d_hashes
    assert not overlap, (
        f"§2d sweep config hashes collide with §2c hashes: {overlap}. "
        "sweep.py would short-circuit against §2c cached outputs, "
        "skipping the §2d runs entirely. Likely cause: plasticity_"
        "mechanism was incorrectly popped from hash at non-default "
        "value, or a base param accidentally matches §2c."
    )


def test_summarize_flags_random_sample_swamped_on_argmax_out_of_bounds():
    """codex-v5 P1-1: argmax_index ∈ [0, budget-1] is a Guard-6(c)
    invariant. Any seed with argmax_index < 0 or > budget-1 routes
    Row 6 SWAMPED at the cell level.
    """
    rows = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.5, winner_k_argmax_index=3)
        for s in range(20, 39)
    ]
    # Seed 39 has argmax_index=40 (out of bounds; budget=40 → max valid=39)
    rows.append(_make_full_row(
        39, "random_sample_threshold", 40, 0.5,
        winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
        winner_k_draw_std=2.5,
        winner_k_argmax_index=40,  # VIOLATION
    ))
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_draw_swamped"] is True
    assert "argmax_index" in cell["winner_k_draw_swamped_reason"]


def test_summarize_emits_argmax_aggregates():
    """codex-v5 P1-1: argmax_index aggregates (min, max across seeds)
    must appear in the per-cell summary so the chronicle can surface
    the full 4-tuple schema (min_draw, max_draw, std_draws, argmax_index).
    """
    rows = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.5, winner_k_argmax_index=s - 20)
        for s in range(20, 40)
    ]
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_argmax_index_min"] == 0    # seed=20 → 0
    assert cell["winner_k_argmax_index_max"] == 19   # seed=39 → 19


def test_summarize_flags_random_sample_swamped_on_missing_kdraw_data():
    """codex-v5 P1-2 + codex-v6 P1-1: random-sample cells with NO
    k-draw data on any of the 4 mandatory columns must route Row 6
    SWAMPED, not silently pass with winner_k_draw_swamped=False. All
    four of (min_draw, max_draw, std_draws, argmax_index) are checked.
    """
    # Random-sample cell where every row has None k-draw columns.
    rows = []
    for s in range(20, 40):
        row = _make_full_row(s, "random_sample_threshold", 40, 0.5)
        row["winner_k_draw_min"] = None
        row["winner_k_draw_max"] = None
        row["winner_k_draw_std"] = None
        row["winner_k_argmax_index"] = None
        rows.append(row)
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_draw_swamped"] is True
    # All 4 columns missing → they all appear in the reason.
    reason = cell["winner_k_draw_swamped_reason"]
    assert "winner_k_draw_min" in reason
    assert "winner_k_draw_max" in reason
    assert "winner_k_draw_std" in reason
    assert "winner_k_argmax_index" in reason


@pytest.mark.parametrize("missing_col", [
    "winner_k_draw_min",
    "winner_k_draw_max",
    "winner_k_draw_std",
    "winner_k_argmax_index",
])
def test_summarize_flags_random_sample_swamped_on_single_missing_kdraw_column(
    missing_col,
):
    """codex-v6 P1-1: 4-tuple enforcement is ALL-OR-NONE. Missing any
    ONE of the 4 mandatory k-draw columns (even if the other 3 are
    present) must route Row 6 SWAMPED. Parametrized across all 4.
    """
    rows = []
    for s in range(20, 40):
        row = _make_full_row(
            s, "random_sample_threshold", 40, 0.5,
            winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
            winner_k_draw_std=2.5, winner_k_argmax_index=3,
        )
        row[missing_col] = None
        rows.append(row)
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_draw_swamped"] is True, (
        f"Missing column {missing_col!r} did not trigger SWAMPED; "
        f"reason={cell['winner_k_draw_swamped_reason']!r}"
    )
    assert missing_col in cell["winner_k_draw_swamped_reason"]


def test_summarize_flags_random_sample_swamped_on_partial_kdraw_data():
    """Partial k-draw coverage (fewer rows with data than total
    members) is also an infrastructure failure → Row 6 SWAMPED.
    Tested with partial coverage on winner_k_draw_max (not _min, so the
    test doesn't alias the column the v5 pytest already covered).
    """
    rows = []
    # 15 rows with full k-draw data, 5 rows with _max=None → partial coverage.
    for s in range(20, 35):
        rows.append(_make_full_row(
            s, "random_sample_threshold", 40, 0.5,
            winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
            winner_k_draw_std=2.5, winner_k_argmax_index=3,
        ))
    for s in range(35, 40):
        row = _make_full_row(
            s, "random_sample_threshold", 40, 0.5,
            winner_k_draw_min=-4.5,
            winner_k_draw_std=2.5, winner_k_argmax_index=3,
        )
        row["winner_k_draw_max"] = None  # partial coverage on _max
        rows.append(row)
    result = summarize(rows)
    cell = result["per_cell"][0]
    assert cell["winner_k_draw_swamped"] is True
    assert "partial k-draw logging failure" in cell["winner_k_draw_swamped_reason"]
    assert "winner_k_draw_max" in cell["winner_k_draw_swamped_reason"]


def test_summarize_std_collapse_exact_threshold_boundary():
    """codex-v5 P2-1: verify the exact 0.05 * budget std-floor boundary.
    For budget=40, floor = 2.0. A seed with std = 1.999 must trigger
    SWAMPED; a seed with std = 2.001 must NOT.
    """
    # Case 1: below-floor (1.999 < 2.0) → SWAMPED
    rows_below = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.5, winner_k_argmax_index=3)
        for s in range(20, 39)
    ]
    rows_below.append(_make_full_row(
        39, "random_sample_threshold", 40, 0.5,
        winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
        winner_k_draw_std=1.999,  # just below 2.0
        winner_k_argmax_index=3,
    ))
    result_below = summarize(rows_below)
    cell_below = result_below["per_cell"][0]
    assert cell_below["winner_k_draw_swamped"] is True, (
        "std_draws=1.999 at budget=40 (floor=2.0) should trigger SWAMPED"
    )

    # Case 2: above-floor (2.001 > 2.0) → clean
    rows_above = [
        _make_full_row(s, "random_sample_threshold", 40, 0.5,
                       winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
                       winner_k_draw_std=2.5, winner_k_argmax_index=3)
        for s in range(20, 39)
    ]
    rows_above.append(_make_full_row(
        39, "random_sample_threshold", 40, 0.5,
        winner_k_draw_min=-4.5, winner_k_draw_max=4.5,
        winner_k_draw_std=2.001,  # just above 2.0
        winner_k_argmax_index=3,
    ))
    result_above = summarize(rows_above)
    cell_above = result_above["per_cell"][0]
    assert cell_above["winner_k_draw_swamped"] is False, (
        "std_draws=2.001 at budget=40 (floor=2.0) should NOT trigger "
        "SWAMPED"
    )


def test_v2d_sweep_yaml_all_random_sample_mechanism():
    """Every config expanded from the §2d sweep YAML must have
    plasticity_mechanism='random_sample_threshold'. Guards against a
    YAML typo that would silently launch a rank-1 sweep named v2d.
    """
    import sys
    import yaml
    from pathlib import Path

    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent.parent / "experiments" / "chem_tape"),
    )
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent.parent / "src"),
    )
    from sweep import expand_grid  # type: ignore[import-not-found]

    repo_root = Path(__file__).resolve().parent.parent
    v2d_yaml = repo_root / "experiments" / "chem_tape" / "sweeps" / "v2" / "v2_5_plasticity_2d.yaml"
    v2d_spec = yaml.safe_load(v2d_yaml.read_text())
    configs = expand_grid(v2d_spec)

    mechanisms = {cfg.plasticity_mechanism for cfg in configs}
    assert mechanisms == {"random_sample_threshold"}

    budgets = {cfg.plasticity_budget for cfg in configs}
    assert budgets == {5, 10, 20, 40}

    seeds = {cfg.seed for cfg in configs}
    assert seeds == set(range(20, 40))


# --- main() end-to-end integration with --paired-plastic40-baseline-csv
# (codex-v5 P2-3) ---


def test_main_paired_plastic40_baseline_flag_writes_confirmatory_to_summary_json(
    tmp_path,
):
    """codex-v5 P2-3: invoke analyze_plasticity.main() as a subprocess
    with --paired-plastic40-baseline-csv pointing at a synthetic §2c
    plasticity.csv; verify that paired_bootstrap_plastic40_vs_random40
    appears in the written plasticity_summary.json with the expected
    keys and non-NaN CI values.
    """
    import subprocess
    import json as _json

    repo_root = Path(__file__).resolve().parent.parent
    analyze_py = repo_root / "experiments" / "chem_tape" / "analyze_plasticity.py"

    # Build a synthetic §2d sweep output dir with 20 random-sample runs
    # at budget=40 seeds 20..39. Each run needs a config.yaml,
    # result.json, and final_population.npz (minimal schema for
    # analyze_run to succeed).
    import numpy as np
    import yaml

    sweep_dir = tmp_path / "v2d_test_sweep"
    sweep_dir.mkdir()
    for s in range(20, 40):
        run_dir = sweep_dir / f"{s:04d}_rs40"
        run_dir.mkdir()
        # Minimal config.yaml (only fields analyze_run + _row_common read).
        cfg_yaml = {
            "arm": "A",
            "seed": s,
            "plasticity_enabled": True,
            "plasticity_mechanism": "random_sample_threshold",
            "plasticity_budget": 40,
            "plasticity_delta": 1.0,
            "seed_fraction": 0.0,
        }
        (run_dir / "config.yaml").write_text(yaml.safe_dump(cfg_yaml))
        # Minimal result.json (best_fitness is what _row_common reads).
        (run_dir / "result.json").write_text(_json.dumps({
            "arm": "A", "seed": s, "best_fitness": 0.5,
        }))
        # Minimal final_population.npz: 10 individuals with all required
        # per-individual arrays + the 4 §2d k-draw arrays.
        P = 10
        npz_payload = {
            "genotypes": np.zeros((P, 32), dtype=np.uint8),
            "fitnesses": np.full(P, 0.5, dtype=np.float32),
            "delta_final": np.full(P, 1.5, dtype=np.float32),
            "test_fitness_frozen": np.full(P, 0.3, dtype=np.float32),
            "test_fitness_plastic": np.full(P, 0.5, dtype=np.float32),
            "train_fitness_frozen": np.full(P, 0.3, dtype=np.float32),
            "train_fitness_plastic": np.full(P, 0.5, dtype=np.float32),
            "has_gt": np.ones(P, dtype=bool),
            "k_draw_min": np.full(P, -3.5, dtype=np.float32),
            "k_draw_max": np.full(P, 3.5, dtype=np.float32),
            "k_draw_std": np.full(P, 2.5, dtype=np.float32),
            "k_argmax_index": np.full(P, 5, dtype=np.int32),
        }
        np.savez(run_dir / "final_population.npz", **npz_payload)

    # Build the §2c baseline CSV with 20 plastic rank-1 budget=40 rows at seeds 20..39.
    baseline_csv = tmp_path / "v2c_baseline_plasticity.csv"
    with baseline_csv.open("w") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "arm", "seed", "plasticity_enabled", "plasticity_mechanism",
                "plasticity_budget", "seed_fraction",
                "best_fitness_test_plastic",
            ],
        )
        writer.writeheader()
        # Alternating solve/non-solve pattern so the paired difference
        # is non-trivial but not all-one / all-zero.
        for s in range(20, 40):
            writer.writerow({
                "arm": "A", "seed": str(s),
                "plasticity_enabled": "True",
                "plasticity_mechanism": "rank1_op_threshold",
                "plasticity_budget": "40", "seed_fraction": "0.0",
                "best_fitness_test_plastic": "1.0" if s % 2 == 0 else "0.0",
            })

    # Invoke analyze_plasticity.main() as a subprocess with the new flag.
    out_dir = tmp_path / "analyzer_out"
    result = subprocess.run(
        [
            "uv", "run", "python",
            str(analyze_py),
            str(sweep_dir),
            "--out", str(out_dir),
            "--paired-plastic40-baseline-csv", str(baseline_csv),
        ],
        capture_output=True, text=True, cwd=str(repo_root),
        timeout=120,
    )
    assert result.returncode == 0, (
        f"analyze_plasticity.main() failed: stderr=\n{result.stderr}"
    )

    summary_path = out_dir / "plasticity_summary.json"
    assert summary_path.exists()
    summary = _json.loads(summary_path.read_text())

    # Primary confirmatory result present in summary JSON.
    assert "paired_bootstrap_plastic40_vs_random40" in summary
    paired = summary["paired_bootstrap_plastic40_vs_random40"]
    key_prefix = "f_and_test_plastic_paired_boot_ci_plastic40_vs_random40"
    # Expected keys from the routine's return dict.
    for suffix in ("_lo", "_hi", "_n_paired", "_swamped",
                   "_swamped_reason", "_point_estimate"):
        assert f"{key_prefix}{suffix}" in paired

    # Should not be SWAMPED (all 20 seeds present on both sides, no duplicates).
    assert paired[f"{key_prefix}_swamped"] is False
    assert paired[f"{key_prefix}_n_paired"] == 20
    # CI endpoints are numeric (not NaN) when no SWAMPED fires.
    assert not np.isnan(paired[f"{key_prefix}_lo"])
    assert not np.isnan(paired[f"{key_prefix}_hi"])

    # Top-level bootstrap_spec_v2d also emitted.
    assert "bootstrap_spec_v2d" in summary
    assert summary["bootstrap_spec_v2d"]["family"] == "plasticity-narrow-plateau"
    assert summary["bootstrap_spec_v2d"]["family_size"] == 3
