"""
Structural Fitness Staircase + Lexicase Selection Experiment.

Tests whether a structurally informed objective + lexicase selection can
guide evolution toward true filter programs instead of shortcut approximations.

Key insight: averaged partial credit + tournament selection lets shortcuts
like count(rest^2(products)) score 5/8 and dominate the population. Lexicase
preserves specialists that solve the 3 anti-alias contexts where shortcuts
fail, and the structural staircase provides gradient toward correct structure.

Two conditions:
  Baseline: averaged partial credit + tournament selection (current approach)
  Treatment: structural staircase + lexicase selection

Both use fixed d1 chemistry, same contexts, same phased curriculum.
"""

import random
import time
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, _count_bonds
from folding_evolution.selection import tournament_select


# ---------------------------------------------------------------------------
# Contexts (8 discriminating contexts)
# ---------------------------------------------------------------------------

def make_contexts():
    """8 contexts with varying collection sizes and price distributions."""
    return [
        {  # 0: 3 products, 1 with price > 200
            "products": [
                {"id": 1, "price": 50, "name": "p1", "status": "active", "category": "tools"},
                {"id": 2, "price": 120, "name": "p2", "status": "inactive", "category": "tech"},
                {"id": 3, "price": 350, "name": "p3", "status": "active", "category": "food"},
            ],
            "employees": [{"id": i, "name": f"a{i}", "department": d, "employee_id": 100+i}
                for i, d in enumerate(["eng", "sales", "eng", "hr", "eng"], 1)],
            "orders": [{"id": 1, "amount": 150}, {"id": 2, "amount": 350}],
            "expenses": [{"id": 1, "amount": 75, "category": "travel"},
                {"id": 2, "amount": 225, "category": "equipment"},
                {"id": 3, "amount": 550, "category": "travel"}],
        },
        {  # 1: 6 products, 4 with price > 200
            "products": [{"id": i, "price": p, "name": f"q{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (80, "active", "tech"), (190, "active", "food"),
                    (310, "inactive", "tools"), (450, "active", "tech"),
                    (620, "active", "food"), (780, "inactive", "tech")], 1)],
            "employees": [{"id": i, "name": f"b{i}", "department": d, "employee_id": 200+i}
                for i, d in enumerate(["sales", "eng"], 1)],
            "orders": [{"id": 1, "amount": 50}, {"id": 2, "amount": 250}, {"id": 3, "amount": 900}],
            "expenses": [{"id": 1, "amount": 400, "category": "equipment"}],
        },
        {  # 2: 2 products, 2 with price > 200  *** ANTI-ALIAS: rest^2 gives 0, target is 2 ***
            "products": [{"id": 1, "price": 430, "name": "r1", "status": "active", "category": "food"},
                {"id": 2, "price": 710, "name": "r2", "status": "active", "category": "tools"}],
            "employees": [{"id": i, "name": f"c{i}", "department": d, "employee_id": 300+i}
                for i, d in enumerate(["eng", "hr", "sales"], 1)],
            "orders": [{"id": 1, "amount": 100}],
            "expenses": [{"id": 1, "amount": 200, "category": "travel"},
                {"id": 2, "amount": 600, "category": "equipment"},
                {"id": 3, "amount": 150, "category": "supplies"},
                {"id": 4, "amount": 800, "category": "equipment"},
                {"id": 5, "amount": 350, "category": "travel"}],
        },
        {  # 3: 5 products, 3 with price > 200
            "products": [{"id": i, "price": p, "name": f"s{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (170, "inactive", "tools"), (90, "active", "food"),
                    (530, "active", "tech"), (650, "active", "tech"),
                    (840, "inactive", "tools")], 1)],
            "employees": [{"id": i, "name": f"d{i}", "department": d, "employee_id": 400+i}
                for i, d in enumerate(["eng", "eng", "eng", "sales"], 1)],
            "orders": [{"id": 1, "amount": 300}, {"id": 2, "amount": 700}],
            "expenses": [{"id": 1, "amount": 500, "category": "travel"},
                {"id": 2, "amount": 100, "category": "supplies"}],
        },
        {  # 4: 4 products, 1 with price > 200  *** ANTI-ALIAS: rest^2 gives 2, target is 1 ***
            "products": [{"id": i, "price": p, "name": f"t{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (40, "active", "food"), (110, "active", "tech"),
                    (160, "inactive", "tools"), (290, "active", "food")], 1)],
            "employees": [{"id": i, "name": f"e{i}", "department": d, "employee_id": 500+i}
                for i, d in enumerate(["hr", "eng", "sales", "eng", "hr", "eng"], 1)],
            "orders": [{"id": i, "amount": a} for i, a in enumerate([200, 400, 600, 150], 1)],
            "expenses": [{"id": 1, "amount": 300, "category": "equipment"},
                {"id": 2, "amount": 700, "category": "travel"}],
        },
        {  # 5: 7 products, 5 with price > 200
            "products": [{"id": i, "price": p, "name": f"u{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (150, "active", "tech"), (60, "inactive", "food"),
                    (340, "active", "tools"), (510, "active", "tech"),
                    (670, "active", "food"), (890, "inactive", "tools"),
                    (550, "active", "tech")], 1)],
            "employees": [{"id": 1, "name": "f1", "department": "eng", "employee_id": 601}],
            "orders": [{"id": 1, "amount": 800}],
            "expenses": [{"id": 1, "amount": 250, "category": "travel"},
                {"id": 2, "amount": 450, "category": "supplies"},
                {"id": 3, "amount": 120, "category": "equipment"}],
        },
        {  # 6: 1 product, 1 with price > 200  *** ANTI-ALIAS: rest^2 gives 0, target is 1 ***
            "products": [{"id": 1, "price": 920, "name": "v1", "status": "active", "category": "tools"}],
            "employees": [{"id": i, "name": f"g{i}", "department": d, "employee_id": 700+i}
                for i, d in enumerate(["sales", "eng", "eng", "hr", "eng", "sales", "eng"], 1)],
            "orders": [{"id": 1, "amount": 450}, {"id": 2, "amount": 50}],
            "expenses": [{"id": 1, "amount": 900, "category": "travel"}],
        },
        {  # 7: 8 products, 6 with price > 200
            "products": [{"id": i, "price": p, "name": f"w{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (30, "inactive", "food"), (180, "active", "tech"),
                    (270, "active", "tools"), (360, "active", "food"),
                    (490, "inactive", "tech"), (580, "active", "tools"),
                    (750, "active", "tech"), (910, "active", "food")], 1)],
            "employees": [{"id": i, "name": f"h{i}", "department": d, "employee_id": 800+i}
                for i, d in enumerate(["eng", "hr", "eng"], 1)],
            "orders": [{"id": i, "amount": a} for i, a in enumerate([120, 330, 560, 780, 990], 1)],
            "expenses": [{"id": 1, "amount": 160, "category": "supplies"},
                {"id": 2, "amount": 340, "category": "travel"},
                {"id": 3, "amount": 620, "category": "equipment"},
                {"id": 4, "amount": 850, "category": "travel"}],
        },
    ]


# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------

EASY_TARGETS: list[tuple[str, Callable, str]] = [
    ("count(products)", lambda ctx: len(ctx["products"]), "products"),
    ("count(employees)", lambda ctx: len(ctx["employees"]), "employees"),
    ("count(rest(products))", lambda ctx: len(ctx["products"]) - 1, "products"),
]

HARD_TARGETS: list[tuple[str, Callable, str]] = [
    ("count(filter(price>200, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 200]),
     "products"),
    ("count(filter(amount>300, orders))",
     lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 300]),
     "orders"),
]


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_partial_credit(output, expected, ctx, data_key):
    """Standard partial credit (current approach)."""
    return partial_credit(output, expected)


def score_structural_staircase(output, expected, ctx, data_key):
    """Structural staircase: rewards intermediate structure toward correct answer.

    Level 1: output is numeric (+0.10)
    Level 2: output in plausible range [0, collection_size] (+0.10)
    Level 3: numeric closeness to target (+0.30 scaled)
    Level 4: exact match (+0.50 bonus)
    """
    if output is None:
        return 0.0

    score = 0.0

    # Level 1: output is numeric
    if not isinstance(output, (int, float)):
        return 0.05  # wrong-type floor

    score += 0.10

    # Level 2: output in plausible range
    collection = ctx.get(data_key, [])
    if 0 <= output <= len(collection):
        score += 0.10

    # Level 3: numeric closeness
    if expected == 0:
        closeness = 1.0 if output == 0 else max(0, 1.0 - abs(output) / 3.0)
    else:
        closeness = max(0, 1.0 - abs(output - expected) / max(abs(expected), 1))
    score += 0.30 * closeness

    # Level 4: exact match
    if output == expected:
        score += 0.50

    return score


# ---------------------------------------------------------------------------
# Evaluation: produces per-case scores (for lexicase)
# ---------------------------------------------------------------------------

