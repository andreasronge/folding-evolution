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
