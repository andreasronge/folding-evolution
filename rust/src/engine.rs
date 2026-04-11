/// Stable engine mechanics: adjacency graph, bond application, fragment map.
/// FragmentMap uses IndexMap to preserve insertion order (matching Python dict).
/// Adjacency uses Vec for deterministic neighbor ordering.

use rustc_hash::{FxHashMap, FxHashSet};
use indexmap::IndexMap;
use crate::fold::Pos;
use crate::chemistry::Fragment;

pub type FragmentMap = IndexMap<Pos, Fragment>;
pub type Adjacency = FxHashMap<Pos, Vec<Pos>>;

const NEIGHBORS: [(i32, i32); 8] = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
];

pub fn build_adjacency(grid: &crate::fold::Grid) -> Adjacency {
    let mut adj = Adjacency::default();
    for &pos in grid.keys() {
        let mut neighbors = Vec::new();
        for &(dx, dy) in &NEIGHBORS {
            let npos = (pos.0 + dx, pos.1 + dy);
            if grid.contains_key(&npos) {
                neighbors.push(npos);
            }
        }
        adj.insert(pos, neighbors);
    }
    adj
}

pub fn get_unconsumed_neighbors(
    pos: Pos,
    adj: &Adjacency,
    consumed: &FxHashSet<Pos>,
    fmap: &FragmentMap,
) -> Vec<(Pos, Fragment)> {
    let mut result = Vec::new();
    if let Some(neighbors) = adj.get(&pos) {
        for &npos in neighbors {
            if !consumed.contains(&npos) {
                if let Some(frag) = fmap.get(&npos) {
                    result.push((npos, frag.clone()));
                }
            }
        }
    }
    result
}

pub fn bond(
    fmap: &mut FragmentMap,
    adj: &mut Adjacency,
    consumed: &mut FxHashSet<Pos>,
    parent_pos: Pos,
    child_positions: &[Pos],
    assembled: Fragment,
) {
    fmap.insert(parent_pos, assembled);
    for &cp in child_positions {
        consumed.insert(cp);
    }

    let mut parent_neighbors: Vec<Pos> = adj
        .get(&parent_pos)
        .cloned()
        .unwrap_or_default();

    for &cp in child_positions {
        if let Some(child_adj) = adj.get(&cp) {
            for &neighbor in child_adj {
                if neighbor != parent_pos
                    && !child_positions.contains(&neighbor)
                    && !parent_neighbors.contains(&neighbor)
                {
                    parent_neighbors.push(neighbor);
                }
            }
        }
    }
    adj.insert(parent_pos, parent_neighbors.clone());

    for &neighbor in &parent_neighbors {
        if !consumed.contains(&neighbor) && neighbor != parent_pos {
            if let Some(neighbor_adj) = adj.get_mut(&neighbor) {
                if !neighbor_adj.contains(&parent_pos) {
                    neighbor_adj.push(parent_pos);
                }
                neighbor_adj.retain(|p| !child_positions.contains(p));
            }
        }
    }
}
