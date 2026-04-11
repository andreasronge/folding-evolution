/// Chemistry: multi-pass assembly of folded grid into AST fragments.
/// Each pass is a separate module with a uniform interface.

pub mod pass_leaf;
pub mod pass_predicate;
pub mod pass_structural;
pub mod pass_composition;
pub mod pass_conditional;

use rustc_hash::FxHashSet;
use crate::types::*;
use crate::ast::AstNode;
use crate::alphabet;
use crate::fold::Grid;
use crate::engine::{self, FragmentMap};

/// Fragment types in the chemistry pipeline.
#[derive(Clone, Debug)]
pub enum Fragment {
    Fn(Op),
    Comparator(Op),
    Connective(Op),
    FieldKey(FieldKey),
    DataSource(DataSource),
    Literal(i64),
    Wildcard,
    Spacer,
    Assembled(AstNode),
}

impl Fragment {
    /// Is this a value fragment (assembled, literal, or data_source)?
    pub fn is_value(&self) -> bool {
        matches!(self, Fragment::Assembled(_) | Fragment::Literal(_) | Fragment::DataSource(_))
    }

    /// Is this an expression fragment (assembled or literal)?
    pub fn is_expression(&self) -> bool {
        matches!(self, Fragment::Assembled(_) | Fragment::Literal(_))
    }

    /// Is this a collection fragment (assembled or data_source)?
    pub fn is_collection(&self) -> bool {
        matches!(self, Fragment::Assembled(_) | Fragment::DataSource(_))
    }

    /// Is this a data fragment (data_source or assembled higher-order)?
    pub fn is_data(&self) -> bool {
        match self {
            Fragment::DataSource(_) => true,
            Fragment::Assembled(ast) => {
                if let AstNode::ListExpr(items) = ast {
                    if let Some(AstNode::Symbol(op)) = items.first() {
                        return matches!(op,
                            Op::Filter | Op::Map | Op::Reduce | Op::GroupBy | Op::Sort
                        );
                    }
                }
                false
            }
            _ => false,
        }
    }

    /// Is this an fn-expression (assembled with head "fn")?
    pub fn is_fn_expression(&self) -> bool {
        if let Fragment::Assembled(AstNode::ListExpr(items)) = self {
            if let Some(AstNode::Symbol(Op::Fn)) = items.first() {
                return true;
            }
        }
        false
    }

    /// Is this a predicate fragment?
    pub fn is_predicate(&self) -> bool {
        if let Fragment::Assembled(AstNode::ListExpr(items)) = self {
            if let Some(head) = items.first() {
                return match head {
                    AstNode::Symbol(op) => matches!(op,
                        Op::Gt | Op::Lt | Op::Eq | Op::And | Op::Or | Op::Not | Op::Contains
                    ),
                    AstNode::NsSymbol { ns: "tool", name: "match" } => true,
                    _ => false,
                };
            }
        }
        false
    }

    /// Is this a set fragment (assembled with head "set")?
    pub fn is_set(&self) -> bool {
        if let Fragment::Assembled(AstNode::ListExpr(items)) = self {
            if let Some(AstNode::Symbol(Op::Set)) = items.first() {
                return true;
            }
        }
        false
    }

    /// Value priority for comparator bond ordering.
    pub fn value_priority(&self) -> i32 {
        match self {
            Fragment::Assembled(_) => 0,
            Fragment::Literal(_) => 1,
            Fragment::DataSource(_) => 2,
            _ => 3,
        }
    }

    /// Convert fragment to AST node.
    pub fn to_ast(&self) -> Option<AstNode> {
        match self {
            Fragment::Assembled(ast) => Some(ast.clone()),
            Fragment::Literal(v) => Some(AstNode::Literal(*v)),
            Fragment::DataSource(ds) => Some(AstNode::NsSymbol { ns: "data", name: ds.to_str() }),
            Fragment::FieldKey(k) => Some(AstNode::Keyword(*k)),
            Fragment::Fn(op) => Some(AstNode::Symbol(*op)),
            Fragment::Comparator(op) => Some(AstNode::Symbol(*op)),
            Fragment::Connective(op) => Some(AstNode::Symbol(*op)),
            Fragment::Wildcard => Some(AstNode::SymbolStr("*".to_string())),
            Fragment::Spacer => None,
        }
    }
}

/// Assemble a folded grid into AST nodes through 5 sequential passes.
pub fn assemble(grid: &Grid) -> Vec<AstNode> {
    let mut adj = engine::build_adjacency(grid);

    let mut fmap = FragmentMap::new();
    let mut wildcard_positions = FxHashSet::default();

    for (&pos, &ch) in grid {
        let frag = alphabet::to_fragment(ch);
        match frag {
            Fragment::Spacer => {}
            Fragment::Wildcard => {
                wildcard_positions.insert(pos);
                fmap.insert(pos, frag);
            }
            _ => {
                fmap.insert(pos, frag);
            }
        }
    }

    let mut consumed = FxHashSet::default();

    // 5 sequential passes
    pass_leaf::run(&mut fmap, &mut adj, &mut consumed);
    pass_predicate::run(&mut fmap, &mut adj, &mut consumed);
    pass_structural::run(&mut fmap, &mut adj, &mut consumed);
    pass_composition::run(&mut fmap, &mut adj, &mut consumed);
    pass_conditional::run(&mut fmap, &mut adj, &mut consumed, &wildcard_positions);

    // Collect unconsumed fragments as AST nodes
    let mut result = Vec::new();
    for (pos, frag) in &fmap {
        if !consumed.contains(pos) {
            if let Some(ast) = frag.to_ast() {
                result.push(ast);
            }
        }
    }
    result
}
