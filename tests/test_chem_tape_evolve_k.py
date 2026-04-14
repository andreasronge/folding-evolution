"""Evolve-K-per-individual (§12).

Cell 0 of each tape is the K-header: K = evolve_k_values[tape[0] % len(values)].
Decode operates on tape[1:] only; cell 0 is never part of the program.
"""

from __future__ import annotations

import numpy as np
import pytest

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import _programs_for_arm
from folding_evolution.chem_tape.evolve import run_evolution


# ---------- Config helpers ----------


def test_evolve_k_value_list_parses_default():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True)
    assert cfg.evolve_k_value_list() == [1, 2, 3, 4, 8, 999]


def test_evolve_k_value_list_custom():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="3,999")
    assert cfg.evolve_k_value_list() == [3, 999]


def test_individual_k_maps_header():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="3,999")
    tape_a = np.array([0, 1, 2, 3], dtype=np.uint8)
    tape_b = np.array([1, 1, 2, 3], dtype=np.uint8)
    tape_c = np.array([4, 1, 2, 3], dtype=np.uint8)  # 4 % 2 = 0 → K=3
    assert cfg.individual_k(tape_a) == 3
    assert cfg.individual_k(tape_b) == 999
    assert cfg.individual_k(tape_c) == 3


# ---------- Hash stability ----------


def test_hash_unchanged_when_evolve_k_off():
    """Existing BP_TOPK configs must have unchanged hashes."""
    c_old = ChemTapeConfig(arm="BP_TOPK", topk=3)
    c_new = ChemTapeConfig(arm="BP_TOPK", topk=3,
                           evolve_k=False, evolve_k_values="1,2,3,4,8,999")
    assert c_old.hash() == c_new.hash()


def test_hash_differs_when_evolve_k_active():
    c1 = ChemTapeConfig(arm="BP_TOPK", topk=3)
    c2 = ChemTapeConfig(arm="BP_TOPK", topk=3, evolve_k=True)
    assert c1.hash() != c2.hash()


# ---------- Decode routes ----------


def test_evolve_k_decode_uses_body_only():
    """_programs_for_arm under evolve-K must skip cell 0 and decode body only."""
    cfg = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,999",
        tape_length=16, backend="numpy",
    )
    # Cell 0 = 0 → K=1. Body cells [1..15] with a single bonded run.
    # Build a tape where body has runs of length 3 and 5, separated by 14.
    tape = np.array([[
        0,                          # header: 0 → K=1
        1, 2, 3,                    # body run of length 3
        14,                         # separator
        4, 5, 6, 7, 8,              # body run of length 5 (longest)
        14, 14, 14, 14, 14, 14,     # separators
    ]], dtype=np.uint8)
    progs = _programs_for_arm(cfg, tape)
    # K=1 picks the longest run only = run of length 5.
    assert progs[0] == [4, 5, 6, 7, 8]


def test_evolve_k_different_k_different_program():
    """Same tape with different header cell → different decoded program."""
    cfg_body_only = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,999",
        tape_length=16, backend="numpy",
    )
    # Cell 0 = 0 → K=1 (K picks longest = length 5).
    tape_k1 = np.array([[
        0, 1, 2, 3, 14, 4, 5, 6, 7, 8, 14, 14, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    # Cell 0 = 1 → K=999 (picks both runs).
    tape_kinf = tape_k1.copy()
    tape_kinf[0, 0] = 1
    progs_k1 = _programs_for_arm(cfg_body_only, tape_k1)
    progs_kinf = _programs_for_arm(cfg_body_only, tape_kinf)
    assert progs_k1[0] == [4, 5, 6, 7, 8]
    assert progs_kinf[0] == [1, 2, 3, 4, 5, 6, 7, 8]


def test_evolve_k_population_heterogeneity():
    """A batch of tapes with different cell-0 values produces different K decodes."""
    cfg = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,999",
        tape_length=16, backend="numpy",
    )
    base = np.array([
        0, 1, 2, 3, 14, 4, 5, 6, 7, 8, 14, 14, 14, 14, 14, 14,
    ], dtype=np.uint8)
    tapes = np.stack([
        base,                       # K=1
        np.concatenate([[1], base[1:]]).astype(np.uint8),  # K=999
    ])
    progs = _programs_for_arm(cfg, tapes)
    assert progs[0] == [4, 5, 6, 7, 8]
    assert progs[1] == [1, 2, 3, 4, 5, 6, 7, 8]


# ---------- Metrics: k_distribution ----------


def test_k_distribution_recorded_under_evolve_k():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=32, generations=4,
        backend="numpy", arm="BP_TOPK", evolve_k=True,
        evolve_k_values="1,3,999", seed=0,
    )
    result = run_evolution(cfg)
    # Every generation record should have a k_distribution array of length 3.
    for s in result.stats.history:
        assert s.k_distribution is not None
        assert s.k_distribution.shape == (3,)
        assert s.k_distribution.sum() == cfg.pop_size


def test_k_distribution_none_under_fixed_k():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=32, generations=4,
        backend="numpy", arm="BP_TOPK", topk=3, seed=0,
    )
    result = run_evolution(cfg)
    for s in result.stats.history:
        assert s.k_distribution is None


