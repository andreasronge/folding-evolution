"""
Experiment 1.8: Neutral Drift Phases — Intermediate Preservation Test.

Tests whether selection is prematurely purging low-fitness intermediates
that are necessary precursors to S3/S4. Alternates between selection
windows (normal evolution) and drift windows (fitness = constant, random
survival) while continuously supplying chemistry-screened motifs.

Four conditions (same motifs, same seeds, same insertion rate):
  A. Continuous selection (baseline)
  B. 10-gen drift every 20 gens (frequent short drift)
  C. 25-gen drift every 50 gens (infrequent long drift)
  D. Weak selection during drift windows (tournament_size=1 instead of 3)

Mechanistic readouts:
  - S1/S2 carrier lifetime (gens before purge)
  - S1/S2 co-occurrence (multiple carriers in same generation)
  - S3 occupancy during vs after drift windows
  - Junk-bond control: stage-specific occupancy, not just avg bonds

Uses dynamics.py engine (develop_batch, Rust VM scoring) for performance.
"""

import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass

from folding_evolution.alphabet import random_genotype, ALPHABET
from folding_evolution.dynamics import (
    partial_credit, evaluate_multi_target,
    _develop_population, _develop_and_score_vm, _develop_and_score_python,
)
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_batch, Program
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
# Chemistry-screened motifs (top S2+ producers from exp_learned_motifs)
# ---------------------------------------------------------------------------

SCREENED_MOTIFS = [
    'DaL', 'KaD', 'aDM', 'jDa', '3aD', 'DaB', 'caD', 'aJD',
    'aDT', 'QaD', 'iDa', 'raD', 'aDl', 'aDi', 'aDG', 'aDP',
    'aD', 'Da', 'KS', 'A7',
]


def mutate_with_motif(genotype: str, rng: random.Random) -> str:
    """75% motif insertion, 25% standard mutation."""
    if rng.random() < 0.75:
        motif = rng.choice(SCREENED_MOTIFS)
        if len(motif) > len(genotype):
            return mutate(genotype, rng)
        pos = rng.randint(0, len(genotype) - len(motif))
        return genotype[:pos] + motif + genotype[pos + len(motif):]
    return mutate(genotype, rng)


# ---------------------------------------------------------------------------
# Per-generation scaffold tracking
# ---------------------------------------------------------------------------

@dataclass
class GenRecord:
    gen: int
    phase: str  # "select" or "drift"
    best_fitness: float
    avg_fitness: float
    best_source: str | None
    best_bonds: int
    stage_counts: dict  # {stage: count}
    s1_plus_count: int  # individuals with stage >= 1
    s2_plus_count: int
    s3_plus_count: int


def record_generation(gen: int, population: list[Individual], phase: str) -> GenRecord:
    """Record detailed scaffold metrics for one generation."""
    best = max(population, key=lambda i: i.fitness)
    avg_fit = sum(i.fitness for i in population) / len(population)
    stage_counts = Counter()
    for ind in population:
        stage_counts[scaffold_stage(ind.program)] += 1

    return GenRecord(
        gen=gen, phase=phase,
        best_fitness=best.fitness,
        avg_fitness=avg_fit,
        best_source=best.program.source if best.program else None,
        best_bonds=best.program.bond_count if best.program else 0,
        stage_counts=dict(stage_counts),
        s1_plus_count=sum(c for s, c in stage_counts.items() if s >= 1),
        s2_plus_count=sum(c for s, c in stage_counts.items() if s >= 2),
        s3_plus_count=sum(c for s, c in stage_counts.items() if s >= 3),
    )


# ---------------------------------------------------------------------------
# Evolution engine with drift phases
# ---------------------------------------------------------------------------

