"""Phase-scheduled outer-totalistic rules.

A phased rule carries `n_phases` distinct outer-totalistic rule tables plus a
schedule vector of length `steps` that assigns each timestep to one of the
phases. At step t the engine applies the rule table indicated by
`schedule[t]`. `n_phases=1` reproduces the plain uniform CA (though with a
16-byte vestigial schedule field that always decodes to 0).

Theoretical motivation: Lee-Xu-Chau showed parity is exactly solvable by a
*sequence* of radius-1 rules even when no single one suffices — breaking the
stationary-rule constraint is a known mechanism for expanding CA
computational power.

Genotype layout (K=4 default, r=1):
    bytes [0 .. P*100):          P rule tables (each 100 bytes)
    bytes [P*100 .. P*100+T):    T schedule entries (each decoded mod P)

Total length = P * 100 + T at K=4/r=1, T=steps.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


def single_table_len(n_states: int) -> int:
    # K * (8*(K-1)+1) for radius=1; phased family uses r=1 only in this round.
    return n_states * (8 * (n_states - 1) + 1)


def genotype_len(n_states: int, n_phases: int, steps: int) -> int:
    return n_phases * single_table_len(n_states) + steps


@dataclass
class DecodedPhased:
    tables: np.ndarray      # (B, n_phases, K, max_sum+1) uint8
    schedule: np.ndarray    # (B, T) int8 (values in [0, n_phases))


def random_genotype(
    n_states: int,
    n_phases: int,
    steps: int,
    rng: random.Random,
) -> np.ndarray:
    """Uniform draw in [0, n_states). Schedule bytes are decoded mod n_phases."""
    length = genotype_len(n_states, n_phases, steps)
    return np.array(
        [rng.randrange(n_states) for _ in range(length)],
        dtype=np.uint8,
    )


def decode_one(
    genotype: np.ndarray,
    n_states: int,
    n_phases: int,
    steps: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (tables, schedule). tables: (P,K,max_sum+1) uint8; schedule: (T,) int8."""
    expected = genotype_len(n_states, n_phases, steps)
    if genotype.size != expected:
        raise ValueError(
            f"Genotype length {genotype.size} != expected {expected} "
            f"(K={n_states}, P={n_phases}, T={steps})"
        )
    tbl_len = single_table_len(n_states)
    tables = genotype[: n_phases * tbl_len].reshape(n_phases, n_states, 8 * (n_states - 1) + 1)
    schedule = (genotype[n_phases * tbl_len:] % n_phases).astype(np.int8)
    return tables.astype(np.uint8), schedule


def decode_batch(
    genotypes: list[np.ndarray],
    n_states: int,
    n_phases: int,
    steps: int,
) -> DecodedPhased:
    decoded = [decode_one(g, n_states, n_phases, steps) for g in genotypes]
    tables = np.stack([d[0] for d in decoded], axis=0)
    schedule = np.stack([d[1] for d in decoded], axis=0)
    return DecodedPhased(tables=tables, schedule=schedule)


def mutate(
    genotype: np.ndarray,
    n_states: int,
    mutation_rate: float,
    rng: random.Random,
) -> np.ndarray:
    """Per-byte random-reset mutation. Values resampled in [0, n_states);
    schedule bytes get decoded mod n_phases at use-time, so a uniform byte
    draw is the right distribution for both halves of the genotype.
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
    if parent_a.size != parent_b.size:
        raise ValueError("Parents must have equal length")
    if parent_a.size < 2:
        return parent_a.copy()
    point = rng.randint(1, parent_a.size - 1)
    child = np.empty_like(parent_a)
    child[:point] = parent_a[:point]
    child[point:] = parent_b[point:]
    return child
