/// Pass 2: Predicate Bonds
/// - comparator + value + value -> (op val1 val2)
/// - fn + expression -> (fn x expr)

use rustc_hash::FxHashSet;
use crate::types::*;
use crate::ast::AstNode;
use crate::fold::Pos;
use crate::engine::{self, FragmentMap, Adjacency};
use crate::chemistry::Fragment;

pub fn run(fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    // Sub-pass 1: comparator bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Comparator(_)) = fmap.get(pos) {
            try_comparator_bond(*pos, fmap, adj, consumed);
        }
    }

    // Sub-pass 2: fn bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(Op::Fn)) = fmap.get(pos) {
            try_fn_bond(*pos, fmap, adj, consumed);
        }
    }
}

fn try_comparator_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let op = match fmap.get(&pos) {
        Some(Fragment::Comparator(op)) => *op,
        _ => return,
    };

    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    let mut values: Vec<(Pos, Fragment)> = neighbors.into_iter()
        .filter(|(_, f)| f.is_value())
        .collect();
    values.sort_by_key(|(_, f)| f.value_priority());

    if values.len() >= 2 {
        let (p1, f1) = &values[0];
        let (p2, f2) = &values[1];
        let ast = AstNode::ListExpr(vec![
            AstNode::Symbol(op),
            f1.to_ast().unwrap(),
            f2.to_ast().unwrap(),
        ]);
        let p1 = *p1;
        let p2 = *p2;
        engine::bond(fmap, adj, consumed, pos, &[p1, p2], Fragment::Assembled(ast));
    }
}

fn try_fn_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    for (npos, nfrag) in &neighbors {
        if nfrag.is_expression() {
            let ast = AstNode::ListExpr(vec![
                AstNode::Symbol(Op::Fn),
                AstNode::SymbolStr("x".to_string()),
                nfrag.to_ast().unwrap(),
            ]);
            engine::bond(fmap, adj, consumed, pos, &[*npos], Fragment::Assembled(ast));
            return;
        }
    }
}
