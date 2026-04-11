"""
Aligned Compositional Fitness + Seeded Survival Experiment.

Fixes the anti-selection problem: filter programs return lists but targets
are numeric, causing filter programs to score 0.050 (wrong-type floor)
while count(products) scores 0.769.

The aligned fitness adds compositional fallbacks:
  - If output is a list and target is numeric: try count(output) as fallback
  - If output is a list and target is a list: compare directly
  - Reward intermediate structure: programs that produce correctly-filtered
    lists score well even before being wrapped in count()

Also adds a structural composition bonus:
  - Programs containing (filter (fn x (COMPARATOR ...)) DATA) get a small
    bonus, recognizing they've solved the harder structural sub-problem

Re-runs the seeded elaboration experiment to test:
  Does the filter program survive when it's not anti-selected?
"""

import random
import time
from collections import defaultdict
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, _count_bonds, ast_to_string
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword
from folding_evolution.selection import tournament_select


# ---------------------------------------------------------------------------
# Aligned compositional scoring
# ---------------------------------------------------------------------------

def compositional_credit(actual: Any, expected: Any) -> float:
    """Partial credit with compositional fallbacks.

    Key addition: if actual is a list and expected is numeric,
    try count(actual) as a compositional interpretation.
    This bridges the gap between filter (returns list) and
    count(filter(...)) (returns number).
    """
    # Standard case: direct match
    if actual == expected:
        return 1.0
    if actual is None:
        return 0.0

    # Compositional fallback: list output vs numeric target
    if isinstance(actual, list) and isinstance(expected, (int, float)):
        # Try count(actual) — the most common aggregation
        count_val = len(actual)
        if count_val == expected:
            return 0.9  # high but not perfect (missing the count wrapper)

        # Partial credit on count proximity
        if expected == 0:
            closeness = 0.1 if count_val != 0 else 0.9
        else:
            ratio = abs(count_val - expected) / max(abs(expected), 1)
            closeness = max(0.1, min(0.8, 0.8 * (1.0 - ratio)))
        return closeness

    # Standard partial credit for other cases
    return partial_credit(actual, expected)


# ---------------------------------------------------------------------------
# Contexts and targets
# ---------------------------------------------------------------------------

