"""Differential test harness for the chem-tape executor.

The Python executor in `chem_tape/executor.py` is the reference implementation
of the spec (§Layer 3 closed semantics). This harness runs it against a
pluggable "candidate" executor on thousands of randomized (program, input)
pairs plus a battery of hand-crafted edge cases.

Purpose: safety net for the upcoming Rust port. To activate the Rust side,
set `CANDIDATE_EXECUTOR` below to the Rust entry point. Until then the
candidate is the Python reference itself, so this suite is tautological —
but it pins the fixture set and the coverage assertions, so the Rust port
gets graded against a fixed rubric the moment it lands.
"""

from __future__ import annotations

import random
from typing import Callable

import pytest

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.executor import OP_CAP, execute_program as py_execute


def _rust_execute(tokens, tape_alphabet, input_value, input_type):
    """Rust executor wrapper matching the Python reference's signature."""
    from _folding_rust import rust_chem_execute
    return rust_chem_execute(
        [int(t) for t in tokens],
        tape_alphabet.slot_12,
        tape_alphabet.slot_13,
        input_value,
        input_type,
    )


CANDIDATE_EXECUTOR: Callable[..., int] = _rust_execute


def _to_i64(x: int) -> int:
    """Wrap a Python unbounded int into the signed 64-bit range.

    The Rust executor uses i64 wrapping arithmetic; Python ints are unbounded.
    In production, predictions are stored in `np.int64` arrays which also wrap,
    so comparing in i64 space matches real-world behavior.
    """
    return ((int(x) + (1 << 63)) % (1 << 64)) - (1 << 63)


SLOT_BINDINGS = [alph.OP_NOP, alph.OP_MAP_EQ_R, alph.OP_MAP_IS_UPPER]


# ---------------- Generators ----------------

def _gen_program(rng: random.Random, length: int) -> list[int]:
    return [rng.randint(0, 15) for _ in range(length)]


def _gen_str(rng: random.Random, length: int) -> str:
    # Include 'R' explicitly so MAP_EQ_R hits truthy paths often; include
    # upper and lower so MAP_IS_UPPER is exercised both ways.
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ R"
    return "".join(rng.choice(chars) for _ in range(length))


def _gen_intlist(rng: random.Random, length: int) -> tuple[int, ...]:
    return tuple(rng.randint(-5, 20) for _ in range(length))


def _gen_alphabet(rng: random.Random) -> alph.TaskAlphabet:
    return alph.TaskAlphabet(
        slot_12=rng.choice(SLOT_BINDINGS),
        slot_13=rng.choice(SLOT_BINDINGS),
    )


# ---------------- Core check ----------------

def _check(program, alphabet, inp_value, inp_type) -> None:
    """Run both executors; assert identical outputs with a clear diff on failure."""
    expected = _to_i64(py_execute(program, alphabet, inp_value, inp_type))
    got = CANDIDATE_EXECUTOR(program, alphabet, inp_value, inp_type)
    assert got == expected, (
        "executor divergence:\n"
        f"  program  = {list(program)}\n"
        f"  alphabet = {alphabet}\n"
        f"  input    = {inp_value!r} (type {inp_type})\n"
        f"  expected = {expected}\n"
        f"  got      = {got}"
    )


# ---------------- Hand-crafted edge cases ----------------

def test_empty_program_both_input_types():
    _check([], alph.TaskAlphabet(), "", "str")
    _check([], alph.TaskAlphabet(), (), "intlist")


def test_every_single_token_on_empty_stack():
    # For each token id, a 1-op program exercises its empty-stack behavior.
    for tid in range(16):
        _check([tid], alph.TaskAlphabet(), "Rabc", "str")
        _check([tid], alph.TaskAlphabet(), (1, 2, 3), "intlist")


def test_every_slot_binding_pair():
    # Slot 12/13 with every combination of {NOP, MAP_EQ_R, MAP_IS_UPPER}.
    for s12 in SLOT_BINDINGS:
        for s13 in SLOT_BINDINGS:
            ab = alph.TaskAlphabet(slot_12=s12, slot_13=s13)
            _check([alph.INPUT, alph.CHARS, alph.SLOT_12], ab, "Rabc", "str")
            _check([alph.INPUT, alph.CHARS, alph.SLOT_13], ab, "Rabc", "str")


def test_reserved_ids_are_nop_in_v1():
    _check([alph.CONST_1, alph.RESERVED_14], alph.TaskAlphabet(), "", "str")
    _check([alph.CONST_1, alph.RESERVED_15], alph.TaskAlphabet(), "", "str")


