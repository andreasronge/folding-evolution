/// AST node types for the folding evolution phenotype.
/// Mirrors the Python ast_nodes.py types.

use crate::types::*;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

#[derive(Clone, Debug)]
pub enum AstNode {
    Literal(i64),
    Symbol(Op),
    SymbolStr(String),       // for non-Op symbols like "x", "*", pattern strings
    Keyword(FieldKey),
    NsSymbol { ns: &'static str, name: &'static str },
    ListExpr(Vec<AstNode>),
}

pub fn count_bonds(node: &AstNode) -> usize {
    match node {
        AstNode::ListExpr(items) => {
            1 + items.iter().map(count_bonds).sum::<usize>()
        }
        _ => 0,
    }
}

pub fn to_string(node: &AstNode) -> String {
    match node {
        AstNode::Literal(v) => v.to_string(),
        AstNode::Symbol(op) => op.to_str().to_string(),
        AstNode::SymbolStr(s) => s.clone(),
        AstNode::Keyword(k) => format!(":{}", k.to_str()),
        AstNode::NsSymbol { ns, name } => format!("{}/{}", ns, name),
        AstNode::ListExpr(items) => {
            let inner: Vec<String> = items.iter().map(to_string).collect();
            format!("({})", inner.join(" "))
        }
    }
}

/// Serialize AST to a compact tagged-tuple Python object.
pub fn to_py_object(py: Python<'_>, node: &AstNode) -> PyResult<PyObject> {
    match node {
        AstNode::Literal(v) => {
            Ok(("Lit", *v).to_object(py))
        }
        AstNode::Symbol(op) => {
            Ok(("Sym", op.to_str()).to_object(py))
        }
        AstNode::SymbolStr(s) => {
            Ok(("Sym", s.as_str()).to_object(py))
        }
        AstNode::Keyword(k) => {
            Ok(("Kw", k.to_str()).to_object(py))
        }
        AstNode::NsSymbol { ns, name } => {
            Ok(("Ns", *ns, *name).to_object(py))
        }
        AstNode::ListExpr(items) => {
            let py_items: Vec<PyObject> = items.iter()
                .map(|i| to_py_object(py, i))
                .collect::<PyResult<_>>()?;
            let items_tuple = PyTuple::new_bound(py, &py_items);
            Ok(("Expr", items_tuple).to_object(py))
        }
    }
}