def run_drift_evolution(
    pop_size: int,
    genotype_length: int,
    total_gens: int,
    contexts: list,
    targets: list,
    seed: int,
    drift_interval: int | None,   # None = no drift, just selection
    drift_duration: int = 0,
    weak_selection: bool = False,  # if True, use tournament_size=1 during drift
):
    """Evolution with periodic drift windows.

    drift_interval: every N gens, enter a drift window
    drift_duration: how many gens the drift window lasts
    weak_selection: if True, use tournament_size=1 during "drift" (not pure random)
    """
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    # Setup Rust VM scoring
    use_vm = _USE_RUST_VM
    rust_ctx = None
    rust_targets = None
    if use_vm:
        rust_ctx = _RustContexts(contexts)
        target_outputs = [[t(ctx) for ctx in contexts] for t in targets]
        rust_targets = _RustTargetOutputs(target_outputs)

    history = []

    for gen in range(total_gens):
        # Determine phase
        if drift_interval is not None and drift_duration > 0:
            cycle_pos = gen % drift_interval
            in_drift = cycle_pos >= (drift_interval - drift_duration)
        else:
            in_drift = False

        phase = "drift" if in_drift else "select"

        # Develop and score population
        if use_vm:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)
            for ind in population:
                ind.fitness = evaluate_multi_target(ind, targets, contexts)

        # Record metrics (need programs for scaffold_stage)
        # VM path sets program.source but not evaluate — we need to
        # develop for scaffold detection
        if use_vm:
            genotypes = [ind.genotype for ind in population]
            programs = develop_batch(genotypes)
            for ind, prog in zip(population, programs):
                ind.program = prog

        record = record_generation(gen, population, phase)
        history.append(record)

        # Produce children with motif-supplying operators
        children = []
        for _ in range(pop_size):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = mutate_with_motif(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        # Evaluate children
        if use_vm:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)
            for ind in children:
                ind.fitness = evaluate_multi_target(ind, targets, contexts)

        # Selection: fitness-based during selection, random/weak during drift
        combined = population + children

        if in_drift and not weak_selection:
            # Pure drift: random survival (shuffle, take first pop_size)
            rng.shuffle(combined)
            population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]
        elif in_drift and weak_selection:
            # Weak selection: tournament_size=1 (random parent) but still mu+lambda
            # The children were already produced with tournament_size=3,
            # but survival is random — keep random pop_size from combined
            combined_with_slight_bias = sorted(
                combined, key=lambda i: i.fitness + rng.random() * 0.5, reverse=True
            )
            population = [Individual(genotype=i.genotype)
                          for i in combined_with_slight_bias[:pop_size]]
        else:
            # Normal selection
            combined.sort(key=lambda ind: ind.fitness, reverse=True)
            population = [Individual(genotype=ind.genotype)
                          for ind in combined[:pop_size]]

    return history


# ---------------------------------------------------------------------------
# Carrier lifetime analysis
# ---------------------------------------------------------------------------

