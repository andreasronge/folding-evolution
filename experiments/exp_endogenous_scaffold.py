"""
Experiment 1.13: Endogenous Scaffold Identification.

Tests whether the hand-coded `scaffold_stage` classifier can be replaced
with endogenous signals that don't encode specific target knowledge.

Three Pareto objective variants compared:

  1. motif_presence: count of screened motifs present as substrings.
     Endogenous — chemistry screening discovered the motifs. Target-aware
     only in that different targets need different screened motif libraries.

  2. structural_pattern: generic AST structure detection. Looks for
     (higher_order (fn x (CMP (get x :ANY) VAL)) data/ANY) without
     specifying which field or data source. Fully target-agnostic.

  3. scaffold_stage: hand-coded for :price (positive control, task-specific)

Tested on both price and amount targets to measure generalization.

If motif_presence works on both targets: the full loop is endogenous —
chemistry discovery + chemistry-derived preservation.

If structural_pattern works: compositional type structure alone suffices,
no motifs or AST classifier needed.

If only scaffold_stage works: preservation is principled but requires
target-specific scaffold knowledge.
"""

import random
import time
from collections import Counter

from folding_evolution.alphabet import random_genotype
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword, NsSymbol
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_batch
from folding_evolution.dynamics import (
    _develop_and_score_vm, _develop_population, evaluate_multi_target,
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
# Target families and motifs (from 1.12)
# ---------------------------------------------------------------------------

PRICE_TARGETS = TARGETS
ORDER_TARGETS = [
    ("count(filter(amount>200, orders))",
     lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 200])),
    ("count(orders)", lambda ctx: len(ctx["orders"])),
]

PRICE_MOTIFS = [
    'DaL', 'KaD', 'aDM', 'jDa', '3aD', 'DaB', 'caD', 'aJD',
    'aDT', 'QaD', 'iDa', 'raD', 'aDl', 'aDi', 'aDG', 'aDP',
    'aD', 'Da', 'KS', 'A7',
]

AMOUNT_MOTIFS = [
    'DfL', 'KfD', 'fDM', 'jDf', '3fD', 'DfB', 'cfD', 'fJD',
    'fDT', 'QfD', 'iDf', 'rfD', 'fDl', 'fDi', 'fDG', 'fDP',
    'fD', 'Df', 'KU', 'AU',
]


def mutate_with_motif(genotype, rng, motifs):
    if rng.random() < 0.75:
        motif = rng.choice(motifs)
        if len(motif) > len(genotype):
            return mutate(genotype, rng)
        pos = rng.randint(0, len(genotype) - len(motif))
        return genotype[:pos] + motif + genotype[pos + len(motif):]
    return mutate(genotype, rng)


# ---------------------------------------------------------------------------
# Three Pareto objectives
# ---------------------------------------------------------------------------

def motif_presence_score(genotype: str, motifs: list[str]) -> int:
    """Count distinct motifs present as substrings in the genotype.
    Endogenous: motifs come from chemistry screening, no AST inspection."""
    return sum(1 for m in motifs if m in genotype)


def structural_pattern_score(prog) -> int:
    """Detect generic compositional AST patterns, field-agnostic.

    G1: (get x :ANY) — any field accessor
    G2: (CMP (get x :ANY) VAL) — comparator applied to any accessor
    G3: (fn x (CMP (get x :ANY) VAL)) — predicate lambda
    G4: (HIGHER_ORDER (fn x ...) data/ANY) — higher-order with predicate
    G5: (WRAPPER (HIGHER_ORDER ...)) — wrapped higher-order

    No field or data source names are hardcoded.
    """
    if prog is None or prog.ast is None:
        return 0
    labels = set()
    _walk_generic(prog.ast, labels)
    for level in (5, 4, 3, 2, 1):
        if f"G{level}" in labels:
            return level
    return 0


def _is_generic_get(node):
    """(get x :ANY) with any field key."""
    return (isinstance(node, ListExpr) and len(node.items) == 3 and
            isinstance(node.items[0], Symbol) and node.items[0].name == "get" and
            isinstance(node.items[2], Keyword))


