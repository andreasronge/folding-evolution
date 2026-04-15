"""End-to-end parity: pop-batch path vs. per-individual Rust path inside
`evaluate_population`.

The fast path in evaluate.py dispatches to `_rust_exec_pop_batch` when
available. We temporarily disable it (monkeypatch `_HAS_POP_BATCH = False`)
and confirm fitnesses + predictions come out bitwise identical against the
per-individual path. This guards against user-visible behaviour changes
from the refactor.
"""

from __future__ import annotations

import random

import numpy as np
import pytest

from folding_evolution.chem_tape import evaluate as ev_mod
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import evaluate_population
from folding_evolution.chem_tape.evolve import random_genotype
from folding_evolution.chem_tape.tasks import build_task


def _run_under_flag(cfg, task, pop, flag_value):
    saved = ev_mod._HAS_POP_BATCH
    ev_mod._HAS_POP_BATCH = flag_value
    try:
        return evaluate_population(pop, task, cfg)
    finally:
        ev_mod._HAS_POP_BATCH = saved


@pytest.mark.skipif(
    not getattr(ev_mod, "_HAS_POP_BATCH", False),
    reason="pop-batch extension not built",
)
@pytest.mark.parametrize("alphabet,task_name,arm", [
    # Cover every arm. A = direct stack-GP (tape is the program, no decode);
    # B = strict longest-active-run; BP = permeable longest-run; BP_TOPK = top-K.
    ("v1", "count_r", "A"),
    ("v1", "count_r", "B"),
    ("v1", "has_upper", "BP"),
    ("v1", "count_r", "BP_TOPK"),
    ("v1", "sum_gt_10", "BP_TOPK"),
    ("v2_probe", "sum_gt_10_v2", "BP_TOPK"),
    ("v2_probe", "sum_gt_10_slot", "BP_TOPK"),
])
def test_pop_batch_matches_per_program_path(alphabet, task_name, arm):
    cfg = ChemTapeConfig(
        task=task_name,
        alphabet=alphabet,
        arm=arm,
        topk=3 if arm == "BP_TOPK" else 1,
        tape_length=32,
        n_examples=32,
        holdout_size=0,
        pop_size=64,
        generations=1,
        seed=7,
    )
    task = build_task(cfg, cfg.seed)
    rng = random.Random(cfg.seed)
    pop = [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]

    fits_fast, preds_fast = _run_under_flag(cfg, task, pop, True)
    fits_slow, preds_slow = _run_under_flag(cfg, task, pop, False)

    assert np.array_equal(preds_fast, preds_slow), (
        f"pop-batch predictions diverge from per-program path under "
        f"alphabet={alphabet}, task={task_name}, arm={arm}"
    )
    assert np.array_equal(fits_fast, fits_slow)


@pytest.mark.skipif(
    not getattr(ev_mod, "_HAS_POP_BATCH", False),
    reason="pop-batch extension not built",
)
def test_pop_batch_matches_per_program_path_evolve_k():
    """§12 evolve-K: cell 0 is the per-individual K header; decode runs on
    tape[1:] at that individual's own K. This path iterates in Python and is
    the most fragile BP_TOPK case — pop-batch must match it exactly."""
    cfg = ChemTapeConfig(
        task="count_r",
        alphabet="v1",
        arm="BP_TOPK",
        topk=3,
        tape_length=32,
        n_examples=16,
        holdout_size=0,
        pop_size=32,
        generations=1,
        evolve_k=True,
        evolve_k_values="1,2,3,8",
        seed=11,
    )
    task = build_task(cfg, cfg.seed)
    rng = random.Random(cfg.seed)
    pop = [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]

    fits_fast, preds_fast = _run_under_flag(cfg, task, pop, True)
    fits_slow, preds_slow = _run_under_flag(cfg, task, pop, False)

    assert np.array_equal(preds_fast, preds_slow)
    assert np.array_equal(fits_fast, fits_slow)


@pytest.mark.skipif(
    not getattr(ev_mod, "_HAS_POP_BATCH", False),
    reason="pop-batch extension not built",
)
def test_pop_batch_matches_per_program_path_at_shipped_scale():
    """Pin parity at the shipped regime (pop=1024). A scale-only divergence
    (memory-pressure, buffer overrun, chunk-size edge case) won't appear at
    pop=64 but would surface here."""
    cfg = ChemTapeConfig(
        task="sum_gt_10_v2",
        alphabet="v2_probe",
        arm="BP_TOPK",
        topk=3,
        bond_protection_ratio=0.5,
        tape_length=32,
        n_examples=64,
        holdout_size=0,
        pop_size=1024,
        generations=1,
        seed=0,
    )
    task = build_task(cfg, cfg.seed)
    rng = random.Random(cfg.seed)
    pop = [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]

    fits_fast, preds_fast = _run_under_flag(cfg, task, pop, True)
    fits_slow, preds_slow = _run_under_flag(cfg, task, pop, False)

    assert np.array_equal(preds_fast, preds_slow)
    assert np.array_equal(fits_fast, fits_slow)
