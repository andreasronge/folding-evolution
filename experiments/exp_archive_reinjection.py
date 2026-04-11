"""
Archive + Reinjection of Scaffold Carriers Experiment.

Tests the survival-time hypothesis: if S3 carriers persist long enough,
does the S3→S4→S5 transition chain fire?

Design:
  - Detect S3/S4/S5 carriers each generation using substructure classification
  - Store them in an archive (genotypes, not just labels)
  - Reinject a small number from the archive each generation
  - Compare: baseline (no archive) vs archive reinjection

The archive preserves the genotype with its fold context, so reinjected
individuals carry the specific spatial arrangement that produced the scaffold.

Three conditions:
  A. Baseline: standard evolution, no archive
  B. Archive reinjection: detect scaffold carriers, archive top ones,
     reinject 5% of population from archive each generation
  C. Archive + Pareto: two-objective selection on (task fitness, scaffold stage),
     plus archive reinjection

Measures:
  - S3/S4/S5 frequency per generation
  - First generation where S4 appears, where S5 appears
  - Whether S5 (count(filter(fn(cmp(get_price))))) ever sweeps
  - Archive size and diversity over time
"""

import random
import time
from collections import defaultdict, Counter
from typing import Any, Callable

from folding_evolution.alphabet import random_genotype
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword
from folding_evolution.dynamics import partial_credit
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, _count_bonds
from folding_evolution.selection import tournament_select


# ---------------------------------------------------------------------------
# Substructure classification
# ---------------------------------------------------------------------------

def scaffold_stage(prog) -> int:
    """Return the highest scaffold stage present in the program.

    0: no useful scaffold
    1: (get x :price)
    2: (> (get x :price) VALUE)
    3: (fn x (> (get x :price) VALUE))
    4: (filter (fn x (> ...)) data/...)
    5: (count/first (filter (fn x (> (get x :price) ...)) data/...))
    """
    if prog.ast is None:
        return 0
    labels = set()
    _classify_walk(prog.ast, labels)

    if "S5" in labels:
        return 5
    if "S4" in labels:
        return 4
    if "S3" in labels:
        return 3
    if "S2" in labels:
        return 2
    if "S1" in labels:
        return 1
    return 0


def _classify_walk(node, labels):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    hn = head.name if isinstance(head, Symbol) else None

    # S1: (get x :price)
    if hn == "get" and len(node.items) == 3 and isinstance(node.items[2], Keyword):
        if node.items[2].name == "price":
            labels.add("S1")

    # S2: (> (get x :price) VALUE)
    if hn in (">", "<", "=") and len(node.items) == 3:
        for op in node.items[1:]:
            if _is_get_price(op):
                labels.add("S2")

    # S3: (fn x (CMP (get x :price) VALUE))
    if hn == "fn" and len(node.items) >= 3:
        body = node.items[2]
        if isinstance(body, ListExpr) and body.items:
            bh = body.items[0]
            if isinstance(bh, Symbol) and bh.name in (">", "<", "="):
                for op in body.items[1:]:
                    if _is_get_price(op):
                        labels.add("S3")

    # S4: (filter/map (fn x (CMP (get x :price) ...)) data/...)
    if hn in ("filter", "map", "reduce", "group_by") and len(node.items) >= 3:
        fn_arg = node.items[1]
        if isinstance(fn_arg, ListExpr) and fn_arg.items:
            fh = fn_arg.items[0]
            if isinstance(fh, Symbol) and fh.name == "fn" and len(fn_arg.items) >= 3:
                body = fn_arg.items[2]
                if isinstance(body, ListExpr) and body.items:
                    bh = body.items[0]
                    if isinstance(bh, Symbol) and bh.name in (">", "<", "="):
                        for op in body.items[1:]:
                            if _is_get_price(op):
                                labels.add("S4")

    # S5: (count/first/... (filter/map (fn x (CMP (get x :price) ...)) data/...))
    if hn in ("count", "first", "rest", "last", "reverse", "sort") and len(node.items) >= 2:
        arg = node.items[1]
        if isinstance(arg, ListExpr) and arg.items:
            ah = arg.items[0]
            if isinstance(ah, Symbol) and ah.name in ("filter", "map"):
                # Check for full chain inside
                inner_labels = set()
                _classify_walk(arg, inner_labels)
                if "S4" in inner_labels:
                    labels.add("S5")

    for item in node.items:
        _classify_walk(item, labels)


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
# Archive
# ---------------------------------------------------------------------------

