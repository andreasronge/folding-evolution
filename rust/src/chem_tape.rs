//! Chem-tape RPN executor — Rust port of `chem_tape/executor.py`.
//!
//! Closed semantics (spec §Layer 3): every token combination produces some
//! integer output; pop-from-empty yields the expected type's default, and
//! wrong-type operands are coerced to the default without consuming the
//! mismatched top. Execution is capped at `OP_CAP` ops; the final int top of
//! stack is returned, else 0.
//!
//! Differs from the Python reference in one place: arithmetic uses i64 with
//! wrapping semantics. Production labels are i64, so the final stored value
//! after `np.int64` assignment matches. The differential test harness
//! normalizes Python outputs to the i64 range before comparison.
//!
//! v2-probe (architecture-v2.md) adds six primitives (MAP_EQ_E, CONST_2,
//! CONST_5, IF_GT, REDUCE_MAX, THRESHOLD_SLOT) at ids 14..19 and shifts
//! separators to 20/21. Dispatch is selected per-call via `alphabet_name`
//! on the PyO3 boundary. Default "v1" preserves the pre-v2 behaviour.

use pyo3::prelude::*;

// ---------- Token ids ----------
// Shared core (ids 0..13) — identical between v1 and v2_probe.
const NOP: u8 = 0;
const INPUT: u8 = 1;
const CONST_0: u8 = 2;
const CONST_1: u8 = 3;
const CHARS: u8 = 4;
const SUM: u8 = 5;
const ANY: u8 = 6;
const ADD: u8 = 7;
const GT: u8 = 8;
const DUP: u8 = 9;
const SWAP: u8 = 10;
const REDUCE_ADD: u8 = 11;
const SLOT_12: u8 = 12;
const SLOT_13: u8 = 13;

// v2-probe primitive ids (execute as NOP under v1).
const MAP_EQ_E: u8 = 14;
const CONST_2: u8 = 15;
const CONST_5: u8 = 16;
const IF_GT: u8 = 17;
const REDUCE_MAX: u8 = 18;
const THRESHOLD_SLOT: u8 = 19;
// v2 separators at 20, 21 (execute as NOP in the stack machine).

const OP_CAP: usize = 256;

// Slot binding names — must match the Python constants in alphabet.py.
const OP_MAP_EQ_R: &str = "MAP_EQ_R";
const OP_MAP_IS_UPPER: &str = "MAP_IS_UPPER";
const OP_MAP_EQ_E_NAME: &str = "MAP_EQ_E";
const OP_REDUCE_ADD_NAME: &str = "REDUCE_ADD";
const OP_REDUCE_MAX_NAME: &str = "REDUCE_MAX";
// Any other slot name (including "NOP") binds to op_nop.

// ---------- Typed stack values ----------

#[derive(Clone)]
enum Value {
    Int(i64),
    IntList(Vec<i64>),
    Str(String),
    CharList(Vec<char>),
}

#[derive(Copy, Clone, PartialEq)]
enum TypeTag {
    Int,
    IntList,
    Str,
    CharList,
    Any,
}

impl Value {
    #[inline]
    fn tag(&self) -> TypeTag {
        match self {
            Value::Int(_) => TypeTag::Int,
            Value::IntList(_) => TypeTag::IntList,
            Value::Str(_) => TypeTag::Str,
            Value::CharList(_) => TypeTag::CharList,
        }
    }
}

#[inline]
fn default_of(t: TypeTag) -> Value {
    match t {
        TypeTag::Int | TypeTag::Any => Value::Int(0),
        TypeTag::IntList => Value::IntList(Vec::new()),
        TypeTag::Str => Value::Str(String::new()),
        TypeTag::CharList => Value::CharList(Vec::new()),
    }
}

/// Spec §Layer 3: empty → default; wrong type → default WITHOUT consuming.
#[inline]
fn safe_pop(stack: &mut Vec<Value>, expected: TypeTag) -> Value {
    match stack.last() {
        None => default_of(expected),
        Some(top) => {
            if expected == TypeTag::Any {
                return stack.pop().unwrap();
            }
            if top.tag() != expected {
                return default_of(expected);
            }
            stack.pop().unwrap()
        }
    }
}

// ---------- Op implementations ----------
//
// Op fns take the task-bound slot closures and threshold via the per-call
// `ExecCtx` rather than global state, so a single executor instance can
// service concurrent contexts if Rayon ever hoists this into parallel use.

struct ExecCtx<'a> {
    slot_12_fn: OpFn,
    slot_13_fn: OpFn,
    threshold: i64,
    alphabet: Alphabet,
    input: &'a Value,
}

