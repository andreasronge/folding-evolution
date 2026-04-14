"""Bond-protected mutation (experiments.md §9 redesign, 2×2 factorial).

When `bond_protection_ratio < 1.0` and arm has a bond structure (BP / BP_TOPK),
cells inside the decode mask mutate at `mutation_rate * bond_protection_ratio`;
cells outside the mask mutate at full `mutation_rate`. Separator cells and
(for K<∞) lower-ranked runs are *not* protected — they mutate at full rate.
"""

from __future__ import annotations

import random
import numpy as np
import pytest

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import mutate


def _count_differences(a: np.ndarray, b: np.ndarray) -> int:
    return int((a != b).sum())


# ---------- r=1.0 leaves existing behaviour unchanged ----------


def test_protection_ratio_1_matches_uniform_mutation():
    """r=1.0 must produce bit-exactly the same child as the pre-§9 uniform path.

    Uses the same seeded RNG in both branches — the random-byte-per-cell order
    is identical, so with r=1.0 the protected branch is skipped and the
    outputs must match.
    """
    cfg_uniform = ChemTapeConfig(
        tape_length=32, arm="BP_TOPK", topk=3, mutation_rate=0.3,
        bond_protection_ratio=1.0, backend="numpy",
    )
    rng_a = random.Random(12345)
    rng_b = random.Random(12345)

    parent = np.array([(i * 7 + 3) % 16 for i in range(32)], dtype=np.uint8)
    # Both paths should trace the same RNG sequence under r=1.0 — the protected
    # branch only diverges when it triggers, which it must not at r=1.0.
    child_a = mutate(parent, cfg_uniform, rng_a)
    # Construct a second cfg with the literal pre-§9 uniform path (same defaults).
    cfg_vanilla = ChemTapeConfig(
        tape_length=32, arm="BP_TOPK", topk=3, mutation_rate=0.3, backend="numpy",
    )  # bond_protection_ratio defaults to 1.0
    child_b = mutate(parent, cfg_vanilla, rng_b)
    assert np.array_equal(child_a, child_b)


# ---------- r=0.0 → protected cells never mutate ----------


def test_protection_ratio_0_freezes_executing_cells_bp():
    """r=0.0 on Arm BP: cells in the longest-runnable run never mutate."""
    cfg = ChemTapeConfig(
        tape_length=32, arm="BP", mutation_rate=1.0,
        bond_protection_ratio=0.0, backend="numpy",
    )
    # Pick a parent with a clear longest run. Cells 5..14 (length 10) is the
    # longest non-separator run; the rest of the tape is separators.
    parent = np.full(32, 14, dtype=np.uint8)  # all separator
    parent[5:15] = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.uint8)

    rng = random.Random(0)
    child = mutate(parent, cfg, rng)

    # With mutation_rate=1.0, every unprotected cell should be resampled.
    # Cells 5..14 are protected (r=0 ⇒ rate 0 ⇒ never touched).
    assert np.array_equal(parent[5:15], child[5:15])
    # Cells 0..4 and 15..31 are separators (unprotected) — at rate 1.0 they're all resampled.
    # Since resample draws uniformly from 0..15, it's vanishingly unlikely that all
    # 22 cells happen to stay at 14. Assert that many of them changed.
    unprotected_changes = _count_differences(parent[np.r_[0:5, 15:32]], child[np.r_[0:5, 15:32]])
    assert unprotected_changes >= 15