class ScaffoldArchive:
    """Archive of scaffold-carrying genotypes, organized by stage."""

    def __init__(self, max_per_stage: int = 20):
        self.max_per_stage = max_per_stage
        # stage -> list of (genotype, fitness, bond_count)
        self.entries: dict[int, list[tuple[str, float, int]]] = defaultdict(list)

    def update(self, population: list[Individual]):
        """Scan population and archive scaffold carriers."""
        for ind in population:
            stage = scaffold_stage(ind.program)
            if stage >= 2:  # archive S2+ carriers
                entries = self.entries[stage]
                # Keep top by bond count (higher bonds = richer fold context)
                entries.append((ind.genotype, ind.fitness, ind.program.bond_count))
                entries.sort(key=lambda e: e[2], reverse=True)
                if len(entries) > self.max_per_stage:
                    self.entries[stage] = entries[:self.max_per_stage]

    def sample(self, n: int, rng: random.Random) -> list[str]:
        """Sample n genotypes from the archive, preferring higher stages."""
        all_entries = []
        for stage in sorted(self.entries.keys(), reverse=True):
            for geno, fit, bonds in self.entries[stage]:
                all_entries.append((stage, geno))

        if not all_entries:
            return []

        # Weighted by stage: S4 carriers are 4x more valuable than S2
        weights = [stage ** 2 for stage, _ in all_entries]
        total_w = sum(weights)
        if total_w == 0:
            return []

        selected = []
        for _ in range(min(n, len(all_entries))):
            r = rng.random() * total_w
            cumulative = 0
            for i, w in enumerate(weights):
                cumulative += w
                if cumulative >= r:
                    selected.append(all_entries[i][1])
                    break

        return selected

    def summary(self) -> str:
        parts = []
        for stage in sorted(self.entries.keys()):
            parts.append(f"S{stage}:{len(self.entries[stage])}")
        return " ".join(parts) if parts else "empty"


# ---------------------------------------------------------------------------
# Evolution
# ---------------------------------------------------------------------------

def evaluate_individual(ind, targets, contexts):
    """Evaluate fitness with partial credit."""
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


