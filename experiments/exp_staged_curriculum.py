"""
Staged Curriculum + Reachable Chemistry Variation Experiment.

Tests whether harder tasks create selection pressure for the evolvable
chemistry to discover useful longer-range bonding.

Three-phase curriculum:
  Phase 1 (gen 0-50):   easy tasks only (count, count-rest -- 2-bond solutions)
  Phase 2 (gen 50-150): easy + hard tasks (count-filter -- 5-bond solutions)
  Phase 3 (gen 150-200): hard tasks only (full pressure for 5-bond programs)

Three conditions:
  A. Fixed d1-only chemistry (baseline)
  B. Fixed d2=0.3 chemistry (tests whether d2 helps on hard tasks)
  C. Evolvable chemistry, d2 initialized U(0.1, 0.3) with occasional large jumps

Measures:
  - Best fitness per generation (overall and per-task)
  - Bond-count distribution
  - Whether best programs are structurally correct (actual filter expressions)
  - For condition C: d2_weight trajectory
"""

import random
import time
from collections import Counter
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.dev_genome import (
    DevGenome, default_dev_genome, dev_genome_metrics, mutate_dev_genome,
)
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_with_dev, _count_bonds
from folding_evolution.selection import tournament_select


# ---------------------------------------------------------------------------
# Contexts (8 discriminating contexts from strict profiler)
# ---------------------------------------------------------------------------

def make_contexts():
    """8 contexts with varying collection sizes and price distributions."""
    return [
        {
            "products": [
                {"id": 1, "price": 50, "name": "p1", "status": "active", "category": "tools"},
                {"id": 2, "price": 120, "name": "p2", "status": "inactive", "category": "tech"},
                {"id": 3, "price": 350, "name": "p3", "status": "active", "category": "food"},
            ],
            "employees": [
                {"id": i, "name": f"a{i}", "department": d, "employee_id": 100+i}
                for i, d in enumerate(["eng", "sales", "eng", "hr", "eng"], 1)
            ],
            "orders": [{"id": 1, "amount": 150}, {"id": 2, "amount": 350}],
            "expenses": [
                {"id": 1, "amount": 75, "category": "travel"},
                {"id": 2, "amount": 225, "category": "equipment"},
                {"id": 3, "amount": 550, "category": "travel"},
            ],
        },
        {
            "products": [
                {"id": i, "price": p, "name": f"q{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (80, "active", "tech"), (190, "active", "food"),
                    (310, "inactive", "tools"), (450, "active", "tech"),
                    (620, "active", "food"), (780, "inactive", "tech"),
                ], 1)
            ],
            "employees": [
                {"id": i, "name": f"b{i}", "department": d, "employee_id": 200+i}
                for i, d in enumerate(["sales", "eng"], 1)
            ],
            "orders": [{"id": 1, "amount": 50}, {"id": 2, "amount": 250}, {"id": 3, "amount": 900}],
            "expenses": [{"id": 1, "amount": 400, "category": "equipment"}],
        },
        {
            "products": [
                {"id": i, "price": p, "name": f"r{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (430, "active", "food"), (710, "active", "tools"),
                ], 1)
            ],
            "employees": [
                {"id": i, "name": f"c{i}", "department": d, "employee_id": 300+i}
                for i, d in enumerate(["eng", "hr", "sales"], 1)
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
        {
            "products": [
                {"id": i, "price": p, "name": f"s{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (170, "inactive", "tools"), (90, "active", "food"),
                    (530, "active", "tech"), (650, "active", "tech"),
                    (840, "inactive", "tools"),
                ], 1)
            ],
            "employees": [
                {"id": i, "name": f"d{i}", "department": d, "employee_id": 400+i}
                for i, d in enumerate(["eng", "eng", "eng", "sales"], 1)
            ],
            "orders": [{"id": 1, "amount": 300}, {"id": 2, "amount": 700}],
            "expenses": [{"id": 1, "amount": 500, "category": "travel"}, {"id": 2, "amount": 100, "category": "supplies"}],
        },
        {
            "products": [
                {"id": i, "price": p, "name": f"t{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (40, "active", "food"), (110, "active", "tech"),
                    (160, "inactive", "tools"), (290, "active", "food"),
                ], 1)
            ],
            "employees": [
                {"id": i, "name": f"e{i}", "department": d, "employee_id": 500+i}
                for i, d in enumerate(["hr", "eng", "sales", "eng", "hr", "eng"], 1)
            ],
            "orders": [{"id": i, "amount": a} for i, a in enumerate([200, 400, 600, 150], 1)],
            "expenses": [{"id": 1, "amount": 300, "category": "equipment"}, {"id": 2, "amount": 700, "category": "travel"}],
        },
        {
            "products": [
                {"id": i, "price": p, "name": f"u{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (150, "active", "tech"), (60, "inactive", "food"),
                    (340, "active", "tools"), (510, "active", "tech"),
                    (670, "active", "food"), (890, "inactive", "tools"),
                    (550, "active", "tech"),
                ], 1)
            ],
            "employees": [{"id": 1, "name": "f1", "department": "eng", "employee_id": 601}],
            "orders": [{"id": 1, "amount": 800}],
            "expenses": [
                {"id": 1, "amount": 250, "category": "travel"},
                {"id": 2, "amount": 450, "category": "supplies"},
                {"id": 3, "amount": 120, "category": "equipment"},
            ],
        },
        {
            "products": [
                {"id": 1, "price": 920, "name": "v1", "status": "active", "category": "tools"},
            ],
            "employees": [
                {"id": i, "name": f"g{i}", "department": d, "employee_id": 700+i}
                for i, d in enumerate(["sales", "eng", "eng", "hr", "eng", "sales", "eng"], 1)
            ],
            "orders": [{"id": 1, "amount": 450}, {"id": 2, "amount": 50}],
            "expenses": [{"id": 1, "amount": 900, "category": "travel"}],
        },
        {
            "products": [
                {"id": i, "price": p, "name": f"w{i}", "status": s, "category": c}
                for i, (p, s, c) in enumerate([
                    (30, "inactive", "food"), (180, "active", "tech"),
                    (270, "active", "tools"), (360, "active", "food"),
                    (490, "inactive", "tech"), (580, "active", "tools"),
                    (750, "active", "tech"), (910, "active", "food"),
                ], 1)
            ],
            "employees": [
                {"id": i, "name": f"h{i}", "department": d, "employee_id": 800+i}
                for i, d in enumerate(["eng", "hr", "eng"], 1)
            ],
            "orders": [{"id": i, "amount": a} for i, a in enumerate([120, 330, 560, 780, 990], 1)],
            "expenses": [
                {"id": 1, "amount": 160, "category": "supplies"},
                {"id": 2, "amount": 340, "category": "travel"},
                {"id": 3, "amount": 620, "category": "equipment"},
                {"id": 4, "amount": 850, "category": "travel"},
            ],
        },
    ]


# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------

EASY_TARGETS: list[tuple[str, Callable]] = [
    ("count(products)", lambda ctx: len(ctx["products"])),
    ("count(employees)", lambda ctx: len(ctx["employees"])),
    ("count(rest(products))", lambda ctx: len(ctx["products"]) - 1),
]

HARD_TARGETS: list[tuple[str, Callable]] = [
    ("count(filter(price>200, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 200])),
    ("count(filter(amount>300, orders))",
     lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 300])),
]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_targets(individual, targets, contexts, dev_genome=None):
    """Evaluate individual on named targets. Returns (overall_score, per_target_scores)."""
    if dev_genome is not None:
        prog = develop_with_dev(individual.genotype, dev_genome)
    else:
        prog = develop(individual.genotype)
    individual.program = prog

    if prog.ast is None:
        return 0.0, {name: 0.0 for name, _ in targets}

    # Data-dependence gate
    gate_outputs = [repr(prog.evaluate(ctx)) for ctx in contexts]
    if len(set(gate_outputs)) <= 1:
        return 0.0, {name: 0.0 for name, _ in targets}

    per_target = {}
    all_scores = []
    for name, target_fn in targets:
        scores = []
        for ctx in contexts:
            output = prog.evaluate(ctx)
            expected = target_fn(ctx)
            scores.append(partial_credit(output, expected))
        avg = sum(scores) / len(scores)
        per_target[name] = avg
        all_scores.extend(scores)

    overall = sum(all_scores) / len(all_scores) if all_scores else 0.0
    return overall, per_target


