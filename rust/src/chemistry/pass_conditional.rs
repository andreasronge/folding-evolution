/// Pass 5: Conditional Bonds
/// - match + pattern_fragments -> (tool/match :pattern pattern_str)
/// - if + predicate + expr [+ expr] -> (if pred then [else])

use rustc_hash::FxHashSet;
use crate::types::*;
use crate::ast::AstNode;
use crate::fold::Pos;
use crate::engine::{self, FragmentMap, Adjacency};
use crate::chemistry::Fragment;

pub fn run(
    fmap: &mut FragmentMap,
    adj: &mut Adjacency,
    consumed: &mut FxHashSet<Pos>,
    wildcard_positions: &FxHashSet<Pos>,
) {
    let positions: Vec<Pos> = fmap.keys().copied().collect();
    for pos in &positions {
        if consumed.contains(pos) { continue; }
        match fmap.get(pos) {
            Some(Fragment::Fn(Op::Match)) => {
                try_match_bond(*pos, fmap, adj, consumed, wildcard_positions);
            }
            Some(Fragment::Fn(Op::If)) => {
                try_if_bond(*pos, fmap, adj, consumed);
            }
            _ => {}
        }
    }
}

fn try_match_bond(
    pos: Pos,
    fmap: &mut FragmentMap,
    adj: &mut Adjacency,
    consumed: &mut FxHashSet<Pos>,
    wildcard_positions: &FxHashSet<Pos>,
) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    let mut pattern_fragments: Vec<(Pos, Fragment)> = neighbors.into_iter()
        .filter(|(_, f)| !matches!(f, Fragment::Fn(_)))
        .collect();
    pattern_fragments.sort_by_key(|(p, _)| *p);

    if pattern_fragments.is_empty() {
        return;
    }

    let mut parts: Vec<String> = Vec::new();
    for (npos, nfrag) in &pattern_fragments {
        if wildcard_positions.contains(npos) {
            parts.push("*".to_string());
        } else {
            let ast = nfrag.to_ast();
            parts.push(format_pattern_ast(&ast));
        }
    }

    let pattern_str = if parts.len() == 1 {
        parts[0].clone()
    } else {
        format!("({})", parts.join(" "))
    };

    let match_ast = AstNode::ListExpr(vec![
        AstNode::NsSymbol { ns: "tool", name: "match" },
        AstNode::Keyword(FieldKey::Pattern),
        AstNode::SymbolStr(pattern_str),
    ]);

    let child_positions: Vec<Pos> = pattern_fragments.iter().map(|(p, _)| *p).collect();
    engine::bond(fmap, adj, consumed, pos, &child_positions, Fragment::Assembled(match_ast));
}

fn try_if_bond(pos: Pos, fmap: &mut FragmentMap, adj: &mut Adjacency, consumed: &mut FxHashSet<Pos>) {
    let neighbors = engine::get_unconsumed_neighbors(pos, adj, consumed, fmap);
    let usable: Vec<(Pos, Fragment)> = neighbors.into_iter()
        .filter(|(_, f)| !matches!(f, Fragment::Fn(Op::If) | Fragment::Fn(Op::Match)))
        .collect();

    let preds: Vec<&(Pos, Fragment)> = usable.iter()
        .filter(|(_, f)| f.is_predicate())
        .collect();
    let non_preds: Vec<&(Pos, Fragment)> = usable.iter()
        .filter(|(_, f)| !f.is_predicate())
        .collect();

    if preds.is_empty() {
        return;
    }

    let mut sorted_frags: Vec<&(Pos, Fragment)> = Vec::new();
    sorted_frags.extend(preds);
    sorted_frags.extend(non_preds);

    if sorted_frags.len() >= 3 {
        let (pp, pf) = sorted_frags[0];
        let (tp, tf) = sorted_frags[1];
        let (ep, ef) = sorted_frags[2];
        let ast = AstNode::ListExpr(vec![
            AstNode::Symbol(Op::If),
            pf.to_ast().unwrap(),
            tf.to_ast().unwrap(),
            ef.to_ast().unwrap(),
        ]);
        engine::bond(fmap, adj, consumed, pos, &[*pp, *tp, *ep], Fragment::Assembled(ast));
    } else if sorted_frags.len() >= 2 {
        let (pp, pf) = sorted_frags[0];
        let (tp, tf) = sorted_frags[1];
        let ast = AstNode::ListExpr(vec![
            AstNode::Symbol(Op::If),
            pf.to_ast().unwrap(),
            tf.to_ast().unwrap(),
        ]);
        engine::bond(fmap, adj, consumed, pos, &[*pp, *tp], Fragment::Assembled(ast));
    }
}

fn format_pattern_ast(ast: &Option<AstNode>) -> String {
    match ast {
        None => "*".to_string(),
        Some(node) => match node {
            AstNode::Symbol(op) => op.to_str().to_string(),
            AstNode::SymbolStr(s) => s.clone(),
            AstNode::Keyword(k) => format!(":{}", k.to_str()),
            AstNode::NsSymbol { ns, name } => format!("{}/{}", ns, name),
            AstNode::Literal(v) => v.to_string(),
            AstNode::ListExpr(items) => {
                let inner: Vec<String> = items.iter()
                    .map(|i| format_pattern_ast(&Some(i.clone())))
                    .collect();
                format!("({})", inner.join(" "))
            }
        }
    }
}
