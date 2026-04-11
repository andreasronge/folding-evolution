/// Pass 1: Leaf Bonds
/// - get + field_key -> (get x :key)
/// - assoc + field_key + value -> (assoc x :key value)

use rustc_hash::FxHashSet;
use crate::types::*;
use crate::ast::AstNode;
use crate::fold::Pos;
use crate::engine::{self, FragmentMap, Adjacency};
use crate::chemistry::Fragment;

pub fn run(fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    // Sub-pass 1: get bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(Op::Get)) = fmap.get(pos) {
            try_get_bond(*pos, fmap, adj, consumed);
        }
    }

    // Sub-pass 2: assoc bonds
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        if let Some(Fragment::Fn(Op::Assoc)) = fmap.get(pos) {
            try_assoc_bond(*pos, fmap, adj, consumed);
        }
    }
}

fn try_get_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    for (npos, nfrag) in &neighbors {
        if let Fragment::FieldKey(key) = nfrag {
            let ast = AstNode::ListExpr(vec![
                AstNode::Symbol(Op::Get),
                AstNode::SymbolStr("x".to_string()),
                AstNode::Keyword(*key),
            ]);
            engine::bond(fmap, adj, consumed, pos, &[*npos], Fragment::Assembled(ast));
            return;
        }
    }
}

fn try_assoc_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);

    let mut key_frag: Option<(Pos, FieldKey)> = None;
    let mut val_frag: Option<(Pos, Fragment)> = None;

    for (npos, nfrag) in &neighbors {
        if key_frag.is_none() {
            if let Fragment::FieldKey(key) = nfrag {
                key_frag = Some((*npos, *key));
                continue;
            }
        }
        if val_frag.is_none() && nfrag.is_value() {
            val_frag = Some((*npos, nfrag.clone()));
        }
    }

    if let (Some((kp, key)), Some((vp, vf))) = (key_frag, val_frag) {
        let val_ast = vf.to_ast().unwrap();
        let ast = AstNode::ListExpr(vec![
            AstNode::Symbol(Op::Assoc),
            AstNode::SymbolStr("x".to_string()),
            AstNode::Keyword(key),
            val_ast,
        ]);
        engine::bond(fmap, adj, consumed, pos, &[kp, vp], Fragment::Assembled(ast));
    }
}
