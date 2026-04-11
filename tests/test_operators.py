"""Tests for genetic operators."""

import random

from folding_evolution.alphabet import ALPHABET
from folding_evolution.operators import (
    crossover,
    deletion,
    insertion,
    mutate,
    point_mutation,
)


def test_point_mutation_changes_one_char():
    rng = random.Random(42)
    original = "ABCDEF"
    mutated = point_mutation(original, rng)
    assert len(mutated) == len(original)
    diffs = sum(1 for a, b in zip(original, mutated) if a != b)
    assert diffs == 1


def test_point_mutation_deterministic():
    result1 = point_mutation("ABCDEF", random.Random(99))
    result2 = point_mutation("ABCDEF", random.Random(99))
    assert result1 == result2


def test_insertion_adds_one_char():
    rng = random.Random(42)
    original = "ABCDEF"
    result = insertion(original, rng)
    assert len(result) == len(original) + 1


def test_insertion_deterministic():
    result1 = insertion("ABCDEF", random.Random(99))
    result2 = insertion("ABCDEF", random.Random(99))
    assert result1 == result2


def test_deletion_removes_one_char():
    rng = random.Random(42)
    original = "ABCDEF"
    result = deletion(original, rng)
    assert len(result) == len(original) - 1


def test_deletion_min_length():
    rng = random.Random(42)
    result = deletion("A", rng)
    assert len(result) == 1  # Falls back to point mutation


def test_deletion_deterministic():
    result1 = deletion("ABCDEF", random.Random(99))
    result2 = deletion("ABCDEF", random.Random(99))
    assert result1 == result2


def test_mutate_picks_random_op():
    rng = random.Random(42)
    original = "ABCDEF"
    result = mutate(original, rng)
    assert result != original or len(result) != len(original)


def test_crossover_produces_offspring():
    rng = random.Random(42)
    a = "AAAAAA"
    b = "BBBBBB"
    child = crossover(a, b, rng)
    assert len(child) > 0
    assert child.startswith("A")  # Head from A
    assert "B" in child  # Tail from B


def test_crossover_deterministic():
    result1 = crossover("ABCDEF", "GHIJKL", random.Random(99))
    result2 = crossover("ABCDEF", "GHIJKL", random.Random(99))
    assert result1 == result2


def test_all_mutations_produce_valid_alphabet():
    rng = random.Random(42)
    genotype = "ABCDEFGHIJ"
    for _ in range(100):
        result = mutate(genotype, rng)
        for ch in result:
            assert ch in ALPHABET, f"Invalid char '{ch}' in mutated genotype"
