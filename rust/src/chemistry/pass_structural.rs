/// Pass 3: Structural Bonds
/// - filter/map/reduce/group_by + fn_expr + data -> (op fn data)
/// - count/first/reverse/sort/rest/last + collection -> (op collection)

use rustc_hash::FxHashSet;
use crate::types::*;
use crate::ast::AstNode;
use crate::fold::Pos;
use crate::engine::{self, FragmentMap, Adjacency};
use crate::chemistry::Fragment;

const HIGHER_ORDER_OPS: &[Op] = &[Op::Filter, Op::Map, Op::Reduce, Op::GroupBy];
const WRAPPER_OPS: &[Op] = &[Op::Count, Op::First, Op::Reverse, Op::Sort, Op::Rest, Op::Last];

pub fn run(fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    // Sub-pass 1: higher-order bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(op)) = fmap.get(pos) {
            if HIGHER_ORDER_OPS.contains(op) {
                try_higher_order_bond(*pos, fmap, adj, consumed);
            }
        }
    }

    // Sub-pass 2: wrapper bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(op)) = fmap.get(pos) {
            if WRAPPER_OPS.contains(op) {
                try_wrapper_bond(*pos, fmap, adj, consumed);
            }
        }
    }
}

fn try_higher_order_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let op = match fmap.get(&pos) {
        Some(Fragment::Fn(op)) => *op,
        _ => return,
    };

    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    let mut fn_frag: Option<(Pos, Fragment)> = None;
    let mut data_frag: Option<(Pos, Fragment)> = None;

    for (npos, nfrag) in neighbors {
        if fn_frag.is_none() && nfrag.is_fn_expression() {
            fn_frag = Some((npos, nfrag));
        } else if data_frag.is_none() && nfrag.is_data() {
            data_frag = Some((npos, nfrag));
        }
    }

    if let (Some((fp, ff)), Some((dp, df))) = (fn_frag, data_frag) {
        let ast = AstNode::ListExpr(vec![
            AstNode::Symbol(op),
            ff.to_ast().unwrap(),
            df.to_ast().unwrap(),
        ]);
        engine::bond(fmap, adj, consumed, pos, &[fp, dp], Fragment::Assembled(ast));
    }
}

fn try_wrapper_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let op = match fmap.get(&pos) {
        Some(Fragment::Fn(op)) => *op,
        _ => return,
    };

    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    for (npos, nfrag) in &neighbors {
        if nfrag.is_collection() {
            let ast = AstNode::ListExpr(vec![
                AstNode::Symbol(op),
                nfrag.to_ast().unwrap(),
            ]);
            engine::bond(fmap, adj, consumed, pos, &[*npos], Fragment::Assembled(ast));
            return;
        }
    }
}
