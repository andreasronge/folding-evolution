/// Fitness scoring: partial_credit + data-dependence gate.
/// Mirrors Python dynamics.py evaluate_multi_target + partial_credit.

use super::bytecode::Bytecode;
use super::context::EvalContext;
use super::eval::execute;
use super::value::{Value, value_repr, values_equal};

/// Coerce a Value to its numeric equivalent, matching Python's bool-is-int semantics.
fn as_numeric(v: &Value) -> Option<i64> {
    match v {
        Value::Int(i) => Some(*i),
        Value::Bool(true) => Some(1),
        Value::Bool(false) => Some(0),
        _ => None,
    }
}

/// Partial credit for near-misses, matching Python dynamics.py.
pub fn partial_credit(actual: &Value, expected: &Value) -> f64 {
    if values_equal(actual, expected) {
        return 1.0;
    }
    if matches!(actual, Value::Nil) {
        return 0.0;
    }

    // Numeric near-miss (bool is numeric in Python: True=1, False=0)
    if let (Some(a), Some(e)) = (as_numeric(actual), as_numeric(expected)) {
        if e == 0 {
            return if a != 0 { 0.1 } else { 1.0 };
        }
        let ratio = ((a - e) as f64).abs() / ((e as f64).abs()).max(1.0);
        return (1.0 - ratio).clamp(0.1, 0.9);
    }

    match actual {
        Value::List(a_list) => match expected {
            Value::List(e_list) => {
                if e_list.is_empty() {
                    return if a_list.is_empty() { 1.0 } else { 0.1 };
                }
                let len_diff = (a_list.len() as f64 - e_list.len() as f64).abs();
                let len_score = 1.0 - (len_diff / e_list.len() as f64).min(1.0);
                0.1 + 0.8 * len_score
            }
            _ => 0.05,
        },
        Value::Dict(a_dict) => match expected {
            Value::Dict(e_dict) => {
                if e_dict.is_empty() {
                    return if a_dict.is_empty() { 1.0 } else { 0.1 };
                }
                0.1
            }
            _ => 0.05,
        },
        _ => 0.05,
    }
}

/// Score an individual: develop -> evaluate across contexts -> fitness.
/// Evaluates once per context (not once per target*context).
pub fn score_individual(
    bytecode: &Bytecode,
    contexts: &[EvalContext],
    target_outputs: &[Vec<Value>],
) -> f64 {
    // Evaluate on all contexts
    let outputs: Vec<Value> = contexts.iter().map(|ctx| execute(bytecode, ctx)).collect();

    // Data-dependence gate: if all outputs have identical repr, fitness = 0
    let reprs: Vec<String> = outputs.iter().map(value_repr).collect();
    let first = &reprs[0];
    if reprs.iter().all(|r| r == first) {
        return 0.0;
    }

    // Score: compare each output against each target's expected value
    let mut total = 0.0;
    let mut count = 0;
    for target_row in target_outputs {
        for (ctx_idx, expected) in target_row.iter().enumerate() {
            total += partial_credit(&outputs[ctx_idx], expected);
            count += 1;
        }
    }

    if count == 0 {
        0.0
    } else {
        total / count as f64
    }
}
