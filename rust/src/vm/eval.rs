/// Stack machine evaluator.
///
/// Error propagation: Operations that would throw TypeError in Python
/// (arithmetic/comparison on incompatible types) produce Value::Error.
/// Any operation receiving Error propagates it. The top-level execute()
/// converts Error to Nil, matching Python's top-level exception catch.

use std::sync::Arc;

use super::bytecode::{Bytecode, Inst};
use super::context::EvalContext;
use super::value::{Value, values_equal};

const MAX_FUEL: u32 = 50_000;
const MAX_LOCALS: usize = 64;

/// Coerce to numeric, matching Python's bool-is-int semantics.
fn as_num(v: &Value) -> Option<i64> {
    match v {
        Value::Int(i) => Some(*i),
        Value::Bool(b) => Some(*b as i64),
        _ => None,
    }
}

/// Compare two lists lexicographically, matching Python's list comparison.
/// Returns None if any element pair can't be ordered (Python raises TypeError).
/// Python compares element-by-element: if elements are equal, move on; if not,
/// try ordering them (TypeError if incomparable types like dict < dict).
fn list_cmp(a: &[Value], b: &[Value]) -> Option<std::cmp::Ordering> {
    for (x, y) in a.iter().zip(b.iter()) {
        // If elements are equal (Python ==), skip to next pair
        if values_equal(x, y) {
            continue;
        }
        // Elements differ — try to order them
        match (x, y) {
            (Value::Str(sx), Value::Str(sy)) => {
                return Some(sx.cmp(sy)); // already know they're not equal
            }
            _ => {
                if let (Some(xi), Some(yi)) = (as_num(x), as_num(y)) {
                    return Some(xi.cmp(&yi));
                }
                // Non-equal, non-orderable types (dict, list, mixed) → TypeError
                return None;
            }
        }
    }
    // All paired elements are equal; compare by length
    Some(a.len().cmp(&b.len()))
}

pub fn execute(bytecode: &Bytecode, context: &EvalContext) -> Value {
    let mut stack: Vec<Value> = Vec::with_capacity(32);
    let mut locals: Vec<Value> = vec![Value::Nil; MAX_LOCALS];
    let result = execute_inner(bytecode, context, &mut locals, &mut stack, 0, MAX_FUEL);
    // Convert Error to Nil at the boundary (matches Python's top-level try/except)
    if result.is_error() { Value::Nil } else { result }
}

fn pop(stack: &mut Vec<Value>) -> Value {
    stack.pop().unwrap_or(Value::Nil)
}

