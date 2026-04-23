"""§v2.5-plasticity-1a runtime-plasticity support.

Three tests:

1. ``plasticity_enabled=False`` at default produces byte-identical
   final-population dumps to the config-default path on a fixed seed.
   This is the principle 23 hash-stability + determinism gate — every
   prior Arm-A sweep must reproduce unchanged after the plasticity
   engineering landed.

2. ``plasticity_enabled=True, plasticity_budget=5`` on a small config
   produces non-zero plasticity state and a non-degenerate Baldwin gap
   (``test_fitness_plastic`` diverges from ``test_fitness_frozen`` on
   at least one individual, and at least one ``delta_final`` is
   non-zero).

3. ``ChemTapeConfig(plasticity_enabled=False, ...)`` at all defaults
   must hash-equal ``ChemTapeConfig()`` — principle 11 hash-exclusion.
"""

from __future__ import annotations

import numpy as np

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution


def _small_cfg(**overrides) -> ChemTapeConfig:
    """Small config sized for fast pytest runs. Uses a task with integer
    inputs and a GT-containing canonical body so plasticity has
    something to act on — the count-r task's comparison-heavy solutions
    exercise the plastic GT path in a single-digit-generations run."""
    base = dict(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=5,
        backend="numpy",
        arm="A",
        seed=7,
        dump_final_population=True,
    )
    base.update(overrides)
    return ChemTapeConfig(**base)


def test_plasticity_disabled_byte_identical():
    """Default (plasticity_enabled=False, plasticity_budget=0) produces
    byte-identical results to a config that names the defaults
    explicitly. Principle 23 + principle 11 at the result layer."""
    cfg_default = _small_cfg()
    cfg_explicit_off = _small_cfg(
        plasticity_enabled=False,
        plasticity_budget=0,
    )

    r_default_1 = run_evolution(cfg_default)
    r_default_2 = run_evolution(cfg_default)
    r_off_1 = run_evolution(cfg_explicit_off)

    # Default → default determinism (sanity).
    assert r_default_1.best_fitness == r_default_2.best_fitness
    assert np.array_equal(r_default_1.best_genotype, r_default_2.best_genotype)

    # Explicit-off == default (principle 23 gate).
    assert r_default_1.best_fitness == r_off_1.best_fitness
    assert np.array_equal(r_default_1.best_genotype, r_off_1.best_genotype)

    # Per-generation history must also match byte-for-byte.
    hist_default = [s.best_fitness for s in r_default_1.stats.history]
    hist_off = [s.best_fitness for s in r_off_1.stats.history]
    assert hist_default == hist_off

    # Frozen path must not emit plasticity columns into the final-pop
    # dump (they would be wasted bytes on non-plastic runs).
    assert r_default_1.final_delta_final is None
    assert r_default_1.final_test_fitness_frozen is None
    assert r_default_1.final_test_fitness_plastic is None


def test_plasticity_enabled_smoke():
    """plasticity_enabled=True with a non-zero budget produces:
      * plasticity columns in final-population dump
      * at least one individual with non-zero delta_final OR divergent
        frozen-vs-plastic test fitness (i.e., plasticity actually acted
        on the program on some individual — not trivially frozen).

    A GT-bypass population would trivially satisfy delta_final == 0
    for every individual AND test_fitness_plastic == test_fitness_frozen
    for every individual. count_r solutions typically contain GT (it's
    a count comparison task), so the smoke signal should surface within
    5 generations at pop=16.
    """
    cfg = _small_cfg(
        plasticity_enabled=True,
        plasticity_budget=5,
        plasticity_delta=1.0,
    )
    r = run_evolution(cfg)

    # Plasticity columns exist.
    assert r.final_delta_final is not None, "delta_final not emitted"
    assert r.final_test_fitness_frozen is not None
    assert r.final_test_fitness_plastic is not None
    assert r.final_train_fitness_frozen is not None
    assert r.final_train_fitness_plastic is not None
    assert r.final_has_gt is not None

    # Shapes match population.
    P = cfg.pop_size
    assert r.final_delta_final.shape == (P,)
    assert r.final_test_fitness_frozen.shape == (P,)
    assert r.final_test_fitness_plastic.shape == (P,)
    assert r.final_has_gt.shape == (P,)

    # At least one individual has non-degenerate plasticity state:
    # either delta_final != 0 OR frozen/plastic test fitness diverge.
    has_nonzero_delta = bool(np.any(r.final_delta_final != 0))
    has_fit_divergence = bool(np.any(
        r.final_test_fitness_plastic != r.final_test_fitness_frozen
    ))
    assert has_nonzero_delta or has_fit_divergence, (
        "plasticity state uniformly zero AND test fitness uniformly "
        "identical — plastic path appears to be a no-op. Check that "
        "the decoded programs contain GT tokens and that the plastic "
        "dispatch actually fires. has_gt fraction: "
        f"{r.final_has_gt.mean():.3f}"
    )


