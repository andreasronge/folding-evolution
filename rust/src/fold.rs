/// Fold: walks a genotype string placing characters on a 2D grid.
/// Self-avoidance: when the next cell is occupied, try left, then right, then skip.
/// Uses IndexMap to preserve insertion order (matching Python dict behavior).

use indexmap::IndexMap;
use crate::types::*;
use crate::alphabet;

pub type Pos = (i32, i32);
pub type Grid = IndexMap<Pos, u8>;

pub fn fold(genotype: &[u8]) -> Grid {
    let mut grid = Grid::new();
    let mut pos: Pos = (0, 0);
    let mut direction = Direction::Right;

    for &ch in genotype {
        if let Some(placed_pos) = place_with_avoidance(&mut grid, pos, direction, ch) {
            let fold_instr = alphabet::fold_instruction(ch);
            direction = next_direction(direction, fold_instr);
            pos = direction.advance(placed_pos.0, placed_pos.1);
        } else {
            pos = direction.advance(pos.0, pos.1);
        }
    }

    grid
}

fn place_with_avoidance(grid: &mut Grid, pos: Pos, direction: Direction, ch: u8) -> Option<Pos> {
    if !grid.contains_key(&pos) {
        grid.insert(pos, ch);
        return Some(pos);
    }

    let left_dir = direction.turn_left();
    let left_pos = left_dir.advance(pos.0, pos.1);
    if !grid.contains_key(&left_pos) {
        grid.insert(left_pos, ch);
        return Some(left_pos);
    }

    let right_dir = direction.turn_right();
    let right_pos = right_dir.advance(pos.0, pos.1);
    if !grid.contains_key(&right_pos) {
        grid.insert(right_pos, ch);
        return Some(right_pos);
    }

    None
}

fn next_direction(direction: Direction, fold_instr: FoldInstruction) -> Direction {
    match fold_instr {
        FoldInstruction::Left => direction.turn_left(),
        FoldInstruction::Right => direction.turn_right(),
        FoldInstruction::Reverse => direction.reverse(),
        FoldInstruction::Straight => direction,
    }
}
