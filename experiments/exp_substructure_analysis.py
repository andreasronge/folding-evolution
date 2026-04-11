"""
Substructure Frequency Analysis.

Scans programs (from evolved populations and random genotypes) for components
of the target filter program:

  L1: (get x :KEY)           -- accessor + field_key bond
  L2: (OP EXPR VALUE)        -- comparator with at least one assembled operand
  L3: (fn x EXPR)            -- fn wrapper around expression
  L4: (filter/map FN DATA)   -- higher-order with fn + data
  L5: (count/first COLL)     -- wrapper around assembled collection

Also detects combinations:
  L1+L2: comparator where one operand is a get-expression
  L2+L3: fn wrapping a comparator
  L3+L4: filter/map applied to fn

This tells us: are useful building blocks being discovered individually?
If so, where does the combination pipeline break?

Two analyses:
  A. Random genotype baseline: frequency of each substructure at various lengths
  B. Evolved population scan: run evolution on hard tasks, track substructure
     frequency over generations
"""

import random
import time
from collections import Counter, defaultdict
from typing import Any

from folding_evolution.alphabet import random_genotype
from folding_evolution.ast_nodes import ASTNode, Keyword, ListExpr, Literal, NsSymbol, Symbol
from folding_evolution.dynamics import partial_credit
from folding_evolution.fold import fold
from folding_evolution.chemistry import assemble
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, _count_bonds, ast_to_string
from folding_evolution.selection import tournament_select


# ---------------------------------------------------------------------------
# Substructure detection
# ---------------------------------------------------------------------------

def detect_substructures(node: ASTNode) -> dict[str, int]:
    """Walk an AST and count occurrences of each target substructure level.

    Returns dict mapping substructure name to count found in this AST.
    """
    counts: dict[str, int] = defaultdict(int)
    _walk(node, counts)
    return dict(counts)


def _walk(node: ASTNode, counts: dict[str, int]):
    """Recursive AST walker that detects substructure patterns."""
    if not isinstance(node, ListExpr) or not node.items:
        return

    head = node.items[0]
    head_name = head.name if isinstance(head, Symbol) else None

    # L1: (get x :KEY)
    if head_name == "get" and len(node.items) == 3:
        if isinstance(node.items[2], Keyword):
            counts["L1_get_field"] += 1

    # L2: (OP EXPR VALUE) where OP is comparator
    if head_name in (">", "<", "=", "+") and len(node.items) == 3:
        counts["L2_comparator"] += 1
        # Check if any operand is an assembled expression (not just literal/data)
        for operand in node.items[1:]:
            if isinstance(operand, ListExpr):
                counts["L2_comparator_with_assembled"] += 1
                break
        # L1+L2: comparator with a get-expression operand
        for operand in node.items[1:]:
            if _is_get_expr(operand):
                counts["L1L2_comparator_with_get"] += 1
                break

    # L3: (fn x EXPR)
    if head_name == "fn" and len(node.items) >= 3:
        counts["L3_fn_wrapper"] += 1
        body = node.items[2] if len(node.items) > 2 else None
        # L2+L3: fn wrapping a comparator
        if body and isinstance(body, ListExpr) and body.items:
            body_head = body.items[0]
            if isinstance(body_head, Symbol) and body_head.name in (">", "<", "="):
                counts["L2L3_fn_with_comparator"] += 1
                # L1+L2+L3: fn wrapping comparator with get
                for operand in body.items[1:]:
                    if _is_get_expr(operand):
                        counts["L1L2L3_fn_comparator_get"] += 1
                        break

    # L4: (filter/map FN DATA)
    if head_name in ("filter", "map", "reduce", "group_by") and len(node.items) >= 3:
        counts["L4_higher_order"] += 1
        fn_arg = node.items[1]
        # L3+L4: higher-order with fn argument
        if isinstance(fn_arg, ListExpr) and fn_arg.items:
            fn_head = fn_arg.items[0]
            if isinstance(fn_head, Symbol) and fn_head.name == "fn":
                counts["L3L4_higher_order_with_fn"] += 1
                # Check for the full chain: filter(fn(comparator(get)))
                if len(fn_arg.items) > 2:
                    body = fn_arg.items[2]
                    if isinstance(body, ListExpr) and body.items:
                        body_head = body.items[0]
                        if isinstance(body_head, Symbol) and body_head.name in (">", "<", "="):
                            counts["L1234_filter_fn_cmp"] += 1
                            for operand in body.items[1:]:
                                if _is_get_expr(operand):
                                    counts["L1234_filter_fn_cmp_get"] += 1
                                    break

    # L5: (count/first/rest/... ASSEMBLED)
    if head_name in ("count", "first", "reverse", "sort", "rest", "last") and len(node.items) >= 2:
        arg = node.items[1]
        if isinstance(arg, ListExpr):
            counts["L5_wrapper_assembled"] += 1
            # count(filter(...))
            if arg.items and isinstance(arg.items[0], Symbol) and arg.items[0].name in ("filter", "map"):
                counts["L5_count_filter"] += 1

    # Recurse into children
    for item in node.items:
        if isinstance(item, ListExpr):
            _walk(item, counts)


