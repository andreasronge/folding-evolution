"""
Experiment 1.12: Generalization — Is Scaffold Protection Task-Specific?

Two levels of generalization test:

Level 1: Same target (filter-price), generic scaffold metric.
  Does Pareto(fitness, bond_count) work as well as Pareto(fitness, scaffold_stage)?
  bond_count requires no knowledge of the target — it just measures how many
  assembly bonds formed, i.e. compositional complexity.

Level 2: Different target, generic scaffold metric.
  Target: count(filter(fn x (> (get x :amount) VALUE)) data/orders)
  The scaffold_stage classifier checks for :price specifically and returns 0
  for :amount programs. So Pareto(fitness, scaffold_stage) has NO signal.
  Only Pareto(fitness, bond_count) can help.

If bond_count Pareto works on both target families, the result is fully
general: you don't need to know the target to protect developmental
intermediates, you just need to value compositional structure.

Conditions:
  A. Continuous selection, original targets (baseline)
  B. Pareto(fitness, scaffold_stage), original targets (1.11 positive control)
  C. Pareto(fitness, bond_count), original targets (Level 1 test)
  D. Continuous selection, orders targets (Level 2 baseline)
  E. Pareto(fitness, bond_count), orders targets (Level 2 test)
"""

import random
import time
from collections import Counter

from folding_evolution.alphabet import random_genotype
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_batch
from folding_evolution.dynamics import (
    partial_credit,
    _develop_and_score_vm, _develop_and_score_python,
    _develop_population, evaluate_multi_target,
)
from folding_evolution.selection import tournament_select

try:
    from _folding_rust import (
        RustContexts as _RustContexts,
        RustTargetOutputs as _RustTargetOutputs,
    )
    _USE_RUST_VM = True
except ImportError:
    _USE_RUST_VM = False

from exp_archive_reinjection import scaffold_stage, make_contexts, TARGETS


# ---------------------------------------------------------------------------
# Target families
# ---------------------------------------------------------------------------

# Original: filter on products by price
PRICE_TARGETS = TARGETS  # [count(filter(price>200, products)), count(products)]

# New: filter on orders by amount — scaffold_stage has NO signal here
ORDER_TARGETS = [
    ("count(filter(amount>200, orders))",
     lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 200])),
    ("count(orders)", lambda ctx: len(ctx["orders"])),
]


# ---------------------------------------------------------------------------
# Motifs — screened for :price, but also include generic bond-formers
# ---------------------------------------------------------------------------

SCREENED_MOTIFS = [
    'DaL', 'KaD', 'aDM', 'jDa', '3aD', 'DaB', 'caD', 'aJD',
    'aDT', 'QaD', 'iDa', 'raD', 'aDl', 'aDi', 'aDG', 'aDP',
    'aD', 'Da', 'KS', 'A7',
]

# For the orders/amount target, we need motifs with 'f' (:amount) and 'U' (data/orders)
# Screen the top bond-formers for :amount the same way we did for :price
# Df = (get x :amount), fD reversed, KU = > + data/orders, etc.
ORDER_MOTIFS = [
    'DfL', 'KfD', 'fDM', 'jDf', '3fD', 'DfB', 'cfD', 'fJD',
    'fDT', 'QfD', 'iDf', 'rfD', 'fDl', 'fDi', 'fDG', 'fDP',
    'fD', 'Df', 'KU', 'AU',
]


def mutate_with_motif(genotype: str, rng: random.Random, motifs: list[str]) -> str:
    if rng.random() < 0.75:
        motif = rng.choice(motifs)
        if len(motif) > len(genotype):
            return mutate(genotype, rng)
        pos = rng.randint(0, len(genotype) - len(motif))
        return genotype[:pos] + motif + genotype[pos + len(motif):]
    return mutate(genotype, rng)


# ---------------------------------------------------------------------------
# Pareto selection variants
# ---------------------------------------------------------------------------

