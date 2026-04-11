/// Dataflow evaluation: K rounds of broadcast message passing on a fixed grid.
///
/// Vectorized model:
/// - `get` on list-of-dicts + field key → list of field values (element-wise)
/// - Comparators on list + scalar → list of booleans (element-wise)
/// - `filter` on bool-list + list-of-dicts → filtered list (boolean mask)
/// - Wildcards relay their best neighbor's value (act as "wires")

use std::sync::Arc;

use crate::alphabet;
use crate::chemistry::Fragment;
use crate::types::*;
use crate::vm::context::EvalContext;
use crate::vm::value::{Value, value_repr, values_equal};
use crate::vm::fitness::partial_credit;

use super::grid::{FixedGrid, NeighborTable, GRID_SIZE};

const NUM_ROUNDS: usize = 5;

// ---------------------------------------------------------------------------
// Output priority: determines which cell's output is the "program result"
// ---------------------------------------------------------------------------

fn output_priority(frag: &Fragment) -> i32 {
    match frag {
        Fragment::Fn(Op::Count | Op::First | Op::Last | Op::Rest
                     | Op::Reverse | Op::Sort) => 5,
        Fragment::Fn(Op::Filter | Op::Map) => 4,
        Fragment::Fn(Op::Contains) => 4,
        Fragment::Connective(_) => 3,
        Fragment::Comparator(_) => 3,
        Fragment::Fn(Op::Get) => 2,
        Fragment::DataSource(_) => 1,
        Fragment::Literal(_) => 0,
        Fragment::FieldKey(_) => -1,
        Fragment::Wildcard => -1,
        _ => -1,
    }
}

/// Priority of a value for neighbor selection (higher = preferred).
fn value_priority(v: &Value) -> i32 {
    match v {
        Value::Nil => -1,
        Value::List(_) => 3,
        Value::Dict(_) => 2,
        Value::Bool(_) => 1,
        Value::Int(_) => 1,
        Value::Str(_) => 0,
        Value::Error => -1,
    }
}

// ---------------------------------------------------------------------------
// Neighbor helpers
// ---------------------------------------------------------------------------

/// Find a neighbor whose output is a list where the first element is a Dict.
fn find_dict_list<'a>(
    idx: usize, neighbors: &NeighborTable, outputs: &'a [Value], grid: &FixedGrid,
) -> Option<&'a Arc<Vec<Value>>> {
    for &nidx in neighbors.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        if let Value::List(items) = &outputs[ni] {
            if !items.is_empty() {
                if matches!(items[0], Value::Dict(_)) {
                    return Some(items);
                }
            }
        }
    }
    None
}

/// Find a neighbor whose output is a Str (field key).
fn find_str_neighbor<'a>(
    idx: usize, neighbors: &NeighborTable, outputs: &'a [Value], grid: &FixedGrid,
) -> Option<&'a Arc<str>> {
    for &nidx in neighbors.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        if let Value::Str(s) = &outputs[ni] {
            return Some(s);
        }
    }
    None
}

/// Find a neighbor whose output is a list of booleans.
fn find_bool_list<'a>(
    idx: usize, neighbors: &NeighborTable, outputs: &'a [Value], grid: &FixedGrid,
) -> Option<&'a Arc<Vec<Value>>> {
    for &nidx in neighbors.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        if let Value::List(items) = &outputs[ni] {
            if !items.is_empty() && matches!(items[0], Value::Bool(_)) {
                return Some(items);
            }
        }
    }
    None
}

/// Find a neighbor that has a non-Nil list output (any kind).
fn find_any_list<'a>(
    idx: usize, neighbors: &NeighborTable, outputs: &'a [Value], grid: &FixedGrid,
) -> Option<&'a Arc<Vec<Value>>> {
    for &nidx in neighbors.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        if let Value::List(items) = &outputs[ni] {
            if !items.is_empty() {
                return Some(items);
            }
        }
    }
    None
}

