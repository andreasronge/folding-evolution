"""
Task Verification Profiler (STRICT): exact-match scoring only.

The partial-credit profiler showed that lenient scoring lets simple programs
score 0.85 on tasks "intended" for 5+ bonds. This version uses exact match
to find the true minimum bond count needed to solve each task.

Also uses 8 contexts (not 5) to reduce accidental correlations, with data
values chosen to maximize divergence between simple and complex computations.
"""

import random
import time
from collections import defaultdict
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.phenotype import develop


def make_discriminating_contexts() -> list[dict]:
    """8 contexts designed to maximize divergence between task complexities.

    Key design: collection sizes and price distributions are chosen so that
    count(products) != count(filter(price>X, products)) != count(rest(products))
    across ALL contexts.
    """
    return [
        {  # 3 products, 1 with price > 200, 0 with price > 500
            "products": [
                {"id": 1, "price": 50, "name": "p1", "status": "active", "category": "tools"},
                {"id": 2, "price": 120, "name": "p2", "status": "inactive", "category": "tech"},
                {"id": 3, "price": 350, "name": "p3", "status": "active", "category": "food"},
            ],
            "employees": [
                {"id": 1, "name": "a1", "department": "eng", "employee_id": 101},
                {"id": 2, "name": "a2", "department": "sales", "employee_id": 102},
                {"id": 3, "name": "a3", "department": "eng", "employee_id": 103},
                {"id": 4, "name": "a4", "department": "hr", "employee_id": 104},
                {"id": 5, "name": "a5", "department": "eng", "employee_id": 105},
            ],
            "orders": [{"id": 1, "amount": 150}, {"id": 2, "amount": 350}],
            "expenses": [
                {"id": 1, "amount": 75, "category": "travel"},
                {"id": 2, "amount": 225, "category": "equipment"},
                {"id": 3, "amount": 550, "category": "travel"},
            ],
        },
        {  # 6 products, 4 with price > 200, 2 with price > 500
            "products": [
                {"id": 1, "price": 80, "name": "q1", "status": "active", "category": "tech"},
                {"id": 2, "price": 190, "name": "q2", "status": "active", "category": "food"},
                {"id": 3, "price": 310, "name": "q3", "status": "inactive", "category": "tools"},
                {"id": 4, "price": 450, "name": "q4", "status": "active", "category": "tech"},
                {"id": 5, "price": 620, "name": "q5", "status": "active", "category": "food"},
                {"id": 6, "price": 780, "name": "q6", "status": "inactive", "category": "tech"},
            ],
            "employees": [
                {"id": 1, "name": "b1", "department": "sales", "employee_id": 201},
                {"id": 2, "name": "b2", "department": "eng", "employee_id": 202},
            ],
            "orders": [{"id": 1, "amount": 50}, {"id": 2, "amount": 250}, {"id": 3, "amount": 900}],
            "expenses": [{"id": 1, "amount": 400, "category": "equipment"}],
        },
        {  # 2 products, 2 with price > 200, 1 with price > 500
            "products": [
                {"id": 1, "price": 430, "name": "r1", "status": "active", "category": "food"},
                {"id": 2, "price": 710, "name": "r2", "status": "active", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "c1", "department": "eng", "employee_id": 301},
                {"id": 2, "name": "c2", "department": "hr", "employee_id": 302},
                {"id": 3, "name": "c3", "department": "sales", "employee_id": 303},
            ],
            "orders": [{"id": 1, "amount": 100}],
            "expenses": [
                {"id": 1, "amount": 200, "category": "travel"},
                {"id": 2, "amount": 600, "category": "equipment"},
                {"id": 3, "amount": 150, "category": "supplies"},
                {"id": 4, "amount": 800, "category": "equipment"},
                {"id": 5, "amount": 350, "category": "travel"},
            ],
        },
        {  # 5 products, 3 with price > 200, 3 with price > 500
            "products": [
                {"id": 1, "price": 170, "name": "s1", "status": "inactive", "category": "tools"},
                {"id": 2, "price": 90, "name": "s2", "status": "active", "category": "food"},
                {"id": 3, "price": 530, "name": "s3", "status": "active", "category": "tech"},
                {"id": 4, "price": 650, "name": "s4", "status": "active", "category": "tech"},
                {"id": 5, "price": 840, "name": "s5", "status": "inactive", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "d1", "department": "eng", "employee_id": 401},
                {"id": 2, "name": "d2", "department": "eng", "employee_id": 402},
                {"id": 3, "name": "d3", "department": "eng", "employee_id": 403},
                {"id": 4, "name": "d4", "department": "sales", "employee_id": 404},
            ],
            "orders": [{"id": 1, "amount": 300}, {"id": 2, "amount": 700}],
            "expenses": [{"id": 1, "amount": 500, "category": "travel"}, {"id": 2, "amount": 100, "category": "supplies"}],
        },
        {  # 4 products, 1 with price > 200, 0 with price > 500
            "products": [
                {"id": 1, "price": 40, "name": "t1", "status": "active", "category": "food"},
                {"id": 2, "price": 110, "name": "t2", "status": "active", "category": "tech"},
                {"id": 3, "price": 160, "name": "t3", "status": "inactive", "category": "tools"},
                {"id": 4, "price": 290, "name": "t4", "status": "active", "category": "food"},
            ],
            "employees": [
                {"id": 1, "name": "e1", "department": "hr", "employee_id": 501},
                {"id": 2, "name": "e2", "department": "eng", "employee_id": 502},
                {"id": 3, "name": "e3", "department": "sales", "employee_id": 503},
                {"id": 4, "name": "e4", "department": "eng", "employee_id": 504},
                {"id": 5, "name": "e5", "department": "hr", "employee_id": 505},
                {"id": 6, "name": "e6", "department": "eng", "employee_id": 506},
            ],
            "orders": [{"id": 1, "amount": 200}, {"id": 2, "amount": 400}, {"id": 3, "amount": 600}, {"id": 4, "amount": 150}],
            "expenses": [{"id": 1, "amount": 300, "category": "equipment"}, {"id": 2, "amount": 700, "category": "travel"}],
        },
        {  # 7 products, 5 with price > 200, 4 with price > 500
            "products": [
                {"id": 1, "price": 150, "name": "u1", "status": "active", "category": "tech"},
                {"id": 2, "price": 60, "name": "u2", "status": "inactive", "category": "food"},
                {"id": 3, "price": 340, "name": "u3", "status": "active", "category": "tools"},
                {"id": 4, "price": 510, "name": "u4", "status": "active", "category": "tech"},
                {"id": 5, "price": 670, "name": "u5", "status": "active", "category": "food"},
                {"id": 6, "price": 890, "name": "u6", "status": "inactive", "category": "tools"},
                {"id": 7, "price": 550, "name": "u7", "status": "active", "category": "tech"},
            ],
            "employees": [{"id": 1, "name": "f1", "department": "eng", "employee_id": 601}],
            "orders": [{"id": 1, "amount": 800}],
            "expenses": [
                {"id": 1, "amount": 250, "category": "travel"},
                {"id": 2, "amount": 450, "category": "supplies"},
                {"id": 3, "amount": 120, "category": "equipment"},
            ],
        },
        {  # 1 product, 1 with price > 200, 1 with price > 500
            "products": [
                {"id": 1, "price": 920, "name": "v1", "status": "active", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "g1", "department": "sales", "employee_id": 701},
                {"id": 2, "name": "g2", "department": "eng", "employee_id": 702},
                {"id": 3, "name": "g3", "department": "eng", "employee_id": 703},
                {"id": 4, "name": "g4", "department": "hr", "employee_id": 704},
                {"id": 5, "name": "g5", "department": "eng", "employee_id": 705},
                {"id": 6, "name": "g6", "department": "sales", "employee_id": 706},
                {"id": 7, "name": "g7", "department": "eng", "employee_id": 707},
            ],
            "orders": [{"id": 1, "amount": 450}, {"id": 2, "amount": 50}],
            "expenses": [{"id": 1, "amount": 900, "category": "travel"}],
        },
        {  # 8 products, 6 with price > 200, 3 with price > 500
            "products": [
                {"id": 1, "price": 30, "name": "w1", "status": "inactive", "category": "food"},
                {"id": 2, "price": 180, "name": "w2", "status": "active", "category": "tech"},
                {"id": 3, "price": 270, "name": "w3", "status": "active", "category": "tools"},
                {"id": 4, "price": 360, "name": "w4", "status": "active", "category": "food"},
                {"id": 5, "price": 490, "name": "w5", "status": "inactive", "category": "tech"},
                {"id": 6, "price": 580, "name": "w6", "status": "active", "category": "tools"},
                {"id": 7, "price": 750, "name": "w7", "status": "active", "category": "tech"},
                {"id": 8, "price": 910, "name": "w8", "status": "active", "category": "food"},
            ],
            "employees": [
                {"id": 1, "name": "h1", "department": "eng", "employee_id": 801},
                {"id": 2, "name": "h2", "department": "hr", "employee_id": 802},
                {"id": 3, "name": "h3", "department": "eng", "employee_id": 803},
            ],
            "orders": [{"id": 1, "amount": 120}, {"id": 2, "amount": 330}, {"id": 3, "amount": 560}, {"id": 4, "amount": 780}, {"id": 5, "amount": 990}],
            "expenses": [
                {"id": 1, "amount": 160, "category": "supplies"},
                {"id": 2, "amount": 340, "category": "travel"},
                {"id": 3, "amount": 620, "category": "equipment"},
                {"id": 4, "amount": 850, "category": "travel"},
            ],
        },
    ]


