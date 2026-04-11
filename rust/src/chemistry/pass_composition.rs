/// Pass 4: Composition Bonds
/// - and/or + expr + expr -> (op expr1 expr2)
/// - not + expr -> (not expr)
/// - set + collection -> (set collection)
/// - contains? + set + value -> (contains? set value)

use rustc_hash::FxHashSet;
use crate::types::*;
use crate::ast::AstNode;
use crate::fold::Pos;
use crate::engine::{self, FragmentMap, Adjacency};
use crate::chemistry::Fragment;

pub fn run(fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    // Sub-pass 1: logical bonds (and/or)
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Connective(op)) = fmap.get(pos) {
            if matches!(op, Op::And | Op::Or) {
                try_logical_bond(*pos, fmap, adj, consumed);
            }
        }
    }

    // Sub-pass 2: not bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Connective(Op::Not)) = fmap.get(pos) {
            try_not_bond(*pos, fmap, adj, consumed);
        }
    }

    // Sub-pass 3: set bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(Op::Set)) = fmap.get(pos) {
            try_set_bond(*pos, fmap, adj, consumed);
        }
    }

    // Sub-pass 4: contains? bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(Op::Contains)) = fmap.get(pos) {
            try_contains_bond(*pos, fmap, adj, consumed);
        }
    }
}

fn try_logical_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let op = match fmap.get(&pos) {
        Some(Fragment::Connective(op)) => *op,
        _ => return,
    };

    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    let exprs: Vec<(Pos, Fragment)> = neighbors.into_iter()
        .filter(|(_, f)| f.is_expression())
        .collect();

    if exprs.len() >= 2 {
        let (p1, f1) = &exprs[0];
        let (p2, f2) = &exprs[1];
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

fn try_not_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    for (npos, nfrag) in &neighbors {
        if nfrag.is_expression() {
            let ast = AstNode::ListExpr(vec![
                AstNode::Symbol(Op::Not),
                nfrag.to_ast().unwrap(),
            ]);
            engine::bond(fmap, adj, consumed, pos, &[*npos], Fragment::Assembled(ast));
            return;
        }
    }
}

fn try_set_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    for (npos, nfrag) in &neighbors {
        if nfrag.is_collection() {
            let ast = AstNode::ListExpr(vec![
                AstNode::Symbol(Op::Set),
                nfrag.to_ast().unwrap(),
            ]);
            engine::bond(fmap, adj, consumed, pos, &[*npos], Fragment::Assembled(ast));
            return;
        }
    }
}

fn try_contains_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    let sets: Vec<(Pos, Fragment)> = neighbors.iter()
        .filter(|(_, f)| f.is_set())
        .cloned()
        .collect();
    let values: Vec<(Pos, Fragment)> = neighbors.iter()
        .filter(|(_, f)| f.is_value())
        .cloned()
        .collect();

    if !sets.is_empty() && !values.is_empty() {
        let (sp, sf) = &sets[0];
        let (vp, vf) = &values[0];
        let ast = AstNode::ListExpr(vec![
            AstNode::Symbol(Op::Contains),
            sf.to_ast().unwrap(),
            vf.to_ast().unwrap(),
        ]);
        let sp = *sp;
        let vp = *vp;
        engine::bond(fmap, adj, consumed, pos, &[sp, vp], Fragment::Assembled(ast));
    }
}
