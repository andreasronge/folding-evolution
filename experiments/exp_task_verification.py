"""
Task Verification Profiler: empirically determine the minimum bond count
needed to achieve high fitness on each candidate task.

For each task x length combination:
  1. Generate 100K random genotypes
  2. Develop each (genotype → program via folding)
  3. Evaluate program on the task's contexts using partial credit
  4. Group by bond count, report max/avg fitness per tier

This answers: "does task X genuinely require 5 bonds, or can a 3-bond
program score 0.9 by accident?"
"""

import random
import time
from collections import defaultdict
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.dynamics import partial_credit
from folding_evolution.phenotype import develop


# ---------------------------------------------------------------------------
# Richer evaluation contexts for filter/predicate tasks
# ---------------------------------------------------------------------------
# Prices use multiples that cross literal thresholds (100, 200, ..., 900).
# Collection sizes vary across contexts so count tasks are data-dependent.
# Department and status values vary so field-comparison tasks are meaningful.

def make_rich_contexts() -> list[dict]:
    """Contexts designed for tasks requiring filtering and field comparison."""
    return [
        {
            "products": [
                {"id": 1, "price": 50, "name": "widget", "status": "active", "category": "tools"},
                {"id": 2, "price": 250, "name": "gadget", "status": "active", "category": "tech"},
                {"id": 3, "price": 450, "name": "gizmo", "status": "inactive", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "alice", "department": "eng", "employee_id": 101},
                {"id": 2, "name": "bob", "department": "sales", "employee_id": 102},
            ],
            "orders": [
                {"id": 1, "amount": 150},
                {"id": 2, "amount": 350},
            ],
            "expenses": [
                {"id": 1, "amount": 75, "category": "travel"},
                {"id": 2, "amount": 225, "category": "equipment"},
                {"id": 3, "amount": 550, "category": "travel"},
            ],
        },
        {
            "products": [
                {"id": 1, "price": 150, "name": "alpha", "status": "active", "category": "tech"},
                {"id": 2, "price": 350, "name": "beta", "status": "active", "category": "tech"},
                {"id": 3, "price": 550, "name": "gamma", "status": "inactive", "category": "food"},
                {"id": 4, "price": 750, "name": "delta", "status": "active", "category": "tools"},
                {"id": 5, "price": 950, "name": "epsilon", "status": "active", "category": "tech"},
            ],
            "employees": [
                {"id": 1, "name": "carol", "department": "eng", "employee_id": 201},
                {"id": 2, "name": "dave", "department": "eng", "employee_id": 202},
                {"id": 3, "name": "eve", "department": "hr", "employee_id": 203},
                {"id": 4, "name": "frank", "department": "sales", "employee_id": 204},
            ],
            "employees": [
                {"id": 1, "name": "carol", "department": "eng", "employee_id": 201},
                {"id": 2, "name": "dave", "department": "eng", "employee_id": 202},
                {"id": 3, "name": "eve", "department": "hr", "employee_id": 203},
                {"id": 4, "name": "frank", "department": "sales", "employee_id": 204},
            ],
            "orders": [
                {"id": 1, "amount": 50},
                {"id": 2, "amount": 250},
                {"id": 3, "amount": 450},
                {"id": 4, "amount": 650},
            ],
            "expenses": [
                {"id": 1, "amount": 100, "category": "equipment"},
                {"id": 2, "amount": 400, "category": "travel"},
            ],
        },
        {
            "products": [
                {"id": 1, "price": 100, "name": "uno", "status": "inactive", "category": "food"},
                {"id": 2, "price": 300, "name": "dos", "status": "active", "category": "tools"},
                {"id": 3, "price": 600, "name": "tres", "status": "active", "category": "tech"},
                {"id": 4, "price": 800, "name": "cuatro", "status": "active", "category": "tech"},
            ],
            "employees": [
                {"id": 1, "name": "grace", "department": "eng", "employee_id": 301},
                {"id": 2, "name": "heidi", "department": "eng", "employee_id": 302},
                {"id": 3, "name": "ivan", "department": "eng", "employee_id": 303},
            ],
            "orders": [
                {"id": 1, "amount": 200},
            ],
            "expenses": [
                {"id": 1, "amount": 300, "category": "equipment"},
                {"id": 2, "amount": 600, "category": "travel"},
                {"id": 3, "amount": 150, "category": "supplies"},
                {"id": 4, "amount": 800, "category": "equipment"},
            ],
        },
        {
            "products": [
                {"id": 1, "price": 200, "name": "pA", "status": "active", "category": "tools"},
                {"id": 2, "price": 400, "name": "pB", "status": "inactive", "category": "food"},
                {"id": 3, "price": 500, "name": "pC", "status": "active", "category": "tech"},
                {"id": 4, "price": 700, "name": "pD", "status": "active", "category": "tech"},
                {"id": 5, "price": 850, "name": "pE", "status": "active", "category": "tools"},
                {"id": 6, "price": 100, "name": "pF", "status": "inactive", "category": "food"},
            ],
            "employees": [
                {"id": 1, "name": "judy", "department": "sales", "employee_id": 401},
            ],
            "orders": [
                {"id": 1, "amount": 100},
                {"id": 2, "amount": 300},
                {"id": 3, "amount": 500},
            ],
            "expenses": [
                {"id": 1, "amount": 200, "category": "travel"},
            ],
        },
        {
            "products": [
                {"id": 1, "price": 350, "name": "x1", "status": "active", "category": "tech"},
                {"id": 2, "price": 650, "name": "x2", "status": "active", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "kate", "department": "hr", "employee_id": 501},
                {"id": 2, "name": "leo", "department": "eng", "employee_id": 502},
                {"id": 3, "name": "mia", "department": "eng", "employee_id": 503},
                {"id": 4, "name": "ned", "department": "sales", "employee_id": 504},
                {"id": 5, "name": "olivia", "department": "eng", "employee_id": 505},
            ],
            "orders": [
                {"id": 1, "amount": 700},
                {"id": 2, "amount": 800},
                {"id": 3, "amount": 50},
                {"id": 4, "amount": 400},
                {"id": 5, "amount": 150},
            ],
            "expenses": [
                {"id": 1, "amount": 450, "category": "travel"},
                {"id": 2, "amount": 100, "category": "supplies"},
                {"id": 3, "amount": 350, "category": "equipment"},
                {"id": 4, "amount": 700, "category": "travel"},
                {"id": 5, "amount": 250, "category": "supplies"},
            ],
        },
    ]