# ---------- Smoke: evolve-K + protection ----------


def test_evolve_k_with_protection_smoke():
    """Evolve-K with r=0.5 protection should run without error and respect
    that header cell is not protected."""
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=4,
        backend="numpy", arm="BP_TOPK", evolve_k=True,
        evolve_k_values="1,3", bond_protection_ratio=0.5, seed=0,
    )
    result = run_evolution(cfg)
    assert 0.0 <= result.best_fitness <= 1.0


# ---------- Reproducibility ----------


def test_evolve_k_is_reproducible():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=6,
        backend="numpy", arm="BP_TOPK", evolve_k=True,
        evolve_k_values="1,3,999", seed=7,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert np.array_equal(r1.best_genotype, r2.best_genotype)
    assert r1.best_fitness == r2.best_fitness


# ---------- §12a: K-prior island initialization ----------


def test_header_cell_for_k_roundtrip():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="1,3,8,999")
    # Header cell values should map back to target K via cfg.individual_k.
    for target_k in [1, 3, 8, 999]:
        header = cfg.header_cell_for_k(target_k)
        fake_tape = np.zeros(4, dtype=np.uint8)
        fake_tape[0] = header
        assert cfg.individual_k(fake_tape) == target_k


def test_header_cell_for_k_raises_for_invalid():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="1,3,8,999")
    with pytest.raises(ValueError):
        cfg.header_cell_for_k(5)


def test_island_k_prior_list_parses_and_defaults():
    c_empty = ChemTapeConfig()
    assert c_empty.island_k_prior_list() == []
    c_set = ChemTapeConfig(island_k_priors="1,3,8,999,1,3,8,999")
    assert c_set.island_k_prior_list() == [1, 3, 8, 999, 1, 3, 8, 999]


def test_hash_stable_when_island_k_priors_empty():
    c1 = ChemTapeConfig(arm="BP_TOPK", evolve_k=True)
    c2 = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, island_k_priors="")
    assert c1.hash() == c2.hash()


def test_island_k_priors_bias_initial_population():
    """With K priors set, each island's gen-0 population should have cell 0
    values corresponding to that island's target K."""
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=32, generations=1,  # minimal
        backend="numpy", arm="BP_TOPK",
        evolve_k=True, evolve_k_values="1,3,8,999",
        n_islands=4, migration_interval=50, migrants_per_island=1,
        island_k_priors="1,3,8,999",
        seed=0,
    )
    result = run_evolution(cfg)
    # gen 0 k_distribution: 8 individuals per island (pop_size/n_islands), 4 priors.
    # Each prior contributes 8 individuals with matching K, so k_distribution[0]
    # should be [8, 8, 8, 8] (one per K-value slot).
    gen0 = result.stats.history[0].k_distribution
    assert gen0 is not None
    assert list(gen0) == [8, 8, 8, 8], f"expected uniform K priors, got {gen0}"


def test_island_k_priors_reproducible():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=32, generations=4,
        backend="numpy", arm="BP_TOPK",
        evolve_k=True, evolve_k_values="1,3,8,999",
        n_islands=4, island_k_priors="1,3,8,999",
        seed=42,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert np.array_equal(r1.best_genotype, r2.best_genotype)


# ---------- §12b: K-niching via fitness sharing ----------


def test_niched_fitness_inactive_at_alpha_zero():
    from folding_evolution.chem_tape.evolve import _compute_niched_fitnesses
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="1,3")
    pop = [np.array([0, 1, 2], dtype=np.uint8) for _ in range(4)]
    raw = np.array([0.3, 0.5, 0.7, 0.2])
    out = _compute_niched_fitnesses(raw, pop, cfg)
    assert np.array_equal(out, raw)


def test_niched_fitness_rewards_rare_k():
    """With alpha > 0 and one rare K, the rare K's effective fitness is boosted."""
    from folding_evolution.chem_tape.evolve import _compute_niched_fitnesses
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True,
                         evolve_k_values="1,3", k_niching_alpha=1.0)
    # 3 individuals at K=1 (cell 0 = 0), 1 at K=3 (cell 0 = 1). Shares: K=1 = 0.75, K=3 = 0.25.
    pop = [
        np.array([0, 1, 2], dtype=np.uint8),  # K=1
        np.array([0, 1, 2], dtype=np.uint8),  # K=1
        np.array([0, 1, 2], dtype=np.uint8),  # K=1
        np.array([1, 1, 2], dtype=np.uint8),  # K=3
    ]
    raw = np.array([1.0, 1.0, 1.0, 1.0])
    out = _compute_niched_fitnesses(raw, pop, cfg)
    # K=1 individuals: raw * (1/0.75) = 1.333
    # K=3 individual:  raw * (1/0.25) = 4.0
    np.testing.assert_allclose(out[:3], 4/3, rtol=1e-6)
    np.testing.assert_allclose(out[3], 4.0, rtol=1e-6)