/// Collect up to 2 non-Nil value neighbors, sorted by value_priority descending.
fn find_two_values<'a>(
    idx: usize, neighbors: &NeighborTable, outputs: &'a [Value], grid: &FixedGrid,
) -> Vec<&'a Value> {
    let mut vals: Vec<&Value> = Vec::new();
    for &nidx in neighbors.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        let v = &outputs[ni];
        if matches!(v, Value::Nil | Value::Error) { continue; }
        vals.push(v);
        if vals.len() >= 4 { break; } // cap scan
    }
    vals.sort_by(|a, b| value_priority(b).cmp(&value_priority(a)));
    vals.truncate(2);
    vals
}

/// Find the best non-Nil neighbor value for relay cells.
fn find_best_relay<'a>(
    idx: usize, neighbors: &NeighborTable, outputs: &'a [Value], grid: &FixedGrid,
) -> Option<&'a Value> {
    let mut best: Option<&Value> = None;
    let mut best_prio = -1;
    for &nidx in neighbors.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        let v = &outputs[ni];
        let prio = value_priority(v);
        if prio > best_prio {
            best_prio = prio;
            best = Some(v);
        }
    }
    best
}

// ---------------------------------------------------------------------------
// Per-cell compute functions
// ---------------------------------------------------------------------------

fn as_num(v: &Value) -> Option<i64> {
    match v {
        Value::Int(i) => Some(*i),
        Value::Bool(b) => Some(*b as i64),
        _ => None,
    }
}

fn compare_scalar(op: Op, a: &Value, b: &Value) -> Value {
    if let (Some(x), Some(y)) = (as_num(a), as_num(b)) {
        Value::Bool(match op {
            Op::Gt => x > y,
            Op::Lt => x < y,
            Op::Eq => x == y,
            _ => false,
        })
    } else if matches!(op, Op::Eq) {
        Value::Bool(values_equal(a, b))
    } else {
        Value::Nil
    }
}

/// Vectorized get: list-of-dicts + field key → list of field values.
fn try_get(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let key = find_str_neighbor(idx, ntable, outputs, grid)?;
    let dicts = find_dict_list(idx, ntable, outputs, grid)?;

    let values: Vec<Value> = dicts.iter().map(|item| {
        if let Value::Dict(d) = item {
            d.get(key.as_ref()).cloned().unwrap_or(Value::Nil)
        } else {
            Value::Nil
        }
    }).collect();
    Some(Value::List(Arc::new(values)))
}

/// Vectorized compare: handles list×scalar → bool-list, scalar×scalar → bool.
fn try_compare(
    idx: usize, op: Op, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let vals = find_two_values(idx, ntable, outputs, grid);
    if vals.len() < 2 { return None; }

    let a = vals[0];
    let b = vals[1];

    match (a, b) {
        // Element-wise: list op scalar
        (Value::List(items), scalar) if !matches!(scalar, Value::List(_)) => {
            let bools: Vec<Value> = items.iter()
                .map(|item| compare_scalar(op, item, scalar))
                .collect();
            Some(Value::List(Arc::new(bools)))
        }
        // Element-wise: scalar op list
        (scalar, Value::List(items)) if !matches!(scalar, Value::List(_)) => {
            let bools: Vec<Value> = items.iter()
                .map(|item| compare_scalar(op, scalar, item))
                .collect();
            Some(Value::List(Arc::new(bools)))
        }
        // Scalar comparison
        _ => {
            let result = compare_scalar(op, a, b);
            if matches!(result, Value::Nil) { None } else { Some(result) }
        }
    }
}