# Candidate tasks
CANDIDATE_TASKS: list[tuple[str, int, Callable[[dict], Any], str]] = [
    # --- Tier 1-2 ---
    ("count(products)", 2, lambda ctx: len(ctx["products"]), "(count data/products)"),
    ("count(employees)", 2, lambda ctx: len(ctx["employees"]), "(count data/employees)"),
    ("count(orders)", 2, lambda ctx: len(ctx["orders"]), "(count data/orders)"),

    # --- Tier 2-3 ---
    ("count(rest(products))", 3, lambda ctx: len(ctx["products"]) - 1, "(count (rest data/products))"),
    ("count(rest(employees))", 3, lambda ctx: len(ctx["employees"]) - 1, "(count (rest data/employees))"),

    # --- Tier 4-5: count of filtered items ---
    # count(filter(price>200)): expected = [1, 4, 2, 3, 1, 5, 1, 6]
    ("count(filter(price>200, products))", 5, lambda ctx: len([p for p in ctx["products"] if p["price"] > 200]),
     "(count (filter (fn x (> (get x :price) 200)) data/products))"),

    # count(filter(price>500)): expected = [0, 2, 1, 3, 0, 4, 1, 3]
    ("count(filter(price>500, products))", 5, lambda ctx: len([p for p in ctx["products"] if p["price"] > 500]),
     "(count (filter (fn x (> (get x :price) 500)) data/products))"),

    # count(filter(amount>200, expenses)): expected = [2, 1, 3, 1, 1, 1, 1, 3]
    ("count(filter(amount>200, expenses))", 5, lambda ctx: len([e for e in ctx["expenses"] if e["amount"] > 200]),
     "(count (filter (fn x (> (get x :amount) 200)) data/expenses))"),

    # count(filter(amount>300, orders)): expected = [1, 1, 0, 1, 2, 1, 1, 3]
    ("count(filter(amount>300, orders))", 5, lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 300]),
     "(count (filter (fn x (> (get x :amount) 300)) data/orders))"),

    # --- Tier 5-6: more complex aggregations ---
    ("count(filter(price>200)) + count(filter(price>500))", 6,
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 200]) + len([p for p in ctx["products"] if p["price"] > 500]),
     "(+ (count (filter ... >200)) (count (filter ... >500)))"),
]


