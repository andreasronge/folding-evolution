"""Rule-family dispatch + outer-totalistic rule encoding.

The `outer_totalistic` family keeps the original semantics: next state is a
function of (self, sum_of_8_neighbors). Genotype = rule table bytes.

Other families live in their own modules (e.g. `rule_decision_tree.py`).
Callers should use the family-agnostic helpers below; they route by
`cfg.rule_family`.

Genotype layout for outer-totalistic:
    Flat uint8 array of length K * (8*(K-1)+1), row-major (self, sum).
    Values already in [0, K).
"""

from __future__ import annotations

import random

import numpy as np

from .config import CAConfig
from . import rule_decision_tree as _dt
from . import rule_banded as _banded


# ---------------- Outer-totalistic helpers ----------------

def rule_shape(n_states: int) -> tuple[int, int]:
    return (n_states, 8 * (n_states - 1) + 1)


def rule_len(n_states: int) -> int:
    r, c = rule_shape(n_states)
    return r * c


def random_genotype(n_states: int, rng: random.Random) -> np.ndarray:
    """Sample a uniform-random outer-totalistic rule table as a flat uint8 genotype."""
    length = rule_len(n_states)
    return np.array(
        [rng.randrange(n_states) for _ in range(length)],
        dtype=np.uint8,
    )


def decode(genotype: np.ndarray, n_states: int) -> np.ndarray:
    """Reshape a flat outer-totalistic genotype into a (K, max_sum+1) table."""
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
    """Per-byte random-reset mutation for outer-totalistic rules."""
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
    """Single-point splice on the flat genotype (shared across families)."""
    if parent_a.size != parent_b.size:
        raise ValueError("Parents must have equal length")
    if parent_a.size < 2:
        return parent_a.copy()
    point = rng.randint(1, parent_a.size - 1)
    child = np.empty_like(parent_a)
    child[:point] = parent_a[:point]
    child[point:] = parent_b[point:]
    return child


# ---------------- Family-agnostic dispatch ----------------

def random_genotype_for(cfg: CAConfig, rng: random.Random) -> np.ndarray:
    fam = cfg.rule_family
    if fam == "outer_totalistic":
        return random_genotype(cfg.n_states, rng)
    if fam == "decision_tree":
        return _dt.random_genotype(cfg.n_states, rng)
    if fam == "banded_ot":
        return _banded.random_genotype(cfg.n_states, cfg.n_bands, rng)
    raise ValueError(f"Unknown rule_family {fam!r}")


def mutate_for(
    genotype: np.ndarray,
    cfg: CAConfig,
    rng: random.Random,
) -> np.ndarray:
    fam = cfg.rule_family
    if fam == "outer_totalistic":
        return mutate(genotype, cfg.n_states, cfg.mutation_rate, rng)
    if fam == "decision_tree":
        return _dt.mutate(genotype, cfg.n_states, cfg.mutation_rate, rng)
    if fam == "banded_ot":
        return _banded.mutate(genotype, cfg.n_states, cfg.mutation_rate, rng)
    raise ValueError(f"Unknown rule_family {fam!r}")


def crossover_for(
    parent_a: np.ndarray,
    parent_b: np.ndarray,
    cfg: CAConfig,
    rng: random.Random,
) -> np.ndarray:
    # Same byte-level splice works for all families; keep single implementation.
    return crossover(parent_a, parent_b, rng)


def genotype_len(cfg: CAConfig) -> int:
    fam = cfg.rule_family
    if fam == "outer_totalistic":
        return rule_len(cfg.n_states)
    if fam == "decision_tree":
        return _dt.genotype_len()
    if fam == "banded_ot":
        return _banded.genotype_len(cfg.n_states, cfg.n_bands)
    raise ValueError(f"Unknown rule_family {fam!r}")
