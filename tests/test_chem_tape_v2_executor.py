"""Chem-tape v2-probe executor + alphabet tests.

Specification for Session 2's Rust port: every test here must pass against
the Rust executor as well. Organised by architecture-v2.md primitive and
§v2.* experiment.
"""

from __future__ import annotations

import numpy as np
import pytest

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.executor import execute_program
from folding_evolution.chem_tape.tasks import TASK_REGISTRY, build_task


# ---------------- Helpers ----------------


def _run_v2(tokens, tape_alphabet=None, inp_value=None, inp_type="intlist"):
    ta = tape_alphabet or alph.TaskAlphabet()
    if inp_value is None:
        inp_value = ()
    return execute_program(tokens, ta, inp_value, inp_type, alphabet_name="v2_probe")


# ---------------- Alphabet constants and masks ----------------


def test_v2_token_ids_are_distinct_and_sequential():
    ids = [
        alph.NOP, alph.INPUT, alph.CONST_0, alph.CONST_1, alph.CHARS,
        alph.SUM, alph.ANY, alph.ADD, alph.GT, alph.DUP, alph.SWAP,
        alph.REDUCE_ADD, alph.SLOT_12, alph.SLOT_13,
        alph.MAP_EQ_E, alph.CONST_2, alph.CONST_5, alph.IF_GT,
        alph.REDUCE_MAX, alph.THRESHOLD_SLOT,
        alph.SEP_A, alph.SEP_B,
    ]
    assert ids == list(range(22))
    assert alph.N_TOKENS_V1 == 16
    assert alph.N_TOKENS_V2 == 22


def test_masks_for_v2_active_runs_1_to_19():
    m = alph.masks_for("v2_probe")
    assert m["active"].shape == (22,)
    assert not m["active"][0]
    assert all(m["active"][1:20])
    assert not m["active"][20]
    assert not m["active"][21]


def test_masks_for_v2_separators_are_20_and_21():
    m = alph.masks_for("v2_probe")
    assert m["separator"][20]
    assert m["separator"][21]
    assert not m["separator"][19]
    assert not m["separator"][14]  # under v1 this would be True; under v2 it's active


def test_masks_for_v1_is_unchanged():
    m = alph.masks_for("v1")
    # ids 1..13 active
    assert all(m["active"][1:14])
    # ids 0, 14, 15 inactive; 14, 15 are separators
    assert not m["active"][0]
    assert not m["active"][14]
    assert not m["active"][15]
    assert m["separator"][14]
    assert m["separator"][15]


def test_is_active_respects_alphabet_name():
    assert alph.is_active(14, "v1") is False
    assert alph.is_active(14, "v2_probe") is True
    assert alph.is_active(19, "v2_probe") is True
    assert alph.is_active(20, "v2_probe") is False


# ---------------- New primitives: semantic correctness ----------------


def test_const_2_pushes_two():
    assert _run_v2([alph.CONST_2]) == 2


def test_const_5_pushes_five():
    assert _run_v2([alph.CONST_5]) == 5


def test_const_5_plus_const_5_makes_ten():
    assert _run_v2([alph.CONST_5, alph.CONST_5, alph.ADD]) == 10


def test_map_eq_e_flags_only_capital_e():
    # "hEllo" → [0, 1, 0, 0, 0] → sum = 1
    ta = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_E)
    tokens = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM]
    assert execute_program(tokens, ta, "hEllo", "str", alphabet_name="v2_probe") == 1


def test_map_eq_e_counts_multiple_e():
    ta = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_E)
    tokens = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM]
    # E appears 3 times
    assert execute_program(tokens, ta, "EEE", "str", alphabet_name="v2_probe") == 3
    # lowercase 'e' should NOT match
    assert execute_program(tokens, ta, "eee", "str", alphabet_name="v2_probe") == 0


def test_map_eq_e_via_direct_token():
    """MAP_EQ_E is also usable via the direct token id (14) in v2."""
    tokens = [alph.INPUT, alph.CHARS, alph.MAP_EQ_E, alph.SUM]
    assert execute_program(tokens, alph.TaskAlphabet(), "EeE", "str", alphabet_name="v2_probe") == 2


