"""Decision-tree rule family.

A rule is a fixed-shape complete binary decision tree of depth D=5 over the
3x3 neighborhood window of each cell. Each internal node tests whether one
of the 9 window positions equals a specific state; the outcome routes to
either child. Leaves emit the next cell state.

Position indexing within the 3x3 window:
    0 = NW, 1 = N,  2 = NE
    3 = W,  4 = C,  5 = E
    6 = SW, 7 = S,  8 = SE

Genotype layout (94 bytes for D=5):
    - bytes [0..31):   pos for each of 31 internal nodes  (byte % 9)
    - bytes [31..62):  val for each of 31 internal nodes  (byte % K)
    - bytes [62..94):  output state for each of 32 leaves (byte % K)

Tree node indexing:
    - internal node i  (i in 0..30) → children (2i+1, 2i+2)
    - leaves have indices 31..62; leaf j at array index (31+j)
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


DEPTH = 5
N_INTERNAL = (1 << DEPTH) - 1      # 31
N_LEAVES = 1 << DEPTH              # 32
N_WINDOW = 9                       # 3x3 neighborhood
GENOTYPE_LEN = 2 * N_INTERNAL + N_LEAVES  # 62 + 32 = 94


@dataclass
class DecodedTree:
    """Decoded, per-rule arrays ready for the engine.

    For a batch of B rules:
        pos:    (B, N_INTERNAL) uint8, values in [0, 9)
        val:    (B, N_INTERNAL) uint8, values in [0, K)
        leaves: (B, N_LEAVES)   uint8, values in [0, K)
    """
    pos: np.ndarray
    val: np.ndarray
    leaves: np.ndarray


def genotype_len() -> int:
    return GENOTYPE_LEN


def random_genotype(n_states: int, rng: random.Random) -> np.ndarray:
    """Uniform byte draw — the decode step will mod to valid ranges."""
    return np.array(
        [rng.randrange(256) for _ in range(GENOTYPE_LEN)],
        dtype=np.uint8,
    )


def decode_one(genotype: np.ndarray, n_states: int) -> DecodedTree:
    """Decode a single genotype into pos/val/leaves arrays (shape prefix = ()))."""
    if genotype.size != GENOTYPE_LEN:
        raise ValueError(
            f"Genotype length {genotype.size} != expected {GENOTYPE_LEN}"
        )
    pos = (genotype[:N_INTERNAL] % N_WINDOW).astype(np.uint8)
    val = (genotype[N_INTERNAL:2 * N_INTERNAL] % n_states).astype(np.uint8)
    leaves = (genotype[2 * N_INTERNAL:] % n_states).astype(np.uint8)
    return DecodedTree(pos=pos, val=val, leaves=leaves)


def decode_batch(genotypes: list[np.ndarray], n_states: int) -> DecodedTree:
    """Decode a batch of genotypes into stacked pos/val/leaves arrays."""
    decoded = [decode_one(g, n_states) for g in genotypes]
    return DecodedTree(
        pos=np.stack([d.pos for d in decoded], axis=0),
        val=np.stack([d.val for d in decoded], axis=0),
        leaves=np.stack([d.leaves for d in decoded], axis=0),
    )


def mutate(
    genotype: np.ndarray,
    n_states: int,
    mutation_rate: float,
    rng: random.Random,
) -> np.ndarray:
    """Byte-level random-reset mutation. Matches outer-totalistic convention."""
    out = genotype.copy()
    for i in range(out.size):
        if rng.random() < mutation_rate:
            out[i] = rng.randrange(256)
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