def evaluate_exact(individual, targets, contexts, dev_genome=None):
    """Exact-match evaluation for reporting (not used in selection)."""
    if dev_genome is not None:
        prog = develop_with_dev(individual.genotype, dev_genome)
    else:
        prog = develop(individual.genotype)

    if prog.ast is None:
        return {name: 0.0 for name, _ in targets}

    gate_outputs = [repr(prog.evaluate(ctx)) for ctx in contexts]
    if len(set(gate_outputs)) <= 1:
        return {name: 0.0 for name, _ in targets}

    per_target = {}
    for name, target_fn in targets:
        matches = sum(1 for ctx in contexts if prog.evaluate(ctx) == target_fn(ctx))
        per_target[name] = matches / len(contexts)
    return per_target


# ---------------------------------------------------------------------------
# Evolution loop with staged curriculum
# ---------------------------------------------------------------------------

def run_staged(
    pop_size: int,
    genotype_length: int,
    generations: int,
    contexts: list[dict],
    dev_genome: DevGenome | None,
    evolve_chemistry: bool,
    dev_mutate_every: int,
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

    dg = dev_genome
    history = []
    dg_trace = []

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

        # Evaluate
        for ind in population:
            ind.fitness, _ = evaluate_targets(ind, active_targets, contexts, dg)

        # Stats
        best = max(population, key=lambda i: i.fitness)
        avg_fit = sum(i.fitness for i in population) / len(population)
        bond_counts = [i.program.bond_count for i in population if i.program]
        avg_bonds = sum(bond_counts) / len(bond_counts) if bond_counts else 0
        max_bonds = max(bond_counts) if bond_counts else 0
        bonds_4plus = sum(1 for b in bond_counts if b >= 4) / len(bond_counts) * 100 if bond_counts else 0

        # Exact match on all tasks (for reporting)
        exact = evaluate_exact(best, EASY_TARGETS + HARD_TARGETS, contexts, dg)

        entry = {
            "gen": gen, "phase": phase,
            "best_fitness": best.fitness, "avg_fitness": avg_fit,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "avg_bonds": avg_bonds, "max_bonds": max_bonds,
            "pct_4plus_bonds": bonds_4plus,
            "exact_scores": exact,
        }
        history.append(entry)

        # Dev genome evolution
        if evolve_chemistry and dg is not None and dev_mutate_every > 0 and gen > 0 and gen % dev_mutate_every == 0:
            # Occasional large jump on d2_weight (p=0.1)
            if rng.random() < 0.1:
                candidate_dg = mutate_dev_genome(dg, rng, sigma=0.05)
                # Replace d2 with uniform draw
                candidate_dg = DevGenome(
                    affinities=candidate_dg.affinities,
                    assembled_preference=candidate_dg.assembled_preference,
                    distance_weights=(candidate_dg.distance_weights[0], rng.uniform(0.0, 1.0)),
                    bond_threshold=candidate_dg.bond_threshold,
                    stability_bonus=candidate_dg.stability_bonus,
                    occupancy_penalty=candidate_dg.occupancy_penalty,
                    top_k=candidate_dg.top_k,
                )
            else:
                candidate_dg = mutate_dev_genome(dg, rng, sigma=0.05)

            # Test: evaluate sample under old and new chemistry
            sample = rng.sample(population, min(20, len(population)))
            old_fit = sum(
                evaluate_targets(Individual(genotype=i.genotype), active_targets, contexts, dg)[0]
                for i in sample
            ) / len(sample)
            new_fit = sum(
                evaluate_targets(Individual(genotype=i.genotype), active_targets, contexts, candidate_dg)[0]
                for i in sample
            ) / len(sample)

            accepted = new_fit >= old_fit - 0.01
            if accepted:
                dg = candidate_dg

            dg_trace.append({
                "gen": gen, "accepted": accepted,
                "d2_weight": dg.distance_weights[1],
                "old_fit": old_fit, "new_fit": new_fit,
            })

        # Reproduce (mu+lambda)
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
            ind.fitness, _ = evaluate_targets(ind, active_targets, contexts, dg)

        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {"history": history, "dg_trace": dg_trace, "final_dg": dg}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    contexts = make_contexts()
    pop_size = 100
    genotype_length = 100
    generations = 200
    n_seeds = 5
    dev_mutate_every = 25

    print("=" * 70)
    print("Staged Curriculum + Reachable Chemistry Experiment")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print(f"Phases: easy(0-50) → easy+hard(50-150) → hard(150-200)")
    print(f"Dev mutate every: {dev_mutate_every} gens")
    print()

    conditions = [
        ("A: Fixed d1-only", None, False),
        ("B: Fixed d2=0.3", "fixed_d2", False),
        ("C: Evolvable d2", "evolvable", True),
    ]

    all_results = {}

    for cond_name, cond_type, evolve in conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        for seed in range(n_seeds):
            if cond_type is None:
                dg = None
            elif cond_type == "fixed_d2":
                base = default_dev_genome()
                dg = DevGenome(
                    affinities=base.affinities,
                    assembled_preference=base.assembled_preference,
                    distance_weights=(1.0, 0.3),
                    bond_threshold=base.bond_threshold,
                    stability_bonus=base.stability_bonus,
                    occupancy_penalty=base.occupancy_penalty,
                    top_k=base.top_k,
                )
            else:  # evolvable
                base = default_dev_genome()
                rng_init = random.Random(seed + 1000)
                d2_init = rng_init.uniform(0.1, 0.3)
                dg = DevGenome(
                    affinities=base.affinities,
                    assembled_preference=base.assembled_preference,
                    distance_weights=(1.0, d2_init),
                    bond_threshold=base.bond_threshold,
                    stability_bonus=base.stability_bonus,
                    occupancy_penalty=base.occupancy_penalty,
                    top_k=base.top_k,
                )

            result = run_staged(
                pop_size, genotype_length, generations,
                contexts, dg, evolve, dev_mutate_every, seed,
            )
            cond_results.append(result)

            final = result["history"][-1]
            exact = final["exact_scores"]
            hard_exact = [exact.get(n, 0) for n, _ in HARD_TARGETS]
            d2w = result["final_dg"].distance_weights[1] if result["final_dg"] else 0

            print(f"  Seed {seed}: fit={final['best_fitness']:.3f} "
                  f"bonds={final['best_bonds']} avg_bonds={final['avg_bonds']:.1f} "
                  f"4+%={final['pct_4plus_bonds']:.0f}% "
                  f"hard_exact={[f'{h:.2f}' for h in hard_exact]} "
                  f"d2={d2w:.3f} "
                  f"src={final['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s\n")
        all_results[cond_name] = cond_results

    # === Summary ===
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n{'Condition':<25s} | {'Best fit':>8s} | {'Avg bonds':>9s} | {'4+ %':>5s} | {'Hard exact avg':>14s}")
    print(f"{'-'*25}-+-{'-'*8}-+-{'-'*9}-+-{'-'*5}-+-{'-'*14}")

    for cond_name, results in all_results.items():
        finals = [r["history"][-1] for r in results]
        avg_best = sum(f["best_fitness"] for f in finals) / len(finals)
        avg_bonds = sum(f["avg_bonds"] for f in finals) / len(finals)
        avg_4plus = sum(f["pct_4plus_bonds"] for f in finals) / len(finals)

        # Average exact-match on hard tasks
        hard_exacts = []
        for f in finals:
            for name, _ in HARD_TARGETS:
                hard_exacts.append(f["exact_scores"].get(name, 0))
        avg_hard_exact = sum(hard_exacts) / len(hard_exacts) if hard_exacts else 0

        print(f"{cond_name:<25s} | {avg_best:8.3f} | {avg_bonds:9.1f} | {avg_4plus:4.0f}% | {avg_hard_exact:14.3f}")

    # Phase transition analysis
    print("\n--- Phase transition analysis (avg across seeds) ---")
    for cond_name, results in all_results.items():
        print(f"\n{cond_name}:")
        for phase_gen in [0, 49, 50, 100, 149, 150, 199]:
            if phase_gen < generations:
                entries = [r["history"][phase_gen] for r in results]
                avg_fit = sum(e["best_fitness"] for e in entries) / len(entries)
                avg_bonds = sum(e["avg_bonds"] for e in entries) / len(entries)
                phase = entries[0]["phase"]
                print(f"  Gen {phase_gen:3d} (phase {phase}): fit={avg_fit:.3f} avg_bonds={avg_bonds:.1f}")

    # d2 evolution trace for condition C
    if "C: Evolvable d2" in all_results:
        print("\n--- d2_weight evolution trace (Condition C) ---")
        for seed, result in enumerate(all_results["C: Evolvable d2"]):
            trace = result["dg_trace"]
            if trace:
                d2_vals = [(t["gen"], t["d2_weight"], t["accepted"]) for t in trace]
                print(f"  Seed {seed}: {[(g, f'{d:.3f}', 'Y' if a else 'N') for g, d, a in d2_vals]}")


if __name__ == "__main__":
    main()