fn execute_inner(
    bytecode: &Bytecode,
    context: &EvalContext,
    locals: &mut [Value],
    stack: &mut Vec<Value>,
    start_ip: usize,
    fuel: u32,
) -> Value {
    let mut ip = start_ip;
    let mut fuel = fuel;
    let instructions = &bytecode.instructions;

    while ip < instructions.len() && fuel > 0 {
        fuel -= 1;
        match &instructions[ip] {
            Inst::PushNil => stack.push(Value::Nil),
            Inst::PushInt(v) => stack.push(Value::Int(*v)),
            Inst::PushStr(idx) => {
                stack.push(Value::Str(bytecode.string_pool[*idx as usize].clone()));
            }
            Inst::LoadData(idx) => {
                stack.push(context.data_sources[*idx as usize].clone());
            }
            Inst::LoadLocal(slot) => {
                stack.push(locals[*slot as usize].clone());
            }

            // --- Collection ops: return Nil on type mismatch (Python returns None) ---

            Inst::Count => {
                let val = pop(stack);
                if val.is_error() { stack.push(Value::Error); }
                else {
                    match val {
                        Value::List(l) => stack.push(Value::Int(l.len() as i64)),
                        _ => stack.push(Value::Nil),
                    }
                }
            }
            Inst::First => {
                let val = pop(stack);
                if val.is_error() { stack.push(Value::Error); }
                else {
                    match val {
                        Value::List(l) if !l.is_empty() => stack.push(l[0].clone()),
                        _ => stack.push(Value::Nil),
                    }
                }
            }
            Inst::Rest => {
                let val = pop(stack);
                if val.is_error() { stack.push(Value::Error); }
                else {
                    match val {
                        Value::List(l) => {
                            if l.len() > 1 {
                                stack.push(Value::List(Arc::new(l[1..].to_vec())));
                            } else {
                                stack.push(Value::List(Arc::new(Vec::new())));
                            }
                        }
                        _ => stack.push(Value::Nil),
                    }
                }
            }
            Inst::GetField => {
                let key = pop(stack);
                let dict = pop(stack);
                if key.is_error() || dict.is_error() { stack.push(Value::Error); }
                else {
                    match (&dict, &key) {
                        (Value::Dict(d), Value::Str(k)) => {
                            stack.push(d.get(k).cloned().unwrap_or(Value::Nil));
                        }
                        _ => stack.push(Value::Nil),
                    }
                }
            }

            // --- Arithmetic: coerce bool→int (Python: bool is int subclass) ---

            Inst::Add => {
                let b = pop(stack);
                let a = pop(stack);
                if a.is_error() || b.is_error() { stack.push(Value::Error); }
                else if let (Some(x), Some(y)) = (as_num(&a), as_num(&b)) {
                    stack.push(Value::Int(x + y));
                } else {
                    match (&a, &b) {
                        // Python: list + list = concatenation
                        (Value::List(x), Value::List(y)) => {
                            let mut concat = Vec::with_capacity(x.len() + y.len());
                            concat.extend_from_slice(x);
                            concat.extend_from_slice(y);
                            stack.push(Value::List(Arc::new(concat)));
                        }
                        _ => stack.push(Value::Error),
                    }
                }
            }
            Inst::Sub => {
                let b = pop(stack);
                let a = pop(stack);
                if a.is_error() || b.is_error() { stack.push(Value::Error); }
                else if let (Some(x), Some(y)) = (as_num(&a), as_num(&b)) {
                    stack.push(Value::Int(x - y));
                } else {
                    stack.push(Value::Error);
                }
            }

            // --- Comparison: coerce bool→int, support list comparison ---

            Inst::Gt => {
                let b = pop(stack);
                let a = pop(stack);
                if a.is_error() || b.is_error() { stack.push(Value::Error); }
                else if let (Some(x), Some(y)) = (as_num(&a), as_num(&b)) {
                    stack.push(Value::Bool(x > y));
                } else {
                    match (&a, &b) {
                        // Python compares lists lexicographically
                        (Value::List(x), Value::List(y)) => {
                            match list_cmp(x, y) {
                                Some(std::cmp::Ordering::Greater) => stack.push(Value::Bool(true)),
                                Some(_) => stack.push(Value::Bool(false)),
                                None => stack.push(Value::Error),
                            }
                        }
                        _ => stack.push(Value::Error),
                    }
                }
            }
            Inst::Lt => {
                let b = pop(stack);
                let a = pop(stack);
                if a.is_error() || b.is_error() { stack.push(Value::Error); }
                else if let (Some(x), Some(y)) = (as_num(&a), as_num(&b)) {
                    stack.push(Value::Bool(x < y));
                } else {
                    match (&a, &b) {
                        (Value::List(x), Value::List(y)) => {
                            match list_cmp(x, y) {
                                Some(std::cmp::Ordering::Less) => stack.push(Value::Bool(true)),
                                Some(_) => stack.push(Value::Bool(false)),
                                None => stack.push(Value::Error),
                            }
                        }
                        _ => stack.push(Value::Error),
                    }
                }
            }

            // --- Eq: Python == doesn't throw, just returns False for different types ---

            Inst::Eq => {
                let b = pop(stack);
                let a = pop(stack);
                if a.is_error() || b.is_error() { stack.push(Value::Error); }
                else { stack.push(Value::Bool(values_equal(&a, &b))); }
            }

            // --- Not: propagates error ---

            Inst::Not => {
                let a = pop(stack);
                if a.is_error() { stack.push(Value::Error); }
                else { stack.push(Value::Bool(!a.is_truthy())); }
            }

            // --- DiscardArgs: pop n values, propagate Error ---

            Inst::DiscardArgs(n) => {
                let mut has_error = false;
                for _ in 0..*n {
                    if pop(stack).is_error() {
                        has_error = true;
                    }
                }
                stack.push(if has_error { Value::Error } else { Value::Nil });
            }

            // --- Control flow ---

            Inst::JumpIfFalse(target) => {
                let cond = pop(stack);
                if cond.is_error() {
                    // Error propagates — treat as "abort this branch"
                    stack.push(Value::Error);
                    break;
                }
                if !cond.is_truthy() {
                    ip = *target as usize;
                    continue;
                }
            }
            Inst::Jump(target) => {
                ip = *target as usize;
                continue;
            }

            // --- Higher-order: error in closure body propagates ---

            Inst::FilterBegin(param_slot, end_ip) => {
                let data = pop(stack);
                if data.is_error() {
                    stack.push(Value::Error);
                    ip = *end_ip as usize;
                    continue;
                }
                match data {
                    Value::List(items) => {
                        let body_start = ip + 1;
                        let mut result = Vec::new();
                        let mut errored = false;
                        for item in items.iter() {
                            locals[*param_slot as usize] = item.clone();
                            let mut body_stack: Vec<Value> = Vec::with_capacity(8);
                            let body_result = execute_inner(
                                bytecode, context, locals, &mut body_stack,
                                body_start, fuel,
                            );
                            if body_result.is_error() {
                                errored = true;
                                break;
                            }
                            if body_result.is_truthy() {
                                result.push(item.clone());
                            }
                        }
                        if errored {
                            stack.push(Value::Error);
                        } else {
                            stack.push(Value::List(Arc::new(result)));
                        }
                        ip = *end_ip as usize;
                        continue;
                    }
                    _ => {
                        stack.push(Value::Nil);
                        ip = *end_ip as usize;
                        continue;
                    }
                }
            }
            Inst::FilterEnd => {
                break;
            }

            Inst::MapBegin(param_slot, end_ip) => {
                let data = pop(stack);
                if data.is_error() {
                    stack.push(Value::Error);
                    ip = *end_ip as usize;
                    continue;
                }
                match data {
                    Value::List(items) => {
                        let body_start = ip + 1;
                        let mut result = Vec::with_capacity(items.len());
                        let mut errored = false;
                        for item in items.iter() {
                            locals[*param_slot as usize] = item.clone();
                            let mut body_stack: Vec<Value> = Vec::with_capacity(8);
                            let body_result = execute_inner(
                                bytecode, context, locals, &mut body_stack,
                                body_start, fuel,
                            );
                            if body_result.is_error() {
                                errored = true;
                                break;
                            }
                            result.push(body_result);
                        }
                        if errored {
                            stack.push(Value::Error);
                        } else {
                            stack.push(Value::List(Arc::new(result)));
                        }
                        ip = *end_ip as usize;
                        continue;
                    }
                    _ => {
                        stack.push(Value::Nil);
                        ip = *end_ip as usize;
                        continue;
                    }
                }
            }
            Inst::MapEnd => {
                break;
            }

            Inst::Return => break,
        }
        ip += 1;
    }

    pop(stack)
}