def _is_get_expr(node: ASTNode) -> bool:
    """Check if node is (get x :KEY)."""
    if isinstance(node, ListExpr) and len(node.items) == 3:
        head = node.items[0]
        return isinstance(head, Symbol) and head.name == "get" and isinstance(node.items[2], Keyword)
    return False


# All substructure names we track
ALL_SUBSTRUCT_NAMES = [
    "L1_get_field",
    "L2_comparator",
    "L2_comparator_with_assembled",
    "L1L2_comparator_with_get",
    "L3_fn_wrapper",
    "L2L3_fn_with_comparator",
    "L1L2L3_fn_comparator_get",
    "L4_higher_order",
    "L3L4_higher_order_with_fn",
    "L1234_filter_fn_cmp",
    "L1234_filter_fn_cmp_get",
    "L5_wrapper_assembled",
    "L5_count_filter",
]


# ---------------------------------------------------------------------------
# Analysis A: Random genotype baseline
# ---------------------------------------------------------------------------

def analyze_random(lengths=(50, 80, 100, 150), n_samples=50_000, seed=42):
    """Scan random genotypes for substructure frequencies."""
    print("=" * 70)
    print("Analysis A: Random Genotype Substructure Frequencies")
    print("=" * 70)

    for length in lengths:
        rng = random.Random(seed)
        # Count how many genotypes contain at least one of each substructure
        has_substruct: dict[str, int] = defaultdict(int)

        t0 = time.time()
        for _ in range(n_samples):
            g = random_genotype(length, rng=rng)
            prog = develop(g)
            if prog.ast is None:
                continue

            # Check ALL fragments, not just the best one
            grid, _ = fold(g)
            frags = assemble(grid)
            combined_counts: dict[str, int] = defaultdict(int)
            for frag in frags:
                sub = detect_substructures(frag)
                for k, v in sub.items():
                    combined_counts[k] += v

            for name in ALL_SUBSTRUCT_NAMES:
                if combined_counts.get(name, 0) > 0:
                    has_substruct[name] += 1

        elapsed = time.time() - t0

        print(f"\nLength {length} ({n_samples:,} genotypes, {elapsed:.1f}s):")
        print(f"  {'Substructure':<35s} | {'Count':>7s} | {'%':>6s}")
        print(f"  {'-'*35}-+-{'-'*7}-+-{'-'*6}")
        for name in ALL_SUBSTRUCT_NAMES:
            count = has_substruct.get(name, 0)
            pct = count / n_samples * 100
            bar = "#" * max(1, int(pct / 2))
            print(f"  {name:<35s} | {count:7d} | {pct:5.1f}% {bar}")


# ---------------------------------------------------------------------------
# Analysis B: Evolved population scan
# ---------------------------------------------------------------------------

def make_contexts():
    """Same discriminating contexts as other experiments."""
    from exp_structural_lexicase import make_contexts as _mc
    return _mc()


HARD_TARGETS = [
    ("count(filter(price>200, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 200])),
    ("count(filter(amount>300, orders))",
     lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 300])),
]

EASY_TARGETS = [
    ("count(products)", lambda ctx: len(ctx["products"])),
    ("count(rest(products))", lambda ctx: len(ctx["products"]) - 1),
]


