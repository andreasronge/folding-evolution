/// Fixed-size grid fold and neighbor lookup.
///
/// Replaces IndexMap<(i32,i32), u8> with a flat [u8; N*N] array.
/// Same fold algorithm (self-avoidance: try left, right, skip).

use crate::types::{Direction, FoldInstruction};
use crate::alphabet;

pub const GRID_N: usize = 32;
pub const GRID_SIZE: usize = GRID_N * GRID_N;
const GRID_CENTER: i32 = GRID_N as i32 / 2;

pub type FixedGrid = [u8; GRID_SIZE];

const DELTAS: [(i32, i32); 8] = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1,  1),
];

/// Pre-computed neighbor table: for each cell, list of valid neighbor indices.
pub struct NeighborTable {
    offsets: [u16; GRID_SIZE],  // start offset into `data`
    lengths: [u8; GRID_SIZE],
    data: Vec<u16>,
}

impl NeighborTable {
    pub fn new() -> Self {
        let mut offsets = [0u16; GRID_SIZE];
        let mut lengths = [0u8; GRID_SIZE];
        let mut data = Vec::with_capacity(GRID_SIZE * 8);

        for idx in 0..GRID_SIZE {
            let row = idx / GRID_N;
            let col = idx % GRID_N;
            offsets[idx] = data.len() as u16;
            let mut count = 0u8;
            for &(dx, dy) in &DELTAS {
                let nr = row as i32 + dy;
                let nc = col as i32 + dx;
                if nr >= 0 && nr < GRID_N as i32 && nc >= 0 && nc < GRID_N as i32 {
                    data.push((nr as usize * GRID_N + nc as usize) as u16);
                    count += 1;
                }
            }
            lengths[idx] = count;
        }

        NeighborTable { offsets, lengths, data }
    }

    #[inline]
    pub fn neighbors(&self, idx: usize) -> &[u16] {
        let start = self.offsets[idx] as usize;
        let len = self.lengths[idx] as usize;
        &self.data[start..start + len]
    }
}

/// Convert (x, y) world coordinates to grid index. Returns None if out of bounds.
#[inline]
fn pos_to_idx(x: i32, y: i32) -> Option<usize> {
    let col = x + GRID_CENTER;
    let row = y + GRID_CENTER;
    if col >= 0 && col < GRID_N as i32 && row >= 0 && row < GRID_N as i32 {
        Some(row as usize * GRID_N + col as usize)
    } else {
        None
    }
}

fn next_direction(direction: Direction, fold_instr: FoldInstruction) -> Direction {
    match fold_instr {
        FoldInstruction::Left => direction.turn_left(),
        FoldInstruction::Right => direction.turn_right(),
        FoldInstruction::Reverse => direction.reverse(),
        FoldInstruction::Straight => direction,
    }
}

/// Fold a genotype onto a fixed N×N grid.
/// Same algorithm as fold.rs but using array indexing instead of IndexMap.
/// Characters that fall outside the grid bounds are skipped.
pub fn fold_fixed(genotype: &[u8]) -> FixedGrid {
    let mut grid = [0u8; GRID_SIZE];
    let mut x: i32 = 0;
    let mut y: i32 = 0;
    let mut dir = Direction::Right;

    for &ch in genotype {
        // Try primary position
        if let Some(idx) = pos_to_idx(x, y) {
            if grid[idx] == 0 {
                grid[idx] = ch;
                let fold_instr = alphabet::fold_instruction(ch);
                dir = next_direction(dir, fold_instr);
                let (nx, ny) = dir.advance(x, y);
                x = nx;
                y = ny;
                continue;
            }
        }

        // Self-avoidance: try left
        let left_dir = dir.turn_left();
        let (lx, ly) = left_dir.advance(x, y);
        if let Some(idx) = pos_to_idx(lx, ly) {
            if grid[idx] == 0 {
                grid[idx] = ch;
                let fold_instr = alphabet::fold_instruction(ch);
                dir = next_direction(dir, fold_instr);
                let (nx, ny) = dir.advance(lx, ly);
                x = nx;
                y = ny;
                continue;
            }
        }

        // Self-avoidance: try right
        let right_dir = dir.turn_right();
        let (rx, ry) = right_dir.advance(x, y);
        if let Some(idx) = pos_to_idx(rx, ry) {
            if grid[idx] == 0 {
                grid[idx] = ch;
                let fold_instr = alphabet::fold_instruction(ch);
                dir = next_direction(dir, fold_instr);
                let (nx, ny) = dir.advance(rx, ry);
                x = nx;
                y = ny;
                continue;
            }
        }

        // Skip: can't place anywhere, advance in current direction
        let (nx, ny) = dir.advance(x, y);
        x = nx;
        y = ny;
    }

    grid
}

/// Count non-empty cells in the grid.
pub fn cell_count(grid: &FixedGrid) -> usize {
    grid.iter().filter(|&&ch| ch != 0).count()
}