def test_wrong_type_on_top_preserves_mismatched_value():
    # INPUT pushes str; SUM expects intlist → returns default 0 without
    # consuming the str (spec §Layer 3). A follow-up CHARS must still see
    # the str and succeed.
    _check(
        [alph.INPUT, alph.SUM, alph.CHARS, alph.SLOT_12],
        alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R),
        "Rab",
        "str",
    )


def test_op_cap_truncation():
    # Programs longer than OP_CAP must be truncated, not executed fully.
    # 300 CONST_1 ops → after OP_CAP ops, top-of-stack is 1.
    _check([alph.CONST_1] * (OP_CAP + 50), alph.TaskAlphabet(), "", "str")
    # Last few ops *after* the cap would have mattered if not capped.
    prog = [alph.CONST_1] * OP_CAP + [alph.CONST_0] * 50  # would overwrite top
    _check(prog, alph.TaskAlphabet(), "", "str")


def test_non_int_final_top_coerces_to_zero():
    _check([alph.INPUT], alph.TaskAlphabet(), "hello", "str")             # str top
    _check([alph.INPUT], alph.TaskAlphabet(), (1, 2), "intlist")          # intlist top
    _check([alph.INPUT, alph.CHARS], alph.TaskAlphabet(), "ab", "str")    # charlist top


def test_empty_string_and_empty_intlist():
    _check([alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM],
           alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R), "", "str")
    _check([alph.INPUT, alph.SUM, alph.CONST_1, alph.GT],
           alph.TaskAlphabet(), (), "intlist")


def test_deep_stack_arithmetic():
    # 1 DUP DUP DUP ADD ADD ADD = 4.
    _check(
        [alph.CONST_1, alph.DUP, alph.DUP, alph.DUP,
         alph.ADD, alph.ADD, alph.ADD],
        alph.TaskAlphabet(), "", "str",
    )


def test_task_shaped_programs_for_sum_gt_10():
    # INPUT SUM CONST_1 ... (build a threshold of 10 from CONST_1s) GT.
    tens = [alph.CONST_1, alph.DUP, alph.ADD] * 3 + [alph.CONST_1, alph.ADD]  # 10
    prog = [alph.INPUT, alph.SUM] + tens + [alph.GT]
    _check(prog, alph.TaskAlphabet(), (3, 4, 5, 6), "intlist")   # sum=18 → 1
    _check(prog, alph.TaskAlphabet(), (0, 1, 2, 3), "intlist")   # sum=6 → 0


def test_task_shaped_programs_for_count_r():
    # count_r pattern: INPUT CHARS MAP_EQ_R SUM.
    prog = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM]
    ab = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R)
    _check(prog, ab, "RaRb", "str")
    _check(prog, ab, "abcd", "str")


def test_task_shaped_programs_for_has_upper():
    prog = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.ANY]
    ab = alph.TaskAlphabet(slot_12=alph.OP_MAP_IS_UPPER)
    _check(prog, ab, "abcABC", "str")
    _check(prog, ab, "abcdef", "str")


# ---------------- Randomized sweep ----------------

@pytest.mark.parametrize("seed", list(range(20)))
def test_random_programs_with_string_inputs(seed):
    rng = random.Random(seed)
    for _ in range(200):
        prog = _gen_program(rng, rng.randint(0, 40))
        ab = _gen_alphabet(rng)
        s = _gen_str(rng, rng.randint(0, 20))
        _check(prog, ab, s, "str")


@pytest.mark.parametrize("seed", list(range(20)))
def test_random_programs_with_intlist_inputs(seed):
    rng = random.Random(seed)
    for _ in range(200):
        prog = _gen_program(rng, rng.randint(0, 40))
        ab = _gen_alphabet(rng)
        xs = _gen_intlist(rng, rng.randint(0, 8))
        _check(prog, ab, xs, "intlist")


@pytest.mark.parametrize("seed", list(range(5)))
def test_random_programs_hit_op_cap(seed):
    rng = random.Random(seed + 1000)
    for _ in range(50):
        prog = _gen_program(rng, OP_CAP + rng.randint(1, 100))
        ab = _gen_alphabet(rng)
        xs = _gen_intlist(rng, 4)
        _check(prog, ab, xs, "intlist")


# ---------------- Coverage sanity ----------------

def test_random_sweep_exercises_every_token_id():
    """Guard: if the generator ever stops producing all 16 token ids, the
    randomized sweep is a poor fixture for the Rust port. Assert coverage."""
    rng = random.Random(0)
    seen: set[int] = set()
    for _ in range(20):
        for tid in _gen_program(rng, 40):
            seen.add(tid)
        if len(seen) == 16:
            break
    assert seen == set(range(16)), f"random generator missed token ids: {set(range(16)) - seen}"