/// Vectorized addition: list+list or list+scalar element-wise.
fn try_plus(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let vals = find_two_values(idx, ntable, outputs, grid);
    if vals.len() < 2 { return None; }

    let a = vals[0];
    let b = vals[1];

    match (a, b) {
        (Value::Int(x), Value::Int(y)) => Some(Value::Int(x + y)),
        (Value::List(items), Value::Int(s)) => {
            let result: Vec<Value> = items.iter().map(|item| {
                if let Some(x) = as_num(item) { Value::Int(x + s) } else { Value::Nil }
            }).collect();
            Some(Value::List(Arc::new(result)))
        }
        (Value::Int(s), Value::List(items)) => {
            let result: Vec<Value> = items.iter().map(|item| {
                if let Some(x) = as_num(item) { Value::Int(s + x) } else { Value::Nil }
            }).collect();
            Some(Value::List(Arc::new(result)))
        }
        _ => None,
    }
}

/// Filter: bool-list + dict-list → filtered list (boolean mask).
fn try_filter(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let bools = find_bool_list(idx, ntable, outputs, grid)?;
    let dicts = find_dict_list(idx, ntable, outputs, grid)?;

    if bools.len() != dicts.len() { return None; }

    let filtered: Vec<Value> = bools.iter().zip(dicts.iter())
        .filter_map(|(b, d)| {
            if matches!(b, Value::Bool(true)) { Some(d.clone()) } else { None }
        })
        .collect();
    Some(Value::List(Arc::new(filtered)))
}

/// Map: apply element-wise field access. Looks for a value-list neighbor.
/// In vectorized mode, the "map" result is already computed upstream by get,
/// so map acts as a pass-through for the best list neighbor.
fn try_map(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    // Find two list neighbors: a fn-like value list and a data list
    // For now, map just passes through the most complex list neighbor
    let list = find_any_list(idx, ntable, outputs, grid)?;
    Some(Value::List(list.clone()))
}

/// Count: list → length.
fn try_count(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let list = find_any_list(idx, ntable, outputs, grid)?;
    Some(Value::Int(list.len() as i64))
}

/// First: list → first element.
fn try_first(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let list = find_any_list(idx, ntable, outputs, grid)?;
    Some(list.first().cloned().unwrap_or(Value::Nil))
}

/// Last: list → last element.
fn try_last(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let list = find_any_list(idx, ntable, outputs, grid)?;
    Some(list.last().cloned().unwrap_or(Value::Nil))
}

/// Rest: list → all but first.
fn try_rest(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let list = find_any_list(idx, ntable, outputs, grid)?;
    if list.len() > 1 {
        Some(Value::List(Arc::new(list[1..].to_vec())))
    } else {
        Some(Value::List(Arc::new(Vec::new())))
    }
}

/// Reverse: list → reversed list.
fn try_reverse(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let list = find_any_list(idx, ntable, outputs, grid)?;
    let mut reversed = list.as_ref().clone();
    reversed.reverse();
    Some(Value::List(Arc::new(reversed)))
}

/// Not: bool → !bool, bool-list → element-wise not.
fn try_not(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    for &nidx in ntable.neighbors(idx) {
        let ni = nidx as usize;
        if grid[ni] == 0 { continue; }
        match &outputs[ni] {
            Value::Bool(b) => return Some(Value::Bool(!b)),
            Value::List(items) if !items.is_empty() && matches!(items[0], Value::Bool(_)) => {
                let result: Vec<Value> = items.iter().map(|v| {
                    Value::Bool(!v.is_truthy())
                }).collect();
                return Some(Value::List(Arc::new(result)));
            }
            _ => {}
        }
    }
    None
}

/// And: two bool-lists → element-wise and, or two bools → and.
fn try_and(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let vals = find_two_values(idx, ntable, outputs, grid);
    if vals.len() < 2 { return None; }
    match (vals[0], vals[1]) {
        (Value::Bool(a), Value::Bool(b)) => Some(Value::Bool(*a && *b)),
        (Value::List(a), Value::List(b)) if a.len() == b.len() => {
            let result: Vec<Value> = a.iter().zip(b.iter())
                .map(|(x, y)| Value::Bool(x.is_truthy() && y.is_truthy()))
                .collect();
            Some(Value::List(Arc::new(result)))
        }
        _ => None,
    }
}

