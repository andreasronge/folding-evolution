"""
Evolvable Chemistry Experiment (Stage 1).

Tests whether population-level evolution of chemistry parameters
(specifically distance-2 bond weight) breaks the complexity ceiling.

Design:
- Population of 100 individuals, genotype length 100, 200 generations
- One shared DevGenome per population, mutated every 50 generations
- DevGenome controls distance-2 bond weight (main lever from diagnostic)
- Compare: fixed chemistry (baseline) vs evolving chemistry
- Task: multi-target fitness on rich contexts
- Metrics per generation: best fitness, avg bonds, DevGenome state

The key question: does evolution discover that enabling d2 bonds
produces higher-complexity programs that score better?
"""

import random
import time
from collections import Counter
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dev_genome import (
    DevGenome, default_dev_genome, dev_genome_metrics, mutate_dev_genome,
)
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop_with_dev, develop, _count_bonds
from folding_evolution.selection import tournament_select


# Rich contexts from the task verification work
def make_rich_contexts():
    """Contexts with varying collection sizes and price ranges."""
    return [
        {
            "products": [
                {"id": 1, "price": 50, "name": "p1", "status": "active", "category": "tools"},
                {"id": 2, "price": 250, "name": "p2", "status": "active", "category": "tech"},
                {"id": 3, "price": 450, "name": "p3", "status": "inactive", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "a1", "department": "eng", "employee_id": 101},
                {"id": 2, "name": "a2", "department": "sales", "employee_id": 102},
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
                {"id": 1, "price": 150, "name": "q1", "status": "active", "category": "tech"},
                {"id": 2, "price": 350, "name": "q2", "status": "active", "category": "tech"},
                {"id": 3, "price": 550, "name": "q3", "status": "inactive", "category": "food"},
                {"id": 4, "price": 750, "name": "q4", "status": "active", "category": "tools"},
                {"id": 5, "price": 950, "name": "q5", "status": "active", "category": "tech"},
            ],
            "employees": [
                {"id": 1, "name": "b1", "department": "sales", "employee_id": 201},
                {"id": 2, "name": "b2", "department": "eng", "employee_id": 202},
                {"id": 3, "name": "b3", "department": "hr", "employee_id": 203},
                {"id": 4, "name": "b4", "department": "eng", "employee_id": 204},
            ],
            "orders": [{"id": 1, "amount": 50}, {"id": 2, "amount": 250}, {"id": 3, "amount": 900}],
            "expenses": [{"id": 1, "amount": 400, "category": "equipment"}],
        },
        {
            "products": [
                {"id": 1, "price": 100, "name": "r1", "status": "inactive", "category": "food"},
                {"id": 2, "price": 300, "name": "r2", "status": "active", "category": "tools"},
                {"id": 3, "price": 600, "name": "r3", "status": "active", "category": "tech"},
                {"id": 4, "price": 800, "name": "r4", "status": "active", "category": "tech"},
            ],
            "employees": [
                {"id": 1, "name": "c1", "department": "eng", "employee_id": 301},
                {"id": 2, "name": "c2", "department": "eng", "employee_id": 302},
                {"id": 3, "name": "c3", "department": "eng", "employee_id": 303},
            ],
            "orders": [{"id": 1, "amount": 200}],
            "expenses": [
                {"id": 1, "amount": 300, "category": "equipment"},
                {"id": 2, "amount": 600, "category": "travel"},
            ],
        },
        {
            "products": [
                {"id": 1, "price": 200, "name": "s1", "status": "active", "category": "tools"},
                {"id": 2, "price": 400, "name": "s2", "status": "inactive", "category": "food"},
                {"id": 3, "price": 700, "name": "s3", "status": "active", "category": "tech"},
                {"id": 4, "price": 850, "name": "s4", "status": "active", "category": "tools"},
                {"id": 5, "price": 100, "name": "s5", "status": "inactive", "category": "food"},
                {"id": 6, "price": 500, "name": "s6", "status": "active", "category": "tech"},
            ],
            "employees": [{"id": 1, "name": "d1", "department": "sales", "employee_id": 401}],
            "orders": [{"id": 1, "amount": 100}, {"id": 2, "amount": 300}, {"id": 3, "amount": 500}],
            "expenses": [{"id": 1, "amount": 200, "category": "travel"}],
        },
        {
            "products": [
                {"id": 1, "price": 350, "name": "t1", "status": "active", "category": "tech"},
                {"id": 2, "price": 650, "name": "t2", "status": "active", "category": "tools"},
            ],
            "employees": [
                {"id": 1, "name": "e1", "department": "hr", "employee_id": 501},
                {"id": 2, "name": "e2", "department": "eng", "employee_id": 502},
                {"id": 3, "name": "e3", "department": "eng", "employee_id": 503},
                {"id": 4, "name": "e4", "department": "sales", "employee_id": 504},
                {"id": 5, "name": "e5", "department": "eng", "employee_id": 505},
            ],
            "orders": [
                {"id": 1, "amount": 700}, {"id": 2, "amount": 800},
                {"id": 3, "amount": 50}, {"id": 4, "amount": 400},
            ],
            "expenses": [
                {"id": 1, "amount": 450, "category": "travel"},
                {"id": 2, "amount": 100, "category": "supplies"},
                {"id": 3, "amount": 350, "category": "equipment"},
            ],
        },
    ]


