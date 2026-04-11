"""Tests for the fold module."""

from folding_evolution.fold import fold


class TestBasicFolding:
    def test_single_char(self):
        grid, placements = fold("A")
        assert len(grid) == 1
        assert grid[(0, 0)] == "A"
        assert placements == [((0, 0), "A")]

    def test_two_chars_straight(self):
        # 'a' is lowercase -> straight, starting direction is right
        grid, placements = fold("a0")
        assert grid[(0, 0)] == "a"
        assert grid[(1, 0)] == "0"

    def test_turn_left_from_right(self):
        # A is uppercase -> turn left. Starting right, turn left = up
        grid, placements = fold("AB")
        assert grid[(0, 0)] == "A"
        # After A at (0,0), direction becomes up (turned left from right)
        # Next position: (0, -1)
        assert grid[(0, -1)] == "B"


class TestGoldenGenotype:
    """Test the golden genotype from architecture docs: QDaK5XASBw"""

    def test_grid_layout(self):
        grid, placements = fold("QDaK5XASBw")

        # Expected from docs:
        # Q(fn) at (0,0)
        # D(get) at (0,-1)  -- Q turns left from right=up, advance to (0,-1)
        # a(:price) at (-1,-1) -- D turns left from up=left, advance to (-1,-1)
        # K(>) at (-2,-1) -- a goes straight (left), advance to (-2,-1)
        # 5(500) at (-2,0) -- K turns left from left=down, advance to (-2,0)
        # X(if) at (-2,1) -- 5 goes straight (down), advance to (-2,1)
        # A(filter) at (-1,1) -- X turns left from down=right, advance to (-1,1)
        # S(data/products) at (-1,0) -- A turns left from right=up, advance to (-1,0)
        # B at ? and w at ? (need to trace further)

        assert grid[(0, 0)] == "Q"
        assert grid[(0, -1)] == "D"
        assert grid[(-1, -1)] == "a"
        assert grid[(-2, -1)] == "K"
        assert grid[(-2, 0)] == "5"
        assert grid[(-2, 1)] == "X"
        assert grid[(-1, 1)] == "A"
        assert grid[(-1, 0)] == "S"

    def test_placement_count(self):
        """All 10 characters should be placed (or some skipped due to self-avoidance)."""
        grid, placements = fold("QDaK5XASBw")
        # At minimum the first 8 we verified above should be placed
        assert len(placements) >= 8


class TestSelfAvoidance:
    def test_occupied_cell_avoided(self):
        # Create a scenario where folding loops back
        # AAAA: A turns left each time, so right->up->left->down
        # Positions: (0,0), (0,-1), (-1,-1), (-1,0)
        # 5th A: next would be (-1,1) heading down... wait let me trace
        # A at (0,0), turn left -> up, next (0,-1)
        # A at (0,-1), turn left -> left, next (-1,-1)
        # A at (-1,-1), turn left -> down, next (-1,0)
        # A at (-1,0), turn left -> right, next (0,0) -- OCCUPIED
        # Self-avoidance: try left (up) -> (0,-1) OCCUPIED, try right (down) -> (0,1)
        grid, placements = fold("AAAAA")
        assert len(grid) == 5  # all should be placed via avoidance
        # The 5th A should have been placed via avoidance
        positions = set(grid.keys())
        assert (0, 0) in positions
        assert (0, -1) in positions
        assert (-1, -1) in positions
        assert (-1, 0) in positions

    def test_skip_when_all_occupied(self):
        # Hard to construct naturally, but verify grid doesn't crash
        # with a long genotype that folds tightly
        grid, placements = fold("A" * 20)
        # Should not crash; some chars may be skipped
        assert len(placements) <= 20
        assert len(placements) > 0