/// Or: two bool-lists → element-wise or, or two bools → or.
fn try_or(
    idx: usize, ntable: &NeighborTable, outputs: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    let vals = find_two_values(idx, ntable, outputs, grid);
    if vals.len() < 2 { return None; }
    match (vals[0], vals[1]) {
        (Value::Bool(a), Value::Bool(b)) => Some(Value::Bool(*a || *b)),
        (Value::List(a), Value::List(b)) if a.len() == b.len() => {
            let result: Vec<Value> = a.iter().zip(b.iter())
                .map(|(x, y)| Value::Bool(x.is_truthy() || y.is_truthy()))
                .collect();
            Some(Value::List(Arc::new(result)))
        }
        _ => None,
    }
}

// ---------------------------------------------------------------------------
// Main evaluation
// ---------------------------------------------------------------------------

/// Evaluate a single individual's grid on one context.
pub fn evaluate_dataflow(
    grid: &FixedGrid,
    context: &EvalContext,
    ntable: &NeighborTable,
) -> Value {
    let mut outputs = vec![Value::Nil; GRID_SIZE];

    // Round 0: initialize data sources, literals, field keys
    for (idx, &ch) in grid.iter().enumerate() {
        if ch == 0 { continue; }
        let frag = alphabet::to_fragment(ch);
        outputs[idx] = match frag {
            Fragment::DataSource(ds) => {
                let ds_idx = match ds {
                    DataSource::Products => 0,
                    DataSource::Employees => 1,
                    DataSource::Orders => 2,
                    DataSource::Expenses => 3,
                };
                context.data_sources[ds_idx].clone()
            }
            Fragment::Literal(v) => Value::Int(v),
            Fragment::FieldKey(k) => Value::Str(Arc::from(k.to_str())),
            _ => Value::Nil,
        };
    }

    // Rounds 1..NUM_ROUNDS: propagate values
    for _round in 1..NUM_ROUNDS {
        // Snapshot: cells read from previous state, write to new state.
        // We clone the outputs so reads are consistent within a round.
        let snapshot = outputs.clone();

        for (idx, &ch) in grid.iter().enumerate() {
            if ch == 0 { continue; }

            // Cells that already have a non-Nil value from initialization persist
            let frag = alphabet::to_fragment(ch);
            match frag {
                Fragment::DataSource(_) | Fragment::Literal(_) | Fragment::FieldKey(_) => {
                    // Keep initial value, don't overwrite
                    continue;
                }
                _ => {}
            }

            // Only try to compute if we haven't produced a useful value yet
            if !matches!(outputs[idx], Value::Nil) { continue; }

            let result = match frag {
                Fragment::Fn(Op::Get) =>
                    try_get(idx, ntable, &snapshot, grid),
                Fragment::Comparator(Op::Gt | Op::Lt | Op::Eq) =>
                    try_compare(idx, match frag { Fragment::Comparator(op) => op, _ => unreachable!() },
                                ntable, &snapshot, grid),
                Fragment::Comparator(Op::Plus) =>
                    try_plus(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::Filter) =>
                    try_filter(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::Map) =>
                    try_map(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::Count) =>
                    try_count(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::First) =>
                    try_first(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::Last) =>
                    try_last(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::Rest) =>
                    try_rest(idx, ntable, &snapshot, grid),
                Fragment::Fn(Op::Reverse) =>
                    try_reverse(idx, ntable, &snapshot, grid),
                Fragment::Connective(Op::Not) =>
                    try_not(idx, ntable, &snapshot, grid),
                Fragment::Connective(Op::And) =>
                    try_and(idx, ntable, &snapshot, grid),
                Fragment::Connective(Op::Or) =>
                    try_or(idx, ntable, &snapshot, grid),
                // Relay cells: wildcards and fn/let/match/if pass through best neighbor
                Fragment::Wildcard
                | Fragment::Fn(Op::Fn | Op::Let | Op::Match | Op::If
                               | Op::Assoc | Op::Set | Op::Contains
                               | Op::Reduce | Op::GroupBy | Op::Sort) => {
                    find_best_relay(idx, ntable, &snapshot, grid).cloned()
                }
                _ => None,
            };

            if let Some(val) = result {
                outputs[idx] = val;
            }
        }
    }

    // Find the best output cell
    find_output(&outputs, grid)
}

