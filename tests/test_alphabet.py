"""Tests for the alphabet module."""

import random

from folding_evolution.alphabet import (
    ALPHABET,
    fold_instruction,
    random_genotype,
    to_fragment,
)


class TestFragmentMapping:
    def test_functions(self):
        assert to_fragment("A") == ("fn_fragment", "filter")
        assert to_fragment("B") == ("fn_fragment", "count")
        assert to_fragment("C") == ("fn_fragment", "map")
        assert to_fragment("D") == ("fn_fragment", "get")
        assert to_fragment("E") == ("fn_fragment", "reduce")
        assert to_fragment("F") == ("fn_fragment", "group_by")
        assert to_fragment("G") == ("fn_fragment", "set")
        assert to_fragment("H") == ("fn_fragment", "contains?")
        assert to_fragment("I") == ("fn_fragment", "first")

    def test_comparators(self):
        assert to_fragment("J") == ("comparator", "+")
        assert to_fragment("K") == ("comparator", ">")
        assert to_fragment("L") == ("comparator", "<")
        assert to_fragment("M") == ("comparator", "=")

    def test_connectives(self):
        assert to_fragment("N") == ("connective", "and")
        assert to_fragment("O") == ("connective", "or")
        assert to_fragment("P") == ("connective", "not")

    def test_function_wrappers(self):
        assert to_fragment("Q") == ("fn_fragment", "fn")
        assert to_fragment("R") == ("fn_fragment", "let")

    def test_data_sources(self):
        assert to_fragment("S") == ("data_source", "products")
        assert to_fragment("T") == ("data_source", "employees")
        assert to_fragment("U") == ("data_source", "orders")
        assert to_fragment("V") == ("data_source", "expenses")

    def test_structural(self):
        assert to_fragment("W") == ("fn_fragment", "match")
        assert to_fragment("X") == ("fn_fragment", "if")
        assert to_fragment("Y") == ("fn_fragment", "assoc")

    def test_spacer(self):
        assert to_fragment("Z") == "spacer"

    def test_field_keys(self):
        assert to_fragment("a") == ("field_key", "price")
        assert to_fragment("b") == ("field_key", "status")
        assert to_fragment("c") == ("field_key", "department")
        assert to_fragment("d") == ("field_key", "id")
        assert to_fragment("e") == ("field_key", "name")
        assert to_fragment("f") == ("field_key", "amount")
        assert to_fragment("g") == ("field_key", "category")
        assert to_fragment("h") == ("field_key", "employee_id")

    def test_collection_functions(self):
        assert to_fragment("i") == ("fn_fragment", "reverse")
        assert to_fragment("j") == ("fn_fragment", "sort")
        assert to_fragment("k") == ("fn_fragment", "rest")
        assert to_fragment("l") == ("fn_fragment", "last")

    def test_wildcards(self):
        for c in "mnopqrstuvwxyz":
            assert to_fragment(c) == "wildcard"

    def test_digits(self):
        assert to_fragment("0") == ("literal", 0)
        assert to_fragment("1") == ("literal", 100)
        assert to_fragment("5") == ("literal", 500)
        assert to_fragment("9") == ("literal", 900)

    def test_unknown_char(self):
        assert to_fragment("!") == "spacer"


class TestFoldInstruction:
    def test_uppercase_turn_left(self):
        for c in "ABCDEFGHIJKLMNOPQRSTUV":
            assert fold_instruction(c) == "left", f"Expected left for {c}"

    def test_w_straight(self):
        assert fold_instruction("W") == "straight"

    def test_x_turn_left(self):
        assert fold_instruction("X") == "left"

    def test_y_turn_right(self):
        assert fold_instruction("Y") == "right"

    def test_z_reverse(self):
        assert fold_instruction("Z") == "reverse"

    def test_lowercase_straight(self):
        for c in "abcdefghijklmnopqrstuvwxyz":
            assert fold_instruction(c) == "straight", f"Expected straight for {c}"

    def test_digits_straight(self):
        for c in "0123456789":
            assert fold_instruction(c) == "straight", f"Expected straight for {c}"


class TestRandomGenotype:
    def test_length(self):
        g = random_genotype(10)
        assert len(g) == 10

    def test_all_chars_valid(self):
        g = random_genotype(100)
        for c in g:
            assert c in ALPHABET

    def test_deterministic_with_seed(self):
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        assert random_genotype(20, rng1) == random_genotype(20, rng2)

    def test_alphabet_size(self):
        assert len(ALPHABET) == 62