def run_experiment(
    pop_size: int, genotype_length: int, generations: int,
    contexts: list, seed: int,
    use_archive: bool, archive_reinject_pct: float = 0.05,
) -> dict:
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    archive = ScaffoldArchive() if use_archive else None
    history = []

    for gen in range(generations):
        # Evaluate
        for ind in population:
            evaluate_individual(ind, TARGETS, contexts)

        # Archive scaffold carriers
        if archive is not None:
            archive.update(population)

        # Stats
        best = max(population, key=lambda i: i.fitness)
        stage_counts = Counter()
        for ind in population:
            stage_counts[scaffold_stage(ind.program)] += 1

        entry = {
            "gen": gen,
            "best_fitness": best.fitness,
            "best_source": best.program.source if best.program else None,
            "best_bonds": best.program.bond_count if best.program else 0,
            "best_stage": scaffold_stage(best.program),
            "stage_counts": dict(stage_counts),
            "archive_summary": archive.summary() if archive else "none",
        }
        history.append(entry)

        # Reproduce
        n_reinject = int(pop_size * archive_reinject_pct) if archive else 0
        n_children = pop_size - n_reinject

        children = []

        # Archive reinjection
        if archive and n_reinject > 0:
            reinjected = archive.sample(n_reinject, rng)
            for geno in reinjected:
                # Mutate the archived genotype slightly to create variation
                child_geno = mutate(geno, rng)
                children.append(Individual(genotype=child_geno))

        # Standard reproduction
        for _ in range(n_children):
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
            evaluate_individual(ind, TARGETS, contexts)

        # (mu+lambda) selection
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
    generations = 300  # longer runs to give transitions time
    n_seeds = 20       # more seeds for statistical power

    print("=" * 70)
    print("Archive + Reinjection Experiment")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {generations}, Seeds: {n_seeds}")
    print(f"Archive reinjection: 5% of population per generation")
    print()

    conditions = [
        ("Baseline (no archive)", False),
        ("Archive + reinjection", True),
    ]

    all_results = {}

    for cond_name, use_archive in conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        s4_found_seeds = 0
        s5_found_seeds = 0

        for seed in range(n_seeds):
            result = run_experiment(
                pop_size, genotype_length, generations,
                contexts, seed, use_archive,
            )
            cond_results.append(result)

            # Find first gen where S4 and S5 appear
            first_s4 = None
            first_s5 = None
            max_stage = 0
            for entry in result["history"]:
                sc = entry["stage_counts"]
                if sc.get(4, 0) > 0 and first_s4 is None:
                    first_s4 = entry["gen"]
                if sc.get(5, 0) > 0 and first_s5 is None:
                    first_s5 = entry["gen"]
                for s in sc:
                    if s > max_stage:
                        max_stage = s

            final = result["history"][-1]
            if first_s4 is not None:
                s4_found_seeds += 1
            if first_s5 is not None:
                s5_found_seeds += 1

            s4_str = f"gen {first_s4}" if first_s4 is not None else "NEVER"
            s5_str = f"gen {first_s5}" if first_s5 is not None else "NEVER"

            print(f"  Seed {seed:2d}: fit={final['best_fitness']:.3f} "
                  f"stage={final['best_stage']} "
                  f"first_S4={s4_str:>8s} first_S5={s5_str:>8s} "
                  f"max_stage={max_stage} "
                  f"src={final['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s")
        print(f"  S4 found in: {s4_found_seeds}/{n_seeds} seeds")
        print(f"  S5 found in: {s5_found_seeds}/{n_seeds} seeds\n")
        all_results[cond_name] = cond_results

    # === Summary ===
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for cond_name, results in all_results.items():
        finals = [r["history"][-1] for r in results]
        avg_fit = sum(f["best_fitness"] for f in finals) / len(finals)
        avg_stage = sum(f["best_stage"] for f in finals) / len(finals)

        # Count seeds where S4/S5 ever appeared
        s4_seeds = sum(1 for r in results if any(e["stage_counts"].get(4, 0) > 0 for e in r["history"]))
        s5_seeds = sum(1 for r in results if any(e["stage_counts"].get(5, 0) > 0 for e in r["history"]))

        # Average first S4/S5 generation (among seeds where they appeared)
        s4_gens = [min(e["gen"] for e in r["history"] if e["stage_counts"].get(4, 0) > 0)
                   for r in results if any(e["stage_counts"].get(4, 0) > 0 for e in r["history"])]
        s5_gens = [min(e["gen"] for e in r["history"] if e["stage_counts"].get(5, 0) > 0)
                   for r in results if any(e["stage_counts"].get(5, 0) > 0 for e in r["history"])]

        avg_s4_gen = sum(s4_gens) / len(s4_gens) if s4_gens else float('inf')
        avg_s5_gen = sum(s5_gens) / len(s5_gens) if s5_gens else float('inf')

        print(f"\n  {cond_name}:")
        print(f"    Avg final fitness: {avg_fit:.3f}")
        print(f"    Avg final stage:   {avg_stage:.1f}")
        print(f"    S4 found:          {s4_seeds}/{n_seeds} seeds (avg gen {avg_s4_gen:.0f})")
        print(f"    S5 found:          {s5_seeds}/{n_seeds} seeds (avg gen {avg_s5_gen:.0f})")

    # Stage frequency over time
    print("\n--- Stage frequency over time (avg across seeds) ---")
    for cond_name, results in all_results.items():
        print(f"\n  {cond_name}:")
        key_gens = [0, 25, 50, 100, 150, 200, 250, 299]
        for gen in key_gens:
            if gen >= generations:
                continue
            s3_counts = []
            s4_counts = []
            s5_counts = []
            for r in results:
                sc = r["history"][gen]["stage_counts"]
                s3_counts.append(sc.get(3, 0))
                s4_counts.append(sc.get(4, 0))
                s5_counts.append(sc.get(5, 0))
            avg_s3 = sum(s3_counts) / len(s3_counts)
            avg_s4 = sum(s4_counts) / len(s4_counts)
            avg_s5 = sum(s5_counts) / len(s5_counts)
            print(f"    Gen {gen:3d}: S3={avg_s3:5.1f} S4={avg_s4:5.1f} S5={avg_s5:5.1f}")


if __name__ == "__main__":
    main()