# Multi-target fitness: products-focused
TARGETS_PRODUCTS = [
    lambda ctx: len(ctx["products"]),               # count(products)
    lambda ctx: len(ctx["products"]) - 1,           # count(rest(products))
    lambda ctx: ctx["products"][0] if ctx["products"] else None,  # first(products)
]

# Multi-target fitness: employees-focused (for regime shift)
TARGETS_EMPLOYEES = [
    lambda ctx: len(ctx["employees"]),
    lambda ctx: len(ctx["employees"]) - 1,
    lambda ctx: ctx["employees"][0] if ctx["employees"] else None,
]


def evaluate_multi_target_dev(individual, targets, contexts, dev_genome):
    """Evaluate using evolvable chemistry."""
    prog = develop_with_dev(individual.genotype, dev_genome)
    individual.program = prog

    if prog.ast is None:
        return 0.0

    gate_outputs = []
    for ctx in contexts:
        gate_outputs.append(repr(prog.evaluate(ctx)))
    if len(set(gate_outputs)) <= 1:
        return 0.0

    scores = []
    for target_fn in targets:
        for ctx in contexts:
            output = prog.evaluate(ctx)
            expected = target_fn(ctx)
            scores.append(partial_credit(output, expected))
    return sum(scores) / len(scores) if scores else 0.0


def evaluate_multi_target_fixed(individual, targets, contexts):
    """Evaluate using fixed (standard) chemistry."""
    prog = develop(individual.genotype)
    individual.program = prog

    if prog.ast is None:
        return 0.0

    gate_outputs = []
    for ctx in contexts:
        gate_outputs.append(repr(prog.evaluate(ctx)))
    if len(set(gate_outputs)) <= 1:
        return 0.0

    scores = []
    for target_fn in targets:
        for ctx in contexts:
            output = prog.evaluate(ctx)
            expected = target_fn(ctx)
            scores.append(partial_credit(output, expected))
    return sum(scores) / len(scores) if scores else 0.0


def run_evolution(
    pop_size: int,
    genotype_length: int,
    generations: int,
    targets: list,
    contexts: list[dict],
    dev_genome: DevGenome | None,
    dev_mutate_every: int,
    seed: int,
) -> dict:
    """Run evolution with optional evolvable chemistry.

    When dev_genome is None, uses fixed chemistry (standard develop()).
    When provided, uses develop_with_dev() and mutates dev_genome every
    dev_mutate_every generations.
    """
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    history = []
    dg = dev_genome
    dg_history = []

    for gen in range(generations):
        # Evaluate
        for ind in population:
            if dg is not None:
                ind.fitness = evaluate_multi_target_dev(ind, targets, contexts, dg)
            else:
                ind.fitness = evaluate_multi_target_fixed(ind, targets, contexts)

        # Stats
        best = max(population, key=lambda i: i.fitness)
        avg_fit = sum(i.fitness for i in population) / len(population)
        bond_counts = [i.program.bond_count for i in population if i.program]
        avg_bonds = sum(bond_counts) / len(bond_counts) if bond_counts else 0
        max_bonds = max(bond_counts) if bond_counts else 0

        history.append({
            "gen": gen,
            "best_fitness": best.fitness,
            "avg_fitness": avg_fit,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "avg_bonds": avg_bonds,
            "max_bonds": max_bonds,
        })

        # Dev genome mutation (population-level)
        if dg is not None and dev_mutate_every > 0 and gen > 0 and gen % dev_mutate_every == 0:
            candidate_dg = mutate_dev_genome(dg, rng)

            # Test candidate: evaluate a sample of population under new chemistry
            sample = rng.sample(population, min(20, len(population)))
            old_fit = sum(
                evaluate_multi_target_dev(Individual(genotype=i.genotype), targets, contexts, dg)
                for i in sample
            ) / len(sample)
            new_fit = sum(
                evaluate_multi_target_dev(Individual(genotype=i.genotype), targets, contexts, candidate_dg)
                for i in sample
            ) / len(sample)

            if new_fit >= old_fit - 0.01:  # accept if not significantly worse
                dg = candidate_dg
                dg_history.append({"gen": gen, "accepted": True, "metrics": dev_genome_metrics(dg)})
            else:
                dg_history.append({"gen": gen, "accepted": False})

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

        # Evaluate children
        for ind in children:
            if dg is not None:
                ind.fitness = evaluate_multi_target_dev(ind, targets, contexts, dg)
            else:
                ind.fitness = evaluate_multi_target_fixed(ind, targets, contexts)

        # (mu+lambda) selection
        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {
        "history": history,
        "dg_history": dg_history,
        "final_dev_genome": dg,
    }