_CMPS = frozenset((">", "<", "="))
_HIGHER_ORDER = frozenset(("filter", "map", "reduce", "group_by"))
_WRAPPERS = frozenset(("count", "first", "rest", "last", "reverse", "sort"))


def _walk_generic(node, labels):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    hn = head.name if isinstance(head, Symbol) else None

    # G1: (get x :ANY)
    if _is_generic_get(node):
        labels.add("G1")

    # G2: (CMP (get x :ANY) VAL) or (CMP VAL (get x :ANY))
    if hn in _CMPS and len(node.items) == 3:
        for op in node.items[1:]:
            if _is_generic_get(op):
                labels.add("G2")

    # G3: (fn x (CMP (get x :ANY) VAL))
    if hn == "fn" and len(node.items) >= 3:
        body = node.items[2]
        if isinstance(body, ListExpr) and body.items:
            bh = body.items[0]
            if isinstance(bh, Symbol) and bh.name in _CMPS:
                for op in body.items[1:]:
                    if _is_generic_get(op):
                        labels.add("G3")

    # G4: (HIGHER_ORDER (fn x ...) data/ANY)
    if hn in _HIGHER_ORDER and len(node.items) >= 3:
        fn_arg = node.items[1]
        data_arg = node.items[2]
        if (isinstance(fn_arg, ListExpr) and fn_arg.items and
                isinstance(fn_arg.items[0], Symbol) and fn_arg.items[0].name == "fn" and
                isinstance(data_arg, NsSymbol) and data_arg.ns == "data"):
            # Check inner is G3 (predicate lambda)
            inner = set()
            _walk_generic(fn_arg, inner)
            if "G3" in inner:
                labels.add("G4")

    # G5: (WRAPPER (HIGHER_ORDER ...))
    if hn in _WRAPPERS and len(node.items) >= 2:
        arg = node.items[1]
        if isinstance(arg, ListExpr) and arg.items:
            ah = arg.items[0]
            if isinstance(ah, Symbol) and ah.name in _HIGHER_ORDER:
                inner = set()
                _walk_generic(arg, inner)
                if "G4" in inner:
                    labels.add("G5")

    for item in node.items:
        _walk_generic(item, labels)


# ---------------------------------------------------------------------------
# NSGA-II fast non-dominated sort (from 1.12)
# ---------------------------------------------------------------------------

def _pareto_sort(scored_list, pop_size):
    n = len(scored_list)
    domination_count = [0] * n
    dominates = [[] for _ in range(n)]

    for i in range(n):
        _, fi, si = scored_list[i]
        for j in range(i + 1, n):
            _, fj, sj = scored_list[j]
            if fi >= fj and si >= sj and (fi > fj or si > sj):
                dominates[i].append(j)
                domination_count[j] += 1
            elif fj >= fi and sj >= si and (fj > fi or sj > si):
                dominates[j].append(i)
                domination_count[i] += 1

    fronts = [[i for i in range(n) if domination_count[i] == 0]]
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

    selected = []
    for front in fronts:
        if len(selected) + len(front) <= pop_size:
            selected.extend(front)
        else:
            front_scored = [(i, scored_list[i][2]) for i in front]
            front_scored.sort(key=lambda x: x[1], reverse=True)
            for i, _ in front_scored:
                if len(selected) >= pop_size:
                    break
                selected.append(i)
            break

    return [Individual(genotype=scored_list[i][0].genotype) for i in selected]


# ---------------------------------------------------------------------------
# Evolution
# ---------------------------------------------------------------------------

