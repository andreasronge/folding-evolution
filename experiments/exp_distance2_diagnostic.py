"""
Quick diagnostic: what happens when we allow distance-2 bonds?

Modifies the adjacency graph to include neighbors at Manhattan distance 2
(16 additional neighbors per position). Measures impact on bond count
distribution and phenotype diversity compared to the standard distance-1 chemistry.

This validates whether spatial constraint is a limiting factor before
investing in the full evolvable chemistry system.
"""

import random
import time
from collections import Counter

from folding_evolution.alphabet import random_genotype
from folding_evolution.fold import fold
from folding_evolution.chemistry import assemble, _build_adjacency, _NEIGHBORS
from folding_evolution.phenotype import _count_bonds, ast_to_string, Program
from folding_evolution.ast_nodes import ASTNode, ListExpr
from folding_evolution.evaluator import evaluate


# Distance-2 neighbor offsets (all positions within Chebyshev distance 2, minus distance-1)
_NEIGHBORS_D2 = [
    (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
    (-2, -1),                                (2, -1),
    (-2,  0),                                (2,  0),
    (-2,  1),                                (2,  1),
    (-2,  2), (-1,  2), (0,  2), (1,  2), (2,  2),
]


def build_adjacency_d2(grid):
    """Build adjacency graph including distance-2 neighbors."""
    positions = grid.keys()
    result = {}
    for pos in positions:
        x, y = pos
        neighbors = []
        # Distance 1 (standard)
        for dx, dy in _NEIGHBORS:
            npos = (x + dx, y + dy)
            if npos in positions:
                neighbors.append(npos)
        # Distance 2
        for dx, dy in _NEIGHBORS_D2:
            npos = (x + dx, y + dy)
            if npos in positions:
                neighbors.append(npos)
        result[pos] = neighbors
    return result


def assemble_d2(grid):
    """Run chemistry with distance-2 adjacency."""
    # We need to monkey-patch the adjacency builder
    # Instead, replicate the assemble logic with our adjacency
    from folding_evolution.alphabet import to_fragment
    from folding_evolution.chemistry import (
        _pass_leaf_bonds, _pass_predicate_bonds, _pass_structural_bonds,
        _pass_composition_bonds, _pass_conditional_bonds,
    )

    adjacency = build_adjacency_d2(grid)

    fragment_map = {}
    for pos, char in grid.items():
        frag = to_fragment(char)
        if frag != "spacer":
            fragment_map[pos] = frag

    wildcard_positions = {pos for pos, frag in fragment_map.items() if frag == "wildcard"}
    consumed = set()

    fragment_map, consumed, adjacency = _pass_leaf_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_predicate_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_structural_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_composition_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_conditional_bonds(
        fragment_map, adjacency, consumed, wildcard_positions
    )

    from folding_evolution.chemistry import _fragment_to_ast
    result = []
    for pos, frag in fragment_map.items():
        if pos not in consumed:
            ast = _fragment_to_ast(frag)
            if ast is not None:
                result.append(ast)
    return result


def develop_d2(genotype):
    """Full pipeline with distance-2 chemistry."""
    grid, placements = fold(genotype)
    if not grid:
        return Program(ast=None, source=None, bond_count=0, evaluate=lambda ctx: None)

    fragments = assemble_d2(grid)
    if not fragments:
        return Program(ast=None, source=None, bond_count=0, evaluate=lambda ctx: None)
    ast = max(fragments, key=_count_bonds)
    bond_count = _count_bonds(ast)
    source = ast_to_string(ast)

    def eval_fn(ctx):
        return evaluate(ast, ctx)

    return Program(ast=ast, source=source, bond_count=bond_count, evaluate=eval_fn)


def compare_bond_distributions(lengths=(50, 80, 100, 150), n_samples=50_000, seed=42):
    """Compare bond-count distributions: standard vs distance-2 chemistry."""
    print("=" * 70)
    print("Distance-2 Bond Diagnostic")
    print("=" * 70)

    from folding_evolution.phenotype import develop

    for length in lengths:
        rng = random.Random(seed)
        d1_counts = Counter()
        d2_counts = Counter()
        d1_max = 0
        d2_max = 0
        d2_max_src = ""
        d2_max_geno = ""

        # Count how often d2 produces MORE bonds than d1
        more_bonds = 0
        fewer_bonds = 0
        same_bonds = 0

        t0 = time.time()
        for _ in range(n_samples):
            g = random_genotype(length, rng=rng)

            p1 = develop(g)
            p2 = develop_d2(g)

            bc1 = p1.bond_count
            bc2 = p2.bond_count
            d1_counts[bc1] += 1
            d2_counts[bc2] += 1

            if bc1 > d1_max:
                d1_max = bc1
            if bc2 > d2_max:
                d2_max = bc2
                d2_max_src = p2.source
                d2_max_geno = g

            if bc2 > bc1:
                more_bonds += 1
            elif bc2 < bc1:
                fewer_bonds += 1
            else:
                same_bonds += 1

        elapsed = time.time() - t0

        d1_avg = sum(k * v for k, v in d1_counts.items()) / n_samples
        d2_avg = sum(k * v for k, v in d2_counts.items()) / n_samples
        d1_4plus = sum(v for k, v in d1_counts.items() if k >= 4) / n_samples * 100
        d2_4plus = sum(v for k, v in d2_counts.items() if k >= 4) / n_samples * 100
        d1_6plus = sum(v for k, v in d1_counts.items() if k >= 6) / n_samples * 100
        d2_6plus = sum(v for k, v in d2_counts.items() if k >= 6) / n_samples * 100

        print(f"\nLength {length} ({n_samples:,} samples, {elapsed:.1f}s):")
        print(f"  {'':20s} | {'Standard (d1)':>14s} | {'Distance-2 (d2)':>16s} | {'Delta':>8s}")
        print(f"  {'-'*20}-+-{'-'*14}-+-{'-'*16}-+-{'-'*8}")
        print(f"  {'Avg bonds':20s} | {d1_avg:14.2f} | {d2_avg:16.2f} | {d2_avg-d1_avg:+8.2f}")
        print(f"  {'Max bonds':20s} | {d1_max:14d} | {d2_max:16d} | {d2_max-d1_max:+8d}")
        print(f"  {'4+ bonds %':20s} | {d1_4plus:13.1f}% | {d2_4plus:15.1f}% | {d2_4plus-d1_4plus:+7.1f}%")
        print(f"  {'6+ bonds %':20s} | {d1_6plus:13.1f}% | {d2_6plus:15.1f}% | {d2_6plus-d1_6plus:+7.1f}%")
        print(f"  {'d2 > d1':20s} | {more_bonds/n_samples*100:13.1f}%")
        print(f"  {'d2 < d1':20s} | {fewer_bonds/n_samples*100:13.1f}%")
        print(f"  {'d2 == d1':20s} | {same_bonds/n_samples*100:13.1f}%")

        if d2_max_src and len(d2_max_src) < 100:
            print(f"  Best d2: {d2_max} bonds: {d2_max_src}")

    # Test on golden genotype
    print(f"\n{'='*70}")
    print("Golden genotype comparison")
    print(f"{'='*70}")
    from folding_evolution.phenotype import develop
    golden = "QDaK5XASBw"
    p1 = develop(golden)
    p2 = develop_d2(golden)
    print(f"  Standard:   {p1.bond_count} bonds: {p1.source}")
    print(f"  Distance-2: {p2.bond_count} bonds: {p2.source}")

    # Mutation robustness comparison
    print(f"\n{'='*70}")
    print("Mutation robustness: golden genotype (610 single-char mutations)")
    print(f"{'='*70}")
    from folding_evolution.alphabet import ALPHABET
    d1_mut_counts = Counter()
    d2_mut_counts = Counter()
    for pos in range(len(golden)):
        for char in ALPHABET:
            if char == golden[pos]:
                continue
            mutant = golden[:pos] + char + golden[pos + 1:]
            m1 = develop(mutant)
            m2 = develop_d2(mutant)
            d1_mut_counts[m1.bond_count] += 1
            d2_mut_counts[m2.bond_count] += 1

    print(f"  {'Bonds':>5s} | {'Standard':>8s} | {'Distance-2':>10s}")
    print(f"  {'-'*5}-+-{'-'*8}-+-{'-'*10}")
    all_bcs = sorted(set(d1_mut_counts.keys()) | set(d2_mut_counts.keys()))
    for bc in all_bcs:
        print(f"  {bc:5d} | {d1_mut_counts.get(bc, 0):8d} | {d2_mut_counts.get(bc, 0):10d}")


if __name__ == "__main__":
    compare_bond_distributions()