def _pareto_sort(scored_list, pop_size):
    """NSGA-II fast non-dominated sort. O(M*N^2) total, not per-front.

    scored_list = [(ind, obj1, obj2), ...]. Returns pop_size individuals.
    """
    n = len(scored_list)
    # For each i: count of solutions dominating i, and list of solutions i dominates
    domination_count = [0] * n
    dominates = [[] for _ in range(n)]

    for i in range(n):
        _, fi, si = scored_list[i]
        for j in range(i + 1, n):
            _, fj, sj = scored_list[j]
            # i dominates j?
            if fi >= fj and si >= sj and (fi > fj or si > sj):
                dominates[i].append(j)
                domination_count[j] += 1
            # j dominates i?
            elif fj >= fi and sj >= si and (fj > fi or sj > si):
                dominates[j].append(i)
                domination_count[i] += 1

    # Front 0: non-dominated
    fronts = [[i for i in range(n) if domination_count[i] == 0]]

    # Build subsequent fronts
    while fronts[-1]:
        next_front = []
        for i in fronts[-1]:
            for j in dominates[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        if next_front:
            fronts.append(next_front)
        else:
            break

    # Fill population front by front
    selected = []
    for front in fronts:
        if len(selected) + len(front) <= pop_size:
            selected.extend(front)
        else:
            # Partial: prefer higher second objective
            front_scored = [(i, scored_list[i][2]) for i in front]
            front_scored.sort(key=lambda x: x[1], reverse=True)
            for i, _ in front_scored:
                if len(selected) >= pop_size:
                    break
                selected.append(i)
            break

    return [Individual(genotype=scored_list[i][0].genotype) for i in selected]


def pareto_scaffold(population, pop_size):
    scored = [(ind, ind.fitness, scaffold_stage(ind.program) if ind.program else 0)
              for ind in population]
    return _pareto_sort(scored, pop_size)


def pareto_bonds(population, pop_size):
    # Cap bond_count at 10 to limit the number of Pareto fronts.
    # Bonds beyond 10 are typically junk accumulation, not useful structure.
    scored = [(ind, ind.fitness,
               min(ind.program.bond_count if ind.program else 0, 10))
              for ind in population]
    return _pareto_sort(scored, pop_size)


# ---------------------------------------------------------------------------
# Scaffold stage for orders/amount targets (for measuring, not selecting)
# ---------------------------------------------------------------------------

def scaffold_stage_generic(prog):
    """Generic scaffold stage based on structural complexity, not specific fields.

    0: no bonds
    1: any 1-bond program (get+key, count+data, etc.)
    2: any 2-bond (comparator+operands, fn+expr, etc.)
    3: any 3-bond
    4: any 4-bond (filter/map + fn + data)
    5: any 5+ bond (wrapper + higher-order)
    """
    if prog is None or prog.ast is None:
        return 0
    bc = prog.bond_count
    if bc >= 5:
        return 5
    return bc


# ---------------------------------------------------------------------------
# Evolution engine
# ---------------------------------------------------------------------------

def run_seed(
    pop_size, genotype_length, total_gens, contexts, targets, seed,
    selection_mode,  # "select", "pareto_scaffold", "pareto_bonds"
    motifs,
    scaffold_every=5,
):
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    use_vm = _USE_RUST_VM
    rust_ctx = None
    rust_targets = None
    if use_vm:
        rust_ctx = _RustContexts(contexts)
        target_outputs = [[t(ctx) for ctx in contexts] for t in targets]
        rust_targets = _RustTargetOutputs(target_outputs)

    best_fitness_ever = 0.0
    best_source_ever = None
    max_stage_ever = 0
    max_bonds_ever = 0
    first_s3 = None
    first_s4 = None
    first_s5 = None
    first_b3 = None  # first 3+ bonds
    first_b4 = None
    first_b5 = None
    stage_trace = []
    filter_programs = []

    for gen in range(total_gens):
        # Develop and score
        if use_vm:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)
            for ind in population:
                ind.fitness = evaluate_multi_target(ind, targets, contexts)

        best = max(population, key=lambda i: i.fitness)
        if best.fitness > best_fitness_ever:
            best_fitness_ever = best.fitness
            best_source_ever = best.program.source if best.program else None

        # Scaffold detection (sampled)
        if gen % scaffold_every == 0 or gen == total_gens - 1:
            genotypes = [ind.genotype for ind in population]
            programs = develop_batch(genotypes)
            for ind, prog in zip(population, programs):
                ind.program = prog

            sc = Counter()
            bc = Counter()
            for ind in population:
                stage = scaffold_stage(ind.program)
                bonds = ind.program.bond_count if ind.program else 0
                sc[stage] += 1
                bc[bonds] += 1

                if stage >= 4 and ind.program.source:
                    src = ind.program.source
                    if "filter" in src and "get x :" in src:
                        filter_programs.append((gen, src, ind.fitness))

            s1p = sum(c for s, c in sc.items() if s >= 1)
            s2p = sum(c for s, c in sc.items() if s >= 2)
            s3p = sum(c for s, c in sc.items() if s >= 3)
            b3p = sum(c for b, c in bc.items() if b >= 3)
            b4p = sum(c for b, c in bc.items() if b >= 4)
            b5p = sum(c for b, c in bc.items() if b >= 5)
            avg_bonds = sum(b * c for b, c in bc.items()) / pop_size

            stage_trace.append((gen, s1p, s2p, s3p, b3p, b4p, b5p, avg_bonds))

            for s in sc:
                if s > max_stage_ever: max_stage_ever = s
            for b in bc:
                if b > max_bonds_ever: max_bonds_ever = b

            if s3p > 0 and first_s3 is None: first_s3 = gen
            if sc.get(4, 0) + sc.get(5, 0) > 0 and first_s4 is None: first_s4 = gen
            if sc.get(5, 0) > 0 and first_s5 is None: first_s5 = gen
            if b3p > 0 and first_b3 is None: first_b3 = gen
            if b4p > 0 and first_b4 is None: first_b4 = gen
            if b5p > 0 and first_b5 is None: first_b5 = gen

        # Reproduce
        children = []
        for _ in range(pop_size):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = mutate_with_motif(parent.genotype, rng, motifs)
            children.append(Individual(genotype=child_geno))

        # Evaluate children
        if use_vm:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)
            for ind in children:
                ind.fitness = evaluate_multi_target(ind, targets, contexts)

        # Selection
        combined = population + children

        if selection_mode in ("pareto_scaffold", "pareto_bonds"):
            # Need programs for Pareto objectives
            genotypes = [ind.genotype for ind in combined]
            programs = develop_batch(genotypes)
            for ind, prog in zip(combined, programs):
                ind.program = prog

            if selection_mode == "pareto_scaffold":
                population = pareto_scaffold(combined, pop_size)
            else:
                population = pareto_bonds(combined, pop_size)
        else:
            combined.sort(key=lambda ind: ind.fitness, reverse=True)
            population = [Individual(genotype=ind.genotype)
                          for ind in combined[:pop_size]]

    return {
        "best_fitness": best_fitness_ever,
        "best_source": best_source_ever,
        "max_stage": max_stage_ever,
        "max_bonds": max_bonds_ever,
        "first_s3": first_s3, "first_s4": first_s4, "first_s5": first_s5,
        "first_b3": first_b3, "first_b4": first_b4, "first_b5": first_b5,
        "filter_programs": filter_programs,
        "stage_trace": stage_trace,
    }