# ---------------------------------------------------------------------------
# Candidate tasks at various intended complexity tiers
# ---------------------------------------------------------------------------
# Each task: (name, intended_bonds, target_fn, description)

CANDIDATE_TASKS: list[tuple[str, int, Callable[[dict], Any], str]] = [
    # --- Tier 1: 1-2 bonds ---
    (
        "count(products)",
        2,
        lambda ctx: len(ctx["products"]),
        "(count data/products)",
    ),
    (
        "count(employees)",
        2,
        lambda ctx: len(ctx["employees"]),
        "(count data/employees)",
    ),
    (
        "first(products)",
        2,
        lambda ctx: ctx["products"][0] if ctx["products"] else None,
        "(first data/products)",
    ),

    # --- Tier 2: 2-3 bonds ---
    (
        "count(rest(products))",
        3,
        lambda ctx: len(ctx["products"]) - 1,
        "(count (rest data/products))",
    ),
    (
        "count(rest(rest(employees)))",
        3,
        lambda ctx: max(0, len(ctx["employees"]) - 2),
        "(count (rest (rest data/employees)))",
    ),

    # --- Tier 3: 4 bonds ---
    # filter requires: filter + fn + predicate(comparator + get + field + literal) + data
    (
        "filter(price>200, products)",
        4,
        lambda ctx: [p for p in ctx["products"] if p["price"] > 200],
        "(filter (fn x (> (get x :price) 200)) data/products)",
    ),
    (
        "filter(price>500, products)",
        4,
        lambda ctx: [p for p in ctx["products"] if p["price"] > 500],
        "(filter (fn x (> (get x :price) 500)) data/products)",
    ),

    # --- Tier 4: 5 bonds ---
    (
        "count(filter(price>200, products))",
        5,
        lambda ctx: len([p for p in ctx["products"] if p["price"] > 200]),
        "(count (filter (fn x (> (get x :price) 200)) data/products))",
    ),
    (
        "count(filter(price>500, products))",
        5,
        lambda ctx: len([p for p in ctx["products"] if p["price"] > 500]),
        "(count (filter (fn x (> (get x :price) 500)) data/products))",
    ),
    (
        "count(filter(amount>200, expenses))",
        5,
        lambda ctx: len([e for e in ctx["expenses"] if e["amount"] > 200]),
        "(count (filter (fn x (> (get x :amount) 200)) data/expenses))",
    ),
    (
        "first(filter(price>200, products))",
        5,
        lambda ctx: next((p for p in ctx["products"] if p["price"] > 200), None),
        "(first (filter (fn x (> (get x :price) 200)) data/products))",
    ),

    # --- Tier 5: 6+ bonds ---
    (
        "count(filter(price>200, products)) + count(employees)",
        6,
        lambda ctx: len([p for p in ctx["products"] if p["price"] > 200]) + len(ctx["employees"]),
        "(+ (count (filter ...)) (count data/employees))",
    ),
    (
        "count(map(get-price, filter(price>200, products)))",
        7,
        lambda ctx: len([p["price"] for p in ctx["products"] if p["price"] > 200]),
        "(count (map (fn x (get x :price)) (filter ...)))",
    ),
]


