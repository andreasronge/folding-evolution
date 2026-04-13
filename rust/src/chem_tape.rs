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

use pyo3::prelude::*;

// ---------- Token ids (spec §Layer 2) ----------

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
// Ids 14, 15 execute as NOP (reserved in v1).

const OP_CAP: usize = 256;

// Slot binding names — must match the Python constants in alphabet.py.
const OP_MAP_EQ_R: &str = "MAP_EQ_R";
const OP_MAP_IS_UPPER: &str = "MAP_IS_UPPER";
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

type OpFn = fn(&mut Vec<Value>, &Value);

fn op_nop(_stack: &mut Vec<Value>, _input: &Value) {}

fn op_input(stack: &mut Vec<Value>, input: &Value) {
    stack.push(input.clone());
}

fn op_const_0(stack: &mut Vec<Value>, _input: &Value) {
    stack.push(Value::Int(0));
}

fn op_const_1(stack: &mut Vec<Value>, _input: &Value) {
    stack.push(Value::Int(1));
}

fn op_chars(stack: &mut Vec<Value>, _input: &Value) {
    let s = match safe_pop(stack, TypeTag::Str) {
        Value::Str(s) => s,
        _ => String::new(),
    };
    stack.push(Value::CharList(s.chars().collect()));
}

fn op_sum(stack: &mut Vec<Value>, _input: &Value) {
    let xs = match safe_pop(stack, TypeTag::IntList) {
        Value::IntList(v) => v,
        _ => Vec::new(),
    };
    // Wrapping sum mirrors i64 overflow behavior.
    let mut acc: i64 = 0;
    for x in xs { acc = acc.wrapping_add(x); }
    stack.push(Value::Int(acc));
}

fn op_any(stack: &mut Vec<Value>, _input: &Value) {
    let xs = match safe_pop(stack, TypeTag::IntList) {
        Value::IntList(v) => v,
        _ => Vec::new(),
    };
    let r = if xs.iter().any(|&x| x != 0) { 1 } else { 0 };
    stack.push(Value::Int(r));
}

fn op_add(stack: &mut Vec<Value>, _input: &Value) {
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

fn op_gt(stack: &mut Vec<Value>, _input: &Value) {
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

fn op_dup(stack: &mut Vec<Value>, _input: &Value) {
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

fn op_swap(stack: &mut Vec<Value>, _input: &Value) {
    let b = stack.pop().unwrap_or(Value::Int(0));
    let a = stack.pop().unwrap_or(Value::Int(0));
    stack.push(b);
    stack.push(a);
}

fn op_reduce_add(stack: &mut Vec<Value>, input: &Value) {
    op_sum(stack, input);
}

fn op_map_eq_r(stack: &mut Vec<Value>, _input: &Value) {
    let xs = match safe_pop(stack, TypeTag::CharList) {
        Value::CharList(v) => v,
        _ => Vec::new(),
    };
    stack.push(Value::IntList(
        xs.iter().map(|&c| if c == 'R' { 1i64 } else { 0 }).collect(),
    ));
}

fn op_map_is_upper(stack: &mut Vec<Value>, _input: &Value) {
    let xs = match safe_pop(stack, TypeTag::CharList) {
        Value::CharList(v) => v,
        _ => Vec::new(),
    };
    // ASCII-only inputs in v1 tasks — matches Python's `str.isupper()` on
    // the test alphabet (ASCII letters + space).
    stack.push(Value::IntList(
        xs.iter().map(|&c| if c.is_ascii_uppercase() { 1i64 } else { 0 }).collect(),
    ));
}

#[inline]
fn resolve_slot_op(name: &str) -> OpFn {
    match name {
        OP_MAP_EQ_R => op_map_eq_r,
        OP_MAP_IS_UPPER => op_map_is_upper,
        _ => op_nop, // "NOP" and anything unknown
    }
}

// ---------- Core execution ----------

fn execute_inner(
    tokens: &[u8],
    slot_12_fn: OpFn,
    slot_13_fn: OpFn,
    input: &Value,
) -> i64 {
    let mut stack: Vec<Value> = Vec::with_capacity(32);
    let mut ops_run = 0usize;
    for &tid in tokens {
        if ops_run >= OP_CAP {
            break;
        }
        match tid {
            NOP => {}
            INPUT => op_input(&mut stack, input),
            CONST_0 => op_const_0(&mut stack, input),
            CONST_1 => op_const_1(&mut stack, input),
            CHARS => op_chars(&mut stack, input),
            SUM => op_sum(&mut stack, input),
            ANY => op_any(&mut stack, input),
            ADD => op_add(&mut stack, input),
            GT => op_gt(&mut stack, input),
            DUP => op_dup(&mut stack, input),
            SWAP => op_swap(&mut stack, input),
            REDUCE_ADD => op_reduce_add(&mut stack, input),
            SLOT_12 => slot_12_fn(&mut stack, input),
            SLOT_13 => slot_13_fn(&mut stack, input),
            _ => {} // 14, 15, and any > 15 are NOP
        }
        ops_run += 1;
    }
    match stack.last() {
        Some(Value::Int(v)) => *v,
        _ => 0,
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
#[pyfunction]
pub fn rust_chem_execute(
    tokens: Vec<u8>,
    slot_12: &str,
    slot_13: &str,
    input_value: &Bound<'_, PyAny>,
    input_type: &str,
) -> PyResult<i64> {
    let input = py_to_value(input_value, input_type)?;
    let s12 = resolve_slot_op(slot_12);
    let s13 = resolve_slot_op(slot_13);
    Ok(execute_inner(&tokens, s12, s13, &input))
}

/// Batched executor: one program, many inputs. Main speedup path — amortizes
/// PyO3 crossing cost and input conversion over E examples.
#[pyfunction]
pub fn rust_chem_execute_batch(
    tokens: Vec<u8>,
    slot_12: &str,
    slot_13: &str,
    input_values: &Bound<'_, pyo3::types::PyList>,
    input_type: &str,
) -> PyResult<Vec<i64>> {
    let s12 = resolve_slot_op(slot_12);
    let s13 = resolve_slot_op(slot_13);
    let mut out = Vec::with_capacity(input_values.len());
    for item in input_values.iter() {
        let v = py_to_value(&item, input_type)?;
        out.push(execute_inner(&tokens, s12, s13, &v));
    }
    Ok(out)
}