/// Select the program output: highest-priority cell with a non-Nil value.
fn find_output(outputs: &[Value], grid: &FixedGrid) -> Value {
    let mut best_idx: Option<usize> = None;
    let mut best_prio = -1;

    for (idx, &ch) in grid.iter().enumerate() {
        if ch == 0 { continue; }
        if matches!(outputs[idx], Value::Nil) { continue; }

        let frag = alphabet::to_fragment(ch);
        let prio = output_priority(&frag);
        if prio > best_prio {
            best_prio = prio;
            best_idx = Some(idx);
        }
    }

    best_idx.map(|idx| outputs[idx].clone()).unwrap_or(Value::Nil)
}

// ---------------------------------------------------------------------------
// Scoring (reuses partial_credit from vm::fitness)
// ---------------------------------------------------------------------------

/// Score a dataflow individual across contexts and targets.
/// Same semantics as vm::fitness::score_individual but using dataflow evaluation.
pub fn score_dataflow(
    grid: &FixedGrid,
    contexts: &[EvalContext],
    target_outputs: &[Vec<Value>],
    ntable: &NeighborTable,
) -> f64 {
    let outputs: Vec<Value> = contexts.iter()
        .map(|ctx| evaluate_dataflow(grid, ctx, ntable))
        .collect();

    // Data-dependence gate
    let reprs: Vec<String> = outputs.iter().map(value_repr).collect();
    if reprs.iter().all(|r| r == &reprs[0]) {
        return 0.0;
    }

    // Partial credit against all targets
    let mut total = 0.0;
    let mut count = 0;
    for target_row in target_outputs {
        for (ctx_idx, expected) in target_row.iter().enumerate() {
            total += partial_credit(&outputs[ctx_idx], expected);
            count += 1;
        }
    }

    if count == 0 { 0.0 } else { total / count as f64 }
}

/// Count active compute cells (non-data, non-literal, non-fieldkey) with output.
/// Analogous to bond_count in the chemistry pipeline.
pub fn dataflow_depth(grid: &FixedGrid, outputs: &[Value]) -> usize {
    let mut count = 0;
    for (idx, &ch) in grid.iter().enumerate() {
        if ch == 0 { continue; }
        if matches!(outputs[idx], Value::Nil) { continue; }
        let frag = alphabet::to_fragment(ch);
        match frag {
            Fragment::Fn(_) | Fragment::Comparator(_) | Fragment::Connective(_) => {
                count += 1;
            }
            _ => {}
        }
    }
    count
}

/// Generate a source description string for the output cell.
pub fn describe_output(grid: &FixedGrid, output_idx: Option<usize>) -> Option<String> {
    let idx = output_idx?;
    let ch = grid[idx];
    if ch == 0 { return None; }
    let frag = alphabet::to_fragment(ch);
    let name = match frag {
        Fragment::Fn(op) => op.to_str(),
        Fragment::Comparator(op) => op.to_str(),
        Fragment::Connective(op) => op.to_str(),
        Fragment::DataSource(ds) => return Some(format!("df:data/{}", ds.to_str())),
        Fragment::Literal(v) => return Some(format!("df:{}", v)),
        Fragment::FieldKey(k) => return Some(format!("df::{}", k.to_str())),
        Fragment::Wildcard => "relay",
        _ => return None,
    };
    Some(format!("df:{}", name))
}