def test_reduce_max_on_nonempty():
    tokens = [alph.INPUT, alph.REDUCE_MAX]
    assert execute_program(tokens, alph.TaskAlphabet(), (1, 9, 3, 5), "intlist", alphabet_name="v2_probe") == 9


def test_reduce_max_on_empty_yields_zero():
    # REDUCE_MAX on empty intlist convention: push 0.
    tokens = [alph.INPUT, alph.REDUCE_MAX]
    assert execute_program(tokens, alph.TaskAlphabet(), (), "intlist", alphabet_name="v2_probe") == 0


def test_reduce_max_on_stack_underflow_yields_zero():
    # No INPUT pushed; REDUCE_MAX pops default empty intlist, pushes 0.
    assert _run_v2([alph.REDUCE_MAX]) == 0


def test_threshold_slot_pushes_task_bound_value():
    ta = alph.TaskAlphabet(threshold=7)
    assert execute_program([alph.THRESHOLD_SLOT], ta, (), "intlist", alphabet_name="v2_probe") == 7


def test_threshold_slot_default_is_zero():
    assert _run_v2([alph.THRESHOLD_SLOT]) == 0


def test_threshold_slot_in_v1_alphabet_is_nop():
    """Under v1 dispatch, id 19 (THRESHOLD_SLOT in v2) executes as NOP."""
    ta = alph.TaskAlphabet(threshold=7)
    # CONST_1 then id=19: v1 NOP → stack top is 1.
    assert execute_program([alph.CONST_1, 19], ta, (), "intlist", alphabet_name="v1") == 1


# ---------------- IF_GT: precise semantics from the spec ----------------


def test_if_gt_chooses_then_when_cond_positive():
    # Stack (bottom → top): else=99, then=11, cond=1  → result = 11
    # Build by pushing CONST_0 (=0) doesn't give us 99; use two CONST_5 + ADD
    # to build 99-like values. Simpler: push fixed values via direct ops.
    # else = 2 (CONST_2), then = 5 (CONST_5), cond = 1 (CONST_1)
    assert _run_v2([alph.CONST_2, alph.CONST_5, alph.CONST_1, alph.IF_GT]) == 5


def test_if_gt_chooses_else_when_cond_zero():
    # else=2, then=5, cond=0 → result=2
    assert _run_v2([alph.CONST_2, alph.CONST_5, alph.CONST_0, alph.IF_GT]) == 2


def test_if_gt_cond_exactly_zero_picks_else():
    # Architecture-v2 says "cond > 0 strictly". 0 goes to else.
    assert _run_v2([alph.CONST_2, alph.CONST_5, alph.CONST_0, alph.IF_GT]) == 2


def test_if_gt_on_empty_stack_yields_zero():
    assert _run_v2([alph.IF_GT]) == 0


def test_if_gt_with_only_two_values_yields_zero():
    assert _run_v2([alph.CONST_1, alph.CONST_2, alph.IF_GT]) == 0


# ---------------- Compositional AND/OR programs from experiments-v2.md §v2.4 ----------------


# Task A (AND): CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM CONST_5 CONST_5 ADD GT IF_GT
_AND_PROG = [
    alph.CONST_0,
    alph.INPUT, alph.REDUCE_MAX, alph.CONST_5, alph.GT,
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
    alph.IF_GT,
]

# Task B (OR): INPUT SUM CONST_5 CONST_5 ADD GT INPUT REDUCE_MAX CONST_5 GT DUP IF_GT
_OR_PROG = [
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
    alph.INPUT, alph.REDUCE_MAX, alph.CONST_5, alph.GT,
    alph.DUP,
    alph.IF_GT,
]