def run_condition(cond_name, n_seeds, pop_size, genotype_length, total_gens,
                  contexts, targets, selection_mode, motifs):
    """Run one condition across all seeds and print results."""
    print(f"--- {cond_name} ---")
    results = []
    t0 = time.time()

    s3_ct = s4_ct = s5_ct = b4_ct = b5_ct = filt_ct = 0

    for seed in range(n_seeds):
        r = run_seed(pop_size, genotype_length, total_gens, contexts, targets,
                     seed, selection_mode, motifs)
        results.append(r)

        if r["first_s3"] is not None: s3_ct += 1
        if r["first_s4"] is not None: s4_ct += 1
        if r["first_s5"] is not None: s5_ct += 1
        if r["first_b4"] is not None: b4_ct += 1
        if r["first_b5"] is not None: b5_ct += 1
        if r["filter_programs"]: filt_ct += 1

        f_s4 = f"gen {r['first_s4']}" if r["first_s4"] is not None else "NEVER"
        f_b5 = f"gen {r['first_b5']}" if r["first_b5"] is not None else "NEVER"
        filt = f"{len(r['filter_programs'])}filt" if r["filter_programs"] else ""

        print(f"  Seed {seed:2d}: fit={r['best_fitness']:.3f} "
              f"maxS={r['max_stage']} S4={f_s4:>8s} "
              f"maxB={r['max_bonds']} B5={f_b5:>8s} {filt}")

    elapsed = time.time() - t0
    print(f"  Time: {elapsed:.1f}s ({elapsed/n_seeds:.1f}s/seed)")
    print(f"  scaffold: S3={s3_ct}/{n_seeds} S4={s4_ct}/{n_seeds} S5={s5_ct}/{n_seeds}")
    print(f"  bonds:    B4={b4_ct}/{n_seeds} B5={b5_ct}/{n_seeds}")
    print(f"  filter programs: {filt_ct}/{n_seeds}\n")

    return results


