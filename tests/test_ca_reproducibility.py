"""Same config + seed twice must produce bitwise-identical results."""

import json

from folding_evolution.ca.config import CAConfig
from folding_evolution.ca.evolve import run_evolution


def test_same_seed_same_result_numpy():
    cfg = CAConfig(
        grid_n=8, steps=8, n_states=4, pop_size=32,
        n_bits=2, n_examples=4, generations=15,
        backend="numpy", seed=42,
    )
    a = run_evolution(cfg)
    b = run_evolution(cfg)
    assert (a.best_genotype == b.best_genotype).all()
    assert a.best_fitness == b.best_fitness
    # Full stats history equal.
    for sa, sb in zip(a.stats.history, b.stats.history):
        assert sa.best_fitness == sb.best_fitness
        assert sa.mean_fitness == sb.mean_fitness
        assert sa.best_genotype_hex == sb.best_genotype_hex


def test_same_seed_same_result_mlx():
    cfg = CAConfig(
        grid_n=8, steps=8, n_states=4, pop_size=32,
        n_bits=2, n_examples=4, generations=10,
        backend="mlx", seed=7,
    )
    a = run_evolution(cfg)
    b = run_evolution(cfg)
    assert (a.best_genotype == b.best_genotype).all()
    assert a.best_fitness == b.best_fitness


def test_different_seed_different_result():
    base = dict(
        grid_n=8, steps=8, n_states=4, pop_size=32,
        n_bits=2, n_examples=4, generations=5, backend="numpy",
    )
    a = run_evolution(CAConfig(**base, seed=1))
    b = run_evolution(CAConfig(**base, seed=2))
    # Different seeds should produce different best genotypes at gen 0.
    assert a.stats.history[0].best_genotype_hex != b.stats.history[0].best_genotype_hex


def test_config_hash_stable():
    c1 = CAConfig(grid_n=16, seed=5)
    c2 = CAConfig(grid_n=16, seed=5)
    c3 = CAConfig(grid_n=16, seed=6)
    assert c1.hash() == c2.hash()
    assert c1.hash() != c3.hash()
    # Hash should be a short hex string.
    assert len(c1.hash()) == 12
    int(c1.hash(), 16)  # parses as hex
