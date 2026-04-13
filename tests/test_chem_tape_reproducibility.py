"""Chem-tape evolution is deterministic given cfg.seed."""

import numpy as np

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution


def test_same_seed_same_outcome():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=3,
        backend="numpy",
        arm="B",
        seed=13,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert r1.best_fitness == r2.best_fitness
    assert np.array_equal(r1.best_genotype, r2.best_genotype)
    assert [s.best_fitness for s in r1.stats.history] == [s.best_fitness for s in r2.stats.history]