def main():
    contexts = make_rich_contexts()
    pop_size = 100
    genotype_length = 100
    generations = 200
    n_seeds = 5
    dev_mutate_every = 50

    print("=" * 70)
    print("Evolvable Chemistry Experiment (Stage 1)")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}")
    print(f"Seeds: {n_seeds}, Dev mutate every: {dev_mutate_every} gens")
    print()

    # --- Run fixed chemistry baseline ---
    print("Running FIXED chemistry baseline...")
    fixed_results = []
    t0 = time.time()
    for seed in range(n_seeds):
        result = run_evolution(
            pop_size, genotype_length, generations,
            TARGETS_PRODUCTS, contexts,
            dev_genome=None, dev_mutate_every=0, seed=seed,
        )
        final = result["history"][-1]
        print(f"  Seed {seed}: best_fit={final['best_fitness']:.3f} "
              f"avg_bonds={final['avg_bonds']:.1f} max_bonds={final['max_bonds']} "
              f"src={final['best_source']}")
        fixed_results.append(result)
    fixed_time = time.time() - t0
    print(f"  Total time: {fixed_time:.1f}s\n")

    # --- Run evolvable chemistry ---
    print("Running EVOLVABLE chemistry...")
    evolving_results = []
    t0 = time.time()
    for seed in range(n_seeds):
        dg = default_dev_genome()
        result = run_evolution(
            pop_size, genotype_length, generations,
            TARGETS_PRODUCTS, contexts,
            dev_genome=dg, dev_mutate_every=dev_mutate_every, seed=seed,
        )
        final = result["history"][-1]
        final_dg = result["final_dev_genome"]
        d2w = final_dg.distance_weights[1] if final_dg else 0
        print(f"  Seed {seed}: best_fit={final['best_fitness']:.3f} "
              f"avg_bonds={final['avg_bonds']:.1f} max_bonds={final['max_bonds']} "
              f"d2_weight={d2w:.3f} "
              f"src={final['best_source']}")
        evolving_results.append(result)
    evolving_time = time.time() - t0
    print(f"  Total time: {evolving_time:.1f}s\n")

    # --- Run fixed chemistry with d2 pre-enabled ---
    print("Running FIXED chemistry with d2=1.0 (upper bound)...")
    d2_fixed_results = []
    t0 = time.time()
    for seed in range(n_seeds):
        dg = default_dev_genome()
        dg_d2 = DevGenome(
            affinities=dg.affinities,
            assembled_preference=dg.assembled_preference,
            distance_weights=(1.0, 1.0),  # d2 always on
            bond_threshold=dg.bond_threshold,
            stability_bonus=dg.stability_bonus,
            occupancy_penalty=dg.occupancy_penalty,
            top_k=dg.top_k,
        )
        result = run_evolution(
            pop_size, genotype_length, generations,
            TARGETS_PRODUCTS, contexts,
            dev_genome=dg_d2, dev_mutate_every=0, seed=seed,
        )
        final = result["history"][-1]
        print(f"  Seed {seed}: best_fit={final['best_fitness']:.3f} "
              f"avg_bonds={final['avg_bonds']:.1f} max_bonds={final['max_bonds']} "
              f"src={final['best_source']}")
        d2_fixed_results.append(result)
    d2_time = time.time() - t0
    print(f"  Total time: {d2_time:.1f}s\n")

    # --- Summary ---
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    def summarize(results, label):
        finals = [r["history"][-1] for r in results]
        avg_best_fit = sum(f["best_fitness"] for f in finals) / len(finals)
        avg_avg_bonds = sum(f["avg_bonds"] for f in finals) / len(finals)
        avg_max_bonds = sum(f["max_bonds"] for f in finals) / len(finals)
        avg_best_bonds = sum(f["best_bonds"] for f in finals) / len(finals)
        print(f"  {label:30s}: best_fit={avg_best_fit:.3f}  "
              f"avg_bonds={avg_avg_bonds:.1f}  max_bonds={avg_max_bonds:.0f}  "
              f"best_bonds={avg_best_bonds:.1f}")

    summarize(fixed_results, "Fixed chemistry (baseline)")
    summarize(evolving_results, "Evolvable chemistry")
    summarize(d2_fixed_results, "Fixed d2=1.0 (upper bound)")

    # Dev genome evolution trace
    print("\nDev genome evolution trace (evolvable runs):")
    for seed, result in enumerate(evolving_results):
        dg_hist = result["dg_history"]
        accepted = sum(1 for h in dg_hist if h.get("accepted"))
        total = len(dg_hist)
        final_dg = result["final_dev_genome"]
        if final_dg:
            m = dev_genome_metrics(final_dg)
            print(f"  Seed {seed}: {accepted}/{total} mutations accepted, "
                  f"d2={m['distance_d2_weight']:.3f} "
                  f"assembled_pref={m['assembled_preference']:.2f} "
                  f"threshold={m['bond_threshold']:.3f}")


if __name__ == "__main__":
    main()
