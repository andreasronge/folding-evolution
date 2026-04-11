"""DevGenome: evolvable chemistry parameters.

Controls how the folding chemistry assembles programs from the 2D grid.
Population-level: one DevGenome shared by all individuals, mutated slowly.

The key idea: the fold is fixed (gives geometry), but the chemistry rules
that determine which fragments bond are parameterized and evolvable.

Design: compatibility families define which fragment types CAN bond.
Within allowed families, affinity weights control HOW STRONGLY they bond.
Disallowed pairs are permanently zero.
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Fragment families: grouping of raw fragment types
# ---------------------------------------------------------------------------
# Each character in the genotype maps to a fragment type (via alphabet.py).
# We group these into families for the compatibility mask.

FAMILY_ACCESSOR = "ACC"       # get, assoc
FAMILY_FIELD_KEY = "FLD"      # price, status, department, id, name, amount, category, employee_id
FAMILY_COMPARATOR = "CMP"     # +, >, <, =
FAMILY_HIGHER_ORDER = "HOR"   # filter, map, reduce, group_by
FAMILY_WRAPPER = "WRP"        # count, first, reverse, sort, rest, last
FAMILY_CONNECTIVE = "CON"     # and, or, not
FAMILY_CONTROL = "CTL"        # if, match
FAMILY_FN_MAKER = "FNM"       # fn, let
FAMILY_DATA_SOURCE = "DAT"    # products, employees, orders, expenses
FAMILY_LITERAL = "LIT"        # 0, 100, ..., 900
FAMILY_STRUCTURAL = "STR"     # set, contains?
FAMILY_WILDCARD = "WLD"       # wildcards (m-z)
FAMILY_SPACER = "SPC"         # Z spacer

ALL_FAMILIES = [
    FAMILY_ACCESSOR, FAMILY_FIELD_KEY, FAMILY_COMPARATOR,
    FAMILY_HIGHER_ORDER, FAMILY_WRAPPER, FAMILY_CONNECTIVE,
    FAMILY_CONTROL, FAMILY_FN_MAKER, FAMILY_DATA_SOURCE,
    FAMILY_LITERAL, FAMILY_STRUCTURAL, FAMILY_WILDCARD, FAMILY_SPACER,
]

# Map from (fragment_kind, fragment_name) to family
_FRAGMENT_TO_FAMILY: dict[str | tuple, str] = {
    ("fn_fragment", "get"): FAMILY_ACCESSOR,
    ("fn_fragment", "assoc"): FAMILY_ACCESSOR,
    ("fn_fragment", "filter"): FAMILY_HIGHER_ORDER,
    ("fn_fragment", "map"): FAMILY_HIGHER_ORDER,
    ("fn_fragment", "reduce"): FAMILY_HIGHER_ORDER,
    ("fn_fragment", "group_by"): FAMILY_HIGHER_ORDER,
    ("fn_fragment", "count"): FAMILY_WRAPPER,
    ("fn_fragment", "first"): FAMILY_WRAPPER,
    ("fn_fragment", "reverse"): FAMILY_WRAPPER,
    ("fn_fragment", "sort"): FAMILY_WRAPPER,
    ("fn_fragment", "rest"): FAMILY_WRAPPER,
    ("fn_fragment", "last"): FAMILY_WRAPPER,
    ("fn_fragment", "fn"): FAMILY_FN_MAKER,
    ("fn_fragment", "let"): FAMILY_FN_MAKER,
    ("fn_fragment", "set"): FAMILY_STRUCTURAL,
    ("fn_fragment", "contains?"): FAMILY_STRUCTURAL,
    ("fn_fragment", "if"): FAMILY_CONTROL,
    ("fn_fragment", "match"): FAMILY_CONTROL,
    ("comparator", "+"): FAMILY_COMPARATOR,
    ("comparator", ">"): FAMILY_COMPARATOR,
    ("comparator", "<"): FAMILY_COMPARATOR,
    ("comparator", "="): FAMILY_COMPARATOR,
    ("connective", "and"): FAMILY_CONNECTIVE,
    ("connective", "or"): FAMILY_CONNECTIVE,
    ("connective", "not"): FAMILY_CONNECTIVE,
    ("data_source", "products"): FAMILY_DATA_SOURCE,
    ("data_source", "employees"): FAMILY_DATA_SOURCE,
    ("data_source", "orders"): FAMILY_DATA_SOURCE,
    ("data_source", "expenses"): FAMILY_DATA_SOURCE,
    "wildcard": FAMILY_WILDCARD,
    "spacer": FAMILY_SPACER,
}

# Field keys and literals are matched by kind prefix
_FAMILY_BY_KIND: dict[str, str] = {
    "field_key": FAMILY_FIELD_KEY,
    "literal": FAMILY_LITERAL,
}


def fragment_family(frag) -> str:
    """Map a fragment (as returned by alphabet.to_fragment) to its family."""
    if isinstance(frag, tuple) and len(frag) == 2:
        # Check exact match first
        if frag in _FRAGMENT_TO_FAMILY:
            return _FRAGMENT_TO_FAMILY[frag]
        # Then check by kind
        kind = frag[0]
        if kind in _FAMILY_BY_KIND:
            return _FAMILY_BY_KIND[kind]
    if isinstance(frag, str):
        return _FRAGMENT_TO_FAMILY.get(frag, FAMILY_SPACER)
    return FAMILY_SPACER


# ---------------------------------------------------------------------------
# Compatibility mask: which family pairs can form bonds
# ---------------------------------------------------------------------------
# These define the STRUCTURE of allowed interactions.
# Weights within allowed pairs are evolvable. Disallowed pairs stay at 0.
#
# The mask captures raw-fragment interactions. Assembled products from
# earlier passes are always available to later passes (controlled by
# assembled_preference weight).

# Allowed pair -> initial affinity weight
# Symmetric: (A, B) implies (B, A)
DEFAULT_AFFINITIES: dict[tuple[str, str], float] = {
    # Pass 1: Leaf bonds
    (FAMILY_ACCESSOR, FAMILY_FIELD_KEY): 1.0,    # get + field_key
    (FAMILY_ACCESSOR, FAMILY_LITERAL): 0.8,      # assoc value
    (FAMILY_ACCESSOR, FAMILY_DATA_SOURCE): 0.8,  # assoc value

    # Pass 2: Predicate bonds
    (FAMILY_COMPARATOR, FAMILY_LITERAL): 1.0,      # > 500
    (FAMILY_COMPARATOR, FAMILY_DATA_SOURCE): 0.8,  # > data/products (unusual but valid)
    (FAMILY_FN_MAKER, FAMILY_LITERAL): 0.6,        # fn wrapping a literal (weak)

    # Pass 3: Structural bonds
    (FAMILY_HIGHER_ORDER, FAMILY_DATA_SOURCE): 1.0,  # filter + data
    (FAMILY_WRAPPER, FAMILY_DATA_SOURCE): 1.0,       # count + data

    # Pass 4: Composition bonds
    (FAMILY_CONNECTIVE, FAMILY_LITERAL): 0.7,        # and/or with literal
    (FAMILY_STRUCTURAL, FAMILY_DATA_SOURCE): 0.9,    # set(data)

    # Pass 5: Conditional bonds
    (FAMILY_CONTROL, FAMILY_LITERAL): 0.6,     # if with literal branch
    (FAMILY_CONTROL, FAMILY_WILDCARD): 0.5,    # match with wildcard
}


def _symmetrize(affinities: dict[tuple[str, str], float]) -> dict[tuple[str, str], float]:
    """Ensure the affinity dict is symmetric."""
    result = dict(affinities)
    for (a, b), w in list(affinities.items()):
        if (b, a) not in result:
            result[(b, a)] = w
    return result


# The full mask: which pairs are allowed to have non-zero affinity
ALLOWED_PAIRS: frozenset[tuple[str, str]] = frozenset(
    (a, b) for a, b in _symmetrize(DEFAULT_AFFINITIES)
)


# ---------------------------------------------------------------------------
# DevGenome dataclass
# ---------------------------------------------------------------------------

@dataclass
class DevGenome:
    """Evolvable chemistry parameters.

    Controls bond formation, spatial reach, assembly behavior.
    Population-level: one per population, mutated slowly.
    """

    # Bond affinities: only for allowed family pairs (sparse)
    # Key: (family_a, family_b), Value: affinity weight [0, 2]
    affinities: dict[tuple[str, str], float]

    # How strongly assembled products from earlier passes are preferred
    # over raw fragments as bond partners. Multiplier on affinity.
    # Current behavior: assembled > literal > data_source (hard priority)
    # With DevGenome: assembled gets affinity * assembled_preference
    assembled_preference: float

    # Distance decay: weights for distance-1 and distance-2 neighbors
    # distance_weights[0] for Chebyshev distance 1 (8-connected)
    # distance_weights[1] for Chebyshev distance 2 (16 additional)
    distance_weights: tuple[float, float]

    # Minimum effective affinity for a bond to form
    bond_threshold: float

    # Stability bonus for formed subassemblies.
    # Higher = assembled modules resist disruption by later passes.
    # Effective cost to consume an assembled product = stability_bonus * its bond_count
    stability_bonus: float

    # Occupancy penalty: reduce affinity for fragments that already
    # participated in bond attempts this pass (steric hindrance).
    # Effective affinity *= (1 - occupancy_penalty * attempt_count)
    occupancy_penalty: float

    # Assembly greediness: how many candidate bonds to consider per position.
    # 1 = current greedy (take first valid), higher = evaluate more options
    top_k: int


def default_dev_genome() -> DevGenome:
    """Create a DevGenome matching current hard-coded chemistry behavior.

    With these defaults, the parameterized chemistry should produce
    identical results to the existing code.
    """
    return DevGenome(
        affinities=_symmetrize(dict(DEFAULT_AFFINITIES)),
        assembled_preference=2.0,
        distance_weights=(1.0, 0.0),  # d1 only, no d2
        bond_threshold=0.5,
        stability_bonus=0.0,    # no stability (matches current greedy)
        occupancy_penalty=0.0,  # no penalty (matches current behavior)
        top_k=1,                # greedy (matches current behavior)
    )


def mutate_dev_genome(
    dg: DevGenome,
    rng: random.Random,
    sigma: float = 0.05,
) -> DevGenome:
    """Mutate a DevGenome with gaussian noise on continuous params.

    Each parameter is perturbed independently with probability 0.3.
    Values are clamped to valid ranges.
    """
    new_affinities = {}
    for pair, weight in dg.affinities.items():
        if rng.random() < 0.3:
            new_w = weight + rng.gauss(0, sigma)
            new_affinities[pair] = max(0.0, min(2.0, new_w))
        else:
            new_affinities[pair] = weight

    def _maybe_mutate(val: float, lo: float, hi: float) -> float:
        if rng.random() < 0.3:
            return max(lo, min(hi, val + rng.gauss(0, sigma)))
        return val

    new_d1 = _maybe_mutate(dg.distance_weights[0], 0.0, 2.0)
    new_d2 = _maybe_mutate(dg.distance_weights[1], 0.0, 1.0)

    new_top_k = dg.top_k
    if rng.random() < 0.1:  # rare mutation
        new_top_k = max(1, min(5, dg.top_k + rng.choice([-1, 1])))

    return DevGenome(
        affinities=new_affinities,
        assembled_preference=_maybe_mutate(dg.assembled_preference, 0.5, 5.0),
        distance_weights=(new_d1, new_d2),
        bond_threshold=_maybe_mutate(dg.bond_threshold, 0.1, 1.5),
        stability_bonus=_maybe_mutate(dg.stability_bonus, 0.0, 2.0),
        occupancy_penalty=_maybe_mutate(dg.occupancy_penalty, 0.0, 1.0),
        top_k=new_top_k,
    )


# ---------------------------------------------------------------------------
# Chemistry metrics: measure the dev genome as a phenotype
# ---------------------------------------------------------------------------

def dev_genome_metrics(dg: DevGenome) -> dict[str, float]:
    """Compute summary metrics for a DevGenome."""
    aff_values = list(dg.affinities.values())
    nonzero = [v for v in aff_values if v > 0.01]

    return {
        "affinity_count": len(aff_values),
        "affinity_nonzero": len(nonzero),
        "affinity_mean": sum(aff_values) / len(aff_values) if aff_values else 0,
        "affinity_max": max(aff_values) if aff_values else 0,
        "affinity_sparsity": 1.0 - len(nonzero) / len(aff_values) if aff_values else 1.0,
        "distance_d1_weight": dg.distance_weights[0],
        "distance_d2_weight": dg.distance_weights[1],
        "assembled_preference": dg.assembled_preference,
        "bond_threshold": dg.bond_threshold,
        "stability_bonus": dg.stability_bonus,
        "occupancy_penalty": dg.occupancy_penalty,
        "top_k": float(dg.top_k),
    }