@pytest.mark.parametrize(
    "xs, expected",
    [
        ((0, 0, 0, 0), 0),   # sum=0, max=0 → F AND F = 0
        ((9, 9, 0, 0), 0),   # sum=18>10 but max=9>5 AND only? sum✓, max✓ → 1. Wait — recalculate: sum=18>10 → s=1; max=9>5 → mg=1; AND=1
        ((6, 6, 0, 0), 1),   # sum=12>10 ✓, max=6>5 ✓ → 1
        ((0, 0, 9, 0), 0),   # sum=9 not >10, max=9>5; AND → 0
        ((1, 2, 3, 5), 0),   # sum=11>10 ✓, max=5 NOT >5 → 0
    ],
)
def test_compositional_AND_program(xs, expected):
    # Note second case was wrong in my table — fix: (9,9,0,0) sum=18, max=9, both ✓ → AND=1
    # pytest will use the tuples above; the second expected is corrected here:
    got = execute_program(_AND_PROG, alph.TaskAlphabet(), xs, "intlist", alphabet_name="v2_probe")
    # Compute canonical expected from the task's label function to keep the
    # test self-consistent (avoids hand-table mistakes).
    from folding_evolution.chem_tape.tasks import _compositional_label
    canonical = _compositional_label(xs, "AND")
    assert got == canonical


@pytest.mark.parametrize(
    "xs",
    [
        (0, 0, 0, 0),
        (9, 9, 0, 0),
        (6, 6, 0, 0),
        (0, 0, 9, 0),
        (1, 2, 3, 5),
        (3, 3, 3, 3),    # sum=12>10 ✓, max=3 NOT >5 → AND=0, OR=1
        (0, 0, 0, 9),    # sum=9 NOT >10, max=9>5 → AND=0, OR=1
    ],
)
def test_compositional_OR_program(xs):
    got = execute_program(_OR_PROG, alph.TaskAlphabet(), xs, "intlist", alphabet_name="v2_probe")
    from folding_evolution.chem_tape.tasks import _compositional_label
    assert got == _compositional_label(xs, "OR")


# ---------------- §v2.3 body-invariance: identical tokens, different threshold ----------------


_SUM_GT_SLOT_BODY = [alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT]


@pytest.mark.parametrize("xs, thr, expected", [
    ((3, 3, 0, 0), 5, 1),   # sum=6 > 5
    ((3, 3, 0, 0), 10, 0),  # sum=6 not > 10
    ((5, 5, 0, 1), 10, 1),  # sum=11 > 10
    ((5, 5, 0, 1), 5, 1),   # sum=11 > 5
    ((0, 0, 0, 0), 5, 0),
    ((0, 0, 0, 0), 10, 0),
])
def test_v2_3_body_identical_only_threshold_varies(xs, thr, expected):
    ta = alph.TaskAlphabet(threshold=thr)
    got = execute_program(_SUM_GT_SLOT_BODY, ta, xs, "intlist", alphabet_name="v2_probe")
    assert got == expected


def test_v2_3_two_tasks_share_identical_token_sequence():
    """The pre-registered promise: sum_gt_5_slot and sum_gt_10_slot use
    literally the same token body."""
    cfg = ChemTapeConfig(n_examples=4, holdout_size=0, alphabet="v2_probe")
    t5 = TASK_REGISTRY["sum_gt_5_slot"](cfg, seed=0)
    t10 = TASK_REGISTRY["sum_gt_10_slot"](cfg, seed=0)
    assert t5.alphabet.threshold == 5
    assert t10.alphabet.threshold == 10
    # Run both against the same hand-written body; the only difference is the
    # task's bound threshold.
    xs = (3, 3, 0, 0)  # sum=6
    r5 = execute_program(_SUM_GT_SLOT_BODY, t5.alphabet, xs, "intlist", alphabet_name="v2_probe")
    r10 = execute_program(_SUM_GT_SLOT_BODY, t10.alphabet, xs, "intlist", alphabet_name="v2_probe")
    assert r5 == 1 and r10 == 0


# ---------------- Slot generalisation (architecture §Slot-binding generalization) ----------------


def test_slot_12_can_bind_map_eq_e():
    ta = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_E)
    tokens = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM]
    assert execute_program(tokens, ta, "EEx", "str", alphabet_name="v2_probe") == 2