type OpFn = fn(&mut Vec<Value>, &ExecCtx<'_>);

#[derive(Copy, Clone, PartialEq)]
enum Alphabet {
    V1,
    V2Probe,
}

fn op_nop(_stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {}

fn op_input(stack: &mut Vec<Value>, ctx: &ExecCtx<'_>) {
    stack.push(ctx.input.clone());
}

fn op_const_0(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    stack.push(Value::Int(0));
}

fn op_const_1(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    stack.push(Value::Int(1));
}

fn op_const_2(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    stack.push(Value::Int(2));
}

fn op_const_5(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    stack.push(Value::Int(5));
}

fn op_chars(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let s = match safe_pop(stack, TypeTag::Str) {
        Value::Str(s) => s,
        _ => String::new(),
    };
    stack.push(Value::CharList(s.chars().collect()));
}

fn op_sum(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let xs = match safe_pop(stack, TypeTag::IntList) {
        Value::IntList(v) => v,
        _ => Vec::new(),
    };
    let mut acc: i64 = 0;
    for x in xs { acc = acc.wrapping_add(x); }
    stack.push(Value::Int(acc));
}

fn op_any(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let xs = match safe_pop(stack, TypeTag::IntList) {
        Value::IntList(v) => v,
        _ => Vec::new(),
    };
    let r = if xs.iter().any(|&x| x != 0) { 1 } else { 0 };
    stack.push(Value::Int(r));
}

fn op_add(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let b = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    let a = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    stack.push(Value::Int(a.wrapping_add(b)));
}

fn op_gt(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let b = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    let a = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    stack.push(Value::Int(if a > b { 1 } else { 0 }));
}

fn op_dup(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    match stack.last() {
        Some(v) => {
            let top = v.clone();
            stack.push(top);
        }
        None => {
            stack.push(Value::Int(0));
            stack.push(Value::Int(0));
        }
    }
}

fn op_swap(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let b = stack.pop().unwrap_or(Value::Int(0));
    let a = stack.pop().unwrap_or(Value::Int(0));
    stack.push(b);
    stack.push(a);
}

fn op_reduce_add(stack: &mut Vec<Value>, ctx: &ExecCtx<'_>) {
    op_sum(stack, ctx);
}

fn op_map_eq_r(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let xs = match safe_pop(stack, TypeTag::CharList) {
        Value::CharList(v) => v,
        _ => Vec::new(),
    };
    stack.push(Value::IntList(
        xs.iter().map(|&c| if c == 'R' { 1i64 } else { 0 }).collect(),
    ));
}

fn op_map_is_upper(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let xs = match safe_pop(stack, TypeTag::CharList) {
        Value::CharList(v) => v,
        _ => Vec::new(),
    };
    stack.push(Value::IntList(
        xs.iter().map(|&c| if c.is_ascii_uppercase() { 1i64 } else { 0 }).collect(),
    ));
}

// --- v2-probe new ops (architecture-v2.md §Proposed alphabet expansion) ---

fn op_map_eq_e(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let xs = match safe_pop(stack, TypeTag::CharList) {
        Value::CharList(v) => v,
        _ => Vec::new(),
    };
    stack.push(Value::IntList(
        xs.iter().map(|&c| if c == 'E' { 1i64 } else { 0 }).collect(),
    ));
}

fn op_if_gt(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    // Architecture-v2: pops (else_val, then_val, cond) with cond on top.
    // Pushes then_val if cond > 0 else else_val. Any underflow → push 0.
    // Matches Python semantics in executor._op_if_gt: if fewer than three
    // values on the stack, drain available ints and push 0.
    if stack.len() < 3 {
        let _ = safe_pop(stack, TypeTag::Int);
        let _ = safe_pop(stack, TypeTag::Int);
        let _ = safe_pop(stack, TypeTag::Int);
        stack.push(Value::Int(0));
        return;
    }
    let cond = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    let then_val = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    let else_val = match safe_pop(stack, TypeTag::Int) {
        Value::Int(v) => v,
        _ => 0,
    };
    stack.push(Value::Int(if cond > 0 { then_val } else { else_val }));
}

fn op_reduce_max(stack: &mut Vec<Value>, _ctx: &ExecCtx<'_>) {
    let xs = match safe_pop(stack, TypeTag::IntList) {
        Value::IntList(v) => v,
        _ => Vec::new(),
    };
    if xs.is_empty() {
        stack.push(Value::Int(0));
        return;
    }
    let mut best = xs[0];
    for &x in xs.iter().skip(1) {
        if x > best { best = x; }
    }
    stack.push(Value::Int(best));
}

fn op_threshold_slot(stack: &mut Vec<Value>, ctx: &ExecCtx<'_>) {
    stack.push(Value::Int(ctx.threshold));
}

#[inline]
fn resolve_slot_op(name: &str) -> OpFn {
    match name {
        OP_MAP_EQ_R => op_map_eq_r,
        OP_MAP_IS_UPPER => op_map_is_upper,
        OP_MAP_EQ_E_NAME => op_map_eq_e,
        OP_REDUCE_ADD_NAME => op_reduce_add,
        OP_REDUCE_MAX_NAME => op_reduce_max,
        _ => op_nop, // "NOP" and anything unknown
    }
}

// ---------- Core execution ----------

fn execute_inner(tokens: &[u8], ctx: &ExecCtx<'_>) -> i64 {
    let mut stack: Vec<Value> = Vec::with_capacity(32);
    let mut ops_run = 0usize;
    for &tid in tokens {
        if ops_run >= OP_CAP {
            break;
        }
        match (tid, ctx.alphabet) {
            // Shared core (ids 0..13) — same in both alphabets.
            (NOP, _) => {}
            (INPUT, _) => op_input(&mut stack, ctx),
            (CONST_0, _) => op_const_0(&mut stack, ctx),
            (CONST_1, _) => op_const_1(&mut stack, ctx),
            (CHARS, _) => op_chars(&mut stack, ctx),
            (SUM, _) => op_sum(&mut stack, ctx),
            (ANY, _) => op_any(&mut stack, ctx),
            (ADD, _) => op_add(&mut stack, ctx),
            (GT, _) => op_gt(&mut stack, ctx),
            (DUP, _) => op_dup(&mut stack, ctx),
            (SWAP, _) => op_swap(&mut stack, ctx),
            (REDUCE_ADD, _) => op_reduce_add(&mut stack, ctx),
            (SLOT_12, _) => (ctx.slot_12_fn)(&mut stack, ctx),
            (SLOT_13, _) => (ctx.slot_13_fn)(&mut stack, ctx),

            // v2-probe primitives (execute as NOP under v1).
            (MAP_EQ_E, Alphabet::V2Probe) => op_map_eq_e(&mut stack, ctx),
            (CONST_2, Alphabet::V2Probe) => op_const_2(&mut stack, ctx),
            (CONST_5, Alphabet::V2Probe) => op_const_5(&mut stack, ctx),
            (IF_GT, Alphabet::V2Probe) => op_if_gt(&mut stack, ctx),
            (REDUCE_MAX, Alphabet::V2Probe) => op_reduce_max(&mut stack, ctx),
            (THRESHOLD_SLOT, Alphabet::V2Probe) => op_threshold_slot(&mut stack, ctx),

            // Everything else (including v2 separators 20/21 and v1's 14/15
            // when not in V2Probe dispatch) executes as NOP.
            _ => {}
        }
        ops_run += 1;
    }
    match stack.last() {
        Some(Value::Int(v)) => *v,
        _ => 0,
    }
}

fn parse_alphabet(name: Option<&str>) -> Alphabet {
    match name.unwrap_or("v1") {
        "v2_probe" => Alphabet::V2Probe,
        _ => Alphabet::V1,
    }
}

// ---------- PyO3 boundary ----------

fn py_to_value(obj: &Bound<'_, PyAny>, input_type: &str) -> PyResult<Value> {
    match input_type {
        "str" => Ok(Value::Str(obj.extract::<String>()?)),
        "intlist" => Ok(Value::IntList(obj.extract::<Vec<i64>>()?)),
        _ => Ok(Value::Int(0)), // unknown type → executor pushes default 0
    }
}

/// Single-program executor. Python wrapper in `chem_tape/executor.py` unpacks
/// TaskAlphabet into the two slot-name strings before calling this.
///
/// `alphabet_name` and `threshold` are optional with v1 defaults, so existing
/// v1 callers can continue to invoke this with 5 positional args.
#[pyfunction]
#[pyo3(signature = (tokens, slot_12, slot_13, input_value, input_type, alphabet_name=None, threshold=None))]
pub fn rust_chem_execute(
    tokens: Vec<u8>,
    slot_12: &str,
    slot_13: &str,
    input_value: &Bound<'_, PyAny>,
    input_type: &str,
    alphabet_name: Option<&str>,
    threshold: Option<i64>,
) -> PyResult<i64> {
    let input = py_to_value(input_value, input_type)?;
    let ctx = ExecCtx {
        slot_12_fn: resolve_slot_op(slot_12),
        slot_13_fn: resolve_slot_op(slot_13),
        threshold: threshold.unwrap_or(0),
        alphabet: parse_alphabet(alphabet_name),
        input: &input,
    };
    Ok(execute_inner(&tokens, &ctx))
}

/// Batched executor: one program, many inputs. Main speedup path — amortizes
/// PyO3 crossing cost and input conversion over E examples.
#[pyfunction]
#[pyo3(signature = (tokens, slot_12, slot_13, input_values, input_type, alphabet_name=None, threshold=None))]
pub fn rust_chem_execute_batch(
    tokens: Vec<u8>,
    slot_12: &str,
    slot_13: &str,
    input_values: &Bound<'_, pyo3::types::PyList>,
    input_type: &str,
    alphabet_name: Option<&str>,
    threshold: Option<i64>,
) -> PyResult<Vec<i64>> {
    let s12 = resolve_slot_op(slot_12);
    let s13 = resolve_slot_op(slot_13);
    let thr = threshold.unwrap_or(0);
    let abc = parse_alphabet(alphabet_name);
    let mut out = Vec::with_capacity(input_values.len());
    for item in input_values.iter() {
        let v = py_to_value(&item, input_type)?;
        let ctx = ExecCtx {
            slot_12_fn: s12,
            slot_13_fn: s13,
            threshold: thr,
            alphabet: abc,
            input: &v,
        };
        out.push(execute_inner(&tokens, &ctx));
    }
    Ok(out)
}