def evaluate_exact(program, target_fn, contexts) -> float:
    """Exact match scoring with data-dependence gate."""
    if program.ast is None:
        return 0.0

    outputs = []
    matches = 0
    for ctx in contexts:
        result = program.evaluate(ctx)
        expected = target_fn(ctx)
        outputs.append(repr(result))
        if result == expected:
            matches += 1

    # Data-dependence gate
    if len(set(outputs)) <= 1:
        return 0.0

    return matches / len(contexts)


def profile_task(task_name, intended_bonds, target_fn, description, contexts,
                 lengths=(50, 100, 150), n_samples=100_000, seed=42):
    """Profile with exact-match scoring."""
    expected = [target_fn(ctx) for ctx in contexts]
    print(f"\n{'='*70}")
    print(f"Task: {task_name} (intended {intended_bonds} bonds)")
    print(f"  Expected: {expected}")

    # Also show what simple programs produce (for comparison)
    for simple_name, simple_src in [
        ("count(products)", "(count data/products)"),
        ("count(rest(products))", "(count (rest data/products))"),
        ("count(employees)", "(count data/employees)"),
    ]:
        simple_out = []
        if simple_name == "count(products)":
            simple_out = [len(ctx["products"]) for ctx in contexts]
        elif simple_name == "count(rest(products))":
            simple_out = [len(ctx["products"]) - 1 for ctx in contexts]
        elif simple_name == "count(employees)":
            simple_out = [len(ctx["employees"]) for ctx in contexts]
        overlap = sum(1 for a, b in zip(expected, simple_out) if a == b)
        print(f"  vs {simple_name:30s}: {simple_out}  ({overlap}/{len(contexts)} exact matches)")

    for length in lengths:
        rng = random.Random(seed)
        tier_max: dict[int, float] = defaultdict(float)
        tier_count: dict[int, int] = defaultdict(int)
        tier_nonzero: dict[int, int] = defaultdict(int)
        tier_best_src: dict[int, tuple[float, str]] = {}

        t0 = time.time()
        for _ in range(n_samples):
            g = random_genotype(length, rng=rng)
            p = develop(g)
            fitness = evaluate_exact(p, target_fn, contexts)
            bc = p.bond_count
            tier_count[bc] += 1
            if fitness > 0:
                tier_nonzero[bc] += 1
            if fitness > tier_max[bc]:
                tier_max[bc] = fitness
                tier_best_src[bc] = (fitness, p.source or "(nil)")

        elapsed = time.time() - t0

        print(f"\n  Length {length} ({n_samples:,} samples, {elapsed:.1f}s):")
        print(f"  {'Bonds':>5s} | {'Count':>7s} | {'Max exact':>9s} | {'Any match':>9s} | Best program")
        print(f"  {'-'*5}-+-{'-'*7}-+-{'-'*9}-+-{'-'*9}-+--{'--'*20}")

        for bc in sorted(tier_count.keys()):
            if bc > 20:
                continue  # skip noise at high bond counts
            max_f = tier_max[bc]
            pct_nz = tier_nonzero.get(bc, 0) / tier_count[bc] * 100
            src = tier_best_src.get(bc, (0, ""))[1]
            if len(src) > 55:
                src = src[:52] + "..."
            # Highlight if this tier achieves high fitness
            marker = " <<<" if max_f >= 0.75 else " **" if max_f >= 0.5 else ""
            print(f"  {bc:5d} | {tier_count[bc]:7d} | {max_f:9.3f} | {pct_nz:8.1f}% | {src}{marker}")

        # Summary
        min_75 = None
        min_100 = None
        for bc in sorted(tier_max.keys()):
            if tier_max[bc] >= 0.75 and min_75 is None:
                min_75 = bc
            if tier_max[bc] >= 1.0 and min_100 is None:
                min_100 = bc

        print(f"\n  Min bonds for >=75% exact: {min_75 if min_75 is not None else 'NONE'}")
        print(f"  Min bonds for 100% exact:  {min_100 if min_100 is not None else 'NONE'}")