def evaluate_per_case(individual, targets, contexts, score_fn):
    """Evaluate individual, returning per-(context, target) scores.

    Returns:
        overall: float (average of all case scores, with data-dependence gate)
        case_scores: list[float] (one per context x target pair)
    """
    prog = develop(individual.genotype)
    individual.program = prog

    if prog.ast is None:
        n_cases = len(targets) * len(contexts)
        return 0.0, [0.0] * n_cases

    # Data-dependence gate
    gate_outputs = [repr(prog.evaluate(ctx)) for ctx in contexts]
    if len(set(gate_outputs)) <= 1:
        n_cases = len(targets) * len(contexts)
        return 0.0, [0.0] * n_cases

    case_scores = []
    for name, target_fn, data_key in targets:
        for ctx in contexts:
            output = prog.evaluate(ctx)
            expected = target_fn(ctx)
            s = score_fn(output, expected, ctx, data_key)
            case_scores.append(s)

    overall = sum(case_scores) / len(case_scores) if case_scores else 0.0
    return overall, case_scores


# ---------------------------------------------------------------------------
# Selection methods
# ---------------------------------------------------------------------------

def lexicase_select(population, all_case_scores, rng):
    """Epsilon-lexicase selection.

    Shuffles test cases, filters to epsilon-best on each case sequentially.
    """
    n_cases = len(all_case_scores[0])
    cases = list(range(n_cases))
    rng.shuffle(cases)

    candidates = list(range(len(population)))

    for case_idx in cases:
        if len(candidates) <= 1:
            break
        best_score = max(all_case_scores[i][case_idx] for i in candidates)
        epsilon = 0.02  # small tolerance
        candidates = [i for i in candidates
                      if all_case_scores[i][case_idx] >= best_score - epsilon]

    return population[rng.choice(candidates)]


# ---------------------------------------------------------------------------
# Evolution loop
# ---------------------------------------------------------------------------

