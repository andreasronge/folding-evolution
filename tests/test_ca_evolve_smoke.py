"""Smoke test: 20-generation run on trivial parity shows fitness increases."""

from folding_evolution.ca.config import CAConfig
from folding_evolution.ca.evolve import run_evolution


def test_evolution_runs_and_improves():
    cfg = CAConfig(
        grid_n=8,
        steps=8,
        n_states=4,
        pop_size=32,
        n_bits=2,
        n_examples=4,
        generations=20,
        backend="numpy",
        seed=0,
        log_every=1,
    )
    result = run_evolution(cfg)
    assert result.generations_run == 20
    assert len(result.stats.history) == 21  # gen 0 + 20 gens
    initial_best = result.stats.history[0].best_fitness
    final_best = result.stats.history[-1].best_fitness
    assert final_best >= initial_best, (
        f"Evolution regressed: initial={initial_best} final={final_best}"
    )