def evaluate_task(program, target_fn, contexts):
    """Evaluate a program on a task using partial credit, with data-dependence gate."""
    if program.ast is None:
        return 0.0

    outputs = []
    scores = []
    for ctx in contexts:
        result = program.evaluate(ctx)
        expected = target_fn(ctx)
        outputs.append(repr(result))
        scores.append(partial_credit(result, expected))

    # Data-dependence gate
    if len(set(outputs)) <= 1:
        return 0.0

    return sum(scores) / len(scores) if scores else 0.0


def profile_task(
    task_name: str,
    intended_bonds: int,
    target_fn: Callable[[dict], Any],
    description: str,
    contexts: list[dict],
    lengths: tuple[int, ...] = (50, 80, 100, 150),
    n_samples: int = 100_000,
    seed: int = 42,
):
    """Profile a single task: what fitness is achievable at each bond count?"""

    # Show expected outputs for sanity check
    print(f"\n{'='*70}")
    print(f"Task: {task_name} (intended {intended_bonds} bonds)")
    print(f"  Program: {description}")
    expected = [target_fn(ctx) for ctx in contexts]
    print(f"  Expected outputs: {expected}")

    for length in lengths:
        rng = random.Random(seed)
        # bond_count -> list of fitness scores
        tier_scores: dict[int, list[float]] = defaultdict(list)
        tier_max_source: dict[int, tuple[float, str, str]] = {}  # bond -> (fitness, source, genotype)

        t0 = time.time()
        for _ in range(n_samples):
            g = random_genotype(length, rng=rng)
            p = develop(g)
            fitness = evaluate_task(p, target_fn, contexts)
            bc = p.bond_count

            tier_scores[bc].append(fitness)
            if bc not in tier_max_source or fitness > tier_max_source[bc][0]:
                tier_max_source[bc] = (fitness, p.source or "(nil)", g)

        elapsed = time.time() - t0

        # Aggregate results
        print(f"\n  Length {length} ({n_samples:,} samples, {elapsed:.1f}s):")
        print(f"  {'Bonds':>5s} | {'Count':>7s} | {'Max fit':>7s} | {'Avg fit':>7s} | {'Pct>0':>6s} | {'Pct>0.5':>7s} | Best program")
        print(f"  {'-'*5}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*6}-+-{'-'*7}-+--{'--'*20}")

        for bc in sorted(tier_scores.keys()):
            scores = tier_scores[bc]
            count = len(scores)
            max_f = max(scores)
            avg_f = sum(scores) / count
            pct_nonzero = sum(1 for s in scores if s > 0) / count * 100
            pct_half = sum(1 for s in scores if s > 0.5) / count * 100
            best_src = tier_max_source[bc][1]
            # Truncate long sources
            if len(best_src) > 60:
                best_src = best_src[:57] + "..."
            print(f"  {bc:5d} | {count:7d} | {max_f:7.3f} | {avg_f:7.4f} | {pct_nonzero:5.1f}% | {pct_half:6.1f}% | {best_src}")

        # Summary line: min bond count needed for >0.8 and >0.95 fitness
        threshold_80 = None
        threshold_95 = None
        for bc in sorted(tier_scores.keys()):
            max_f = max(tier_scores[bc])
            if max_f > 0.8 and threshold_80 is None:
                threshold_80 = bc
            if max_f > 0.95 and threshold_95 is None:
                threshold_95 = bc

        print(f"\n  Min bonds for max_fitness > 0.8: {threshold_80 if threshold_80 is not None else 'NONE'}")
        print(f"  Min bonds for max_fitness > 0.95: {threshold_95 if threshold_95 is not None else 'NONE'}")

        # Show best program at the threshold
        if threshold_95 is not None and threshold_95 in tier_max_source:
            f, src, geno = tier_max_source[threshold_95]
            print(f"  Best at threshold: {src}")
            print(f"    fitness={f:.3f}, genotype={geno}")