/// Full evaluate + score for a single genotype. Returns (fitness, source, depth).
pub fn develop_and_score_dataflow(
    genotype: &[u8],
    contexts: &[EvalContext],
    target_outputs: &[Vec<Value>],
    ntable: &NeighborTable,
) -> (f64, Option<String>, usize) {
    let grid = super::grid::fold_fixed(genotype);

    let fitness = score_dataflow(&grid, contexts, target_outputs, ntable);

    // Evaluate once more with first context to get output cell + depth
    let mut outputs = vec![Value::Nil; GRID_SIZE];
    // Re-run to capture outputs (duplicates work but keeps API clean)
    for (idx, &ch) in grid.iter().enumerate() {
        if ch == 0 { continue; }
        let frag = alphabet::to_fragment(ch);
        outputs[idx] = match frag {
            Fragment::DataSource(ds) => {
                let ds_idx = match ds {
                    DataSource::Products => 0, DataSource::Employees => 1,
                    DataSource::Orders => 2, DataSource::Expenses => 3,
                };
                contexts[0].data_sources[ds_idx].clone()
            }
            Fragment::Literal(v) => Value::Int(v),
            Fragment::FieldKey(k) => Value::Str(Arc::from(k.to_str())),
            _ => Value::Nil,
        };
    }
    for _ in 1..NUM_ROUNDS {
        let snapshot = outputs.clone();
        for (idx, &ch) in grid.iter().enumerate() {
            if ch == 0 { continue; }
            let frag = alphabet::to_fragment(ch);
            match frag {
                Fragment::DataSource(_) | Fragment::Literal(_) | Fragment::FieldKey(_) => continue,
                _ => {}
            }
            if !matches!(outputs[idx], Value::Nil) { continue; }
            let result = try_compute_cell(idx, &frag, ntable, &snapshot, &grid);
            if let Some(val) = result {
                outputs[idx] = val;
            }
        }
    }

    let depth = dataflow_depth(&grid, &outputs);

    // Find output cell for source description
    let mut best_idx: Option<usize> = None;
    let mut best_prio = -1;
    for (idx, &ch) in grid.iter().enumerate() {
        if ch == 0 { continue; }
        if matches!(outputs[idx], Value::Nil) { continue; }
        let frag = alphabet::to_fragment(ch);
        let prio = output_priority(&frag);
        if prio > best_prio {
            best_prio = prio;
            best_idx = Some(idx);
        }
    }
    let source = describe_output(&grid, best_idx);

    (fitness, source, depth)
}

/// Helper: dispatch cell computation by fragment type.
fn try_compute_cell(
    idx: usize, frag: &Fragment, ntable: &NeighborTable, snapshot: &[Value], grid: &FixedGrid,
) -> Option<Value> {
    match frag {
        Fragment::Fn(Op::Get) => try_get(idx, ntable, snapshot, grid),
        Fragment::Comparator(op @ (Op::Gt | Op::Lt | Op::Eq)) =>
            try_compare(idx, *op, ntable, snapshot, grid),
        Fragment::Comparator(Op::Plus) => try_plus(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::Filter) => try_filter(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::Map) => try_map(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::Count) => try_count(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::First) => try_first(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::Last) => try_last(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::Rest) => try_rest(idx, ntable, snapshot, grid),
        Fragment::Fn(Op::Reverse) => try_reverse(idx, ntable, snapshot, grid),
        Fragment::Connective(Op::Not) => try_not(idx, ntable, snapshot, grid),
        Fragment::Connective(Op::And) => try_and(idx, ntable, snapshot, grid),
        Fragment::Connective(Op::Or) => try_or(idx, ntable, snapshot, grid),
        Fragment::Wildcard
        | Fragment::Fn(Op::Fn | Op::Let | Op::Match | Op::If
                       | Op::Assoc | Op::Set | Op::Contains
                       | Op::Reduce | Op::GroupBy | Op::Sort) => {
            find_best_relay(idx, ntable, snapshot, grid).cloned()
        }
        _ => None,
    }
}
