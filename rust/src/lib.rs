mod types;
mod alphabet;
mod fold;
mod ast;
mod engine;
mod chemistry;

use pyo3::prelude::*;

/// Develop a genotype into a phenotype (fold + chemistry + best AST selection).
/// Returns (ast_tuple, source_string, bond_count) or None if no valid program.
/// Releases the GIL during computation.
#[pyfunction]
fn rust_develop(py: Python<'_>, genotype: &str) -> PyResult<Option<(PyObject, String, usize)>> {
    let genotype_bytes = genotype.as_bytes().to_vec();

    // Do all computation without GIL
    let result = py.allow_threads(move || {
        let grid = fold::fold(&genotype_bytes);
        let fragments = chemistry::assemble(&grid);
        if fragments.is_empty() {
            return None;
        }
        let best = fragments.into_iter()
            .max_by_key(|f| ast::count_bonds(f))
            .unwrap();
        let bond_count = ast::count_bonds(&best);
        let source = ast::to_string(&best);
        Some((best, source, bond_count))
    });

    match result {
        None => Ok(None),
        Some((ast_node, source, bond_count)) => {
            let py_ast = ast::to_py_object(py, &ast_node)?;
            Ok(Some((py_ast, source, bond_count)))
        }
    }
}

#[pymodule]
fn _folding_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_develop, m)?)?;
    Ok(())
}
