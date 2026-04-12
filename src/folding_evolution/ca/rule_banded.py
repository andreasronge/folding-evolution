"""Banded non-uniform outer-totalistic rules.

The grid's N rows are partitioned into `n_bands` contiguous horizontal bands;
each band carries its own outer-totalistic rule table. Cells in different
bands may respond differently to the same local neighborhood — breaking the
spatial uniformity of the base CA while keeping every other property the
same (same K, same 8-neighbor Moore stencil, same row-0 input clamp, same
readout convention).

Genotype layout (bytes, K=4 defaults):
    [ band_0 rule table | band_1 rule table | ... | band_{B-1} rule table ]
Each band's rule table is K × (8*(K-1)+1) = 100 bytes at K=4.
Total length = n_bands × 100 bytes (= 300 at n_bands=3, K=4).

Band boundaries for a grid with N rows and B bands:
    rows [round(i*N/B), round((i+1)*N/B)) belong to band i.
For N=16, B=3: rows 0..4 (band 0), 5..10 (band 1), 11..15 (band 2).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


def single_band_shape(n_states: int) -> tuple[int, int]:
    return (n_states, 8 * (n_states - 1) + 1)


def single_band_len(n_states: int) -> int:
    r, c = single_band_shape(n_states)
    return r * c


def genotype_len(n_states: int, n_bands: int) -> int:
    return n_bands * single_band_len(n_states)


def band_boundaries(grid_n: int, n_bands: int) -> np.ndarray:
    """Return an (n_bands+1,) int array of row boundaries for grid_n rows.

    Rows [boundaries[i], boundaries[i+1]) belong to band i. First boundary
    is always 0 and last is always grid_n.
    """
    return np.array(
        [int(round(i * grid_n / n_bands)) for i in range(n_bands + 1)],
        dtype=np.int64,
    )


def row_to_band(grid_n: int, n_bands: int) -> np.ndarray:
    """(grid_n,) int64 array: row_to_band[row] = band index that row belongs to."""
    bounds = band_boundaries(grid_n, n_bands)
    out = np.zeros((grid_n,), dtype=np.int64)
    for b in range(n_bands):
        out[bounds[b]:bounds[b + 1]] = b
    return out


@dataclass
class DecodedBanded:
    """Per-rule arrays ready for the engine.

    For a batch of B rules:
        tables: (B, n_bands, K, max_sum+1) uint8
    """
    tables: np.ndarray  # (B, n_bands, K, max_sum+1)


def random_genotype(n_states: int, n_bands: int, rng: random.Random) -> np.ndarray:
    length = genotype_len(n_states, n_bands)
    return np.array(
        [rng.randrange(n_states) for _ in range(length)],
        dtype=np.uint8,
    )


def decode_one(
    genotype: np.ndarray,
    n_states: int,
    n_bands: int,
) -> np.ndarray:
    """Decode a flat genotype into a (n_bands, K, max_sum+1) table array."""
    expected = genotype_len(n_states, n_bands)
    if genotype.size != expected:
        raise ValueError(
            f"Genotype length {genotype.size} != expected {expected} "
            f"(K={n_states}, n_bands={n_bands})"
        )
    shape = single_band_shape(n_states)
    per_band = shape[0] * shape[1]
    return genotype.reshape(n_bands, shape[0], shape[1]).astype(np.uint8)


def decode_batch(
    genotypes: list[np.ndarray],
    n_states: int,
    n_bands: int,
) -> DecodedBanded:
    stacks = [decode_one(g, n_states, n_bands) for g in genotypes]
    return DecodedBanded(tables=np.stack(stacks, axis=0))


def mutate(
    genotype: np.ndarray,
    n_states: int,
    mutation_rate: float,
    rng: random.Random,
) -> np.ndarray:
    """Per-byte random-reset mutation (same semantics as OT rule)."""
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
    if parent_a.size != parent_b.size:
        raise ValueError("Parents must have equal length")
    if parent_a.size < 2:
        return parent_a.copy()
    point = rng.randint(1, parent_a.size - 1)
    child = np.empty_like(parent_a)
    child[:point] = parent_a[:point]
    child[point:] = parent_b[point:]
    return child
