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
        // Pick first fragment with max bond count (matching Python's max() tie-breaking)
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
    });

    match result {
        None => Ok(None),
        Some((ast_node, source, bond_count)) => {
            let py_ast = ast::to_py_object(py, &ast_node)?;
            Ok(Some((py_ast, source, bond_count)))
        }
    }
}

/// Debug: return grid positions in insertion order.
#[pyfunction]
fn rust_fold_grid(genotype: &str) -> Vec<((i32, i32), u8)> {
    let grid = fold::fold(genotype.as_bytes());
    grid.into_iter().collect()
}

/// Debug: return all unconsumed fragments after assembly.
#[pyfunction]
fn rust_assemble_debug(genotype: &str) -> Vec<(String, usize)> {
    let grid = fold::fold(genotype.as_bytes());
    let fragments = chemistry::assemble(&grid);
    fragments.iter().map(|f| {
        (ast::to_string(f), ast::count_bonds(f))
    }).collect()
}

/// Debug: return adjacency lists.
#[pyfunction]
fn rust_adjacency(genotype: &str) -> Vec<((i32, i32), Vec<(i32, i32)>)> {
    let grid = fold::fold(genotype.as_bytes());
    let adj = engine::build_adjacency(&grid);
    // Return in grid insertion order
    grid.keys().map(|&pos| {
        let neighbors = adj.get(&pos).cloned().unwrap_or_default();
        (pos, neighbors)
    }).collect()
}

#[pymodule]
fn _folding_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_develop, m)?)?;
    m.add_function(wrap_pyfunction!(rust_fold_grid, m)?)?;
    m.add_function(wrap_pyfunction!(rust_adjacency, m)?)?;
    m.add_function(wrap_pyfunction!(rust_assemble_debug, m)?)?;
    Ok(())
}