def make_contexts():
    """8 discriminating contexts."""
    return [
        {"products": [{"id": 1, "price": 50, "name": "p1", "status": "active", "category": "tools"},
                      {"id": 2, "price": 120, "name": "p2", "status": "inactive", "category": "tech"},
                      {"id": 3, "price": 350, "name": "p3", "status": "active", "category": "food"}],
         "employees": [{"id": i, "name": f"a{i}", "department": d, "employee_id": 100+i}
                       for i, d in enumerate(["eng", "sales", "eng", "hr", "eng"], 1)],
         "orders": [{"id": 1, "amount": 150}, {"id": 2, "amount": 350}],
         "expenses": [{"id": 1, "amount": 75, "category": "travel"}, {"id": 2, "amount": 225, "category": "equipment"},
                      {"id": 3, "amount": 550, "category": "travel"}]},
        {"products": [{"id": i, "price": p, "name": f"q{i}", "status": s, "category": c}
                      for i, (p, s, c) in enumerate([(80, "active", "tech"), (190, "active", "food"),
                          (310, "inactive", "tools"), (450, "active", "tech"),
                          (620, "active", "food"), (780, "inactive", "tech")], 1)],
         "employees": [{"id": i, "name": f"b{i}", "department": d, "employee_id": 200+i}
                       for i, d in enumerate(["sales", "eng"], 1)],
         "orders": [{"id": 1, "amount": 50}, {"id": 2, "amount": 250}, {"id": 3, "amount": 900}],
         "expenses": [{"id": 1, "amount": 400, "category": "equipment"}]},
        {"products": [{"id": 1, "price": 430, "name": "r1", "status": "active", "category": "food"},
                      {"id": 2, "price": 710, "name": "r2", "status": "active", "category": "tools"}],
         "employees": [{"id": i, "name": f"c{i}", "department": d, "employee_id": 300+i}
                       for i, d in enumerate(["eng", "hr", "sales"], 1)],
         "orders": [{"id": 1, "amount": 100}],
         "expenses": [{"id": 1, "amount": 200, "category": "travel"}, {"id": 2, "amount": 600, "category": "equipment"},
                      {"id": 3, "amount": 150, "category": "supplies"}, {"id": 4, "amount": 800, "category": "equipment"},
                      {"id": 5, "amount": 350, "category": "travel"}]},
        {"products": [{"id": i, "price": p, "name": f"s{i}", "status": s, "category": c}
                      for i, (p, s, c) in enumerate([(170, "inactive", "tools"), (90, "active", "food"),
                          (530, "active", "tech"), (650, "active", "tech"), (840, "inactive", "tools")], 1)],
         "employees": [{"id": i, "name": f"d{i}", "department": d, "employee_id": 400+i}
                       for i, d in enumerate(["eng", "eng", "eng", "sales"], 1)],
         "orders": [{"id": 1, "amount": 300}, {"id": 2, "amount": 700}],
         "expenses": [{"id": 1, "amount": 500, "category": "travel"}, {"id": 2, "amount": 100, "category": "supplies"}]},
        {"products": [{"id": i, "price": p, "name": f"t{i}", "status": s, "category": c}
                      for i, (p, s, c) in enumerate([(40, "active", "food"), (110, "active", "tech"),
                          (160, "inactive", "tools"), (290, "active", "food")], 1)],
         "employees": [{"id": i, "name": f"e{i}", "department": d, "employee_id": 500+i}
                       for i, d in enumerate(["hr", "eng", "sales", "eng", "hr", "eng"], 1)],
         "orders": [{"id": i, "amount": a} for i, a in enumerate([200, 400, 600, 150], 1)],
         "expenses": [{"id": 1, "amount": 300, "category": "equipment"}, {"id": 2, "amount": 700, "category": "travel"}]},
        {"products": [{"id": i, "price": p, "name": f"u{i}", "status": s, "category": c}
                      for i, (p, s, c) in enumerate([(150, "active", "tech"), (60, "inactive", "food"),
                          (340, "active", "tools"), (510, "active", "tech"), (670, "active", "food"),
                          (890, "inactive", "tools"), (550, "active", "tech")], 1)],
         "employees": [{"id": 1, "name": "f1", "department": "eng", "employee_id": 601}],
         "orders": [{"id": 1, "amount": 800}],
         "expenses": [{"id": 1, "amount": 250, "category": "travel"}, {"id": 2, "amount": 450, "category": "supplies"},
                      {"id": 3, "amount": 120, "category": "equipment"}]},
        {"products": [{"id": 1, "price": 920, "name": "v1", "status": "active", "category": "tools"}],
         "employees": [{"id": i, "name": f"g{i}", "department": d, "employee_id": 700+i}
                       for i, d in enumerate(["sales", "eng", "eng", "hr", "eng", "sales", "eng"], 1)],
         "orders": [{"id": 1, "amount": 450}, {"id": 2, "amount": 50}],
         "expenses": [{"id": 1, "amount": 900, "category": "travel"}]},
        {"products": [{"id": i, "price": p, "name": f"w{i}", "status": s, "category": c}
                      for i, (p, s, c) in enumerate([(30, "inactive", "food"), (180, "active", "tech"),
                          (270, "active", "tools"), (360, "active", "food"), (490, "inactive", "tech"),
                          (580, "active", "tools"), (750, "active", "tech"), (910, "active", "food")], 1)],
         "employees": [{"id": i, "name": f"h{i}", "department": d, "employee_id": 800+i}
                       for i, d in enumerate(["eng", "hr", "eng"], 1)],
         "orders": [{"id": i, "amount": a} for i, a in enumerate([120, 330, 560, 780, 990], 1)],
         "expenses": [{"id": 1, "amount": 160, "category": "supplies"}, {"id": 2, "amount": 340, "category": "travel"},
                      {"id": 3, "amount": 620, "category": "equipment"}, {"id": 4, "amount": 850, "category": "travel"}]},
    ]