def analyze_evolved(pop_size=100, genotype_length=100, generations=200,
                    n_seeds=5, seed_base=0):
    """Run evolution on hard tasks and track substructure frequency per generation."""
    print("\n" + "=" * 70)
    print("Analysis B: Evolved Population Substructure Frequencies")
    print("=" * 70)

    contexts = make_contexts()
    all_targets = EASY_TARGETS + HARD_TARGETS

    # Track substructure frequency across generations (averaged over seeds)
    gen_substruct: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for seed in range(n_seeds):
        rng = random.Random(seed_base + seed)
        develop.cache_clear()

        population = [
            Individual(genotype=random_genotype(genotype_length, rng))
            for _ in range(pop_size)
        ]

        print(f"\n  Seed {seed}:")

        for gen in range(generations):
            # Evaluate
            for ind in population:
                ind.program = develop(ind.genotype)
                # Multi-target partial credit
                if ind.program.ast is None:
                    ind.fitness = 0.0
                    continue
                gate = [repr(ind.program.evaluate(ctx)) for ctx in contexts]
                if len(set(gate)) <= 1:
                    ind.fitness = 0.0
                    continue
                scores = []
                for name, tfn in all_targets:
                    for ctx in contexts:
                        scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
                ind.fitness = sum(scores) / len(scores)

            # Substructure scan: check ALL fragments in ALL individuals
            pop_has: dict[str, int] = defaultdict(int)
            for ind in population:
                grid, _ = fold(ind.genotype)
                frags = assemble(grid)
                ind_counts: dict[str, int] = defaultdict(int)
                for frag in frags:
                    sub = detect_substructures(frag)
                    for k, v in sub.items():
                        ind_counts[k] += v
                for name in ALL_SUBSTRUCT_NAMES:
                    if ind_counts.get(name, 0) > 0:
                        pop_has[name] += 1

            # Record frequency (fraction of population)
            for name in ALL_SUBSTRUCT_NAMES:
                freq = pop_has.get(name, 0) / pop_size
                gen_substruct[gen][name].append(freq)

            # Print progress at key generations
            if gen in (0, 10, 25, 50, 100, 150, 199):
                best = max(population, key=lambda i: i.fitness)
                n_l1 = pop_has.get("L1_get_field", 0)
                n_l2l3 = pop_has.get("L2L3_fn_with_comparator", 0)
                n_l4 = pop_has.get("L3L4_higher_order_with_fn", 0)
                n_full = pop_has.get("L1234_filter_fn_cmp_get", 0)
                print(f"    Gen {gen:3d}: fit={best.fitness:.3f} "
                      f"L1(get)={n_l1} L2L3(fn+cmp)={n_l2l3} "
                      f"L3L4(filter+fn)={n_l4} full_chain={n_full} "
                      f"best={best.program.source}")

            # Reproduce
            children = []
            for _ in range(pop_size):
                if rng.random() < 0.7:
                    a = tournament_select(population, 3, rng)
                    b = tournament_select(population, 3, rng)
                    child_geno = crossover(a.genotype, b.genotype, rng)
                else:
                    parent = tournament_select(population, 3, rng)
                    child_geno = mutate(parent.genotype, rng)
                children.append(Individual(genotype=child_geno))

            for ind in children:
                ind.program = develop(ind.genotype)
                if ind.program.ast is None:
                    ind.fitness = 0.0
                    continue
                gate = [repr(ind.program.evaluate(ctx)) for ctx in contexts]
                if len(set(gate)) <= 1:
                    ind.fitness = 0.0
                    continue
                scores = []
                for name, tfn in all_targets:
                    for ctx in contexts:
                        scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
                ind.fitness = sum(scores) / len(scores)

            combined = population + children
            combined.sort(key=lambda i: i.fitness, reverse=True)
            population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    # Summary: average frequency over seeds at key generations
    print("\n" + "=" * 70)
    print("Substructure frequency over generations (avg across seeds)")
    print("=" * 70)

    key_gens = [0, 10, 25, 50, 100, 150, 199]
    key_names = [
        "L1_get_field", "L2_comparator", "L1L2_comparator_with_get",
        "L3_fn_wrapper", "L2L3_fn_with_comparator", "L1L2L3_fn_comparator_get",
        "L4_higher_order", "L3L4_higher_order_with_fn",
        "L1234_filter_fn_cmp", "L1234_filter_fn_cmp_get",
        "L5_wrapper_assembled", "L5_count_filter",
    ]

    # Header
    gen_header = "".join(f" Gen{g:>4d}" for g in key_gens)
    print(f"\n  {'Substructure':<35s} |{gen_header}")
    print(f"  {'-'*35}-+{'-'*len(gen_header)}")

    for name in key_names:
        vals = []
        for g in key_gens:
            if g in gen_substruct and name in gen_substruct[g]:
                avg = sum(gen_substruct[g][name]) / len(gen_substruct[g][name])
                vals.append(f"{avg*100:7.1f}%")
            else:
                vals.append(f"{'?':>7s}")
        print(f"  {name:<35s} | {''.join(vals)}")

    # Key diagnostic: does selection INCREASE or DECREASE each substructure?
    print("\n--- Trend: Gen 0 → Gen 199 (increase = building blocks being selected FOR) ---")
    for name in key_names:
        if 0 in gen_substruct and 199 in gen_substruct:
            g0 = gen_substruct[0][name]
            g199 = gen_substruct[199][name]
            avg0 = sum(g0) / len(g0) if g0 else 0
            avg199 = sum(g199) / len(g199) if g199 else 0
            delta = avg199 - avg0
            direction = "↑" if delta > 0.02 else "↓" if delta < -0.02 else "→"
            print(f"  {name:<35s}: {avg0*100:5.1f}% → {avg199*100:5.1f}%  {direction} ({delta*100:+.1f}%)")


def main():
    analyze_random()
    analyze_evolved()


if __name__ == "__main__":
    main()