def test_plasticity_hash_stability_at_defaults():
    """All five plasticity config fields at default must be excluded
    from hash — principle 11. Existing sweep hashes remain addressable
    after the plasticity engineering landed."""
    cfg_default = ChemTapeConfig()
    cfg_explicit = ChemTapeConfig(
        plasticity_enabled=False,
        plasticity_budget=0,
        plasticity_mechanism="rank1_op_threshold",
        plasticity_train_fraction=0.75,
        plasticity_delta=1.0,
    )
    assert cfg_default.hash() == cfg_explicit.hash(), (
        "plasticity defaults leaked into hash: "
        f"default={cfg_default.hash()} explicit={cfg_explicit.hash()}"
    )

    # Flipping plasticity_enabled MUST change the hash.
    cfg_enabled = ChemTapeConfig(plasticity_enabled=True)
    assert cfg_default.hash() != cfg_enabled.hash(), (
        "plasticity_enabled=True did not change hash — existing sweeps "
        "would collide with plastic sweeps"
    )

    # A non-default budget also changes hash.
    cfg_budget5 = ChemTapeConfig(plasticity_enabled=True, plasticity_budget=5)
    assert cfg_default.hash() != cfg_budget5.hash()
    assert cfg_enabled.hash() != cfg_budget5.hash()


# ---------------- §v2.5-plasticity-2d random_sample_threshold ----------------


def test_random_sample_mechanism_smoke():
    """§v2.5-plasticity-2d: plasticity_mechanism='random_sample_threshold'
    dispatches to the new executor, emits the four k-draw summary arrays,
    and produces a non-degenerate delta_final distribution (at least one
    individual with delta != 0 on a GT-containing task).
    """
    cfg = _small_cfg(
        plasticity_enabled=True,
        plasticity_budget=5,
        plasticity_mechanism="random_sample_threshold",
        plasticity_delta=1.0,
    )
    r = run_evolution(cfg)

    # Schema: all 4 k-draw arrays emitted.
    assert r.final_k_draw_min is not None, "k_draw_min not emitted"
    assert r.final_k_draw_max is not None
    assert r.final_k_draw_std is not None
    assert r.final_k_argmax_index is not None

    P = cfg.pop_size
    assert r.final_k_draw_min.shape == (P,)
    assert r.final_k_draw_max.shape == (P,)
    assert r.final_k_draw_std.shape == (P,)
    assert r.final_k_argmax_index.shape == (P,)

    # Support-bound invariant: min/max within [-budget, +budget]
    # (GT-bypass individuals emit 0s so they trivially satisfy the bound).
    budget = cfg.plasticity_budget
    assert bool(np.all(r.final_k_draw_min >= -budget - 1e-9))
    assert bool(np.all(r.final_k_draw_max <= budget + 1e-9))
    # argmax_index within [0, k-1]
    assert bool(np.all(r.final_k_argmax_index >= 0))
    assert bool(np.all(r.final_k_argmax_index < budget))

    # Non-degenerate: at least one GT individual has non-zero std over
    # its k draws (rng actually drew something).
    has_gt = r.final_has_gt.astype(bool)
    if has_gt.any():
        assert float(r.final_k_draw_std[has_gt].max()) > 0.0, (
            "all GT individuals' k-draw std = 0; rng may have collapsed"
        )


def test_random_sample_mechanism_rank1_unaffected():
    """rank-1 path produces no k-draw arrays; mechanism dispatch does
    not contaminate the rank1_op_threshold output schema."""
    cfg_rank1 = _small_cfg(
        plasticity_enabled=True,
        plasticity_budget=5,
        plasticity_mechanism="rank1_op_threshold",
    )
    r = run_evolution(cfg_rank1)
    assert r.final_k_draw_min is None
    assert r.final_k_draw_max is None
    assert r.final_k_draw_std is None
    assert r.final_k_argmax_index is None


