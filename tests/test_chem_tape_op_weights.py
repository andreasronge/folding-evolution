"""op_weights (map-bias notebook §15): weighted op draws, hash-stable at default."""

import random

import numpy as np

from folding_evolution.chem_tape import evolve, tagged
from folding_evolution.chem_tape.config import ChemTapeConfig


def test_default_is_uniform_and_hash_stable():
    assert ChemTapeConfig().op_probs(22) is None
    assert ChemTapeConfig().hash() == ChemTapeConfig(op_weights="").hash()
    assert ChemTapeConfig().hash() != ChemTapeConfig(op_weights="3:2").hash()


def test_stack_draws_follow_weights():
    cfg = ChemTapeConfig(alphabet="v2_imax", arm="BP_TOPK", topk=3, fast_rng=True,
                         op_weights="22:10", tape_length=2000)
    rng = evolve.make_rng(cfg)
    g = evolve.random_genotype(cfg, rng)
    assert abs((g == 22).mean() - 10 / 32) < 0.03
    m = evolve.mutate(np.zeros(2000, dtype=np.uint8), cfg.__class__(**{**cfg.__dict__, "mutation_rate": 1.0}), rng)
    assert abs((m == 22).mean() - 10 / 32) < 0.03


def test_tagged_draws_follow_weights():
    p = ChemTapeConfig(op_weights="24:10").op_probs(tagged.N_OPS_COMB)
    g = tagged.random_genotype(3000, random.Random(0), tagged.N_OPS_COMB, p)
    assert abs((g[:3000] == 24).mean() - 10 / 34) < 0.03


def test_stack_weights_without_fast_rng():
    cfg = ChemTapeConfig(alphabet="v2_imax", arm="BP_TOPK", topk=3, op_weights="22:10",
                         tape_length=2000, mutation_rate=1.0)
    m = evolve.mutate(np.zeros(2000, dtype=np.uint8), cfg, random.Random(0))
    assert abs((m == 22).mean() - 10 / 32) < 0.03


def test_bad_weights_rejected_at_construction():
    import pytest
    for bad in ("22:0", "22:-1", "22:nan", "22:inf", "99:2"):
        with pytest.raises(ValueError):
            ChemTapeConfig(op_weights=bad)