def main():
    contexts = make_rich_contexts()

    print("Task Verification Profiler")
    print("=" * 70)
    print(f"Contexts: {len(contexts)} (collection sizes vary)")
    print(f"Context product counts: {[len(c['products']) for c in contexts]}")
    print(f"Context employee counts: {[len(c['employees']) for c in contexts]}")

    # Use fewer samples for quick run, override with full 100K for final
    n_samples = 100_000
    lengths = (50, 100, 150)

    for name, intended, target_fn, desc in CANDIDATE_TASKS:
        profile_task(
            name, intended, target_fn, desc,
            contexts, lengths=lengths, n_samples=n_samples,
        )

    print("\n" + "=" * 70)
    print("SUMMARY: Verified difficulty tiers")
    print("=" * 70)
    print("\nA task is 'verified tier N' if the minimum bond count to achieve")
    print(">0.8 max fitness at length 100 is N or higher.\n")

    # Quick re-run for summary table
    print(f"{'Task':<42s} | {'Intended':>8s} | Verified (length 100)")
    print(f"{'-'*42}-+-{'-'*8}-+--{'-'*25}")

    for name, intended, target_fn, desc in CANDIDATE_TASKS:
        rng = random.Random(42)
        tier_max: dict[int, float] = defaultdict(float)
        for _ in range(n_samples):
            g = random_genotype(100, rng=rng)
            p = develop(g)
            fitness = evaluate_task(p, target_fn, contexts)
            bc = p.bond_count
            if fitness > tier_max[bc]:
                tier_max[bc] = fitness

        verified_80 = None
        for bc in sorted(tier_max.keys()):
            if tier_max[bc] > 0.8:
                verified_80 = bc
                break

        label = f"{verified_80}" if verified_80 is not None else "NONE"
        match = "✓" if verified_80 is not None and verified_80 >= intended else "✗ (easier)"
        print(f"{name:<42s} | {intended:>8d} | {label:>4s} bonds {match}")


if __name__ == "__main__":
    main()
