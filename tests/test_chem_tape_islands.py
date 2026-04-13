"""Island-model GA (experiments.md §4): smoke, reproducibility, migration
semantics, and backwards-compatibility with the panmictic path.
"""

import random

import numpy as np
import pytest

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import (
    _migrate,
    _run_evolution_islands,
    _run_evolution_panmictic,
    random_genotype,
    run_evolution,
)


# ---------- Dispatcher / back-compat ----------


def test_n_islands_1_falls_back_to_panmictic():
    """n_islands=1 must produce bitwise-identical results to the panmictic path."""
    cfg_panmictic = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0, tape_length=16,
        pop_size=16, generations=3, backend="numpy", arm="B", seed=0,
        n_islands=1,
    )
    r_via_dispatcher = run_evolution(cfg_panmictic)
    r_direct = _run_evolution_panmictic(cfg_panmictic)
    assert np.array_equal(r_via_dispatcher.best_genotype, r_direct.best_genotype)
    assert r_via_dispatcher.best_fitness == r_direct.best_fitness


def test_n_islands_gt_1_routes_to_island_path():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0, tape_length=16,
        pop_size=16, generations=3, backend="numpy", arm="B", seed=0,
        n_islands=4, migration_interval=10,
    )
    # Direct call vs dispatcher should match bitwise.
    r_dispatch = run_evolution(cfg)
    r_direct = _run_evolution_islands(cfg)
    assert np.array_equal(r_dispatch.best_genotype, r_direct.best_genotype)


def test_islands_pop_must_divide_evenly():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=8, holdout_size=0, tape_length=16,
        pop_size=15, generations=2, backend="numpy", arm="B", seed=0,
        n_islands=4,
    )
    with pytest.raises(ValueError, match="divisible"):
        run_evolution(cfg)


# ---------- Migration semantics ----------


def test_migrate_ring_topology_preserves_population_size():
    """Each island's size must stay constant after migration."""
    cfg = ChemTapeConfig(
        tape_length=8, pop_size=32, n_islands=4, migrants_per_island=2,
    )
    rng = random.Random(42)
    islands = [
        [random_genotype(cfg, rng) for _ in range(8)] for _ in range(4)
    ]
    # Arbitrary per-island fitness so the elite/worst selection is well-defined.
    island_fits = [np.linspace(0, 1, 8) for _ in range(4)]

    new_islands = _migrate(islands, island_fits, cfg, rng)
    assert len(new_islands) == 4
    for isl in new_islands:
        assert len(isl) == 8


def test_migrate_sends_elite_to_next_island():
    """The top-fit individual of island i should appear in island (i+1) mod n."""
    cfg = ChemTapeConfig(
        tape_length=8, pop_size=32, n_islands=4, migrants_per_island=1,
    )
    rng = random.Random(0)
    # Give each island a distinctive set of genotypes so we can trace migration.
    # Island i's individuals = uniform arrays of value i * 4 + k for k in 0..7.
    islands = [
        [np.full(8, (i * 10 + k) % 16, dtype=np.uint8) for k in range(8)]
        for i in range(4)
    ]
    # Make index 3 the elite in every island.
    island_fits = [
        np.array([0.1, 0.1, 0.1, 1.0, 0.1, 0.1, 0.1, 0.1]) for _ in range(4)
    ]
    new_islands = _migrate(islands, island_fits, cfg, rng)

    # Elite of island i is islands[i][3]. After migration, it should appear in
    # island (i+1) mod 4, replacing the worst (index 0, fitness 0.1 — tied but
    # argsort returns index 0).
    for src in range(4):
        dest = (src + 1) % 4
        expected = islands[src][3]
        # The migrant replaces one of the tied "worst" slots in dest. Find it.
        assert any(np.array_equal(expected, new_islands[dest][k]) for k in range(8))


def test_migrate_replaces_worst_individuals():
    """The worst individual in a receiving island must be evicted by a migrant."""
    cfg = ChemTapeConfig(
        tape_length=8, pop_size=32, n_islands=4, migrants_per_island=1,
    )
    rng = random.Random(0)
    # Island 0 will receive from island 3. Track island 0's worst individual.
    islands = [
        [np.full(8, i + k, dtype=np.uint8) for k in range(8)]
        for i in range(4)
    ]
    # Island 0's worst (fitness 0.0) is index 0.
    fits = np.zeros(8); fits[0] = 0.0; fits[1:] = 0.5
    island_fits = [fits.copy() for _ in range(4)]

    worst_before = islands[0][0].copy()
    new_islands = _migrate(islands, island_fits, cfg, rng)
    # The worst-before individual should NOT appear in new_islands[0] if it's
    # been replaced by the migrant from island 3 (elite of island 3).
    worst_present_after = any(
        np.array_equal(worst_before, g) for g in new_islands[0]
    )
    # Island 0's original worst was np.full(8, 0) — value 0 everywhere.
    # Its elite (island 3 index 3) is np.full(8, 3+3=6). So after migration,
    # island 0 has no cell equal to the "original worst" pattern.
    assert not worst_present_after


# ---------- Reproducibility ----------


def test_island_run_reproducible_under_fixed_seed():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0, tape_length=16,
        pop_size=16, generations=3, backend="numpy", arm="B", seed=7,
        n_islands=4, migration_interval=2, migrants_per_island=2,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert r1.best_fitness == r2.best_fitness
    assert np.array_equal(r1.best_genotype, r2.best_genotype)


# ---------- Smoke ----------


def test_island_run_completes_without_error():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0, tape_length=16,
        pop_size=32, generations=5, backend="numpy", arm="B", seed=0,
        n_islands=4, migration_interval=3, migrants_per_island=2,
    )
    result = run_evolution(cfg)
    assert result.generations_run >= 1
    assert 0.0 <= result.best_fitness <= 1.0


def test_island_with_bp_arm():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0, tape_length=16,
        pop_size=32, generations=5, backend="numpy", arm="BP", seed=0,
        n_islands=4, migration_interval=3, migrants_per_island=2,
    )
    result = run_evolution(cfg)
    assert 0.0 <= result.best_fitness <= 1.0