def test_random_sample_mechanism_reproducibility():
    """Same config + same seed → same final population (per-individual
    rng is seeded deterministically from (cfg.seed, individual_index,
    cfg.hash()), so two runs produce identical k-draws).
    """
    cfg = _small_cfg(
        plasticity_enabled=True,
        plasticity_budget=5,
        plasticity_mechanism="random_sample_threshold",
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert np.array_equal(r1.final_k_draw_min, r2.final_k_draw_min)
    assert np.array_equal(r1.final_k_draw_max, r2.final_k_draw_max)
    assert np.array_equal(r1.final_k_draw_std, r2.final_k_draw_std)
    assert np.array_equal(r1.final_k_argmax_index, r2.final_k_argmax_index)
    assert np.array_equal(r1.final_delta_final, r2.final_delta_final)


def test_random_sample_hash_differs_from_rank1():
    """§v2.5-plasticity-2d hash-dedup discipline (prereg checklist item
    3): random_sample_threshold is a non-default plasticity_mechanism, so
    `cfg.hash()` MUST include it (not popped), producing a distinct
    config hash from the rank-1 default. Prevents a §2d sweep from
    accidentally short-circuiting on §2c's cached outputs.
    """
    cfg_rank1 = ChemTapeConfig(
        plasticity_enabled=True, plasticity_budget=5,
        plasticity_mechanism="rank1_op_threshold",
    )
    cfg_random = ChemTapeConfig(
        plasticity_enabled=True, plasticity_budget=5,
        plasticity_mechanism="random_sample_threshold",
    )
    assert cfg_rank1.hash() != cfg_random.hash(), (
        "rank1_op_threshold and random_sample_threshold produced the "
        "same config hash — §2d sweep would dedup against §2c outputs. "
        f"rank1={cfg_rank1.hash()} random={cfg_random.hash()}"
    )


def test_random_sample_argmax_selects_best_train_draw():
    """When k=1, the single drawn δ is the selected δ (argmax trivial).
    The test pins this guarantee explicitly so argmax tiebreak logic
    cannot silently regress when k=1.
    """
    cfg = _small_cfg(
        plasticity_enabled=True,
        plasticity_budget=1,
        plasticity_mechanism="random_sample_threshold",
    )
    r = run_evolution(cfg)
    # For every GT individual at budget=1, argmax_index must be 0.
    has_gt = r.final_has_gt.astype(bool)
    if has_gt.any():
        assert int(r.final_k_argmax_index[has_gt].max()) == 0
        assert int(r.final_k_argmax_index[has_gt].min()) == 0
        # delta_final must equal the single draw (k_draw_min == k_draw_max
        # because only one sample was drawn).
        np.testing.assert_array_equal(
            r.final_k_draw_min[has_gt], r.final_k_draw_max[has_gt]
        )


def test_random_sample_gt_bypass_emits_vacuous_kdraws():
    """GT-bypass individuals (no GT token in the decoded program) cannot
    use plasticity; the mechanism emits (0, 0, 0, 0) vacuous k-draw
    summary for schema uniformity. Guard-6(c) invariants are filtered
    to has_gt=True individuals at chronicle time; the pytest asserts the
    vacuous values here so the filter has a stable target.
    """
    # To deliberately hit GT-bypass, use a config whose population will
    # be unlikely to contain GT in every individual within 5 gens at
    # pop=16. count_r solutions have GT often; use a tiny pop so some
    # individuals drift away from GT across generations.
    cfg = _small_cfg(
        plasticity_enabled=True,
        plasticity_budget=5,
        plasticity_mechanism="random_sample_threshold",
        pop_size=8,
        generations=2,
    )
    r = run_evolution(cfg)
    has_gt = r.final_has_gt.astype(bool)
    if (~has_gt).any():
        # At least one GT-bypass exists; verify vacuous summary.
        for i in np.where(~has_gt)[0]:
            assert r.final_k_draw_min[i] == 0.0
            assert r.final_k_draw_max[i] == 0.0
            assert r.final_k_draw_std[i] == 0.0
            assert r.final_k_argmax_index[i] == 0
            assert r.final_delta_final[i] == 0.0