def analyze_carrier_lifetimes(history: list[GenRecord]) -> dict:
    """Compute S1/S2/S3 carrier lifetime and co-occurrence statistics."""
    # Track consecutive generations with S1+, S2+, S3+ carriers
    s1_runs = []
    s2_runs = []
    s3_runs = []
    current_s1 = 0
    current_s2 = 0
    current_s3 = 0

    # Co-occurrence: how many gens have 2+ carriers at each level
    s1_cooccur = 0
    s2_cooccur = 0

    # Phase-separated metrics
    drift_s1_total = 0
    drift_s2_total = 0
    drift_s3_total = 0
    drift_gens = 0
    select_s1_total = 0
    select_s2_total = 0
    select_s3_total = 0
    select_gens = 0

    for rec in history:
        if rec.s1_plus_count > 0:
            current_s1 += 1
        else:
            if current_s1 > 0:
                s1_runs.append(current_s1)
            current_s1 = 0

        if rec.s2_plus_count > 0:
            current_s2 += 1
        else:
            if current_s2 > 0:
                s2_runs.append(current_s2)
            current_s2 = 0

        if rec.s3_plus_count > 0:
            current_s3 += 1
        else:
            if current_s3 > 0:
                s3_runs.append(current_s3)
            current_s3 = 0

        if rec.s1_plus_count >= 2:
            s1_cooccur += 1
        if rec.s2_plus_count >= 2:
            s2_cooccur += 1

        if rec.phase == "drift":
            drift_gens += 1
            drift_s1_total += rec.s1_plus_count
            drift_s2_total += rec.s2_plus_count
            drift_s3_total += rec.s3_plus_count
        else:
            select_gens += 1
            select_s1_total += rec.s1_plus_count
            select_s2_total += rec.s2_plus_count
            select_s3_total += rec.s3_plus_count

    # Close open runs
    if current_s1 > 0: s1_runs.append(current_s1)
    if current_s2 > 0: s2_runs.append(current_s2)
    if current_s3 > 0: s3_runs.append(current_s3)

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    return {
        "s1_avg_lifetime": avg(s1_runs),
        "s1_max_lifetime": max(s1_runs) if s1_runs else 0,
        "s1_n_runs": len(s1_runs),
        "s2_avg_lifetime": avg(s2_runs),
        "s2_max_lifetime": max(s2_runs) if s2_runs else 0,
        "s2_n_runs": len(s2_runs),
        "s3_avg_lifetime": avg(s3_runs),
        "s3_max_lifetime": max(s3_runs) if s3_runs else 0,
        "s3_n_runs": len(s3_runs),
        "s1_cooccur_gens": s1_cooccur,
        "s2_cooccur_gens": s2_cooccur,
        "drift_s1_density": drift_s1_total / drift_gens if drift_gens > 0 else 0,
        "drift_s2_density": drift_s2_total / drift_gens if drift_gens > 0 else 0,
        "drift_s3_density": drift_s3_total / drift_gens if drift_gens > 0 else 0,
        "select_s1_density": select_s1_total / select_gens if select_gens > 0 else 0,
        "select_s2_density": select_s2_total / select_gens if select_gens > 0 else 0,
        "select_s3_density": select_s3_total / select_gens if select_gens > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def main():
    pop_size = 100
    genotype_length = 100
    total_gens = 300
    n_seeds = 20
    contexts = make_contexts()
    targets = [tfn for _, tfn in TARGETS]

    conditions = [
        ("A. Continuous selection", None, 0, False),
        ("B. Drift 10/20 (short frequent)", 20, 10, False),
        ("C. Drift 25/50 (long infrequent)", 50, 25, False),
        ("D. Weak selection 10/20", 20, 10, True),
    ]

    print("=" * 70)
    print("Experiment 1.8: Neutral Drift Phases — Preservation Test")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {total_gens}, "
          f"Seeds: {n_seeds}")
    print(f"Motifs: {SCREENED_MOTIFS[:6]}... ({len(SCREENED_MOTIFS)} total)")
    print(f"Rust VM: {'YES' if _USE_RUST_VM else 'NO'}")
    print()

    all_results = {}

    for cond_name, drift_interval, drift_duration, weak in conditions:
        print(f"--- {cond_name} ---")
        cond_histories = []
        cond_lifetimes = []
        t0 = time.time()

        s3_found = 0
        s4_found = 0
        s5_found = 0

        for seed in range(n_seeds):
            history = run_drift_evolution(
                pop_size, genotype_length, total_gens, contexts, targets,
                seed, drift_interval, drift_duration, weak,
            )
            cond_histories.append(history)

            # Track scaffold discovery
            first = {}
            max_stage = 0
            for rec in history:
                for s in range(3, 6):
                    if rec.stage_counts.get(s, 0) > 0 and s not in first:
                        first[s] = rec.gen
                for s in rec.stage_counts:
                    if s > max_stage:
                        max_stage = s

            if 3 in first: s3_found += 1
            if 4 in first: s4_found += 1
            if 5 in first: s5_found += 1

            # Carrier lifetime analysis
            lifetimes = analyze_carrier_lifetimes(history)
            cond_lifetimes.append(lifetimes)

            final = history[-1]
            f_s3 = f"gen {first[3]}" if 3 in first else "NEVER"
            f_s4 = f"gen {first[4]}" if 4 in first else "NEVER"
            f_s5 = f"gen {first[5]}" if 5 in first else "NEVER"
            s1_life = f"{lifetimes['s1_avg_lifetime']:.1f}"
            s2_life = f"{lifetimes['s2_avg_lifetime']:.1f}"

            print(f"  Seed {seed:2d}: fit={final.best_fitness:.3f} "
                  f"S3={f_s3:>8s} S4={f_s4:>8s} S5={f_s5:>8s} "
                  f"s1_life={s1_life:>4s} s2_life={s2_life:>4s} "
                  f"src={final.best_source}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s")
        print(f"  S3: {s3_found}/{n_seeds}, S4: {s4_found}/{n_seeds}, "
              f"S5: {s5_found}/{n_seeds}\n")
        all_results[cond_name] = (cond_histories, cond_lifetimes)

    # ======================================================================
    # SUMMARY
    # ======================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for cond_name, (histories, lifetimes) in all_results.items():
        s3_seeds = sum(1 for h in histories if any(
            r.stage_counts.get(3, 0) > 0 for r in h))
        s4_seeds = sum(1 for h in histories if any(
            r.stage_counts.get(4, 0) > 0 for r in h))
        s5_seeds = sum(1 for h in histories if any(
            r.stage_counts.get(5, 0) > 0 for r in h))

        avg_fit = sum(h[-1].best_fitness for h in histories) / len(histories)
        avg_bonds = sum(h[-1].best_bonds for h in histories) / len(histories)

        # Aggregate lifetime metrics
        avg_s1_life = sum(l["s1_avg_lifetime"] for l in lifetimes) / len(lifetimes)
        avg_s2_life = sum(l["s2_avg_lifetime"] for l in lifetimes) / len(lifetimes)
        avg_s3_life = sum(l["s3_avg_lifetime"] for l in lifetimes) / len(lifetimes)
        avg_s1_cooccur = sum(l["s1_cooccur_gens"] for l in lifetimes) / len(lifetimes)
        avg_s2_cooccur = sum(l["s2_cooccur_gens"] for l in lifetimes) / len(lifetimes)

        print(f"\n  {cond_name}:")
        print(f"    Avg fitness: {avg_fit:.3f}, Avg bonds: {avg_bonds:.1f}")
        print(f"    S3: {s3_seeds}/{n_seeds}, S4: {s4_seeds}/{n_seeds}, "
              f"S5: {s5_seeds}/{n_seeds}")
        print(f"    Carrier lifetimes (avg gens): S1={avg_s1_life:.1f}, "
              f"S2={avg_s2_life:.1f}, S3={avg_s3_life:.1f}")
        print(f"    Co-occurrence (gens with 2+ carriers): "
              f"S1={avg_s1_cooccur:.1f}, S2={avg_s2_cooccur:.1f}")

        # Phase-separated densities (only for drift conditions)
        if any(l["drift_s1_density"] > 0 for l in lifetimes):
            avg_drift_s1 = sum(l["drift_s1_density"] for l in lifetimes) / len(lifetimes)
            avg_drift_s2 = sum(l["drift_s2_density"] for l in lifetimes) / len(lifetimes)
            avg_select_s1 = sum(l["select_s1_density"] for l in lifetimes) / len(lifetimes)
            avg_select_s2 = sum(l["select_s2_density"] for l in lifetimes) / len(lifetimes)
            print(f"    Density during drift: S1={avg_drift_s1:.2f}, S2={avg_drift_s2:.2f}")
            print(f"    Density during selection: S1={avg_select_s1:.2f}, S2={avg_select_s2:.2f}")

    # Stage frequency over time (avg across seeds)
    print("\n--- Stage occupancy over time (avg across seeds) ---")
    for cond_name, (histories, _) in all_results.items():
        print(f"\n  {cond_name}:")
        key_gens = [0, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250, 299]
        for gen in key_gens:
            if gen >= total_gens:
                continue
            s1_avg = sum(h[gen].s1_plus_count for h in histories) / len(histories)
            s2_avg = sum(h[gen].s2_plus_count for h in histories) / len(histories)
            s3_avg = sum(h[gen].s3_plus_count for h in histories) / len(histories)
            phase = histories[0][gen].phase
            print(f"    Gen {gen:3d} [{phase:6s}]: "
                  f"S1+={s1_avg:5.1f} S2+={s2_avg:5.1f} S3+={s3_avg:5.1f}")


if __name__ == "__main__":
    main()
