"""Map-bias notebook §4, steps 1-3: standard lexicase, lineage tracking,
alphabet-specific decode separators."""

from __future__ import annotations

import random

import numpy as np
import pytest

from folding_evolution.chem_tape import engine_numpy
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import _programs_for_arm
from folding_evolution.chem_tape.evolve import _lexicase_select, run_evolution

try:
    from _folding_rust import rust_chem_decode_topk
except ImportError:  # pragma: no cover
    rust_chem_decode_topk = None


def _small(**kw) -> ChemTapeConfig:
    base = dict(task="sum_gt_10_AND_max_gt_5", alphabet="v2_probe", arm="BP_TOPK", topk=3,
                bond_protection_ratio=0.5, pop_size=64, generations=30, backend="numpy",
                n_examples=64, holdout_size=0, seed=3)
    base.update(kw)
    return ChemTapeConfig(**base)


# ---------- step 1: lexicase ----------

def test_standard_lexicase_is_uniform_over_individuals_when_no_case_splits():
    # Two behaviour groups that pass every case: the filter never narrows, so
    # standard lexicase must pick individuals uniformly (group share ∝ size).
    groups = [np.arange(0, 9), np.array([9])]
    group_cases = np.ones((2, 5), dtype=bool)
    rng = random.Random(0)
    picks = [_lexicase_select(groups, group_cases, rng) for _ in range(4000)]
    assert 0.05 < np.mean(np.array(picks) == 9) < 0.15  # expected 0.10


def test_group_lexicase_gives_equal_share_per_group():
    groups = [np.arange(0, 9), np.array([9])]
    group_cases = np.ones((2, 5), dtype=bool)
    rng = random.Random(0)
    picks = [_lexicase_select(groups, group_cases, rng, weight_by_size=False) for _ in range(4000)]
    assert 0.45 < np.mean(np.array(picks) == 9) < 0.55  # expected 0.50


def test_lexicase_modes_hash_differently():
    assert _small(selection_mode="lexicase").hash() != _small(selection_mode="lexicase_group").hash()


# ---------- step 2: lineage ----------

@pytest.mark.parametrize("mode", ["tournament", "lexicase"])
def test_lineage_tracking_does_not_change_the_run(mode):
    plain = run_evolution(_small(selection_mode=mode))
    tracked = run_evolution(_small(selection_mode=mode, track_lineage=True))
    assert [s.best_genotype_hex for s in plain.stats.history] == \
           [s.best_genotype_hex for s in tracked.stats.history]
    assert tracked.lineage is not None and plain.lineage is None


def test_lineage_chain_is_consistent():
    res = run_evolution(_small(track_lineage=True))
    lin = res.lineage
    n = len(lin["generation"])
    assert list(lin["generation"]) == list(range(n))
    assert lin["fitness"][-1] == pytest.approx(res.best_fitness)
    assert np.array_equal(lin["genome"][-1], res.best_genotype)
    for k in range(1, n):
        assert lin["index"][k - 1] == lin["parent_main"][k]
        if lin["kind"][k] == 1:  # the walk follows the fitter parent
            assert lin["fitness"][k - 1] >= lin["other_fitness"][k]
        if lin["kind"][k] == 0:  # elite copies are unmutated
            assert np.array_equal(lin["genome"][k], lin["genome"][k - 1])
        if lin["kind"][k] == 2 and not lin["mutated"][k]:
            assert np.array_equal(lin["genome"][k], lin["genome"][k - 1])


def test_lineage_rejected_for_islands():
    with pytest.raises(ValueError):
        run_evolution(_small(track_lineage=True, n_islands=2))


# ---------- step 3: separators ----------

def test_default_decode_keeps_legacy_separators():
    cfg = _small()
    assert cfg.decode_separators() == (14, 15)
    assert _small(alphabet_separators=True, alphabet="v1").decode_separators() == (14, 15)


def test_alphabet_separators_split_on_20_21_and_execute_14_15():
    tape = np.array([[1, 5, 15, 8, 20, 1, 18, 14, 16, 8, 21, 3]], dtype=np.uint8)
    legacy = _programs_for_arm(_small(topk=3), tape)[0]
    fixed = _programs_for_arm(_small(topk=3, alphabet_separators=True), tape)[0]
    assert 15 not in legacy and 14 not in legacy and 20 in legacy
    assert fixed == [1, 5, 15, 8, 1, 18, 14, 16, 8, 3]


@pytest.mark.skipif(rust_chem_decode_topk is None, reason="Rust extension not built")
@pytest.mark.parametrize("seps", [None, (20, 21)])
def test_rust_and_numpy_decode_agree(seps):
    rng = np.random.default_rng(1)
    tapes = rng.integers(0, 22, size=(300, 32), dtype=np.uint8)
    args = () if seps is None else (list(seps),)
    rust = rust_chem_decode_topk(tapes.tobytes(), 32, 3, [], False, *args)
    mask = engine_numpy.compute_topk_runnable_mask(tapes, 3, seps)
    numpy_progs = [tapes[b][mask[b]].tolist() for b in range(tapes.shape[0])]
    assert [list(p) for p in rust] == numpy_progs