def print_summary(name, results, n_seeds):
    """Print summary for one condition."""
    s3 = sum(1 for r in results if r["first_s3"] is not None)
    s4 = sum(1 for r in results if r["first_s4"] is not None)
    s5 = sum(1 for r in results if r["first_s5"] is not None)
    b4 = sum(1 for r in results if r["first_b4"] is not None)
    b5 = sum(1 for r in results if r["first_b5"] is not None)
    filt = sum(1 for r in results if r["filter_programs"])
    avg_fit = sum(r["best_fitness"] for r in results) / len(results)

    # Avg bonds at end
    avg_final_bonds = 0
    for r in results:
        if r["stage_trace"]:
            avg_final_bonds += r["stage_trace"][-1][7]  # avg_bonds
    avg_final_bonds /= len(results)

    print(f"  {name}:")
    print(f"    Avg fitness: {avg_fit:.3f}, Avg bonds (final): {avg_final_bonds:.1f}")
    print(f"    Scaffold: S3={s3}/{n_seeds} S4={s4}/{n_seeds} S5={s5}/{n_seeds}")
    print(f"    Bonds:    B4={b4}/{n_seeds} B5={b5}/{n_seeds}")
    print(f"    Filter programs: {filt}/{n_seeds}")


def print_stage_trace(name, results):
    """Print stage trace for one condition."""
    print(f"\n  {name}:")
    all_gens = sorted(set(g for r in results for g, *_ in r["stage_trace"]))
    for gen in all_gens:
        if gen > 0 and gen % 25 != 0 and gen != all_gens[-1]:
            continue
        s1_v, s2_v, s3_v, b3_v, b4_v, b5_v, ab_v = [], [], [], [], [], [], []
        for r in results:
            for g, s1, s2, s3, b3, b4, b5, ab in r["stage_trace"]:
                if g == gen:
                    s1_v.append(s1); s2_v.append(s2); s3_v.append(s3)
                    b3_v.append(b3); b4_v.append(b4); b5_v.append(b5)
                    ab_v.append(ab)
                    break
        if s1_v:
            a = lambda v: sum(v) / len(v)
            print(f"    Gen {gen:3d}: S1+={a(s1_v):5.1f} S2+={a(s2_v):5.1f} "
                  f"S3+={a(s3_v):5.1f} | B3+={a(b3_v):5.1f} B4+={a(b4_v):5.1f} "
                  f"B5+={a(b5_v):5.1f} avgB={a(ab_v):4.1f}")


def main():
    pop_size = 100
    genotype_length = 100
    total_gens = 300
    n_seeds = 20
    contexts = make_contexts()
    price_targets = [tfn for _, tfn in PRICE_TARGETS]
    order_targets = [tfn for _, tfn in ORDER_TARGETS]

    print("=" * 75)
    print("Experiment 1.12: Generalization Test")
    print("=" * 75)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {total_gens}, "
          f"Seeds: {n_seeds}")
    print(f"Rust VM: {'YES' if _USE_RUST_VM else 'NO'}")

    # ==================================================================
    print(f"\n{'='*75}")
    print("LEVEL 1: Same target (filter-price), generic scaffold metric")
    print(f"{'='*75}\n")

    all_L1 = {}
    all_L1["A. Select (baseline)"] = run_condition(
        "A. Continuous selection", n_seeds, pop_size, genotype_length,
        total_gens, contexts, price_targets, "select", SCREENED_MOTIFS)
    all_L1["B. Pareto(scaffold_stage)"] = run_condition(
        "B. Pareto(fitness, scaffold_stage) [1.11 control]", n_seeds,
        pop_size, genotype_length, total_gens, contexts, price_targets,
        "pareto_scaffold", SCREENED_MOTIFS)
    all_L1["C. Pareto(bond_count)"] = run_condition(
        "C. Pareto(fitness, bond_count) [generic]", n_seeds, pop_size,
        genotype_length, total_gens, contexts, price_targets,
        "pareto_bonds", SCREENED_MOTIFS)

    # ==================================================================
    print(f"\n{'='*75}")
    print("LEVEL 2: Different target (filter-amount on orders), generic metric")
    print(f"{'='*75}\n")

    all_L2 = {}
    all_L2["D. Select (baseline)"] = run_condition(
        "D. Continuous selection, ORDER targets", n_seeds, pop_size,
        genotype_length, total_gens, contexts, order_targets,
        "select", ORDER_MOTIFS)
    all_L2["E. Pareto(bond_count)"] = run_condition(
        "E. Pareto(fitness, bond_count), ORDER targets [Level 2]", n_seeds,
        pop_size, genotype_length, total_gens, contexts, order_targets,
        "pareto_bonds", ORDER_MOTIFS)

    # ==================================================================
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)

    print("\n  Level 1 — Same target, generic scaffold:")
    for name, results in all_L1.items():
        print_summary(name, results, n_seeds)

    print("\n  Level 2 — Different target, generic scaffold:")
    for name, results in all_L2.items():
        print_summary(name, results, n_seeds)

    print("\n--- Stage/Bond traces ---")
    for name, results in {**all_L1, **all_L2}.items():
        print_stage_trace(name, results)


if __name__ == "__main__":
    main()
