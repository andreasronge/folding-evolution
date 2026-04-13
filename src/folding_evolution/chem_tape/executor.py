"""RPN stack executor for chem-tape v1.

Closed semantics (spec §Layer 3): every combination of tokens produces some
output, never crashes. Pop-from-empty yields the op's declared input-type
default; wrong-typed operands are coerced to the same default. Execution is
capped at 256 ops; the final top-of-stack (if int) is returned, else 0.
"""

from __future__ import annotations

from typing import Callable

from . import alphabet as alph


# ---------------- Value representation ----------------
#
# Every value on the stack is (type_tag, payload):
#   - "int":      Python int
#   - "intlist":  tuple[int, ...]         (immutable; produced by MAP_* / CHARS)
#   - "str":      str                      (input-only in v1)
#   - "charlist": tuple[str, ...]          (single-char strings; produced by CHARS)

DEFAULTS: dict[str, object] = {
    "int": 0,
    "intlist": (),
    "str": "",
    "charlist": (),
}

OP_CAP = 256


def safe_pop(stack: list, expected_type: str):
    """Pop a value of `expected_type` from the stack.

    Spec §Layer 3: empty stack → the declared type's default; wrong type → the
    declared type's default *without consuming* the mismatched top (so the
    caller can't get stuck peeling off values of the wrong type). The "any"
    sentinel matches any type.
    """
    if not stack:
        return DEFAULTS[expected_type] if expected_type != "any" else DEFAULTS["int"]
    if expected_type == "any":
        ttag, payload = stack.pop()
        return (ttag, payload)
    ttag, payload = stack[-1]
    if ttag != expected_type:
        return DEFAULTS[expected_type]
    stack.pop()
    return payload


def push_int(stack: list, v: int) -> None:
    stack.append(("int", int(v)))


def push_intlist(stack: list, v) -> None:
    stack.append(("intlist", tuple(int(x) for x in v)))


def push_str(stack: list, v: str) -> None:
    stack.append(("str", str(v)))


def push_charlist(stack: list, v) -> None:
    stack.append(("charlist", tuple(v)))


# ---------------- Op implementations ----------------

def _op_nop(stack: list, inp_value, inp_type: str) -> None:
    return


def _op_input(stack: list, inp_value, inp_type: str) -> None:
    if inp_type == "str":
        push_str(stack, inp_value)
    elif inp_type == "intlist":
        push_intlist(stack, inp_value)
    else:
        # Unknown input type → push default int.
        push_int(stack, 0)


def _op_const_0(stack: list, inp_value, inp_type: str) -> None:
    push_int(stack, 0)


def _op_const_1(stack: list, inp_value, inp_type: str) -> None:
    push_int(stack, 1)


def _op_chars(stack: list, inp_value, inp_type: str) -> None:
    s = safe_pop(stack, "str")
    push_charlist(stack, list(s))


def _op_sum(stack: list, inp_value, inp_type: str) -> None:
    xs = safe_pop(stack, "intlist")
    push_int(stack, sum(xs))


def _op_any(stack: list, inp_value, inp_type: str) -> None:
    xs = safe_pop(stack, "intlist")
    push_int(stack, 1 if any(x != 0 for x in xs) else 0)


def _op_add(stack: list, inp_value, inp_type: str) -> None:
    b = safe_pop(stack, "int")   # top
    a = safe_pop(stack, "int")
    push_int(stack, a + b)


def _op_gt(stack: list, inp_value, inp_type: str) -> None:
    b = safe_pop(stack, "int")   # top
    a = safe_pop(stack, "int")
    push_int(stack, 1 if a > b else 0)


def _op_dup(stack: list, inp_value, inp_type: str) -> None:
    # Polymorphic; on empty stack, duplicate an int default.
    if not stack:
        push_int(stack, 0)
        push_int(stack, 0)
        return
    top = stack[-1]
    stack.append(top)


def _op_swap(stack: list, inp_value, inp_type: str) -> None:
    # Polymorphic pop-in-reverse with defaults.
    b = stack.pop() if stack else ("int", 0)
    a = stack.pop() if stack else ("int", 0)
    stack.append(b)
    stack.append(a)


def _op_reduce_add(stack: list, inp_value, inp_type: str) -> None:
    # v1: fixed combinator = sum. Higher-order reduce is a v2 feature.
    xs = safe_pop(stack, "intlist")
    push_int(stack, sum(xs))


def _op_map_eq_r(stack: list, inp_value, inp_type: str) -> None:
    xs = safe_pop(stack, "charlist")
    push_intlist(stack, [1 if c == "R" else 0 for c in xs])


def _op_map_is_upper(stack: list, inp_value, inp_type: str) -> None:
    xs = safe_pop(stack, "charlist")
    push_intlist(stack, [1 if isinstance(c, str) and c.isupper() else 0 for c in xs])


# ---------------- Op table indexed by token id ----------------

OpFn = Callable[[list, object, str], None]

# Shared token dispatch (ids 0..11). Ids 14 and 15 execute as NOP in v1.
_SHARED_OPS: dict[int, OpFn] = {
    alph.NOP:        _op_nop,
    alph.INPUT:      _op_input,
    alph.CONST_0:    _op_const_0,
    alph.CONST_1:    _op_const_1,
    alph.CHARS:      _op_chars,
    alph.SUM:        _op_sum,
    alph.ANY:        _op_any,
    alph.ADD:        _op_add,
    alph.GT:         _op_gt,
    alph.DUP:        _op_dup,
    alph.SWAP:       _op_swap,
    alph.REDUCE_ADD: _op_reduce_add,
    alph.RESERVED_14: _op_nop,
    alph.RESERVED_15: _op_nop,
}

# Slot-name → op function. Slot names come from `TaskAlphabet.slot_12/13`.
_SLOT_OPS: dict[str, OpFn] = {
    alph.OP_NOP:          _op_nop,
    alph.OP_MAP_EQ_R:     _op_map_eq_r,
    alph.OP_MAP_IS_UPPER: _op_map_is_upper,
}


def resolve_op(token_id: int, tape_alphabet: alph.TaskAlphabet) -> OpFn:
    """Return the op function for a token id under the given task-bound alphabet."""
    if token_id == alph.SLOT_12:
        return _SLOT_OPS[tape_alphabet.slot_12]
    if token_id == alph.SLOT_13:
        return _SLOT_OPS[tape_alphabet.slot_13]
    return _SHARED_OPS.get(token_id, _op_nop)


# ---------------- Program execution ----------------

def execute_program(
    tokens,
    tape_alphabet: alph.TaskAlphabet,
    input_value,
    input_type: str,
) -> int:
    """Run `tokens` as an RPN program against `input_value` (typed by input_type).

    Returns an integer; non-int tops are coerced to 0 (spec §Layer 3: "top of
    stack is the output" — v1 tasks always expect int labels, so non-int tops
    are treated as a failed program).
    """
    stack: list = []
    ops_run = 0
    for tid in tokens:
        if ops_run >= OP_CAP:
            break
        op = resolve_op(int(tid), tape_alphabet)
        op(stack, input_value, input_type)
        ops_run += 1
    if not stack:
        return 0
    ttag, payload = stack[-1]
    if ttag == "int":
        return int(payload)
    return 0
