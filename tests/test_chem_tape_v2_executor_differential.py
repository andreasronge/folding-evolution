"""v2-probe differential test: Python reference vs Rust under alphabet="v2_probe".

Mirror of `test_chem_tape_executor_differential.py`, but exercising the v2
token range (0..21) and the new slot bindings (MAP_EQ_E, REDUCE_ADD,
REDUCE_MAX). Also runs every v1 hand-crafted case under v2_probe to confirm
the v1 subset still behaves identically when v2 dispatch is active.

Spec source-of-truth: tests/test_chem_tape_v2_executor.py (Python-only).
This file confirms the Rust port matches that spec on identical inputs.
"""

from __future__ import annotations

import random

import pytest

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.executor import OP_CAP, execute_program as py_execute


def _to_i64(x: int) -> int:
    return ((int(x) + (1 << 63)) % (1 << 64)) - (1 << 63)


def _rust_execute_v2(tokens, tape_alphabet, input_value, input_type):
    from _folding_rust import rust_chem_execute
    return rust_chem_execute(
        [int(t) for t in tokens],
        tape_alphabet.slot_12,
        tape_alphabet.slot_13,
        input_value,
        input_type,
        alphabet_name="v2_probe",
        threshold=int(tape_alphabet.threshold),
    )


def _check(program, alphabet, inp_value, inp_type) -> None:
    expected = _to_i64(
        py_execute(program, alphabet, inp_value, inp_type, alphabet_name="v2_probe")
    )
    got = _rust_execute_v2(program, alphabet, inp_value, inp_type)
    assert got == expected, (
        "v2 executor divergence:\n"
        f"  program  = {list(program)}\n"
        f"  alphabet = slot_12={alphabet.slot_12!r} slot_13={alphabet.slot_13!r} threshold={alphabet.threshold}\n"
        f"  input    = {inp_value!r} (type {inp_type})\n"
        f"  expected = {expected}\n"
        f"  got      = {got}"
    )


# Slot bindings expanded for v2 (all six legal names).
SLOT_BINDINGS_V2 = [
    alph.OP_NOP,
    alph.OP_MAP_EQ_R,
    alph.OP_MAP_IS_UPPER,
    alph.OP_MAP_EQ_E,
    alph.OP_REDUCE_ADD,
    alph.OP_REDUCE_MAX,
]


# ---------------- Hand-crafted v2 edge cases ----------------


def test_every_single_token_in_v2_alphabet_on_empty_stack():
    # All 22 token ids in v2 dispatch — including the 6 new primitives and
    # both separators (20, 21).
    for tid in range(22):
        _check([tid], alph.TaskAlphabet(), "Rabc", "str")
        _check([tid], alph.TaskAlphabet(), (1, 2, 3), "intlist")


def test_const_2_const_5_basic():
    _check([alph.CONST_2], alph.TaskAlphabet(), (), "intlist")
    _check([alph.CONST_5], alph.TaskAlphabet(), (), "intlist")
    _check([alph.CONST_5, alph.CONST_5, alph.ADD], alph.TaskAlphabet(), (), "intlist")


def test_map_eq_e_via_direct_token_and_via_slot():
    ta_slot = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_E)
    _check([alph.INPUT, alph.CHARS, alph.MAP_EQ_E, alph.SUM], alph.TaskAlphabet(), "ElEphant", "str")
    _check([alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM], ta_slot, "ElEphant", "str")


def test_reduce_max_basic_and_empty():
    _check([alph.INPUT, alph.REDUCE_MAX], alph.TaskAlphabet(), (1, 9, 3, 5), "intlist")
    _check([alph.INPUT, alph.REDUCE_MAX], alph.TaskAlphabet(), (), "intlist")
    _check([alph.REDUCE_MAX], alph.TaskAlphabet(), (), "intlist")


@pytest.mark.parametrize("threshold", [-5, 0, 1, 5, 10, 100])
def test_threshold_slot_pushes_task_bound_value(threshold):
    ta = alph.TaskAlphabet(threshold=threshold)
    _check([alph.THRESHOLD_SLOT], ta, (), "intlist")
    _check([alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT], ta, (3, 3, 3, 3), "intlist")


def test_if_gt_choosing_branches():
    # cond=1 → then; cond=0 → else; underflow → 0
    ta = alph.TaskAlphabet()
    _check([alph.CONST_2, alph.CONST_5, alph.CONST_1, alph.IF_GT], ta, (), "intlist")
    _check([alph.CONST_2, alph.CONST_5, alph.CONST_0, alph.IF_GT], ta, (), "intlist")
    _check([alph.IF_GT], ta, (), "intlist")
    _check([alph.CONST_1, alph.CONST_2, alph.IF_GT], ta, (), "intlist")


def test_separators_pass_through_as_nop():
    _check([alph.CONST_1, alph.SEP_A, alph.SEP_B], alph.TaskAlphabet(), (), "intlist")


