"""Genetic operators for genotype strings.

Operates on the genotype string directly. The folding process creates the
non-linear mapping to phenotype, so simple string operations can have
complex phenotypic effects.
"""

from __future__ import annotations

import random

from .alphabet import ALPHABET


def point_mutation(genotype: str, rng: random.Random) -> str:
    """Flip one character to a random character from ALPHABET."""
    if not genotype:
        return genotype
    pos = rng.randrange(len(genotype))
    chars = list(genotype)
    chars[pos] = rng.choice(ALPHABET)
    return "".join(chars)


def insertion(genotype: str, rng: random.Random) -> str:
    """Insert a random character at a random position."""
    pos = rng.randrange(len(genotype) + 1)
    char = rng.choice(ALPHABET)
    return genotype[:pos] + char + genotype[pos:]


def deletion(genotype: str, rng: random.Random) -> str:
    """Delete a character at a random position (min length 1)."""
    if len(genotype) <= 1:
        return point_mutation(genotype, rng)
    pos = rng.randrange(len(genotype))
    return genotype[:pos] + genotype[pos + 1:]


def mutate(genotype: str, rng: random.Random) -> str:
    """Apply a random mutation (point, insertion, or deletion)."""
    op = rng.choice([point_mutation, insertion, deletion])
    return op(genotype, rng)


def crossover(parent_a: str, parent_b: str, rng: random.Random) -> str:
    """Single-point splice: cut A at random pos, cut B at random pos, join head_A + tail_B."""
    cut_a = rng.randrange(1, len(parent_a)) if len(parent_a) > 1 else 1
    cut_b = rng.randrange(1, len(parent_b)) if len(parent_b) > 1 else 1
    return parent_a[:cut_a] + parent_b[cut_b:]
