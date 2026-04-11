"""
Experiment 1.5: Learned Motif Library.

The central open question: can the system discover and accumulate useful
motifs endogenously rather than having them hand-coded?

Design:
  Phase 1 — Discovery: run many short evolution runs on EASY tasks
    (count, first, rest — things evolution can solve). Extract all 2-4
    char substrings from fit individuals. Score each by how often it
    participates in scaffold assemblies (S1+) when placed in random
    fold contexts. Compare frequencies against random genotype baseline
    to compute enrichment ratios.

  Phase 2 — Application: use the top-N learned motifs as the motif
    insertion operator on HARD tasks (filter). Compare:
      A. No motifs (baseline)
      B. Learned motifs (from Phase 1)
      C. Hand-coded motifs (positive control)
      D. Random motifs (negative control — random 2-4 char strings)

  This tests constructional selection: does evolution on easy tasks
  shape the GP map by enriching functional subsequences that transfer
  to harder tasks?
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

from exp_archive_reinjection import (
    scaffold_stage, make_contexts, TARGETS as HARD_TARGETS, ScaffoldArchive,
)


# Easy targets — things evolution can reliably solve (same contexts as hard)
EASY_TARGETS = [
    ("count(products)", lambda ctx: len(ctx["products"])),
    ("count(employees)", lambda ctx: len(ctx["employees"])),
]


# ---------------------------------------------------------------------------
# Phase 1: Discovery — evolve on easy tasks, extract motifs
# ---------------------------------------------------------------------------

def run_easy_evolution(pop_size, genotype_length, generations, targets, contexts, seed):
    """Short evolution run on easy tasks. Returns final population."""
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

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
            for _, tfn in targets:
                for ctx in contexts:
                    scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
            ind.fitness = sum(scores) / len(scores)

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
            for _, tfn in targets:
                for ctx in contexts:
                    scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
            ind.fitness = sum(scores) / len(scores)

        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    # Re-evaluate final population so callers see fitness/program
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
        for _, tfn in targets:
            for ctx in contexts:
                scores.append(partial_credit(ind.program.evaluate(ctx), tfn(ctx)))
        ind.fitness = sum(scores) / len(scores)

    return population


def extract_substrings(genotype: str, min_len=2, max_len=4) -> list[str]:
    """Extract all substrings of length min_len..max_len."""
    subs = []
    for length in range(min_len, max_len + 1):
        for start in range(len(genotype) - length + 1):
            subs.append(genotype[start:start + length])
    return subs


def score_motif_assembly(motif: str, n_contexts=200, genotype_length=100) -> dict:
    """Score a motif by placing it in random genotype contexts and checking assembly.

    Returns dict with scaffold stage frequencies.
    """
    rng = random.Random(hash(motif) & 0xFFFFFFFF)
    stage_counts = Counter()

    for _ in range(n_contexts):
        g = random_genotype(genotype_length, rng)
        # Insert motif at random position
        pos = rng.randint(0, len(g) - len(motif))
        g_with_motif = g[:pos] + motif + g[pos + len(motif):]
        p = develop(g_with_motif)
        stage_counts[scaffold_stage(p)] += 1

    return dict(stage_counts)


def discover_motifs(
    n_runs=50, pop_size=50, genotype_length=80, generations=50,
    top_n=20, n_assembly_tests=200,
):
    """Phase 1: run easy-task evolution, extract and score motifs."""
    print("=" * 70)
    print("Phase 1: Motif Discovery from Easy-Task Evolution")
    print("=" * 70)
    print(f"  {n_runs} evolution runs, pop={pop_size}, len={genotype_length}, "
          f"gens={generations}")
    print()

    contexts = make_contexts()

    # Collect substrings from fit individuals across all runs
    evolved_substrings = Counter()
    total_fit_individuals = 0
    t0 = time.time()

    for run_idx in range(n_runs):
        # Use all easy targets together — more selection pressure,
        # more programs pass the data-dependence gate
        population = run_easy_evolution(
            pop_size, genotype_length, generations,
            EASY_TARGETS, contexts, seed=run_idx,
        )

        # Extract substrings from all individuals with nonzero fitness
        population.sort(key=lambda i: i.fitness, reverse=True)
        for ind in population:
            if ind.fitness > 0.05:
                total_fit_individuals += 1
                for sub in extract_substrings(ind.genotype):
                    evolved_substrings[sub] += 1

    elapsed = time.time() - t0
    print(f"  Discovery phase: {elapsed:.1f}s, {total_fit_individuals} fit individuals")
    print(f"  Unique substrings extracted: {len(evolved_substrings):,}")

    # Compute baseline: substring frequencies in random genotypes
    rng = random.Random(9999)
    random_substrings = Counter()
    n_random = total_fit_individuals  # match sample size
    for _ in range(max(n_random, 500)):
        g = random_genotype(genotype_length, rng)
        for sub in extract_substrings(g):
            random_substrings[sub] += 1

    # Compute enrichment: evolved_freq / random_freq
    enrichment = {}
    for sub, count in evolved_substrings.items():
        random_count = random_substrings.get(sub, 0)
        if random_count > 0:
            enrichment[sub] = count / random_count
        elif count >= 3:
            # Appears in evolved but never in random — highly enriched
            enrichment[sub] = count * 10.0  # large enrichment score

    # Sort by enrichment, take top candidates
    enriched = sorted(enrichment.items(), key=lambda x: x[1], reverse=True)

    print(f"\n  Top 30 enriched substrings (evolved/random ratio):")
    for sub, ratio in enriched[:30]:
        p = develop(sub)
        prog = p.source if p.source else "(no program)"
        evolved_ct = evolved_substrings[sub]
        random_ct = random_substrings.get(sub, 0)
        print(f"    '{sub}' enrichment={ratio:6.1f}x "
              f"(evolved={evolved_ct}, random={random_ct}) -> {prog}")

    # Now score top candidates by assembly potential
    print(f"\n  Scoring top {min(top_n * 3, len(enriched))} candidates "
          f"by assembly potential ({n_assembly_tests} random contexts each)...")

    candidates = [sub for sub, _ in enriched[:top_n * 3]]
    motif_scores = []
    t0 = time.time()

    for motif in candidates:
        stages = score_motif_assembly(motif, n_contexts=n_assembly_tests)
        # Score: weighted by stage (higher = more valuable)
        total = sum(stages.values())
        score = sum(stage * count for stage, count in stages.items()) / total
        s1_plus = sum(count for stage, count in stages.items() if stage >= 1) / total
        motif_scores.append((motif, score, s1_plus, stages))

    elapsed = time.time() - t0
    print(f"  Assembly scoring: {elapsed:.1f}s")

    # Sort by assembly score, take top_n
    motif_scores.sort(key=lambda x: x[1], reverse=True)

    print(f"\n  Top {top_n} learned motifs (by assembly potential):")
    print(f"    {'Motif':>6s} | {'Score':>5s} | {'S1+%':>5s} | {'Program':30s} | Enrichment")
    print(f"    {'-'*6}-+-{'-'*5}-+-{'-'*5}-+-{'-'*30}-+-{'-'*10}")

    learned_motifs = []
    for motif, score, s1_plus, stages in motif_scores[:top_n]:
        p = develop(motif)
        prog = p.source if p.source else "(no program)"
        ratio = enrichment.get(motif, 0)
        print(f"    '{motif:>4s}' | {score:5.2f} | {s1_plus*100:4.1f}% | {prog:30s} | {ratio:.1f}x")
        learned_motifs.append(motif)

    # Check overlap with hand-coded motifs
    hand_coded = {"Da", "DaK", "QDa", "QDaK", "AS", "BS"}
    overlap = set(learned_motifs) & hand_coded
    print(f"\n  Overlap with hand-coded motifs: {overlap if overlap else 'NONE'}")
    print(f"  Hand-coded motifs in top 30 enriched: "
          f"{[s for s, _ in enriched[:30] if s in hand_coded]}")

    return learned_motifs


# ---------------------------------------------------------------------------
# Phase 2: Application — use learned motifs on hard tasks
# ---------------------------------------------------------------------------

def mutate_insert_motif(genotype: str, motifs: list[str], rng: random.Random) -> str:
    """Insert a motif from the given library at a random position."""
    motif = rng.choice(motifs)
    if len(motif) > len(genotype):
        return mutate(genotype, rng)
    insert_pos = rng.randint(0, len(genotype) - len(motif))
    return genotype[:insert_pos] + motif + genotype[insert_pos + len(motif):]


HAND_CODED_MOTIFS = ["Da", "DaK", "QDa", "QDaK", "AS", "BS"]


def make_random_motifs(n=20, rng=None):
    """Generate random 2-4 char motifs as negative control."""
    if rng is None:
        rng = random.Random(12345)
    motifs = []
    for _ in range(n):
        length = rng.randint(2, 4)
        motif = "".join(rng.choice(ALPHABET) for _ in range(length))
        motifs.append(motif)
    return motifs


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


def run_hard_evolution(
    pop_size, genotype_length, generations, contexts, seed,
    motifs=None, use_archive=True,
):
    """Evolution on hard tasks with optional motif insertion."""
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
            evaluate_individual(ind, HARD_TARGETS, contexts)

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
                if motifs:
                    child_geno = mutate_insert_motif(geno, motifs, rng)
                else:
                    child_geno = mutate(geno, rng)
                children.append(Individual(genotype=child_geno))

        for _ in range(pop_size - len(children)):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                if motifs and rng.random() < 0.75:
                    # 75% of mutations are motif insertions (~22.5% overall)
                    child_geno = mutate_insert_motif(parent.genotype, motifs, rng)
                else:
                    child_geno = mutate(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        for ind in children:
            evaluate_individual(ind, HARD_TARGETS, contexts)

        combined = population + children
        combined.sort(key=lambda i: i.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {"history": history}


def run_application_phase(screened_motifs, evolved_motifs=None,
                          pop_size=100, genotype_length=100,
                          generations=300, n_seeds=20):
    """Phase 2: compare motif sources on hard tasks."""
    print("\n" + "=" * 70)
    print("Phase 2: Application — Screened vs Evolved vs Hand-Coded vs Random")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, "
          f"Seeds: {n_seeds}")
    print()

    contexts = make_contexts()
    random_motifs = make_random_motifs(n=20)

    conditions = [
        ("A. No motifs (baseline)", None),
        ("B. Chemistry-screened motifs", screened_motifs),
        ("C. Hand-coded motifs", HAND_CODED_MOTIFS),
        ("D. Random motifs (control)", random_motifs),
    ]
    if evolved_motifs:
        conditions.insert(2, ("B2. Evolution-mined motifs", evolved_motifs))

    all_results = {}

    for cond_name, motifs in conditions:
        print(f"--- {cond_name} ---")
        if motifs:
            print(f"    Motifs: {motifs[:8]}{'...' if len(motifs) > 8 else ''}")
        cond_results = []
        t0 = time.time()

        s3_found = 0
        s4_found = 0
        s5_found = 0

        for seed in range(n_seeds):
            result = run_hard_evolution(
                pop_size, genotype_length, generations, contexts, seed,
                motifs=motifs, use_archive=True,
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
        print(f"  S3 found: {s3_found}/{n_seeds}, S4: {s4_found}/{n_seeds}, "
              f"S5: {s5_found}/{n_seeds}\n")
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
        avg_bonds = sum(f["best_bonds"] for f in finals) / len(finals)

        print(f"\n  {cond_name}:")
        print(f"    Avg fitness: {avg_fit:.3f}")
        print(f"    Avg bonds:   {avg_bonds:.1f}")
        print(f"    S3 found: {s3_seeds}/{n_seeds} seeds")
        print(f"    S4 found: {s4_seeds}/{n_seeds} seeds")
        print(f"    S5 found: {s5_seeds}/{n_seeds} seeds")

    # Stage frequency over time for screened motifs
    if "B. Chemistry-screened motifs" in all_results:
        print("\n--- Stage frequency over time (screened motifs, avg across seeds) ---")
        results = all_results["B. Chemistry-screened motifs"]
        for gen in [0, 10, 25, 50, 100, 150, 200, 250, 299]:
            if gen >= generations:
                continue
            s_avgs = {}
            for s in range(6):
                vals = [r["history"][gen]["stage_counts"].get(s, 0) for r in results]
                s_avgs[s] = sum(vals) / len(vals)
            print(f"    Gen {gen:3d}: " + " ".join(f"S{s}={s_avgs[s]:5.1f}" for s in range(6)))


def screen_chemistry_motifs(max_len=3, n_contexts=100, genotype_length=100, top_n=20):
    """Screen all possible short substrings by bond production in random contexts.

    This is an endogenous discovery method that uses the chemistry itself
    (not evolution, not hand-coding) to identify which character combinations
    reliably produce bonds when embedded in random genotypes.
    """
    print("\n" + "=" * 70)
    print("Chemistry Screening: Bond Production by Substring")
    print("=" * 70)

    all_candidates = []

    for length in range(2, max_len + 1):
        # Generate all possible substrings of this length
        if length == 2:
            candidates = [a + b for a in ALPHABET for b in ALPHABET]
        elif length == 3:
            candidates = [a + b + c for a in ALPHABET for b in ALPHABET for c in ALPHABET]
        else:
            continue  # 4+ is too many

        print(f"\n  Screening {len(candidates):,} substrings of length {length}...")
        t0 = time.time()

        for motif in candidates:
            rng = random.Random(hash(motif) & 0xFFFFFFFF)
            total_bonds = 0
            total_s1_plus = 0
            total_s2_plus = 0

            for _ in range(n_contexts):
                g = random_genotype(genotype_length, rng)
                pos = rng.randint(0, len(g) - len(motif))
                g_with = g[:pos] + motif + g[pos + len(motif):]
                p = develop(g_with)
                total_bonds += p.bond_count
                stage = scaffold_stage(p)
                if stage >= 1:
                    total_s1_plus += 1
                if stage >= 2:
                    total_s2_plus += 1

            avg_bonds = total_bonds / n_contexts
            s1_rate = total_s1_plus / n_contexts
            s2_rate = total_s2_plus / n_contexts

            if avg_bonds > 0.5 or s1_rate > 0.02:
                all_candidates.append((motif, avg_bonds, s1_rate, s2_rate))

        elapsed = time.time() - t0
        print(f"  Screened in {elapsed:.1f}s, {len(all_candidates)} candidates so far")

    # Also compute baseline (no motif insertion)
    rng = random.Random(42)
    baseline_bonds = 0
    baseline_s1 = 0
    for _ in range(n_contexts * 10):
        g = random_genotype(genotype_length, rng)
        p = develop(g)
        baseline_bonds += p.bond_count
        if scaffold_stage(p) >= 1:
            baseline_s1 += 1
    baseline_avg = baseline_bonds / (n_contexts * 10)
    baseline_s1_rate = baseline_s1 / (n_contexts * 10)
    print(f"\n  Baseline (no motif): avg_bonds={baseline_avg:.2f}, S1+={baseline_s1_rate*100:.1f}%")

    # Sort by scaffold stage rate (S1+), then by bond count
    all_candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)

    print(f"\n  Top {top_n} chemistry-screened motifs:")
    print(f"    {'Motif':>6s} | {'Bonds':>5s} | {'S1+%':>5s} | {'S2+%':>5s} | {'Program':30s}")
    print(f"    {'-'*6}-+-{'-'*5}-+-{'-'*5}-+-{'-'*5}-+-{'-'*30}")

    screened_motifs = []
    for motif, avg_bonds, s1_rate, s2_rate in all_candidates[:top_n]:
        p = develop(motif)
        prog = p.source if p.source else "(no program)"
        print(f"    '{motif:>4s}' | {avg_bonds:5.2f} | {s1_rate*100:4.1f}% | {s2_rate*100:4.1f}% | {prog}")
        screened_motifs.append(motif)

    # Check overlap with hand-coded
    hand_coded = {"Da", "DaK", "QDa", "QDaK", "AS", "BS"}
    overlap = set(screened_motifs) & hand_coded
    print(f"\n  Overlap with hand-coded motifs: {overlap if overlap else 'NONE'}")

    # Show where hand-coded motifs rank
    motif_dict = {m: (b, s1, s2) for m, b, s1, s2 in all_candidates}
    print(f"  Hand-coded motif scores:")
    for hm in sorted(hand_coded):
        if hm in motif_dict:
            b, s1, s2 = motif_dict[hm]
            p = develop(hm)
            rank = next(i for i, (m, _, _, _) in enumerate(all_candidates) if m == hm) + 1
            print(f"    '{hm}': bonds={b:.2f} S1+={s1*100:.1f}% S2+={s2*100:.1f}% "
                  f"rank={rank}/{len(all_candidates)} -> {p.source}")
        else:
            print(f"    '{hm}': below screening threshold")

    return screened_motifs


def main():
    # Phase 0: Chemistry screening (endogenous, no evolution needed)
    screened_motifs = screen_chemistry_motifs(max_len=3, n_contexts=100, top_n=20)

    # Phase 1: Evolution-based discovery (for comparison)
    evolved_motifs = discover_motifs(
        n_runs=30, pop_size=100, genotype_length=100,
        generations=100, top_n=20, n_assembly_tests=200,
    )

    # Phase 2: Application — compare all sources
    run_application_phase(screened_motifs, evolved_motifs)


if __name__ == "__main__":
    main()