def run_seed(
    pop_size, genotype_length, total_gens, contexts, targets, seed,
    objective,  # "select", "scaffold", "motif", "structural"
    motifs, scaffold_every=5,
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

    best_fit = 0.0
    best_src = None
    max_s = 0
    max_g = 0  # max generic structural pattern
    first_s3 = first_s4 = first_s5 = None
    first_g3 = first_g4 = first_g5 = None
    trace = []
    filter_progs = []

    for gen in range(total_gens):
        # Score
        if use_vm:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)
            for ind in population:
                ind.fitness = 0.0

        best = max(population, key=lambda i: i.fitness)
        if best.fitness > best_fit:
            best_fit = best.fitness
            best_src = best.program.source if best.program else None

        # Scaffold/pattern detection (sampled)
        if gen % scaffold_every == 0 or gen == total_gens - 1:
            genotypes = [ind.genotype for ind in population]
            programs = develop_batch(genotypes)
            for ind, prog in zip(population, programs):
                ind.program = prog

            sc = Counter()
            gc = Counter()
            for ind in population:
                s = scaffold_stage(ind.program)
                g = structural_pattern_score(ind.program)
                sc[s] += 1
                gc[g] += 1
                if g >= 4 and ind.program.source and "filter" in ind.program.source:
                    filter_progs.append((gen, ind.program.source, ind.fitness))

            s1p = sum(c for s, c in sc.items() if s >= 1)
            s2p = sum(c for s, c in sc.items() if s >= 2)
            s3p = sum(c for s, c in sc.items() if s >= 3)
            s4p = sum(c for s, c in sc.items() if s >= 4)
            s5p = sum(c for s, c in sc.items() if s >= 5)
            g3p = sum(c for g, c in gc.items() if g >= 3)
            g4p = sum(c for g, c in gc.items() if g >= 4)
            g5p = sum(c for g, c in gc.items() if g >= 5)

            trace.append((gen, s3p, s4p, s5p, g3p, g4p, g5p))

            for s in sc:
                if s > max_s: max_s = s
            for g in gc:
                if g > max_g: max_g = g

            if s3p > 0 and first_s3 is None: first_s3 = gen
            if s4p > 0 and first_s4 is None: first_s4 = gen
            if s5p > 0 and first_s5 is None: first_s5 = gen
            if g3p > 0 and first_g3 is None: first_g3 = gen
            if g4p > 0 and first_g4 is None: first_g4 = gen
            if g5p > 0 and first_g5 is None: first_g5 = gen

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

        if use_vm:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)

        combined = population + children

        if objective == "select":
            combined.sort(key=lambda ind: ind.fitness, reverse=True)
            population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]
        else:
            # Pareto: need programs
            genotypes = [ind.genotype for ind in combined]
            programs = develop_batch(genotypes)
            for ind, prog in zip(combined, programs):
                ind.program = prog

            if objective == "scaffold":
                scored = [(i, i.fitness, scaffold_stage(i.program)) for i in combined]
            elif objective == "motif":
                scored = [(i, i.fitness, motif_presence_score(i.genotype, motifs))
                          for i in combined]
            elif objective == "structural":
                scored = [(i, i.fitness, structural_pattern_score(i.program))
                          for i in combined]
            population = _pareto_sort(scored, pop_size)

    return {
        "best_fitness": best_fit,
        "best_source": best_src,
        "max_stage": max_s,
        "max_generic": max_g,
        "first_s3": first_s3, "first_s4": first_s4, "first_s5": first_s5,
        "first_g3": first_g3, "first_g4": first_g4, "first_g5": first_g5,
        "trace": trace,
        "filter_programs": filter_progs,
    }


def run_condition(label, n_seeds, pop_size, genotype_length, total_gens,
                  contexts, targets, objective, motifs):
    print(f"--- {label} ---")
    results = []
    t0 = time.time()
    s_ct = [0, 0, 0]  # s3, s4, s5
    g_ct = [0, 0, 0]  # g3, g4, g5
    f_ct = 0
    for seed in range(n_seeds):
        r = run_seed(pop_size, genotype_length, total_gens, contexts, targets,
                     seed, objective, motifs)
        results.append(r)
        for k, key in enumerate(["first_s3", "first_s4", "first_s5"]):
            if r[key] is not None: s_ct[k] += 1
        for k, key in enumerate(["first_g3", "first_g4", "first_g5"]):
            if r[key] is not None: g_ct[k] += 1
        if r["filter_programs"]: f_ct += 1

    elapsed = time.time() - t0
    print(f"  Time: {elapsed:.1f}s ({elapsed/n_seeds:.1f}s/seed)")
    print(f"  Scaffold (S3,S4,S5): {s_ct[0]}/{n_seeds}, {s_ct[1]}/{n_seeds}, {s_ct[2]}/{n_seeds}")
    print(f"  Generic  (G3,G4,G5): {g_ct[0]}/{n_seeds}, {g_ct[1]}/{n_seeds}, {g_ct[2]}/{n_seeds}")
    print(f"  Filter programs: {f_ct}/{n_seeds}\n")
    return results


