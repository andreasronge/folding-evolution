"""
Module-Generating Operators Experiment.

Tests whether substring duplication and transposition operators increase
the frequency of mid-level scaffold modules (S3, S4) by creating spatial
density of useful character combinations.

New operators:
  - Substring duplication: copy a random 3-8 char substring to another position
  - Substring transposition: move a random 3-8 char substring to another position
  - Motif insertion: insert a known-useful 2-3 char motif (Da, DaK, QDa) at random position

Three conditions:
  A. Baseline: standard operators (point mutation, insertion, deletion, crossover)
  B. + Duplication/transposition: add substring dup and transpose to operator mix
  C. + Motif insertion: add known-motif insertion (strongest intervention)

Measures:
  - S1-S5 frequency in random genotypes with each operator set
  - S1-S5 frequency over evolutionary generations
  - First generation where S3, S4, S5 appear
  - Whether S5 (full target) ever emerges
"""

import random
import time
from collections import Counter, defaultdict

from folding_evolution.alphabet import random_genotype, ALPHABET
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop
from folding_evolution.selection import tournament_select


# Import scaffold_stage from archive experiment
from exp_archive_reinjection import scaffold_stage, make_contexts, TARGETS, ScaffoldArchive


# ---------------------------------------------------------------------------
# New operators
# ---------------------------------------------------------------------------