def run_experiment(
    pop_size: int,
    genotype_length: int,
    generations: int,
    contexts: list[dict],
    score_fn: Callable,
    use_lexicase: bool,
    seed: int,
    phase_boundaries: tuple[int, int] = (50, 150),
) -> dict:
    rng = random.Random(seed)
    develop.cache_clear()

    phase1_end, phase2_end = phase_boundaries

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    history = []

    for gen in range(generations):
        # Select targets based on phase
        if gen < phase1_end:
            active_targets = EASY_TARGETS
            phase = 1
        elif gen < phase2_end:
            active_targets = EASY_TARGETS + HARD_TARGETS
            phase = 2
        else:
            active_targets = HARD_TARGETS
            phase = 3

        # Evaluate all individuals
        all_case_scores = {}
        for idx, ind in enumerate(population):
            overall, cases = evaluate_per_case(ind, active_targets, contexts, score_fn)
            ind.fitness = overall
            all_case_scores[idx] = cases

        # Stats
        best = max(population, key=lambda i: i.fitness)
        avg_fit = sum(i.fitness for i in population) / len(population)
        bond_counts = [i.program.bond_count for i in population if i.program]
        avg_bonds = sum(bond_counts) / len(bond_counts) if bond_counts else 0
        max_bonds = max(bond_counts) if bond_counts else 0

        # Exact match on hard tasks (for reporting, always computed)
        hard_exact = {}
        if best.program and best.program.ast is not None:
            gate = [repr(best.program.evaluate(ctx)) for ctx in contexts]
            if len(set(gate)) > 1:
                for name, target_fn, _ in HARD_TARGETS:
                    matches = sum(1 for ctx in contexts
                                  if best.program.evaluate(ctx) == target_fn(ctx))
                    hard_exact[name] = matches / len(contexts)

        # Check if best program contains a filter expression
        has_filter = False
        if best.program and best.program.source:
            has_filter = "filter" in best.program.source

        entry = {
            "gen": gen, "phase": phase,
            "best_fitness": best.fitness, "avg_fitness": avg_fit,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "avg_bonds": avg_bonds, "max_bonds": max_bonds,
            "hard_exact": hard_exact,
            "has_filter": has_filter,
        }
        history.append(entry)

        # Reproduce
        children = []
        for _ in range(pop_size):
            if rng.random() < 0.7:
                if use_lexicase:
                    a = lexicase_select(population, all_case_scores, rng)
                    b = lexicase_select(population, all_case_scores, rng)
                else:
                    a = tournament_select(population, 3, rng)
                    b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                if use_lexicase:
                    parent = lexicase_select(population, all_case_scores, rng)
                else:
                    parent = tournament_select(population, 3, rng)
                child_geno = mutate(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        # Evaluate children
        child_case_scores = {}
        for idx, ind in enumerate(children):
            overall, cases = evaluate_per_case(ind, active_targets, contexts, score_fn)
            ind.fitness = overall
            child_case_scores[idx] = cases

        # (mu+lambda) selection based on overall fitness
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
    generations = 200
    n_seeds = 10

    print("=" * 70)
    print("Structural Staircase + Lexicase Selection Experiment")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print(f"Phases: easy(0-50) → easy+hard(50-150) → hard(150-200)")
    print(f"Contexts: 8 (3 anti-alias for rest^2 shortcut)")
    print()

    # Expected values for reference
    target_vals = [len([p for p in c["products"] if p["price"] > 200]) for c in contexts]
    rest2_vals = [max(0, len(c["products"]) - 2) for c in contexts]
    print(f"Hard target (price>200):    {target_vals}")
    print(f"Best shortcut (rest^2):     {rest2_vals}")
    anti_alias = [i for i, (a, b) in enumerate(zip(target_vals, rest2_vals)) if a != b]
    print(f"Anti-alias contexts:        {anti_alias} (rest^2 fails here)")
    print()

    conditions = [
        ("Baseline (partial+tournament)", score_partial_credit, False),
        ("Staircase + tournament", score_structural_staircase, False),
        ("Partial + lexicase", score_partial_credit, True),
        ("Staircase + lexicase", score_structural_staircase, True),
    ]

    all_results = {}

    for cond_name, score_fn, use_lex in conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        filter_count = 0
        for seed in range(n_seeds):
            result = run_experiment(
                pop_size, genotype_length, generations,
                contexts, score_fn, use_lex, seed,
            )
            cond_results.append(result)

            final = result["history"][-1]
            hard_exact = final["hard_exact"]
            he_str = [f'{hard_exact.get(n, 0):.2f}' for n, _, _ in HARD_TARGETS]
            filt = "FILTER!" if final["has_filter"] else ""

            if final["has_filter"]:
                filter_count += 1

            print(f"  Seed {seed:2d}: fit={final['best_fitness']:.3f} "
                  f"bonds={final['best_bonds']} "
                  f"hard_exact={he_str} "
                  f"{filt} "
                  f"src={final['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s, Filter programs found: {filter_count}/{n_seeds}\n")
        all_results[cond_name] = cond_results

    # === Summary ===
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    header = f"{'Condition':<30s} | {'Fit':>5s} | {'Bonds':>5s} | {'Hard exact':>10s} | {'Filters':>7s}"
    print(f"\n{header}")
    print(f"{'-'*30}-+-{'-'*5}-+-{'-'*5}-+-{'-'*10}-+-{'-'*7}")

    for cond_name, results in all_results.items():
        finals = [r["history"][-1] for r in results]
        avg_fit = sum(f["best_fitness"] for f in finals) / len(finals)
        avg_bonds = sum(f["best_bonds"] for f in finals) / len(finals)

        hard_exacts = []
        for f in finals:
            for name, _, _ in HARD_TARGETS:
                hard_exacts.append(f["hard_exact"].get(name, 0))
        avg_hard = sum(hard_exacts) / len(hard_exacts) if hard_exacts else 0

        n_filters = sum(1 for f in finals if f["has_filter"])

        print(f"{cond_name:<30s} | {avg_fit:5.3f} | {avg_bonds:5.1f} | {avg_hard:10.3f} | {n_filters:>3d}/{n_seeds}")

    # Phase transition detail for best condition
    print("\n--- Phase transition (Staircase + lexicase) ---")
    if "Staircase + lexicase" in all_results:
        results = all_results["Staircase + lexicase"]
        for gen_idx in [0, 25, 49, 50, 75, 100, 149, 150, 175, 199]:
            entries = [r["history"][gen_idx] for r in results]
            avg_fit = sum(e["best_fitness"] for e in entries) / len(entries)
            avg_bonds = sum(e["avg_bonds"] for e in entries) / len(entries)
            n_filt = sum(1 for e in entries if e["has_filter"])
            phase = entries[0]["phase"]
            print(f"  Gen {gen_idx:3d} (phase {phase}): fit={avg_fit:.3f} "
                  f"avg_bonds={avg_bonds:.1f} filters={n_filt}/{n_seeds}")

    # Check anti-alias context performance
    print("\n--- Anti-alias context analysis (final gen, Staircase + lexicase) ---")
    if "Staircase + lexicase" in all_results:
        results = all_results["Staircase + lexicase"]
        for seed, result in enumerate(results):
            final = result["history"][-1]
            if final["best_source"]:
                prog = develop(next(
                    i for i in [Individual(genotype=random_genotype(100, random.Random(0)))]
                    # Actually we need the best individual's genotype...
                    # Just report what we have
                ))
                # Report the exact scores we already have
                he = final["hard_exact"]
                has_f = "FILTER" if final["has_filter"] else "no-filter"
                if he:
                    print(f"  Seed {seed}: {has_f} hard_exact={he}")


if __name__ == "__main__":
    main()
