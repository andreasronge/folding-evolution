mod types;
mod alphabet;
mod fold;
mod ast;
mod engine;
mod chemistry;
mod vm;
mod dataflow;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use rayon::prelude::*;

use vm::bytecode;
use vm::context::{EvalContext, py_to_value, value_to_py};
use vm::fitness;
use vm::value::Value;

// ---------- helpers ----------------------------------------------------------

/// Shared logic: fold + assemble + select best AST.
fn develop_inner(genotype_bytes: &[u8]) -> Option<(ast::AstNode, String, usize)> {
    let grid = fold::fold(genotype_bytes);
    let fragments = chemistry::assemble(&grid);
    if fragments.is_empty() {
        return None;
    }
    let mut best_idx = 0;
    let mut best_bonds = ast::count_bonds(&fragments[0]);
    for (i, f) in fragments.iter().enumerate().skip(1) {
        let bonds = ast::count_bonds(f);
        if bonds > best_bonds {
            best_bonds = bonds;
            best_idx = i;
        }
    }
    let best = fragments.into_iter().nth(best_idx).unwrap();
    let bond_count = ast::count_bonds(&best);
    let source = ast::to_string(&best);
    Some((best, source, bond_count))
}

// ---------- single develop ---------------------------------------------------

/// Develop a genotype into a phenotype (fold + chemistry + best AST selection).
/// Returns (ast_tuple, source_string, bond_count) or None if no valid program.
#[pyfunction]
fn rust_develop(py: Python<'_>, genotype: &str) -> PyResult<Option<(PyObject, String, usize)>> {
    let genotype_bytes = genotype.as_bytes().to_vec();

    let result = py.allow_threads(move || develop_inner(&genotype_bytes));

    match result {
        None => Ok(None),
        Some((ast_node, source, bond_count)) => {
            let py_ast = ast::to_py_object(py, &ast_node)?;
            Ok(Some((py_ast, source, bond_count)))
        }
    }
}

// ---------- batch develop ----------------------------------------------------

/// Batch develop: process multiple genotypes in parallel using Rayon.
#[pyfunction]
fn rust_develop_batch(py: Python<'_>, genotypes: Vec<String>) -> PyResult<Vec<Option<(PyObject, String, usize)>>> {
    let results: Vec<Option<(ast::AstNode, String, usize)>> = py.allow_threads(|| {
        genotypes.par_iter().map(|g| develop_inner(g.as_bytes())).collect()
    });

    results.into_iter().map(|opt| {
        match opt {
            None => Ok(None),
            Some((ast_node, source, bond_count)) => {
                let py_ast = ast::to_py_object(py, &ast_node)?;
                Ok(Some((py_ast, source, bond_count)))
            }
        }
    }).collect()
}

// ---------- VM PyClasses -----------------------------------------------------

/// Pre-converted evaluation contexts (Python dicts -> Rust Values).
/// Create once, reuse across all evaluations in an experiment.
#[pyclass]
struct RustContexts {
    contexts: Vec<EvalContext>,
}

#[pymethods]
impl RustContexts {
    #[new]
    fn new(py_contexts: &Bound<'_, PyList>) -> PyResult<Self> {
        let mut contexts = Vec::new();
        for item in py_contexts.iter() {
            let dict = item.downcast::<PyDict>()?;
            contexts.push(EvalContext::from_py_dict(dict)?);
        }
        Ok(RustContexts { contexts })
    }
}

/// Pre-computed target outputs: target_outputs[target_idx][context_idx] = expected Value.
/// Compute in Python once, pass to Rust for scoring.
#[pyclass]
struct RustTargetOutputs {
    outputs: Vec<Vec<Value>>,
}

#[pymethods]
impl RustTargetOutputs {
    #[new]
    fn new(py_outputs: &Bound<'_, PyList>) -> PyResult<Self> {
        let mut outputs = Vec::new();
        for target_row in py_outputs.iter() {
            let row_list = target_row.downcast::<PyList>()?;
            let mut row = Vec::new();
            for val in row_list.iter() {
                row.push(py_to_value(&val)?);
            }
            outputs.push(row);
        }
        Ok(RustTargetOutputs { outputs })
    }
}

// ---------- combined develop + score batch -----------------------------------

/// Combined develop + compile + evaluate + score for an entire population.
/// Returns: [(fitness, source_or_none, bond_count), ...] per genotype.
/// All computation happens in Rust with GIL released and Rayon parallelism.
#[pyfunction]
fn rust_develop_and_score_batch(
    py: Python<'_>,
    genotypes: Vec<String>,
    contexts: &RustContexts,
    targets: &RustTargetOutputs,
) -> PyResult<Vec<(f64, Option<String>, usize)>> {
    let ctx_slice = &contexts.contexts;
    let target_slice = &targets.outputs;

    let results = py.allow_threads(|| {
        genotypes.par_iter().map(|g| {
            match develop_inner(g.as_bytes()) {
                None => (0.0f64, None, 0usize),
                Some((ast_node, source, bond_count)) => {
                    let bc = bytecode::compile(&ast_node, source.clone(), bond_count);
                    let score = fitness::score_individual(&bc, ctx_slice, target_slice);
                    (score, Some(source), bond_count)
                }
            }
        }).collect::<Vec<_>>()
    });

    Ok(results)
}