def mutate_duplicate_substring(genotype: str, rng: random.Random) -> str:
    """Copy a random 3-8 char substring to another random position.

    The original stays in place. The copy is inserted, potentially
    shifting downstream characters and changing fold topology.
    """
    if len(genotype) < 6:
        return mutate(genotype, rng)

    substr_len = rng.randint(3, min(8, len(genotype) // 2))
    src_start = rng.randint(0, len(genotype) - substr_len)
    substr = genotype[src_start:src_start + substr_len]

    # Insert at random position
    insert_pos = rng.randint(0, len(genotype))
    result = genotype[:insert_pos] + substr + genotype[insert_pos:]

    # Trim back to original length: remove from end opposite to insertion
    # This preserves the new insertion and its immediate fold context
    return result[:len(genotype)]


def mutate_transpose_substring(genotype: str, rng: random.Random) -> str:
    """Move a random 3-8 char substring to another random position.

    The substring is removed from its original position and inserted elsewhere.
    This changes the fold context of both the moved region and its surroundings.
    """
    if len(genotype) < 10:
        return mutate(genotype, rng)

    max_len = min(8, len(genotype) // 3)
    if max_len < 3:
        return mutate(genotype, rng)
    substr_len = rng.randint(3, max_len)
    src_start = rng.randint(0, len(genotype) - substr_len)
    substr = genotype[src_start:src_start + substr_len]

    # Remove the substring
    remaining = genotype[:src_start] + genotype[src_start + substr_len:]

    # Insert at a new random position
    insert_pos = rng.randint(0, len(remaining))
    result = remaining[:insert_pos] + substr + remaining[insert_pos:]

    return result


# Known useful motifs for the filter program chain
_USEFUL_MOTIFS = [
    "Da",    # get + :price -> (get x :price)
    "DaK",   # get + :price + > -> comparator with get
    "QDa",   # fn + get + :price
    "QDaK",  # fn + get + :price + >
    "AS",    # filter + data/products
    "BS",    # count + data/products
]


def mutate_insert_motif(genotype: str, rng: random.Random) -> str:
    """Insert a known-useful motif at a random position.

    Replaces characters at the insertion point (doesn't grow the genotype).
    This is the strongest intervention — provides known building blocks
    but lets the fold determine whether they bond usefully.
    """
    motif = rng.choice(_USEFUL_MOTIFS)
    insert_pos = rng.randint(0, len(genotype) - len(motif))
    result = genotype[:insert_pos] + motif + genotype[insert_pos + len(motif):]
    return result


def apply_operator(genotype: str, rng: random.Random, operator_set: str) -> str:
    """Apply a random operator from the given set.

    Operator sets:
      'standard': point mutation, insertion, deletion (via mutate())
      'module': standard + duplication + transposition
      'motif': standard + duplication + transposition + motif insertion
    """
    if operator_set == "standard":
        return mutate(genotype, rng)

    r = rng.random()
    if operator_set == "module":
        if r < 0.5:
            return mutate(genotype, rng)  # standard
        elif r < 0.75:
            return mutate_duplicate_substring(genotype, rng)
        else:
            return mutate_transpose_substring(genotype, rng)
    elif operator_set == "motif":
        if r < 0.4:
            return mutate(genotype, rng)  # standard
        elif r < 0.6:
            return mutate_duplicate_substring(genotype, rng)
        elif r < 0.75:
            return mutate_transpose_substring(genotype, rng)
        else:
            return mutate_insert_motif(genotype, rng)

    return mutate(genotype, rng)


# ---------------------------------------------------------------------------
# Analysis 1: Random genotype scaffold frequencies with each operator
# ---------------------------------------------------------------------------

def analyze_random_frequencies(n_samples=20_000, genotype_length=100):
    """Apply operators to random genotypes and measure scaffold frequencies."""
    print("=" * 70)
    print("Analysis 1: Scaffold Frequency After One Operator Application")
    print("=" * 70)
    print(f"  {n_samples:,} random genotypes × 1 operator application each\n")

    for op_name in ["standard", "module", "motif"]:
        rng = random.Random(42)
        stage_counts = Counter()

        # Generate random genotypes and apply one operator
        for _ in range(n_samples):
            g = random_genotype(genotype_length, rng)
            g_mutated = apply_operator(g, rng, op_name)
            p = develop(g_mutated)
            stage_counts[scaffold_stage(p)] += 1

        print(f"  Operator set: {op_name}")
        for s in range(6):
            count = stage_counts.get(s, 0)
            pct = count / n_samples * 100
            bar = "#" * max(0, int(pct * 2))
            print(f"    S{s}: {count:6d} ({pct:6.2f}%) {bar}")
        print()

    # Also show baseline (no operator, just random genotypes)
    rng = random.Random(42)
    stage_counts = Counter()
    for _ in range(n_samples):
        g = random_genotype(genotype_length, rng)
        p = develop(g)
        stage_counts[scaffold_stage(p)] += 1

    print(f"  Baseline (raw random genotypes):")
    for s in range(6):
        count = stage_counts.get(s, 0)
        pct = count / n_samples * 100
        print(f"    S{s}: {count:6d} ({pct:6.2f}%)")
    print()


# ---------------------------------------------------------------------------
# Analysis 2: Iterated operator application (random walk)
# ---------------------------------------------------------------------------

def analyze_random_walk(n_walks=5000, steps=50, genotype_length=100):
    """Apply operators repeatedly and measure scaffold frequency at each step."""
    print("=" * 70)
    print("Analysis 2: Random Walk — Scaffold Frequency Over 50 Operator Steps")
    print("=" * 70)

    for op_name in ["standard", "module", "motif"]:
        rng = random.Random(42)
        step_stages = defaultdict(Counter)

        for _ in range(n_walks):
            g = random_genotype(genotype_length, rng)
            for step in range(steps):
                g = apply_operator(g, rng, op_name)
                if step in (0, 4, 9, 19, 29, 49):
                    p = develop(g)
                    step_stages[step][scaffold_stage(p)] += 1

        print(f"\n  {op_name}:")
        print(f"    {'Step':>4s} | {'S0':>6s} {'S1':>6s} {'S2':>6s} {'S3':>6s} {'S4':>6s} {'S5':>6s}")
        print(f"    {'-'*4}-+-{'-'*6}-{'-'*6}-{'-'*6}-{'-'*6}-{'-'*6}-{'-'*6}")
        for step in sorted(step_stages.keys()):
            counts = step_stages[step]
            total = sum(counts.values())
            vals = [f"{counts.get(s, 0)/total*100:5.1f}%" for s in range(6)]
            print(f"    {step:4d} | {' '.join(vals)}")


# ---------------------------------------------------------------------------
# Analysis 3: Evolution with module operators
# ---------------------------------------------------------------------------

def evaluate_individual(ind, targets, contexts):
    ind.program = develop(ind.genotype)
    if ind.program.ast is None:
        ind.fitness = 0.0
        return
    gate = [repr(ind.program.evaluate(ctx)) for ctx in contexts]
    if len(set(gate)) <= 1:
        ind.fitness = 0.0
        return
    scores = []
    for _, tfn in targets:
        for ctx in contexts:
            scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
    ind.fitness = sum(scores) / len(scores)


def run_evolution(
    pop_size, genotype_length, generations, contexts, seed,
    operator_set, use_archive=True,
):
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    archive = ScaffoldArchive(max_per_stage=30) if use_archive else None
    history = []

    for gen in range(generations):
        for ind in population:
            evaluate_individual(ind, TARGETS, contexts)

        if archive:
            archive.update(population)

        best = max(population, key=lambda i: i.fitness)
        stage_counts = Counter()
        for ind in population:
            stage_counts[scaffold_stage(ind.program)] += 1

        history.append({
            "gen": gen,
            "best_fitness": best.fitness,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "best_stage": scaffold_stage(best.program),
            "stage_counts": dict(stage_counts),
        })

        # Reproduce
        n_reinject = 5 if archive else 0
        children = []

        # Archive reinjection (mutated)
        if archive:
            reinjected = archive.sample(n_reinject, rng)
            for geno in reinjected:
                child_geno = apply_operator(geno, rng, operator_set)
                children.append(Individual(genotype=child_geno))

        # Standard reproduction
        for _ in range(pop_size - len(children)):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = apply_operator(parent.genotype, rng, operator_set)
            children.append(Individual(genotype=child_geno))

        for ind in children:
            evaluate_individual(ind, TARGETS, contexts)

        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {"history": history}


def analyze_evolution(pop_size=100, genotype_length=100, generations=300, n_seeds=20):
    """Run evolution with different operator sets and compare scaffold discovery."""
    print("\n" + "=" * 70)
    print("Analysis 3: Evolution with Module Operators")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print()

    contexts = make_contexts()

    conditions = [
        ("Standard operators", "standard"),
        ("+ Dup/transpose", "module"),
        ("+ Motif insertion", "motif"),
    ]

    all_results = {}

    for cond_name, op_set in conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        s3_found = 0
        s4_found = 0
        s5_found = 0

        for seed in range(n_seeds):
            result = run_evolution(
                pop_size, genotype_length, generations, contexts, seed,
                operator_set=op_set, use_archive=True,
            )
            cond_results.append(result)

            # Find first appearance of each stage
            first = {}
            max_stage = 0
            for entry in result["history"]:
                for s in range(3, 6):
                    if entry["stage_counts"].get(s, 0) > 0 and s not in first:
                        first[s] = entry["gen"]
                for s in entry["stage_counts"]:
                    if s > max_stage:
                        max_stage = s

            if 3 in first: s3_found += 1
            if 4 in first: s4_found += 1
            if 5 in first: s5_found += 1

            final = result["history"][-1]
            f_s3 = f"gen {first[3]}" if 3 in first else "NEVER"
            f_s4 = f"gen {first[4]}" if 4 in first else "NEVER"
            f_s5 = f"gen {first[5]}" if 5 in first else "NEVER"

            print(f"  Seed {seed:2d}: fit={final['best_fitness']:.3f} "
                  f"S3={f_s3:>8s} S4={f_s4:>8s} S5={f_s5:>8s} "
                  f"max={max_stage} src={final['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s")
        print(f"  S3 found: {s3_found}/{n_seeds}, S4: {s4_found}/{n_seeds}, S5: {s5_found}/{n_seeds}\n")
        all_results[cond_name] = cond_results

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for cond_name, results in all_results.items():
        s3_seeds = sum(1 for r in results if any(e["stage_counts"].get(3, 0) > 0 for e in r["history"]))
        s4_seeds = sum(1 for r in results if any(e["stage_counts"].get(4, 0) > 0 for e in r["history"]))
        s5_seeds = sum(1 for r in results if any(e["stage_counts"].get(5, 0) > 0 for e in r["history"]))

        finals = [r["history"][-1] for r in results]
        avg_fit = sum(f["best_fitness"] for f in finals) / len(finals)

        print(f"\n  {cond_name}:")
        print(f"    Avg fitness: {avg_fit:.3f}")
        print(f"    S3 found: {s3_seeds}/{n_seeds} seeds")
        print(f"    S4 found: {s4_seeds}/{n_seeds} seeds")
        print(f"    S5 found: {s5_seeds}/{n_seeds} seeds")

    # Stage frequency over time for motif condition
    print("\n--- Stage frequency over time (motif operators, avg across seeds) ---")
    if "+ Motif insertion" in all_results:
        results = all_results["+ Motif insertion"]
        for gen in [0, 10, 25, 50, 100, 150, 200, 250, 299]:
            if gen >= generations:
                continue
            s_avgs = {}
            for s in range(6):
                vals = [r["history"][gen]["stage_counts"].get(s, 0) for r in results]
                s_avgs[s] = sum(vals) / len(vals)
            print(f"    Gen {gen:3d}: " + " ".join(f"S{s}={s_avgs[s]:5.1f}" for s in range(6)))


def main():
    analyze_random_frequencies()
    analyze_random_walk()
    analyze_evolution()


if __name__ == "__main__":
    main()
