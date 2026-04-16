"""RPN stack executor for chem-tape.

Closed semantics (spec §Layer 3): every combination of tokens produces some
output, never crashes. Pop-from-empty yields the op's declared input-type
default; wrong-typed operands are coerced to the same default. Execution is
capped at 256 ops; the final top-of-stack (if int) is returned, else 0.

v1 dispatch is unchanged. v2-probe (architecture-v2.md) adds six new ops
(MAP_EQ_E, CONST_2, CONST_5, IF_GT, REDUCE_MAX, THRESHOLD_SLOT) and shifts
separators to ids 20/21. The dispatch variant is selected per-call via the
`alphabet_name` argument threaded to `execute_program` / `resolve_op`.
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

def _op_nop(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    return


def _op_input(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    if inp_type == "str":
        push_str(stack, inp_value)
    elif inp_type == "intlist":
        push_intlist(stack, inp_value)
    else:
        # Unknown input type → push default int.
        push_int(stack, 0)


def _op_const_0(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    push_int(stack, 0)


def _op_const_1(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    push_int(stack, 1)


def _op_const_2(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    push_int(stack, 2)


def _op_const_5(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    push_int(stack, 5)


def _op_chars(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    s = safe_pop(stack, "str")
    push_charlist(stack, list(s))


def _op_sum(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    xs = safe_pop(stack, "intlist")
    push_int(stack, sum(xs))


def _op_any(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    xs = safe_pop(stack, "intlist")
    push_int(stack, 1 if any(x != 0 for x in xs) else 0)


def _op_add(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    b = safe_pop(stack, "int")   # top
    a = safe_pop(stack, "int")
    push_int(stack, a + b)


def _op_gt(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    b = safe_pop(stack, "int")   # top
    a = safe_pop(stack, "int")
    push_int(stack, 1 if a > b else 0)


def _op_dup(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    # Polymorphic; on empty stack, duplicate an int default.
    if not stack:
        push_int(stack, 0)
        push_int(stack, 0)
        return
    top = stack[-1]
    stack.append(top)


def _op_swap(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    # Polymorphic pop-in-reverse with defaults.
    b = stack.pop() if stack else ("int", 0)
    a = stack.pop() if stack else ("int", 0)
    stack.append(b)
    stack.append(a)


def _op_reduce_add(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    # v1 / v2-probe: fixed combinator = sum. Semantic alias of SUM. Higher-order
    # reduce is a v2-full feature, out of scope for the probe.
    xs = safe_pop(stack, "intlist")
    push_int(stack, sum(xs))


def _op_map_eq_r(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    xs = safe_pop(stack, "charlist")
    push_intlist(stack, [1 if c == "R" else 0 for c in xs])


def _op_map_is_upper(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    xs = safe_pop(stack, "charlist")
    push_intlist(stack, [1 if isinstance(c, str) and c.isupper() else 0 for c in xs])


# --- v2-probe new ops (architecture-v2.md §Proposed alphabet expansion) ---

def _op_map_eq_e(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    xs = safe_pop(stack, "charlist")
    push_intlist(stack, [1 if c == "E" else 0 for c in xs])


def _op_if_gt(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    """Value-level selector. Pops (else_val, then_val, cond) with cond on top.

    Pushes `then_val if cond > 0 else else_val`. Both branches are already-
    evaluated ints; not a control operator. `cond > 0` is strictly positive.
    Any underflow → push 0 (architecture-v2.md §Proposed alphabet expansion).
    """
    # Underflow policy: if we do not have at least three ints on the stack
    # (where "three ints" means three typed-int values, per §Layer 3 wrong-
    # type-does-not-consume), we push 0 and return. Use the standard safe_pop
    # signal (a non-int top leaves the stack alone and yields default 0).
    if len(stack) < 3:
        # Architecture-v2: "Any underflow → push 0." Don't leave partial
        # consumption; just push the int default and drop any popped values.
        # Drain up to three ints via safe_pop (stops on wrong-type/empty).
        safe_pop(stack, "int"); safe_pop(stack, "int"); safe_pop(stack, "int")
        push_int(stack, 0)
        return
    cond = safe_pop(stack, "int")
    then_val = safe_pop(stack, "int")
    else_val = safe_pop(stack, "int")
    push_int(stack, then_val if cond > 0 else else_val)


def _op_reduce_max(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    """Reduce top-of-stack intlist to max(elements). Empty → 0; underflow → 0."""
    xs = safe_pop(stack, "intlist")
    if not xs:
        push_int(stack, 0)
        return
    push_int(stack, max(xs))


def _op_threshold_slot(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    """Push the task-bound integer `ta.threshold`. No stack consumption."""
    push_int(stack, int(ta.threshold))


def _op_sum_left2(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    """Push sum of input[0:2] (first two elements of intlist). §v2.4-proxy-3."""
    if inp_type == "intlist" and isinstance(inp_value, (list, tuple)) and len(inp_value) >= 2:
        push_int(stack, int(inp_value[0]) + int(inp_value[1]))
    else:
        push_int(stack, 0)


def _op_sum_right2(stack: list, inp_value, inp_type: str, ta: alph.TaskAlphabet) -> None:
    """Push sum of input[2:4] (last two elements of length-4 intlist). §v2.4-proxy-3."""
    if inp_type == "intlist" and isinstance(inp_value, (list, tuple)) and len(inp_value) >= 4:
        push_int(stack, int(inp_value[2]) + int(inp_value[3]))
    else:
        push_int(stack, 0)


# ---------------- Op tables indexed by token id ----------------

OpFn = Callable[[list, object, str, alph.TaskAlphabet], None]

# v1 dispatch (ids 0..15). Ids 14, 15 execute as NOP.
_OPS_V1: dict[int, OpFn] = {
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

# v2-probe dispatch (ids 0..21). Same shared core at 0..13; ids 14..19 are
# new primitives; ids 20, 21 are separators (execute as NOP in the stack-
# machine sense — bonding rules handle their boundary role separately).
_OPS_V2: dict[int, OpFn] = {
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
    alph.MAP_EQ_E:   _op_map_eq_e,
    alph.CONST_2:    _op_const_2,
    alph.CONST_5:    _op_const_5,
    alph.IF_GT:      _op_if_gt,
    alph.REDUCE_MAX: _op_reduce_max,
    alph.THRESHOLD_SLOT: _op_threshold_slot,
    alph.SEP_A:      _op_nop,
    alph.SEP_B:      _op_nop,
}

# v2-split dispatch: extends v2 with SUM_LEFT2/SUM_RIGHT2.
_OPS_V2_SPLIT: dict[int, OpFn] = {**_OPS_V2,
    alph.SUM_LEFT2:  _op_sum_left2,
    alph.SUM_RIGHT2: _op_sum_right2,
}

# Slot-name → op function. Extended from v1 set with MAP_EQ_E and REDUCE_MAX
# (architecture-v2.md §Slot-binding generalization). REDUCE_ADD is also
# exposed as a slot binding for §v2.5's aggregator-variation design.
_SLOT_OPS: dict[str, OpFn] = {
    alph.OP_NOP:          _op_nop,
    alph.OP_MAP_EQ_R:     _op_map_eq_r,
    alph.OP_MAP_IS_UPPER: _op_map_is_upper,
    alph.OP_MAP_EQ_E:     _op_map_eq_e,
    alph.OP_REDUCE_ADD:   _op_reduce_add,
    alph.OP_REDUCE_MAX:   _op_reduce_max,
}


def _dispatch_table(alphabet_name: str) -> dict[int, OpFn]:
    if alphabet_name == "v2_split":
        return _OPS_V2_SPLIT
    if alphabet_name == "v2_probe":
        return _OPS_V2
    return _OPS_V1


def resolve_op(
    token_id: int,
    tape_alphabet: alph.TaskAlphabet,
    alphabet_name: str = "v1",
) -> OpFn:
    """Return the op function for a token id under the given task-bound alphabet.

    Slot ids (12, 13) always dispatch through `TaskAlphabet`; other ids use
    the alphabet-variant dispatch table.
    """
    if token_id == alph.SLOT_12:
        return _SLOT_OPS.get(tape_alphabet.slot_12, _op_nop)
    if token_id == alph.SLOT_13:
        return _SLOT_OPS.get(tape_alphabet.slot_13, _op_nop)
    return _dispatch_table(alphabet_name).get(token_id, _op_nop)


# ---------------- Program execution ----------------

def execute_program(
    tokens,
    tape_alphabet: alph.TaskAlphabet,
    input_value,
    input_type: str,
    alphabet_name: str = "v1",
) -> int:
    """Run `tokens` as an RPN program against `input_value` (typed by input_type).

    Returns an integer; non-int tops are coerced to 0 (spec §Layer 3: "top of
    stack is the output" — v1 tasks always expect int labels, so non-int tops
    are treated as a failed program).
    """
    stack: list = []
    ops_run = 0
    table = _dispatch_table(alphabet_name)
    for tid in tokens:
        if ops_run >= OP_CAP:
            break
        tid_i = int(tid)
        if tid_i == alph.SLOT_12:
            op = _SLOT_OPS.get(tape_alphabet.slot_12, _op_nop)
        elif tid_i == alph.SLOT_13:
            op = _SLOT_OPS.get(tape_alphabet.slot_13, _op_nop)
        else:
            op = table.get(tid_i, _op_nop)
        op(stack, input_value, input_type, tape_alphabet)
        ops_run += 1
    if not stack:
        return 0
    ttag, payload = stack[-1]
    if ttag == "int":
        return int(payload)
    return 0
