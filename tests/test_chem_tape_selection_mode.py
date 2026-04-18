"""§v2.4-proxy-5c selection_mode support.

Three tests:

1. `selection_mode="tournament"` produces byte-identical results to the
   default config (no selection_mode field). This is the principle 23
   hash-stability requirement — all prior sweeps must reproduce unchanged.

2. `selection_mode="ranking"` and `selection_mode="truncation"` don't crash
   and produce well-formed EvolutionResult objects on a small config.

3. `ChemTapeConfig(selection_mode="tournament").hash() == ChemTapeConfig().hash()`
   — the default-value hash exclusion is correct.
"""

from __future__ import annotations

import numpy as np

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution


def _small_cfg(**overrides) -> ChemTapeConfig:
    """Small panmictic config sized for fast pytest runs."""
    base = dict(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=32,
        generations=10,
        backend="numpy",
        arm="BP_TOPK",
        topk=3,
        seed=7,
    )
    base.update(overrides)
    return ChemTapeConfig(**base)


def test_tournament_matches_default():
    """`selection_mode="tournament"` is byte-identical to the default
    config (no selection_mode field). Determinism on both sides + no
    divergence in the RNG sequence between the two paths."""
    cfg_default = _small_cfg()
    cfg_tournament = _small_cfg(selection_mode="tournament")

    r_default_1 = run_evolution(cfg_default)
    r_default_2 = run_evolution(cfg_default)
    r_tourn_1 = run_evolution(cfg_tournament)
    r_tourn_2 = run_evolution(cfg_tournament)

    # Default → default determinism (sanity).
    assert r_default_1.best_fitness == r_default_2.best_fitness
    assert np.array_equal(r_default_1.best_genotype, r_default_2.best_genotype)

    # Tournament-explicit → tournament-explicit determinism (sanity).
    assert r_tourn_1.best_fitness == r_tourn_2.best_fitness
    assert np.array_equal(r_tourn_1.best_genotype, r_tourn_2.best_genotype)

    # Tournament-explicit == default (principle 23 hash-stability gate).
    assert r_default_1.best_fitness == r_tourn_1.best_fitness
    assert np.array_equal(r_default_1.best_genotype, r_tourn_1.best_genotype)
    # Per-generation history must also match byte-for-byte.
    hist_default = [s.best_fitness for s in r_default_1.stats.history]
    hist_tourn = [s.best_fitness for s in r_tourn_1.stats.history]
    assert hist_default == hist_tourn


def test_ranking_runs_and_produces_valid_output():
    """`selection_mode="ranking"` produces a well-formed result."""
    cfg = _small_cfg(
        selection_mode="ranking",
        pop_size=32,
        generations=5,
        n_examples=16,
    )
    result = run_evolution(cfg)

    assert 0.0 <= result.best_fitness <= 1.0
    assert result.best_genotype.shape == (cfg.tape_length,)
    assert result.best_genotype.dtype == np.uint8


def test_truncation_runs_and_produces_valid_output():
    """`selection_mode="truncation"` produces a well-formed result."""
    cfg = _small_cfg(
        selection_mode="truncation",
        pop_size=32,
        generations=5,
        n_examples=16,
    )
    result = run_evolution(cfg)

    assert 0.0 <= result.best_fitness <= 1.0
    assert result.best_genotype.shape == (cfg.tape_length,)
    assert result.best_genotype.dtype == np.uint8


def test_hash_stability_at_defaults():
    """selection_mode="tournament" and selection_top_fraction=0.5 at their
    default values must be excluded from the hash — principle 11 + the
    Plans/prereg_v2-4-proxy-5c baseline-reproduction gate."""
    cfg_default = ChemTapeConfig()
    cfg_explicit_tournament = ChemTapeConfig(selection_mode="tournament")
    cfg_explicit_topfrac = ChemTapeConfig(selection_top_fraction=0.5)
    cfg_both_explicit = ChemTapeConfig(
        selection_mode="tournament", selection_top_fraction=0.5
    )

    assert cfg_default.hash() == cfg_explicit_tournament.hash()
    assert cfg_default.hash() == cfg_explicit_topfrac.hash()
    assert cfg_default.hash() == cfg_both_explicit.hash()

    # Non-default values DO change the hash.
    cfg_ranking = ChemTapeConfig(selection_mode="ranking")
    cfg_topfrac_07 = ChemTapeConfig(selection_top_fraction=0.7)
    assert cfg_default.hash() != cfg_ranking.hash()
    assert cfg_default.hash() != cfg_topfrac_07.hash()
