"""
Seeded Module Elaboration Experiment.

Tests whether evolution can grow partial filter substructures into complete
filter programs when seeded into the population.

Four seeding stages (progressive substructures of the target filter program):
  Stage 1: (get x :price)                           -- 1 bond, genotype "Da"
  Stage 2: (> (get x :price) 500)                   -- 2 bonds, genotype "DaK5"
  Stage 3: (fn x (> (get x :price) 500))            -- 3 bonds, genotype "QDaK5"
  Stage 4: (filter (fn x (> (get x :price) 500)) data/products)  -- 4 bonds, genotype "QDaK5XAS"

For each stage:
  - Seed 20% of population with the stage genotype (padded with random chars)
  - Run evolution on hard tasks (count(filter(price>200, products)))
  - Track: does the seeded substructure survive? Elaborate? Degrade?
  - Measure: substructure survival rate, bond count trajectory, fitness

The decisive fork:
  If seeded modules elaborate → problem is discovery, solution is archives/building-blocks
  If seeded modules degrade → problem is chemistry hostility, solution is softer chemistry
"""

import random
import time
from collections import defaultdict

from folding_evolution.alphabet import random_genotype
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, _count_bonds, ast_to_string
from folding_evolution.fold import fold
from folding_evolution.chemistry import assemble
from folding_evolution.selection import tournament_select


# ---------------------------------------------------------------------------
# Seeded genotype construction
# ---------------------------------------------------------------------------

SEED_STAGES = {
    "S1_get_field": "Da",           # (get x :price) - 1 bond
    "S2_comparator": "DaK5",        # (> (get x :price) 500) - 2 bonds
    "S3_fn_predicate": "QDaK5",     # (fn x (> (get x :price) 500)) - 3 bonds
    "S4_filter": "QDaK5XAS",        # (filter (fn x ...) data/products) - 4 bonds
}


def make_seeded_genotype(core: str, target_length: int, rng: random.Random) -> str:
    """Create a genotype with the core motif padded to target length.

    Places the core at a random position with random padding before/after.
    """
    pad_needed = target_length - len(core)
    if pad_needed <= 0:
        return core[:target_length]
    pre_len = rng.randint(0, pad_needed)
    post_len = pad_needed - pre_len
    pre = random_genotype(pre_len, rng) if pre_len > 0 else ""
    post = random_genotype(post_len, rng) if post_len > 0 else ""
    return pre + core + post


# ---------------------------------------------------------------------------
# Substructure detection (focused on the filter chain)
# ---------------------------------------------------------------------------

