"""track_exact_any (map-bias §24): no effect on the run, hash-stable at default."""

import numpy as np

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution


def _cfg(**kw):
    return ChemTapeConfig(task="mbs_xor", arm="TAG", alphabet="tagged", tape_length=32, pop_size=64,
                          generations=8, n_examples=64, holdout_size=0, selection_mode="lexicase",
                          fitness_metric="balanced", fast_rng=True, backend="numpy", seed=3, **kw)


def test_hash_stable_at_default():
    assert _cfg().hash() == _cfg(track_exact_any=False).hash()
    assert _cfg().hash() != _cfg(track_exact_any=True).hash()


def test_replays_untracked_run():
    a = run_evolution(_cfg())
    b = run_evolution(_cfg(track_exact_any=True))
    assert np.array_equal(a.best_genotype, b.best_genotype)
    assert a.exact_any is None
    assert set(b.exact_any) == {"first_gen", "final_count", "gens_with_exact", "n_checked"}


def test_k_alternating_and_plasticity():
    import pytest
    c = ChemTapeConfig(task="mbs_xor", arm="BP_TOPK", alphabet="v2_probe", topk=3, tape_length=32,
                       pop_size=64, generations=6, n_examples=64, holdout_size=0, selection_mode="lexicase",
                       fitness_metric="balanced", fast_rng=True, backend="numpy", seed=1,
                       k_alternating_period=2, k_alternating_values="1,3")
    a = run_evolution(c)
    from dataclasses import replace
    b = run_evolution(replace(c, track_exact_any=True))
    assert np.array_equal(a.best_genotype, b.best_genotype)
    with pytest.raises(ValueError):
        run_evolution(_cfg(track_exact_any=True, plasticity_enabled=True))