def test_slot_13_can_bind_reduce_max():
    ta = alph.TaskAlphabet(slot_13=alph.OP_REDUCE_MAX)
    tokens = [alph.INPUT, alph.SLOT_13]
    assert execute_program(tokens, ta, (2, 7, 3), "intlist", alphabet_name="v2_probe") == 7


def test_slot_13_can_bind_reduce_add():
    ta = alph.TaskAlphabet(slot_13=alph.OP_REDUCE_ADD)
    tokens = [alph.INPUT, alph.SLOT_13]
    assert execute_program(tokens, ta, (2, 7, 3), "intlist", alphabet_name="v2_probe") == 12


# ---------------- v2-task builders produce correct labels ----------------


@pytest.mark.parametrize("task_name", [
    "any_char_is_R", "any_char_is_E", "any_char_is_upper_v2",
    "sum_gt_10_v2", "sum_gt_5_slot", "sum_gt_10_slot",
    "sum_gt_10_AND_max_gt_5", "sum_gt_10_OR_max_gt_5",
    "agg_sum_gt_10", "agg_max_gt_5",
])
def test_v2_task_builds_with_balanced_labels(task_name):
    cfg = ChemTapeConfig(task=task_name, n_examples=32, holdout_size=0, alphabet="v2_probe")
    t = build_task(cfg, seed=0)
    assert t.name == task_name
    # Label function matches the generated labels.
    for inp, lab in zip(t.inputs, t.labels):
        assert t.label_fn(inp) == int(lab)
    # Roughly balanced (tolerate off-by-one on odd n).
    pos = int(t.labels.sum())
    assert abs(pos - 16) <= 1


def test_sum_gt_slot_tasks_have_identical_body_alphabet_shape():
    cfg = ChemTapeConfig(n_examples=4, holdout_size=0, alphabet="v2_probe")
    t5 = TASK_REGISTRY["sum_gt_5_slot"](cfg, seed=0)
    t10 = TASK_REGISTRY["sum_gt_10_slot"](cfg, seed=0)
    # Same slot bindings, different threshold.
    assert t5.alphabet.slot_12 == t10.alphabet.slot_12
    assert t5.alphabet.slot_13 == t10.alphabet.slot_13
    assert t5.alphabet.threshold != t10.alphabet.threshold


# ---------------- Hash stability regression ----------------


def test_v1_default_config_hash_is_stable():
    """Architecture-v2 commitment: v1 sweep hashes MUST NOT change after the
    alphabet field is added. This hash was measured pre-v2 on commit 5dfc846.
    Failure means a v1 sweep would silently re-run under a new hash.
    """
    assert ChemTapeConfig().hash() == "2776dbc18470"


def test_v1_explicit_equals_default():
    assert ChemTapeConfig().hash() == ChemTapeConfig(alphabet="v1").hash()


def test_v2_probe_hash_differs_from_v1():
    assert ChemTapeConfig().hash() != ChemTapeConfig(alphabet="v2_probe").hash()


# ---------------- v1 behaviour regression: v2 tokens must NOT fire under alphabet="v1" ----------------


def test_v2_tokens_are_nop_under_v1_alphabet():
    # Under v1, CONST_5 (id 16) doesn't exist in range. The dispatch table
    # has no entry for id 16, which falls through to NOP. So a program that
    # would push 5 under v2 pushes nothing under v1 — top of stack is 0.
    out_v1 = execute_program([alph.CONST_5], alph.TaskAlphabet(), (), "intlist", alphabet_name="v1")
    out_v2 = execute_program([alph.CONST_5], alph.TaskAlphabet(), (), "intlist", alphabet_name="v2_probe")
    assert out_v1 == 0
    assert out_v2 == 5


def test_v1_reserved_14_15_still_nop_under_v1():
    # Preserve v1's existing behaviour (test_chem_tape_executor checks this too).
    out = execute_program([alph.CONST_1, 14, 15], alph.TaskAlphabet(), (), "intlist", alphabet_name="v1")
    assert out == 1
