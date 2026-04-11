"""
Chemistry-Aware Duplication Experiment.

Tests whether biasing substring duplication toward bonded (active) regions
of the genotype increases scaffold frequency endogenously — without
hand-coded motif knowledge.

Hypothesis: generic substring duplication failed (see exp_module_operators)
because it duplicated random substrings. Chemistry-aware duplication
targets the regions the fold/chemistry has already validated as functional
(bonded). If this raises S3 density even modestly, it validates that the
developmental process itself can identify what to duplicate.

Four conditions:
  A. Baseline: standard operators (point mutation, insertion, deletion, crossover)
  B. + Generic dup: random substring duplication (replicates prior negative result)
  C. + Chemistry-aware dup: duplicate substrings from bonded regions
  D. + Hand-coded motifs: known-useful motif insertion (positive control)

Measures:
  - S1-S5 frequency in random walks and evolutionary runs
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
from folding_evolution.phenotype import develop, get_bonded_indices
from folding_evolution.selection import tournament_select

from exp_archive_reinjection import scaffold_stage, make_contexts, TARGETS, ScaffoldArchive


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

def mutate_duplicate_substring(genotype: str, rng: random.Random) -> str:
    """Copy a random 3-8 char substring to another random position.
    (Generic, unbiased — baseline comparison.)"""
    if len(genotype) < 6:
        return mutate(genotype, rng)

    substr_len = rng.randint(3, min(8, len(genotype) // 2))
    src_start = rng.randint(0, len(genotype) - substr_len)
    substr = genotype[src_start:src_start + substr_len]

    insert_pos = rng.randint(0, len(genotype))
    result = genotype[:insert_pos] + substr + genotype[insert_pos:]
    return result[:len(genotype)]


def _find_bonded_runs(bonded: set[int], genotype_len: int) -> list[tuple[int, int]]:
    """Find contiguous runs of bonded indices.

    Returns list of (start, end) tuples where genotype[start:end]
    is a contiguous sequence of bonded characters. Minimum run length 2.
    """
    if not bonded:
        return []
    sorted_b = sorted(bonded)
    runs = []
    run_start = sorted_b[0]
    prev = sorted_b[0]
    for idx in sorted_b[1:]:
        if idx == prev + 1:
            prev = idx
        else:
            if prev - run_start >= 1:  # at least 2 chars
                runs.append((run_start, prev + 1))
            run_start = idx
            prev = idx
    if prev - run_start >= 1:
        runs.append((run_start, prev + 1))
    return runs


def mutate_chemistry_aware_dup(genotype: str, rng: random.Random) -> str:
    """Duplicate a contiguous bonded run to another position.

    Contiguous bonded runs are self-contained fold-and-bond motifs:
    their fold instructions create the spatial adjacency, their character
    types create the bonds. Duplicating the run preserves both properties.

    1. Fold the genotype and identify bonded character indices.
    2. Find contiguous runs of bonded chars (min length 2).
    3. Pick a run (weighted by length — longer runs = richer motifs).
    4. Insert at a random position (overwriting to preserve length).

    If no contiguous bonded runs exist, falls back to standard mutation.
    """
    bonded = get_bonded_indices(genotype)
    runs = _find_bonded_runs(bonded, len(genotype))

    if not runs:
        return mutate(genotype, rng)

    # Weight by run length (longer runs = more complex motifs)
    weights = [end - start for start, end in runs]
    total_w = sum(weights)
    r = rng.random() * total_w
    cumulative = 0
    chosen_run = runs[0]
    for i, w in enumerate(weights):
        cumulative += w
        if cumulative >= r:
            chosen_run = runs[i]
            break

    start, end = chosen_run
    substr = genotype[start:end]

    # Cap at 8 chars to avoid massive overwrites
    if len(substr) > 8:
        offset = rng.randint(0, len(substr) - 8)
        substr = substr[offset:offset + 8]

    # Insert at a random position, overwrite to preserve length
    insert_pos = rng.randint(0, len(genotype) - len(substr))
    result = genotype[:insert_pos] + substr + genotype[insert_pos + len(substr):]
    return result


# Known useful motifs (positive control — from exp_module_operators)
_USEFUL_MOTIFS = ["Da", "DaK", "QDa", "QDaK", "AS", "BS"]


def mutate_insert_motif(genotype: str, rng: random.Random) -> str:
    """Insert a known-useful motif at a random position (positive control)."""
    motif = rng.choice(_USEFUL_MOTIFS)
    insert_pos = rng.randint(0, len(genotype) - len(motif))
    return genotype[:insert_pos] + motif + genotype[insert_pos + len(motif):]


def apply_operator(genotype: str, rng: random.Random, operator_set: str) -> str:
    """Apply a random operator from the given set.

    Operator sets:
      'standard': point mutation, insertion, deletion (via mutate())
      'generic_dup': standard + generic substring duplication
      'chem_dup': standard + chemistry-aware duplication
      'motif': standard + hand-coded motif insertion (positive control)
    """
    if operator_set == "standard":
        return mutate(genotype, rng)

    r = rng.random()
    if operator_set == "generic_dup":
        if r < 0.75:
            return mutate(genotype, rng)
        else:
            return mutate_duplicate_substring(genotype, rng)

    elif operator_set == "chem_dup":
        if r < 0.75:
            return mutate(genotype, rng)
        else:
            return mutate_chemistry_aware_dup(genotype, rng)

    elif operator_set == "motif":
        if r < 0.75:
            return mutate(genotype, rng)
        else:
            return mutate_insert_motif(genotype, rng)

    elif operator_set == "cross_chem_dup":
        # Handled separately in evolution (needs population access)
        return mutate(genotype, rng)

    return mutate(genotype, rng)


def mutate_cross_individual_dup(
    genotype: str, donor: str, rng: random.Random,
) -> str:
    """Transfer a bonded run from a donor genotype into the recipient.

    Cross-individual chemistry-aware duplication: extract a contiguous
    bonded run from the donor (a fit individual), insert it into the
    recipient. This spreads useful motifs discovered by one individual
    to others in the population.
    """
    bonded = get_bonded_indices(donor)
    runs = _find_bonded_runs(bonded, len(donor))

    if not runs:
        return mutate(genotype, rng)

    # Pick a run weighted by length
    weights = [end - start for start, end in runs]
    total_w = sum(weights)
    r = rng.random() * total_w
    cumulative = 0
    chosen_run = runs[0]
    for i, w in enumerate(weights):
        cumulative += w
        if cumulative >= r:
            chosen_run = runs[i]
            break

    start, end = chosen_run
    substr = donor[start:end]
    max_len = min(8, len(genotype) - 1)
    if max_len < 2:
        return mutate(genotype, rng)
    if len(substr) > max_len:
        offset = rng.randint(0, len(substr) - max_len)
        substr = substr[offset:offset + max_len]

    insert_pos = rng.randint(0, len(genotype) - len(substr))
    return genotype[:insert_pos] + substr + genotype[insert_pos + len(substr):]


# ---------------------------------------------------------------------------
# Analysis 1: Random walk scaffold frequencies
# ---------------------------------------------------------------------------

def analyze_random_walk(n_walks=5000, steps=50, genotype_length=100):
    """Apply operators repeatedly and measure scaffold frequency at each step."""
    print("=" * 70)
    print("Analysis 1: Random Walk — Scaffold Frequency Over 50 Operator Steps")
    print("=" * 70)
    print(f"  {n_walks:,} walks x {steps} steps, genotype length {genotype_length}\n")

    for op_name in ["standard", "generic_dup", "chem_dup", "motif"]:
        rng = random.Random(42)
        step_stages = defaultdict(Counter)

        t0 = time.time()
        for _ in range(n_walks):
            g = random_genotype(genotype_length, rng)
            for step in range(steps):
                g = apply_operator(g, rng, op_name)
                if step in (0, 4, 9, 19, 29, 49):
                    p = develop(g)
                    step_stages[step][scaffold_stage(p)] += 1
        elapsed = time.time() - t0

        print(f"  {op_name} ({elapsed:.1f}s):")
        print(f"    {'Step':>4s} | {'S0':>6s} {'S1':>6s} {'S2':>6s} {'S3':>6s} {'S4':>6s} {'S5':>6s}")
        print(f"    {'-'*4}-+-{'-'*6}-{'-'*6}-{'-'*6}-{'-'*6}-{'-'*6}-{'-'*6}")
        for step in sorted(step_stages.keys()):
            counts = step_stages[step]
            total = sum(counts.values())
            vals = [f"{counts.get(s, 0)/total*100:5.1f}%" for s in range(6)]
            print(f"    {step:4d} | {' '.join(vals)}")
        print()


# ---------------------------------------------------------------------------
# Analysis 2: What does chemistry-aware dup actually duplicate?
# ---------------------------------------------------------------------------

def analyze_dup_content(n_samples=10000, genotype_length=100):
    """Characterize bonded runs and what chemistry-aware dup selects."""
    print("=" * 70)
    print("Analysis 2: Bonded Runs in Random Genotypes")
    print("=" * 70)

    rng = random.Random(42)
    n_with_bonds = 0
    n_with_runs = 0
    total_bonded_fraction = 0.0
    all_run_lengths = []
    run_contents = Counter()

    for _ in range(n_samples):
        g = random_genotype(genotype_length, rng)
        bonded = get_bonded_indices(g)

        if bonded:
            n_with_bonds += 1
            total_bonded_fraction += len(bonded) / len(g)

            runs = _find_bonded_runs(bonded, len(g))
            if runs:
                n_with_runs += 1
                for start, end in runs:
                    all_run_lengths.append(end - start)
                    run_contents[g[start:end]] += 1

    print(f"  Genotypes with bonds: {n_with_bonds}/{n_samples} "
          f"({n_with_bonds/n_samples*100:.1f}%)")
    print(f"  Genotypes with contiguous runs (len>=2): {n_with_runs}/{n_samples} "
          f"({n_with_runs/n_samples*100:.1f}%)")
    if n_with_bonds > 0:
        print(f"  Avg bonded fraction: {total_bonded_fraction/n_with_bonds*100:.1f}%")

    if all_run_lengths:
        print(f"\n  Bonded run statistics:")
        print(f"    Total runs found: {len(all_run_lengths)}")
        print(f"    Avg runs per genotype: {len(all_run_lengths)/n_samples:.1f}")
        print(f"    Avg run length: {sum(all_run_lengths)/len(all_run_lengths):.1f}")
        length_dist = Counter(all_run_lengths)
        print(f"    Length distribution:")
        for length in sorted(length_dist.keys())[:10]:
            count = length_dist[length]
            print(f"      len={length}: {count:5d} ({count/len(all_run_lengths)*100:.1f}%)")

        print(f"\n  Top 20 most common bonded runs:")
        for substr, count in run_contents.most_common(20):
            pct = count / len(all_run_lengths) * 100
            # Show what program this substring produces
            p = develop(substr)
            prog = p.source if p.source else "(no program)"
            print(f"    '{substr}' x{count:4d} ({pct:4.1f}%) -> {prog}")
    print()


# ---------------------------------------------------------------------------
# Analysis 3: Evolution with chemistry-aware dup
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

        if archive:
            reinjected = archive.sample(n_reinject, rng)
            for geno in reinjected:
                child_geno = apply_operator(geno, rng, operator_set)
                children.append(Individual(genotype=child_geno))

        for _ in range(pop_size - len(children)):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            elif operator_set == "cross_chem_dup" and rng.random() < 0.33:
                # Cross-individual: pick recipient + fit donor
                recipient = tournament_select(population, 3, rng)
                donor = tournament_select(population, 3, rng)
                child_geno = mutate_cross_individual_dup(
                    recipient.genotype, donor.genotype, rng,
                )
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
    print("=" * 70)
    print("Analysis 3: Evolution with Chemistry-Aware Duplication")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print()

    contexts = make_contexts()

    conditions = [
        ("Standard operators", "standard"),
        ("+ Generic dup", "generic_dup"),
        ("+ Chemistry-aware dup", "chem_dup"),
        ("+ Cross-individual dup", "cross_chem_dup"),
        ("+ Hand-coded motifs", "motif"),
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
        s3_seeds = sum(1 for r in results if any(
            e["stage_counts"].get(3, 0) > 0 for e in r["history"]))
        s4_seeds = sum(1 for r in results if any(
            e["stage_counts"].get(4, 0) > 0 for e in r["history"]))
        s5_seeds = sum(1 for r in results if any(
            e["stage_counts"].get(5, 0) > 0 for e in r["history"]))

        finals = [r["history"][-1] for r in results]
        avg_fit = sum(f["best_fitness"] for f in finals) / len(finals)

        print(f"\n  {cond_name}:")
        print(f"    Avg fitness: {avg_fit:.3f}")
        print(f"    S3 found: {s3_seeds}/{n_seeds} seeds")
        print(f"    S4 found: {s4_seeds}/{n_seeds} seeds")
        print(f"    S5 found: {s5_seeds}/{n_seeds} seeds")

    # Stage frequency over time for chem_dup condition
    print("\n--- Stage frequency over time (chem-aware dup, avg across seeds) ---")
    if "+ Chemistry-aware dup" in all_results:
        results = all_results["+ Chemistry-aware dup"]
        for gen in [0, 10, 25, 50, 100, 150, 200, 250, 299]:
            if gen >= generations:
                continue
            s_avgs = {}
            for s in range(6):
                vals = [r["history"][gen]["stage_counts"].get(s, 0) for r in results]
                s_avgs[s] = sum(vals) / len(vals)
            print(f"    Gen {gen:3d}: " + " ".join(f"S{s}={s_avgs[s]:5.1f}" for s in range(6)))


def main():
    analyze_dup_content()
    analyze_random_walk()
    analyze_evolution()


if __name__ == "__main__":
    main()
