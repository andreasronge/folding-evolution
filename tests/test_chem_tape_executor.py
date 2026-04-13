"""Chem-tape executor: per-op correctness + closed-semantics guarantees (§Layer 3)."""

import numpy as np

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.executor import execute_program, OP_CAP


def _run(tokens, alphabet=None, inp_value="", inp_type="str") -> int:
    alphabet = alphabet or alph.TaskAlphabet()
    return execute_program(tokens, alphabet, inp_value, inp_type)


def test_empty_program_yields_zero():
    assert _run([]) == 0


def test_all_nop_program_yields_zero():
    assert _run([alph.NOP, alph.NOP, alph.NOP]) == 0


def test_reserved_ids_execute_as_nop():
    # CONST_1 then RESERVED_14 — reserved should not alter top of stack.
    assert _run([alph.CONST_1, alph.RESERVED_14]) == 1
    assert _run([alph.CONST_1, alph.RESERVED_15]) == 1


def test_add_basic():
    # CONST_1 DUP ADD → 1+1 = 2
    assert _run([alph.CONST_1, alph.DUP, alph.ADD]) == 2


def test_add_on_empty_stack_yields_zero():
    assert _run([alph.ADD]) == 0


def test_gt_basic():
    # 1 1 ADD 1 GT → (2 > 1) = 1
    assert _run([alph.CONST_1, alph.DUP, alph.ADD, alph.CONST_1, alph.GT]) == 1
    # 1 1 GT → (1 > 1) = 0
    assert _run([alph.CONST_1, alph.CONST_1, alph.GT]) == 0


def test_swap_exchanges_top_two():
    # 0 1 SWAP → top is 0, below is 1; GT (1 > 0) = 1.
    assert _run([alph.CONST_0, alph.CONST_1, alph.SWAP, alph.GT]) == 1


def test_dup_duplicates_top():
    assert _run([alph.CONST_1, alph.DUP, alph.ADD]) == 2


def test_chars_and_map_eq_r_count_r_idiom():
    """INPUT CHARS MAP_EQ_R SUM on 'RrRx' → 2 (count of 'R')."""
    alphabet = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R)
    tokens = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM]
    assert execute_program(tokens, alphabet, "RrRx", "str") == 2


def test_map_is_upper_idiom_any():
    """INPUT CHARS MAP_IS_UPPER ANY → 1 iff any uppercase present."""
    alphabet = alph.TaskAlphabet(slot_12=alph.OP_MAP_IS_UPPER)
    tokens = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.ANY]
    assert execute_program(tokens, alphabet, "hello", "str") == 0
    assert execute_program(tokens, alphabet, "helloR", "str") == 1


def test_sum_on_intlist_input():
    """INPUT SUM → sum of the intlist input."""
    tokens = [alph.INPUT, alph.SUM]
    assert execute_program(tokens, alph.TaskAlphabet(), (1, 2, 3, 4), "intlist") == 10


def test_reduce_add_equals_sum_in_v1():
    """v1 REDUCE_ADD is a fixed sum combinator."""
    tokens = [alph.INPUT, alph.REDUCE_ADD]
    assert execute_program(tokens, alph.TaskAlphabet(), (2, 3, 5), "intlist") == 10


def test_wrong_type_operand_coerced_to_default():
    """ADD expects ints; after CHARS the top is a charlist — ADD sees 0+0 = 0."""
    alphabet = alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R)
    tokens = [alph.INPUT, alph.CHARS, alph.ADD]
    # With non-int top, ADD coerces both operands to int default (0).
    assert execute_program(tokens, alphabet, "abc", "str") == 0


def test_non_int_final_top_coerced_to_zero():
    """INPUT CHARS alone leaves a charlist on top; final output must be int-coerced."""
    tokens = [alph.INPUT, alph.CHARS]
    assert execute_program(tokens, alph.TaskAlphabet(), "xy", "str") == 0


def test_op_cap_truncates():
    """Programs longer than OP_CAP are truncated."""
    # Build a long sequence: start with CONST_1, then hundreds of NOPs, then never
    # reach an ADD past the cap. The top remains 1.
    tokens = [alph.CONST_1] + [alph.NOP] * (OP_CAP + 50) + [alph.CONST_0]
    # Within cap: CONST_1 + 255 NOPs → top is 1. CONST_0 past cap is skipped.
    assert execute_program(tokens, alph.TaskAlphabet(), "", "str") == 1


def test_any_on_empty_intlist():
    assert _run([alph.ANY]) == 0


def test_any_on_intlist_with_zeros():
    """INPUT ANY on (0,0,0) → 0."""
    assert execute_program([alph.INPUT, alph.ANY], alph.TaskAlphabet(), (0, 0, 0), "intlist") == 0
    assert execute_program([alph.INPUT, alph.ANY], alph.TaskAlphabet(), (0, 1, 0), "intlist") == 1


def test_slot_nop_is_no_op():
    """A task with slot_12=NOP treats token 12 as NOP."""
    alphabet = alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP)
    tokens = [alph.CONST_1, alph.SLOT_12, alph.SLOT_13]
    assert execute_program(tokens, alphabet, "", "str") == 1