def classify_program(prog) -> dict[str, bool]:
    """Classify what substructures a program contains."""
    result = {
        "has_get_price": False,
        "has_comparator_get": False,
        "has_fn_comparator_get": False,
        "has_filter_fn": False,
        "has_filter_fn_comparator": False,
        "has_filter_fn_comparator_get": False,
        "has_trivial_filter": False,  # filter(fn x LITERAL)
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
                    # fn x LITERAL — trivially true
                    result["has_trivial_filter"] = True

    for item in node.items:
        _classify_walk(item, result)


def _is_get_price(node):
    return (isinstance(node, ListExpr) and len(node.items) == 3 and
            isinstance(node.items[0], Symbol) and node.items[0].name == "get" and
            isinstance(node.items[2], Keyword) and node.items[2].name == "price")


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


TARGETS = [
    ("count(filter(price>200, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 200])),
    ("count(products)", lambda ctx: len(ctx["products"])),
]


# ---------------------------------------------------------------------------
# Evolution with seeded population
# ---------------------------------------------------------------------------

def run_seeded(
    stage_name: str, core_genotype: str,
    pop_size: int, genotype_length: int, generations: int,
    contexts: list, seed: int, seed_fraction: float = 0.2,
) -> dict:
    rng = random.Random(seed)
    develop.cache_clear()

    n_seeded = int(pop_size * seed_fraction)
    n_random = pop_size - n_seeded

    # Create population: seeded + random
    population = []
    for _ in range(n_seeded):
        g = make_seeded_genotype(core_genotype, genotype_length, rng)
        population.append(Individual(genotype=g))
    for _ in range(n_random):
        population.append(Individual(genotype=random_genotype(genotype_length, rng)))

    history = []

    for gen in range(generations):
        # Evaluate
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
                    scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
            ind.fitness = sum(scores) / len(scores)

        # Classify all programs
        pop_classes = defaultdict(int)
        for ind in population:
            cl = classify_program(ind.program)
            for k, v in cl.items():
                if v:
                    pop_classes[k] += 1

        best = max(population, key=lambda i: i.fitness)
        best_cl = classify_program(best.program)
        avg_bonds = sum(i.program.bond_count for i in population if i.program) / pop_size

        entry = {
            "gen": gen,
            "best_fitness": best.fitness,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "avg_bonds": avg_bonds,
            "pop_classes": dict(pop_classes),
            "best_classes": best_cl,
        }
        history.append(entry)

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
            for _, tfn in TARGETS:
                for ctx in contexts:
                    scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
            ind.fitness = sum(scores) / len(scores)

        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {"history": history}


def main():
    contexts = make_contexts()
    pop_size = 100
    genotype_length = 100
    generations = 100
    n_seeds = 5

    print("=" * 70)
    print("Seeded Module Elaboration Experiment")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print(f"Seed fraction: 20% of population seeded with core genotype")
    print()

    # Verify stage genotypes
    print("Stage genotypes:")
    for name, core in SEED_STAGES.items():
        p = develop(core)
        print(f"  {name}: \"{core}\" -> {p.bond_count} bonds: {p.source}")
    print()

    # Also run unseeded control
    all_conditions = [("Control (no seeding)", "")] + list(SEED_STAGES.items())

    all_results = {}

    for cond_name, core in all_conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        for seed in range(n_seeds):
            if core:
                result = run_seeded(cond_name, core, pop_size, genotype_length,
                                    generations, contexts, seed)
            else:
                # Control: no seeding
                result = run_seeded(cond_name, "", pop_size, genotype_length,
                                    generations, contexts, seed, seed_fraction=0.0)
            cond_results.append(result)

            final = result["history"][-1]
            pc = final["pop_classes"]
            n_get = pc.get("has_get_price", 0)
            n_cmp = pc.get("has_comparator_get", 0)
            n_fn = pc.get("has_fn_comparator_get", 0)
            n_filt = pc.get("has_filter_fn_comparator_get", 0)
            n_triv = pc.get("has_trivial_filter", 0)

            print(f"  Seed {seed}: fit={final['best_fitness']:.3f} bonds={final['best_bonds']} "
                  f"get_price={n_get} cmp_get={n_cmp} fn_cmp_get={n_fn} "
                  f"filter_full={n_filt} trivial_filter={n_triv} "
                  f"src={final['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s\n")
        all_results[cond_name] = cond_results

    # === Summary: substructure survival ===
    print("=" * 70)
    print("SUBSTRUCTURE SURVIVAL: Gen 0 → Gen 99")
    print("=" * 70)

    key_classes = [
        "has_get_price", "has_comparator_get", "has_fn_comparator_get",
        "has_filter_fn", "has_filter_fn_comparator", "has_filter_fn_comparator_get",
        "has_trivial_filter",
    ]

    for cond_name, results in all_results.items():
        print(f"\n{cond_name}:")
        for cls in key_classes:
            g0_vals = [r["history"][0]["pop_classes"].get(cls, 0) for r in results]
            g99_vals = [r["history"][-1]["pop_classes"].get(cls, 0) for r in results]
            avg0 = sum(g0_vals) / len(g0_vals)
            avg99 = sum(g99_vals) / len(g99_vals)
            direction = "↑" if avg99 > avg0 + 2 else "↓" if avg99 < avg0 - 2 else "→"
            print(f"  {cls:<35s}: {avg0:5.1f} → {avg99:5.1f}  {direction}")

    # === Key question: did any condition produce a REAL filter program? ===
    print("\n" + "=" * 70)
    print("DID ANY CONDITION PRODUCE filter(fn(>(get x :price) VALUE)) data/products)?")
    print("=" * 70)
    for cond_name, results in all_results.items():
        found = False
        for seed, r in enumerate(results):
            for entry in r["history"]:
                if entry["pop_classes"].get("has_filter_fn_comparator_get", 0) > 0:
                    found = True
                    print(f"  {cond_name} seed {seed} gen {entry['gen']}: "
                          f"{entry['pop_classes']['has_filter_fn_comparator_get']} individuals")
                    break
            if found:
                break
        if not found:
            print(f"  {cond_name}: NEVER")


if __name__ == "__main__":
    main()