def test_niched_fitness_uniform_when_balanced():
    """When all K values are equally represented, niching produces uniform
    multipliers so selection order is unchanged."""
    from folding_evolution.chem_tape.evolve import _compute_niched_fitnesses
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True,
                         evolve_k_values="1,3", k_niching_alpha=0.5)
    pop = [np.array([0, 1, 2], dtype=np.uint8) for _ in range(2)] + \
          [np.array([1, 1, 2], dtype=np.uint8) for _ in range(2)]
    raw = np.array([0.5, 0.3, 0.7, 0.9])
    out = _compute_niched_fitnesses(raw, pop, cfg)
    # All shares = 0.5 → all multipliers equal. Order preserved up to scaling.
    assert np.argmax(raw) == np.argmax(out)
    assert np.argmin(raw) == np.argmin(out)


def test_hash_unchanged_when_niching_off():
    c1 = ChemTapeConfig(arm="BP_TOPK", evolve_k=True)
    c2 = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, k_niching_alpha=0.0)
    assert c1.hash() == c2.hash()


def test_hash_changes_with_niching():
    c1 = ChemTapeConfig(arm="BP_TOPK", evolve_k=True)
    c2 = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, k_niching_alpha=0.5)
    assert c1.hash() != c2.hash()


# ---------- §12c: migrate body, adopt host K ----------


def test_migrate_body_adopt_host_k_overwrites_header():
    """Under this policy, migrants arriving at an island have their cell 0
    overwritten with the host island's prior K header."""
    from folding_evolution.chem_tape.evolve import _migrate
    cfg = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,3,8,999",
        tape_length=8, pop_size=8,
        n_islands=4, migration_interval=50, migrants_per_island=1,
        island_k_priors="1,3,8,999", migrate_body_adopt_host_k=True,
    )
    # Island 0 (K=1 prior) holds a high-fitness individual with K=999 header.
    islands = []
    islands.append([np.array([3, 5, 5, 5, 5, 5, 5, 5], dtype=np.uint8)])  # K=999
    islands.append([np.array([1, 9, 9, 9, 9, 9, 9, 9], dtype=np.uint8)])  # K=3
    islands.append([np.array([2, 7, 7, 7, 7, 7, 7, 7], dtype=np.uint8)])  # K=8
    islands.append([np.array([3, 1, 1, 1, 1, 1, 1, 1], dtype=np.uint8)])  # K=999
    fits = [np.array([1.0]) for _ in range(4)]
    rng = __import__("random").Random(0)
    new_islands = _migrate(islands, fits, cfg, rng)
    # island 0's incoming migrant is from island 3 (src = 0-1 mod 4 = 3).
    # Under adopt_host_k, migrant's cell 0 → island 0's prior K header (K=1 → header=0).
    arrived_0 = new_islands[0][0]  # replaced in position 0 (only member)
    assert int(arrived_0[0]) == cfg.header_cell_for_k(1), \
        f"expected cell 0 = header_for_K=1 (= 0), got {int(arrived_0[0])}"
    # Body should be from island 3's migrant: [1,1,1,1,1,1,1]
    assert list(arrived_0[1:]) == [1, 1, 1, 1, 1, 1, 1]


def test_migrate_without_adopt_preserves_source_header():
    """Default migration (no §12c flag) leaves migrant's cell 0 intact."""
    from folding_evolution.chem_tape.evolve import _migrate
    cfg = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,3,8,999",
        tape_length=8, pop_size=8,
        n_islands=4, migration_interval=50, migrants_per_island=1,
        island_k_priors="1,3,8,999", migrate_body_adopt_host_k=False,
    )
    islands = [
        [np.array([3, 5, 5, 5, 5, 5, 5, 5], dtype=np.uint8)],  # src for island 0
        [np.array([1, 9, 9, 9, 9, 9, 9, 9], dtype=np.uint8)],
        [np.array([2, 7, 7, 7, 7, 7, 7, 7], dtype=np.uint8)],
        [np.array([3, 1, 1, 1, 1, 1, 1, 1], dtype=np.uint8)],
    ]
    fits = [np.array([1.0]) for _ in range(4)]
    rng = __import__("random").Random(0)
    new_islands = _migrate(islands, fits, cfg, rng)
    # Migrant from island 3 to island 0: cell 0 remains 3 (source header).
    assert int(new_islands[0][0][0]) == 3
