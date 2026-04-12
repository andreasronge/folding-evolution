"""Outer-totalistic CA rule encoding.

Genotype = rule table bytes. For K states and 8 neighbors, the max neighbor sum
is 8*(K-1), so the table shape is (K, 8*(K-1)+1). Each entry ∈ [0, K).

Indexing:
    next_state = rule_table[self_state, sum_of_8_neighbors]

Genotype layout: flat uint8 array, length K * (8*(K-1)+1), row-major (self, sum).
Values are already in [0, K) — no separate validity step.
"""

from __future__ import annotations

import random

import numpy as np


def rule_shape(n_states: int) -> tuple[int, int]:
    return (n_states, 8 * (n_states - 1) + 1)


def rule_len(n_states: int) -> int:
    r, c = rule_shape(n_states)
    return r * c


def random_genotype(n_states: int, rng: random.Random) -> np.ndarray:
    """Sample a uniform-random rule table as a flat uint8 genotype."""
    length = rule_len(n_states)
    return np.array(
        [rng.randrange(n_states) for _ in range(length)],
        dtype=np.uint8,
    )


def decode(genotype: np.ndarray, n_states: int) -> np.ndarray:
    """Reshape a flat genotype into a 2-D rule table of shape (K, max_sum+1)."""
    shape = rule_shape(n_states)
    expected = shape[0] * shape[1]
    if genotype.size != expected:
        raise ValueError(
            f"Genotype length {genotype.size} does not match K={n_states} "
            f"(expected {expected})"
        )
    return genotype.reshape(shape).astype(np.uint8)


def mutate(
    genotype: np.ndarray,
    n_states: int,
    mutation_rate: float,
    rng: random.Random,
) -> np.ndarray:
    """Per-byte random-reset mutation.

    Each byte is independently replaced with a uniform random [0, K) draw
    with probability mutation_rate. Returns a new array (does not modify input).
    """
    out = genotype.copy()
    for i in range(out.size):
        if rng.random() < mutation_rate:
            out[i] = rng.randrange(n_states)
    return out


def crossover(
    parent_a: np.ndarray,
    parent_b: np.ndarray,
    rng: random.Random,
) -> np.ndarray:
    """Single-point splice on the flat genotype."""
    if parent_a.size != parent_b.size:
        raise ValueError("Parents must have equal length")
    if parent_a.size < 2:
        return parent_a.copy()
    point = rng.randint(1, parent_a.size - 1)
    child = np.empty_like(parent_a)
    child[:point] = parent_a[:point]
    child[point:] = parent_b[point:]
    return child