# §v2.4 compositional programs (architecture-v2 §v2.4 example bodies).
_AND_PROG = [
    alph.CONST_0,
    alph.INPUT, alph.REDUCE_MAX, alph.CONST_5, alph.GT,
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
    alph.IF_GT,
]
_OR_PROG = [
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
    alph.INPUT, alph.REDUCE_MAX, alph.CONST_5, alph.GT,
    alph.DUP,
    alph.IF_GT,
]


@pytest.mark.parametrize("xs", [
    (0, 0, 0, 0),
    (9, 9, 0, 0),
    (6, 6, 0, 0),
    (0, 0, 9, 0),
    (1, 2, 3, 5),
    (3, 3, 3, 3),
    (0, 0, 0, 9),
])
def test_compositional_AND_program_differential(xs):
    _check(_AND_PROG, alph.TaskAlphabet(), xs, "intlist")


@pytest.mark.parametrize("xs", [
    (0, 0, 0, 0),
    (9, 9, 0, 0),
    (6, 6, 0, 0),
    (0, 0, 9, 0),
    (1, 2, 3, 5),
    (3, 3, 3, 3),
    (0, 0, 0, 9),
])
def test_compositional_OR_program_differential(xs):
    _check(_OR_PROG, alph.TaskAlphabet(), xs, "intlist")


# §v2.3: identical body, different threshold.
_SUM_GT_SLOT_BODY = [alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT]


@pytest.mark.parametrize("xs, thr", [
    ((3, 3, 0, 0), 5),
    ((3, 3, 0, 0), 10),
    ((5, 5, 0, 1), 10),
    ((5, 5, 0, 1), 5),
    ((0, 0, 0, 0), 5),
    ((0, 0, 0, 0), 10),
])
def test_v2_3_body_invariance_differential(xs, thr):
    _check(_SUM_GT_SLOT_BODY, alph.TaskAlphabet(threshold=thr), xs, "intlist")


# Slot generalisation matrix.


def test_every_v2_slot_binding_pair():
    for s12 in SLOT_BINDINGS_V2:
        for s13 in SLOT_BINDINGS_V2:
            ta = alph.TaskAlphabet(slot_12=s12, slot_13=s13, threshold=7)
            _check([alph.INPUT, alph.CHARS, alph.SLOT_12], ta, "RrEeXx", "str")
            _check([alph.INPUT, alph.SLOT_13], ta, (1, 5, 9, 2), "intlist")


# ---------------- Randomized v2 sweep ----------------


def _gen_program_v2(rng: random.Random, length: int) -> list[int]:
    return [rng.randint(0, 21) for _ in range(length)]


def _gen_str(rng: random.Random, length: int) -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ R"
    return "".join(rng.choice(chars) for _ in range(length))


def _gen_intlist(rng: random.Random, length: int) -> tuple[int, ...]:
    return tuple(rng.randint(-5, 20) for _ in range(length))


def _gen_alphabet_v2(rng: random.Random) -> alph.TaskAlphabet:
    return alph.TaskAlphabet(
        slot_12=rng.choice(SLOT_BINDINGS_V2),
        slot_13=rng.choice(SLOT_BINDINGS_V2),
        threshold=rng.randint(-20, 20),
    )


@pytest.mark.parametrize("seed", list(range(20)))
def test_random_v2_programs_string(seed):
    rng = random.Random(seed)
    for _ in range(200):
        prog = _gen_program_v2(rng, rng.randint(0, 40))
        ab = _gen_alphabet_v2(rng)
        _check(prog, ab, _gen_str(rng, rng.randint(0, 20)), "str")


@pytest.mark.parametrize("seed", list(range(20)))
def test_random_v2_programs_intlist(seed):
    rng = random.Random(seed)
    for _ in range(200):
        prog = _gen_program_v2(rng, rng.randint(0, 40))
        ab = _gen_alphabet_v2(rng)
        _check(prog, ab, _gen_intlist(rng, rng.randint(0, 8)), "intlist")


def test_op_cap_under_v2():
    _check([alph.CONST_1] * (OP_CAP + 50), alph.TaskAlphabet(), "", "str")
    prog = [alph.CONST_5] * OP_CAP + [alph.CONST_0] * 50
    _check(prog, alph.TaskAlphabet(), "", "str")


# ---------------- v1 cases re-run under v2_probe (superset preservation) ----------------


def test_v1_count_r_idiom_under_v2_dispatch():
    ta = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R)
    _check([alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM], ta, "RaRRb", "str")


def test_v1_sum_gt_10_idiom_under_v2_dispatch():
    tens = [alph.CONST_1, alph.DUP, alph.ADD] * 3 + [alph.CONST_1, alph.ADD]
    prog = [alph.INPUT, alph.SUM] + tens + [alph.GT]
    _check(prog, alph.TaskAlphabet(), (3, 4, 5, 6), "intlist")
    _check(prog, alph.TaskAlphabet(), (0, 1, 2, 3), "intlist")
