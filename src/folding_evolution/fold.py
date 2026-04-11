"""Fold: walks a genotype string placing characters on a 2D grid.

Each character's fold instruction determines the direction of the next step.
Self-avoidance: when the next cell is occupied, try left, then right, then skip.
"""

from __future__ import annotations

from .alphabet import fold_instruction

Position = tuple[int, int]
Direction = str  # "up" | "down" | "left" | "right"
Grid = dict[Position, str]


def fold(genotype: str) -> tuple[Grid, list[tuple[Position, str]]]:
    """Fold a genotype string onto a 2D grid.

    Returns (grid, placements) where grid maps (x, y) -> character,
    and placements is an ordered list of (position, char) tuples.
    """
    grid: Grid = {}
    placements: list[tuple[Position, str]] = []
    pos: Position = (0, 0)
    direction: Direction = "right"

    for char in genotype:
        result = _place_with_avoidance(grid, pos, direction, char)
        if result is not None:
            placed_pos, grid = result
            placements.append((placed_pos, char))
            direction = _next_direction(direction, char)
            pos = _advance(placed_pos, direction)
        else:
            # Skip: can't place anywhere
            pos = _advance(pos, direction)

    return grid, placements


def _place_with_avoidance(
    grid: Grid, pos: Position, direction: Direction, char: str
) -> tuple[Position, Grid] | None:
    """Try to place char at pos; if occupied try left, right, then skip."""
    if pos not in grid:
        new_grid = {**grid, pos: char}
        return pos, new_grid

    # Try left
    left_dir = _turn_left(direction)
    left_pos = _advance(pos, left_dir)
    if left_pos not in grid:
        new_grid = {**grid, left_pos: char}
        return left_pos, new_grid

    # Try right
    right_dir = _turn_right(direction)
    right_pos = _advance(pos, right_dir)
    if right_pos not in grid:
        new_grid = {**grid, right_pos: char}
        return right_pos, new_grid

    return None


def _next_direction(direction: Direction, char: str) -> Direction:
    """Compute next direction from current direction and character's fold instruction."""
    instr = fold_instruction(char)
    if instr == "left":
        return _turn_left(direction)
    if instr == "right":
        return _turn_right(direction)
    if instr == "reverse":
        return _reverse(direction)
    return direction  # straight


def _advance(pos: Position, direction: Direction) -> Position:
    """Move one step in the given direction."""
    x, y = pos
    if direction == "right":
        return (x + 1, y)
    if direction == "left":
        return (x - 1, y)
    if direction == "up":
        return (x, y - 1)
    if direction == "down":
        return (x, y + 1)
    return pos


def _turn_left(direction: Direction) -> Direction:
    return {"right": "up", "up": "left", "left": "down", "down": "right"}[direction]


def _turn_right(direction: Direction) -> Direction:
    return {"right": "down", "down": "left", "left": "up", "up": "right"}[direction]


def _reverse(direction: Direction) -> Direction:
    return {"right": "left", "left": "right", "up": "down", "down": "up"}[direction]