def main():
    pop_size = 100
    genotype_length = 100
    total_gens = 300
    n_seeds = 20
    contexts = make_contexts()
    price_targets = [tfn for _, tfn in PRICE_TARGETS]
    amount_targets = [tfn for _, tfn in ORDER_TARGETS]

    print("=" * 75)
    print("Experiment 1.13: Endogenous Scaffold Identification")
    print("=" * 75)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {total_gens}, "
          f"Seeds: {n_seeds}")
    print(f"Rust VM: {'YES' if _USE_RUST_VM else 'NO'}\n")

    # Level 1: Price target
    print("=" * 75)
    print("LEVEL 1: Price target (filter-price)")
    print("=" * 75 + "\n")

    results_price = {}
    results_price["A. Continuous select"] = run_condition(
        "A. Continuous selection", n_seeds, pop_size, genotype_length,
        total_gens, contexts, price_targets, "select", PRICE_MOTIFS)
    results_price["B. Pareto(motif_presence)"] = run_condition(
        "B. Pareto(motif_presence) — ENDOGENOUS", n_seeds, pop_size, genotype_length,
        total_gens, contexts, price_targets, "motif", PRICE_MOTIFS)
    results_price["C. Pareto(structural_pattern)"] = run_condition(
        "C. Pareto(structural_pattern) — GENERIC", n_seeds, pop_size, genotype_length,
        total_gens, contexts, price_targets, "structural", PRICE_MOTIFS)
    results_price["D. Pareto(scaffold_stage)"] = run_condition(
        "D. Pareto(scaffold_stage) — TASK-SPECIFIC control", n_seeds, pop_size,
        genotype_length, total_gens, contexts, price_targets, "scaffold", PRICE_MOTIFS)

    # Level 2: Amount target
    print("=" * 75)
    print("LEVEL 2: Amount target (filter-amount on orders)")
    print("=" * 75 + "\n")

    results_amount = {}
    results_amount["E. Continuous select"] = run_condition(
        "E. Continuous selection (amount)", n_seeds, pop_size, genotype_length,
        total_gens, contexts, amount_targets, "select", AMOUNT_MOTIFS)
    results_amount["F. Pareto(motif_presence)"] = run_condition(
        "F. Pareto(motif_presence) amount — ENDOGENOUS", n_seeds, pop_size,
        genotype_length, total_gens, contexts, amount_targets, "motif", AMOUNT_MOTIFS)
    results_amount["G. Pareto(structural_pattern)"] = run_condition(
        "G. Pareto(structural_pattern) amount — GENERIC", n_seeds, pop_size,
        genotype_length, total_gens, contexts, amount_targets, "structural",
        AMOUNT_MOTIFS)

    # ==========================================================
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)

    def print_summary(label, results):
        s3 = sum(1 for r in results if r["first_s3"] is not None)
        s4 = sum(1 for r in results if r["first_s4"] is not None)
        s5 = sum(1 for r in results if r["first_s5"] is not None)
        g3 = sum(1 for r in results if r["first_g3"] is not None)
        g4 = sum(1 for r in results if r["first_g4"] is not None)
        g5 = sum(1 for r in results if r["first_g5"] is not None)
        filt = sum(1 for r in results if r["filter_programs"])
        avg_fit = sum(r["best_fitness"] for r in results) / len(results)

        print(f"\n  {label}:")
        print(f"    Avg fitness: {avg_fit:.3f}")
        print(f"    Scaffold S3/S4/S5: {s3}/{n_seeds}, {s4}/{n_seeds}, {s5}/{n_seeds}")
        print(f"    Generic  G3/G4/G5: {g3}/{n_seeds}, {g4}/{n_seeds}, {g5}/{n_seeds}")
        print(f"    Filter programs: {filt}/{n_seeds}")

    print("\nLevel 1 — Price target:")
    for label, r in results_price.items():
        print_summary(label, r)
    print("\nLevel 2 — Amount target (scaffold_stage returns 0, use Generic columns):")
    for label, r in results_amount.items():
        print_summary(label, r)


if __name__ == "__main__":
    main()
