"""Banded-phased outer-totalistic rules.

Combines spatial specialization (§11.a banded_ot — different rule per row-band)
with temporal specialization (§11.b phased_ot — different rule per timestep).
Each (band, phase) cell of the rule table is a full K×(max_sum+1) OT rule.

At timestep t, cells in band b apply `tables[schedule[t], b]`.

Genotype layout (K=4, n_bands=B, n_phases=P, steps=T):
    bytes [0 .. P*B*100):          P*B rule tables (each 100 bytes)
    bytes [P*B*100 .. P*B*100+T):  schedule — T entries decoded mod P

Total length = P * B * 100 + T at K=4, r=1.

Mutation/crossover are byte-level; schedule bytes get decoded mod n_phases.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


def single_table_len(n_states: int) -> int:
    return n_states * (8 * (n_states - 1) + 1)


def genotype_len(n_states: int, n_phases: int, n_bands: int, steps: int) -> int:
    return n_phases * n_bands * single_table_len(n_states) + steps


@dataclass
class DecodedBandedPhased:
    tables: np.ndarray      # (B, n_phases, n_bands, K, max_sum+1) uint8
    schedule: np.ndarray    # (B, T) int8 (values in [0, n_phases))


def random_genotype(
    n_states: int,
    n_phases: int,
    n_bands: int,
    steps: int,
    rng: random.Random,
) -> np.ndarray:
    length = genotype_len(n_states, n_phases, n_bands, steps)
    return np.array(
        [rng.randrange(n_states) for _ in range(length)],
        dtype=np.uint8,
    )


def decode_one(
    genotype: np.ndarray,
    n_states: int,
    n_phases: int,
    n_bands: int,
    steps: int,
) -> tuple[np.ndarray, np.ndarray]:
    expected = genotype_len(n_states, n_phases, n_bands, steps)
    if genotype.size != expected:
        raise ValueError(
            f"Genotype length {genotype.size} != expected {expected}"
        )
    tbl_len = single_table_len(n_states)
    total_tables = n_phases * n_bands
    tables_flat = genotype[: total_tables * tbl_len]
    tables = tables_flat.reshape(
        n_phases, n_bands, n_states, 8 * (n_states - 1) + 1
    ).astype(np.uint8)
    schedule = (genotype[total_tables * tbl_len:] % n_phases).astype(np.int8)
    return tables, schedule


def decode_batch(
    genotypes: list[np.ndarray],
    n_states: int,
    n_phases: int,
    n_bands: int,
    steps: int,
) -> DecodedBandedPhased:
    decoded = [decode_one(g, n_states, n_phases, n_bands, steps) for g in genotypes]
    tables = np.stack([d[0] for d in decoded], axis=0)
    schedule = np.stack([d[1] for d in decoded], axis=0)
    return DecodedBandedPhased(tables=tables, schedule=schedule)


def mutate(
    genotype: np.ndarray,
    n_states: int,
    mutation_rate: float,
    rng: random.Random,
) -> np.ndarray:
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