def main():
    contexts = make_discriminating_contexts()

    print("Task Verification Profiler — STRICT (exact match)")
    print("=" * 70)
    print(f"Contexts: {len(contexts)}")
    print(f"Product counts per context: {[len(c['products']) for c in contexts]}")

    # Verify expected outputs are distinct for key tasks
    print("\nExpected output profiles:")
    for name, _, fn, _ in CANDIDATE_TASKS:
        vals = [fn(ctx) for ctx in contexts]
        print(f"  {name:45s}: {vals}")

    n_samples = 100_000
    lengths = (50, 100, 150)

    for name, intended, target_fn, desc in CANDIDATE_TASKS:
        profile_task(name, intended, target_fn, desc, contexts, lengths=lengths, n_samples=n_samples)

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY: Verified difficulty tiers (exact match, length 100)")
    print("=" * 70)
    print(f"\n{'Task':<50s} | {'Intended':>8s} | {'Min for 75%':>11s} | {'Min for 100%':>12s}")
    print(f"{'-'*50}-+-{'-'*8}-+-{'-'*11}-+-{'-'*12}")

    for name, intended, target_fn, desc in CANDIDATE_TASKS:
        rng = random.Random(42)
        tier_max: dict[int, float] = defaultdict(float)
        for _ in range(n_samples):
            g = random_genotype(100, rng=rng)
            p = develop(g)
            fitness = evaluate_exact(p, target_fn, contexts)
            bc = p.bond_count
            if fitness > tier_max[bc]:
                tier_max[bc] = fitness

        min_75 = next((bc for bc in sorted(tier_max) if tier_max[bc] >= 0.75), None)
        min_100 = next((bc for bc in sorted(tier_max) if tier_max[bc] >= 1.0), None)

        label_75 = str(min_75) if min_75 is not None else "NONE"
        label_100 = str(min_100) if min_100 is not None else "NONE"
        print(f"{name:<50s} | {intended:>8d} | {label_75:>11s} | {label_100:>12s}")


if __name__ == "__main__":
    main()