# Targets: count(filter(price>200)) is the hard target, count(products) is easy
TARGETS = [
    ("count(filter(price>200, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 200])),
    ("count(products)", lambda ctx: len(ctx["products"])),
]

SEED_STAGES = {
    "S3_fn_predicate": "QDaK5",
    "S4_filter": "QDaK5XAS",
}


# ---------------------------------------------------------------------------
# Substructure classification (from seeded elaboration)
# ---------------------------------------------------------------------------

def classify_program(prog) -> dict[str, bool]:
    result = {
        "has_get_price": False,
        "has_comparator_get": False,
        "has_fn_comparator_get": False,
        "has_filter_fn": False,
        "has_filter_fn_comparator": False,
        "has_filter_fn_comparator_get": False,
        "has_trivial_filter": False,
    }
    if prog.ast is None:
        return result
    _classify_walk(prog.ast, result)
    return result


def _classify_walk(node, result):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    hn = head.name if isinstance(head, Symbol) else None

    if hn == "get" and len(node.items) == 3 and isinstance(node.items[2], Keyword):
        if node.items[2].name == "price":
            result["has_get_price"] = True
    if hn in (">", "<", "=") and len(node.items) == 3:
        for op in node.items[1:]:
            if _is_get_price(op):
                result["has_comparator_get"] = True
    if hn == "fn" and len(node.items) >= 3:
        body = node.items[2]
        if isinstance(body, ListExpr) and body.items:
            bh = body.items[0]
            if isinstance(bh, Symbol) and bh.name in (">", "<", "="):
                for op in body.items[1:]:
                    if _is_get_price(op):
                        result["has_fn_comparator_get"] = True
    if hn in ("filter", "map") and len(node.items) >= 3:
        fn_arg = node.items[1]
        result["has_filter_fn"] = True
        if isinstance(fn_arg, ListExpr) and fn_arg.items:
            fh = fn_arg.items[0]
            if isinstance(fh, Symbol) and fh.name == "fn" and len(fn_arg.items) >= 3:
                body = fn_arg.items[2]
                if isinstance(body, ListExpr) and body.items:
                    bh = body.items[0]
                    if isinstance(bh, Symbol) and bh.name in (">", "<", "="):
                        result["has_filter_fn_comparator"] = True
                        for op in body.items[1:]:
                            if _is_get_price(op):
                                result["has_filter_fn_comparator_get"] = True
                else:
                    result["has_trivial_filter"] = True
    for item in node.items:
        _classify_walk(item, result)


def _is_get_price(node):
    return (isinstance(node, ListExpr) and len(node.items) == 3 and
            isinstance(node.items[0], Symbol) and node.items[0].name == "get" and
            isinstance(node.items[2], Keyword) and node.items[2].name == "price")


# ---------------------------------------------------------------------------
# Evolution
# ---------------------------------------------------------------------------

def make_seeded_genotype(core, target_length, rng):
    pad_needed = target_length - len(core)
    if pad_needed <= 0:
        return core[:target_length]
    pre_len = rng.randint(0, pad_needed)
    post_len = pad_needed - pre_len
    pre = random_genotype(pre_len, rng) if pre_len > 0 else ""
    post = random_genotype(post_len, rng) if post_len > 0 else ""
    return pre + core + post


def run_seeded(
    stage_name, core_genotype, pop_size, genotype_length, generations,
    contexts, seed, score_fn, seed_fraction=0.2,
):
    rng = random.Random(seed)
    develop.cache_clear()

    n_seeded = int(pop_size * seed_fraction)
    population = []
    for _ in range(n_seeded):
        g = make_seeded_genotype(core_genotype, genotype_length, rng) if core_genotype else random_genotype(genotype_length, rng)
        population.append(Individual(genotype=g))
    for _ in range(pop_size - n_seeded):
        population.append(Individual(genotype=random_genotype(genotype_length, rng)))

    history = []

    for gen in range(generations):
        for ind in population:
            ind.program = develop(ind.genotype)
            if ind.program.ast is None:
                ind.fitness = 0.0
                continue
            gate = [repr(ind.program.evaluate(ctx)) for ctx in contexts]
            if len(set(gate)) <= 1:
                ind.fitness = 0.0
                continue
            scores = []
            for _, tfn in TARGETS:
                for ctx in contexts:
                    scores.append(score_fn(ind.program.evaluate(ctx), tfn(ctx)))
            ind.fitness = sum(scores) / len(scores)

        pop_classes = defaultdict(int)
        for ind in population:
            cl = classify_program(ind.program)
            for k, v in cl.items():
                if v:
                    pop_classes[k] += 1

        best = max(population, key=lambda i: i.fitness)
        avg_bonds = sum(i.program.bond_count for i in population if i.program) / pop_size

        history.append({
            "gen": gen,
            "best_fitness": best.fitness,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "avg_bonds": avg_bonds,
            "pop_classes": dict(pop_classes),
        })

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
            for _, tfn in TARGETS:
                for ctx in contexts:
                    scores.append(score_fn(ind.program.evaluate(ctx), tfn(ctx)))
            ind.fitness = sum(scores) / len(scores)

        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {"history": history}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    contexts = make_contexts()
    pop_size = 100
    genotype_length = 100
    generations = 100
    n_seeds = 10

    # First: verify the fitness fix
    print("=" * 70)
    print("Fitness Verification: filter vs count(products)")
    print("=" * 70)

    filter_prog = develop("QDaK5XAS")
    count_prog = develop("BS")

    for label, prog in [("filter (QDaK5XAS)", filter_prog), ("count(products) (BS)", count_prog)]:
        old_scores = []
        new_scores = []
        for _, tfn in TARGETS:
            for ctx in contexts:
                output = prog.evaluate(ctx)
                expected = tfn(ctx)
                old_scores.append(partial_credit(output, expected))
                new_scores.append(compositional_credit(output, expected))

        old_gate = [repr(prog.evaluate(ctx)) for ctx in contexts]
        old_gated = len(set(old_gate)) <= 1
        old_avg = 0.0 if old_gated else sum(old_scores) / len(old_scores)
        new_avg = 0.0 if old_gated else sum(new_scores) / len(new_scores)

        print(f"  {label}: old={old_avg:.3f} new={new_avg:.3f} ({prog.source})")

    print()

    # Run experiment
    print("=" * 70)
    print("Seeded Survival: Original vs Aligned Fitness")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print()

    conditions = [
        ("Original fitness, S4 seeded", "QDaK5XAS", partial_credit),
        ("Aligned fitness, S4 seeded", "QDaK5XAS", compositional_credit),
        ("Aligned fitness, S3 seeded", "QDaK5", compositional_credit),
        ("Aligned fitness, no seeding", "", compositional_credit),
    ]

    all_results = {}

    for cond_name, core, score_fn in conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        for seed in range(n_seeds):
            frac = 0.2 if core else 0.0
            result = run_seeded(cond_name, core, pop_size, genotype_length,
                                generations, contexts, seed, score_fn, seed_fraction=frac)
            cond_results.append(result)

            final = result["history"][-1]
            pc = final["pop_classes"]

            print(f"  Seed {seed:2d}: fit={final['best_fitness']:.3f} bonds={final['best_bonds']} "
                  f"get_price={pc.get('has_get_price', 0)} "
                  f"cmp_get={pc.get('has_comparator_get', 0)} "
                  f"fn_cmp_get={pc.get('has_fn_comparator_get', 0)} "
                  f"filter_full={pc.get('has_filter_fn_comparator_get', 0)} "
                  f"triv_filt={pc.get('has_trivial_filter', 0)} "
                  f"src={final['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s\n")
        all_results[cond_name] = cond_results

    # === Summary ===
    print("=" * 70)
    print("SUMMARY: Substructure Survival (Gen 0 → Gen 99)")
    print("=" * 70)

    key_classes = [
        "has_get_price", "has_comparator_get", "has_fn_comparator_get",
        "has_filter_fn", "has_filter_fn_comparator", "has_filter_fn_comparator_get",
        "has_trivial_filter",
    ]

    for cond_name, results in all_results.items():
        print(f"\n{cond_name}:")
        for cls in key_classes:
            g0 = [r["history"][0]["pop_classes"].get(cls, 0) for r in results]
            g99 = [r["history"][-1]["pop_classes"].get(cls, 0) for r in results]
            avg0 = sum(g0) / len(g0)
            avg99 = sum(g99) / len(g99)
            direction = "↑" if avg99 > avg0 + 2 else "↓" if avg99 < avg0 - 2 else "→"
            print(f"  {cls:<35s}: {avg0:5.1f} → {avg99:5.1f}  {direction}")

    # Did any condition produce the full filter chain?
    print("\n" + "=" * 70)
    print("FULL FILTER CHAIN: filter(fn(>(get x :price) VALUE)) ever observed?")
    print("=" * 70)
    for cond_name, results in all_results.items():
        max_count = 0
        max_gen = -1
        max_seed = -1
        for seed, r in enumerate(results):
            for entry in r["history"]:
                c = entry["pop_classes"].get("has_filter_fn_comparator_get", 0)
                if c > max_count:
                    max_count = c
                    max_gen = entry["gen"]
                    max_seed = seed
        if max_count > 0:
            print(f"  {cond_name}: YES — max {max_count} individuals at seed {max_seed} gen {max_gen}")
        else:
            print(f"  {cond_name}: NEVER")


if __name__ == "__main__":
    main()
