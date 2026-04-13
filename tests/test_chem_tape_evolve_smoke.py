"""Smoke test: short chem-tape evolution completes and records history."""

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution


def test_arm_b_smoke_numpy():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=4,
        backend="numpy",
        arm="B",
        seed=0,
    )
    result = run_evolution(cfg)
    assert result.generations_run == 4
    assert len(result.stats.history) == 5  # gen 0 + 4 evolved gens
    initial = result.stats.history[0].best_fitness
    final = result.stats.history[-1].best_fitness
    assert final >= initial


def test_arm_a_smoke_numpy():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=4,
        backend="numpy",
        arm="A",
        seed=0,
    )
    result = run_evolution(cfg)
    assert result.generations_run == 4
    assert 0.0 <= result.best_fitness <= 1.0