/// Evaluate a single genotype on all contexts using the VM.
/// Returns list of Python objects (one per context).
/// Useful for testing VM equivalence with the Python evaluator.
#[pyfunction]
fn rust_vm_evaluate(
    py: Python<'_>,
    genotype: &str,
    contexts: &RustContexts,
) -> PyResult<Vec<PyObject>> {
    let genotype_bytes = genotype.as_bytes().to_vec();
    let ctx_slice = &contexts.contexts;

    let results = py.allow_threads(move || {
        match develop_inner(&genotype_bytes) {
            None => ctx_slice.iter().map(|_| Value::Nil).collect::<Vec<_>>(),
            Some((ast_node, source, bond_count)) => {
                let bc = bytecode::compile(&ast_node, source, bond_count);
                ctx_slice.iter().map(|ctx| vm::eval::execute(&bc, ctx)).collect()
            }
        }
    });

    results.iter().map(|v| value_to_py(py, v)).collect()
}

// ---------- dataflow (alternative representation) ----------------------------

/// Dataflow develop + score batch: fold onto fixed grid, K rounds of broadcast
/// message passing, fitness scoring. An alternative to the chemistry pipeline.
/// Returns: [(fitness, source_or_none, depth), ...] per genotype.
#[pyfunction]
fn rust_dataflow_develop_and_score_batch(
    py: Python<'_>,
    genotypes: Vec<String>,
    contexts: &RustContexts,
    targets: &RustTargetOutputs,
) -> PyResult<Vec<(f64, Option<String>, usize)>> {
    let ctx_slice = &contexts.contexts;
    let target_slice = &targets.outputs;

    let results = py.allow_threads(|| {
        // Build neighbor table once (shared across all individuals)
        let ntable = dataflow::grid::NeighborTable::new();

        genotypes.par_iter().map(|g| {
            dataflow::evaluate::develop_and_score_dataflow(
                g.as_bytes(), ctx_slice, target_slice, &ntable,
            )
        }).collect::<Vec<_>>()
    });

    Ok(results)
}

/// Evaluate a single genotype using dataflow on all contexts.
/// Returns list of Python objects (one per context). For testing equivalence.
#[pyfunction]
fn rust_dataflow_evaluate(
    py: Python<'_>,
    genotype: &str,
    contexts: &RustContexts,
) -> PyResult<Vec<PyObject>> {
    let ntable = dataflow::grid::NeighborTable::new();
    let grid = dataflow::grid::fold_fixed(genotype.as_bytes());

    let results: Vec<Value> = contexts.contexts.iter()
        .map(|ctx| dataflow::evaluate::evaluate_dataflow(&grid, ctx, &ntable))
        .collect();

    results.iter().map(|v| value_to_py(py, v)).collect()
}

// ---------- debug functions --------------------------------------------------

#[pyfunction]
fn rust_fold_grid(genotype: &str) -> Vec<((i32, i32), u8)> {
    let grid = fold::fold(genotype.as_bytes());
    grid.into_iter().collect()
}

#[pyfunction]
fn rust_assemble_debug(genotype: &str) -> Vec<(String, usize)> {
    let grid = fold::fold(genotype.as_bytes());
    let fragments = chemistry::assemble(&grid);
    fragments.iter().map(|f| {
        (ast::to_string(f), ast::count_bonds(f))
    }).collect()
}

#[pyfunction]
fn rust_adjacency(genotype: &str) -> Vec<((i32, i32), Vec<(i32, i32)>)> {
    let grid = fold::fold(genotype.as_bytes());
    let adj = engine::build_adjacency(&grid);
    grid.keys().map(|&pos| {
        let neighbors = adj.get(&pos).cloned().unwrap_or_default();
        (pos, neighbors)
    }).collect()
}

// ---------- module -----------------------------------------------------------

#[pymodule]
fn _folding_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_develop, m)?)?;
    m.add_function(wrap_pyfunction!(rust_develop_batch, m)?)?;
    m.add_function(wrap_pyfunction!(rust_develop_and_score_batch, m)?)?;
    m.add_function(wrap_pyfunction!(rust_vm_evaluate, m)?)?;
    m.add_function(wrap_pyfunction!(rust_dataflow_develop_and_score_batch, m)?)?;
    m.add_function(wrap_pyfunction!(rust_dataflow_evaluate, m)?)?;
    m.add_function(wrap_pyfunction!(rust_fold_grid, m)?)?;
    m.add_function(wrap_pyfunction!(rust_adjacency, m)?)?;
    m.add_function(wrap_pyfunction!(rust_assemble_debug, m)?)?;
    m.add_class::<RustContexts>()?;
    m.add_class::<RustTargetOutputs>()?;
    Ok(())
}