def test_protection_ratio_0_freezes_only_top_k_runs():
    """r=0.0 on Arm BP_TOPK with K=2: only top-2 runs are frozen; smaller runs mutate."""
    cfg = ChemTapeConfig(
        tape_length=32, arm="BP_TOPK", topk=2, mutation_rate=1.0,
        bond_protection_ratio=0.0, backend="numpy",
    )
    # Three runs: length 8 at 0..7, length 5 at 10..14, length 2 at 18..19.
    parent = np.full(32, 14, dtype=np.uint8)
    parent[0:8]   = np.arange(1, 9, dtype=np.uint8)       # len 8 → top-1
    parent[10:15] = np.arange(1, 6, dtype=np.uint8)       # len 5 → top-2
    parent[18:20] = np.array([3, 4], dtype=np.uint8)      # len 2 → NOT in top-2

    rng = random.Random(1)
    child = mutate(parent, cfg, rng)

    # Top-2 runs are protected (frozen).
    assert np.array_equal(parent[0:8], child[0:8])
    assert np.array_equal(parent[10:15], child[10:15])
    # Length-2 run at 18..19 is NOT protected — at mutation_rate=1.0 both cells resample.
    # The length-2 run contains only values {3,4}; post-resample they can take any 0..15 value.
    # Run the check across multiple RNG seeds to rule out the ~(2/16)² chance of identity.
    diffs = 0
    for s in range(20):
        c = mutate(parent, cfg, random.Random(s))
        if not np.array_equal(parent[18:20], c[18:20]):
            diffs += 1
    assert diffs >= 17  # overwhelmingly often the unprotected run mutates


# ---------- Arms A and B: protection flag has no effect ----------


def test_protection_no_op_on_arm_a():
    """Arm A has no bond structure; bond_protection_ratio is ignored."""
    cfg_prot = ChemTapeConfig(
        tape_length=32, arm="A", mutation_rate=1.0,
        bond_protection_ratio=0.0, backend="numpy",
    )
    cfg_uniform = ChemTapeConfig(
        tape_length=32, arm="A", mutation_rate=1.0, backend="numpy",
    )
    parent = np.arange(32, dtype=np.uint8) % 16
    # Same RNG seed → identical output regardless of protection setting (A ignores it).
    c1 = mutate(parent, cfg_prot, random.Random(7))
    c2 = mutate(parent, cfg_uniform, random.Random(7))
    assert np.array_equal(c1, c2)


def test_protection_no_op_on_arm_b():
    """Arm B (strict): currently the protection flag applies only to BP/BP_TOPK;
    Arm B uses the uniform path."""
    cfg_prot = ChemTapeConfig(
        tape_length=32, arm="B", mutation_rate=1.0,
        bond_protection_ratio=0.0, backend="numpy",
    )
    cfg_uniform = ChemTapeConfig(
        tape_length=32, arm="B", mutation_rate=1.0, backend="numpy",
    )
    parent = np.arange(32, dtype=np.uint8) % 16
    c1 = mutate(parent, cfg_prot, random.Random(7))
    c2 = mutate(parent, cfg_uniform, random.Random(7))
    assert np.array_equal(c1, c2)


# ---------- Hash stability ----------


def test_hash_unchanged_when_protection_is_default():
    """Adding bond_protection_ratio with default r=1.0 must not change existing hashes."""
    c_bp = ChemTapeConfig(arm="BP", bond_protection_ratio=1.0)
    c_bp_explicit = ChemTapeConfig(arm="BP")  # default
    c_topk = ChemTapeConfig(arm="BP_TOPK", topk=3, bond_protection_ratio=1.0)
    c_topk_explicit = ChemTapeConfig(arm="BP_TOPK", topk=3)
    assert c_bp.hash() == c_bp_explicit.hash()
    assert c_topk.hash() == c_topk_explicit.hash()


def test_hash_differs_when_protection_is_active():
    c1 = ChemTapeConfig(arm="BP_TOPK", topk=3, bond_protection_ratio=1.0)
    c2 = ChemTapeConfig(arm="BP_TOPK", topk=3, bond_protection_ratio=0.1)
    assert c1.hash() != c2.hash()


# ---------- Smoke test: full evolution with protection ----------


@pytest.mark.parametrize("ratio", [0.1, 0.3])
def test_bp_topk_with_protection_smoke(ratio):
    from folding_evolution.chem_tape.evolve import run_evolution

    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=6,
        backend="numpy",
        arm="BP_TOPK",
        topk=3,
        bond_protection_ratio=ratio,
        seed=0,
    )
    result = run_evolution(cfg)
    assert 0.0 <= result.best_fitness <= 1.0
