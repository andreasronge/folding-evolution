"""
S3→S4 Transition Analysis.

Maps the exact probability and mechanism of each structural step in the
filter program assembly chain. Answers:

1. How often does mutation of S3 genotypes produce S4 assemblies?
2. How often does mutation of S4 produce count(S4)?
3. Which character positions and substitutions create successful transitions?
4. Does crossover between partial-module genotypes ever combine them?
5. What is the fold-context fragility of each stage?

Works at two scales:
- Core genotypes (short, no padding): pure structural transition analysis
- Padded genotypes (length 100): realistic evolutionary context
"""

import random
import time
from collections import defaultdict, Counter

from folding_evolution.alphabet import random_genotype, ALPHABET
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword
from folding_evolution.fold import fold
from folding_evolution.chemistry import assemble
from folding_evolution.operators import crossover
from folding_evolution.phenotype import develop, _count_bonds, ast_to_string


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify(prog) -> set[str]:
    """Return set of structural labels for a program."""
    labels = set()
    if prog.ast is None:
        return labels
    _classify_walk(prog.ast, labels)
    return labels


def _classify_walk(node, labels):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    hn = head.name if isinstance(head, Symbol) else None

    # L1: (get x :KEY)
    if hn == "get" and len(node.items) == 3 and isinstance(node.items[2], Keyword):
        labels.add("L1_get")
        if node.items[2].name == "price":
            labels.add("L1_get_price")

    # L2: comparator with assembled operand
    if hn in (">", "<", "=") and len(node.items) == 3:
        labels.add("L2_cmp")
        for op in node.items[1:]:
            if _is_get(op):
                labels.add("L2_cmp_get")
            if _is_get_price(op):
                labels.add("L2_cmp_get_price")

    # L3: (fn x EXPR)
    if hn == "fn" and len(node.items) >= 3:
        labels.add("L3_fn")
        body = node.items[2]
        if isinstance(body, ListExpr) and body.items:
            bh = body.items[0]
            if isinstance(bh, Symbol) and bh.name in (">", "<", "="):
                labels.add("L3_fn_cmp")
                for op in body.items[1:]:
                    if _is_get_price(op):
                        labels.add("L3_fn_cmp_get_price")

    # L4: (filter/map FN DATA)
    if hn in ("filter", "map", "reduce", "group_by") and len(node.items) >= 3:
        labels.add("L4_higher")
        fn_arg = node.items[1]
        data_arg = node.items[2]
        if isinstance(fn_arg, ListExpr) and fn_arg.items:
            fh = fn_arg.items[0]
            if isinstance(fh, Symbol) and fh.name == "fn":
                labels.add("L4_higher_fn")
                # Check if fn has a real predicate
                if len(fn_arg.items) >= 3:
                    body = fn_arg.items[2]
                    if isinstance(body, ListExpr) and body.items:
                        bh = body.items[0]
                        if isinstance(bh, Symbol) and bh.name in (">", "<", "="):
                            labels.add("L4_filter_fn_cmp")
                            for op in body.items[1:]:
                                if _is_get_price(op):
                                    labels.add("L4_filter_fn_cmp_get_price")
                    else:
                        labels.add("L4_trivial_filter")  # fn x LITERAL
        if isinstance(data_arg, ListExpr) and data_arg.items:
            dh = data_arg.items[0]
            if isinstance(dh, Symbol) and dh.name in ("filter", "map"):
                labels.add("L4_nested")

    # L5: (count/first COLLECTION)
    if hn in ("count", "first", "rest", "last", "reverse", "sort"):
        labels.add("L5_wrapper")
        if len(node.items) >= 2:
            arg = node.items[1]
            if isinstance(arg, ListExpr) and arg.items:
                ah = arg.items[0]
                if isinstance(ah, Symbol) and ah.name == "filter":
                    labels.add("L5_count_filter")
                    # Check for full target: count(filter(fn(cmp(get price))))
                    if "L4_filter_fn_cmp_get_price" in labels or _check_full_chain(arg):
                        labels.add("FULL_TARGET")

    for item in node.items:
        _classify_walk(item, labels)


def _check_full_chain(filter_node):
    """Check if a filter node contains the full predicate chain."""
    if not isinstance(filter_node, ListExpr) or len(filter_node.items) < 3:
        return False
    fn_arg = filter_node.items[1]
    if not isinstance(fn_arg, ListExpr) or not fn_arg.items:
        return False
    if not (isinstance(fn_arg.items[0], Symbol) and fn_arg.items[0].name == "fn"):
        return False
    if len(fn_arg.items) < 3:
        return False
    body = fn_arg.items[2]
    if not isinstance(body, ListExpr) or not body.items:
        return False
    bh = body.items[0]
    if not (isinstance(bh, Symbol) and bh.name in (">", "<", "=")):
        return False
    for op in body.items[1:]:
        if _is_get_price(op):
            return True
    return False


def _is_get(node):
    return (isinstance(node, ListExpr) and len(node.items) >= 2 and
            isinstance(node.items[0], Symbol) and node.items[0].name == "get")


def _is_get_price(node):
    return (isinstance(node, ListExpr) and len(node.items) == 3 and
            isinstance(node.items[0], Symbol) and node.items[0].name == "get" and
            isinstance(node.items[2], Keyword) and node.items[2].name == "price")


# ---------------------------------------------------------------------------
# Analysis 1: Core genotype transitions (short genotypes)
# ---------------------------------------------------------------------------

def analyze_core_transitions():
    """Analyze transitions on short genotypes without padding."""
    print("=" * 70)
    print("Analysis 1: Core Genotype Transitions")
    print("=" * 70)

    stages = {
        "S1": ("Da", "L1_get_price"),
        "S2": ("DaK5", "L2_cmp_get_price"),
        "S3": ("QDaK5", "L3_fn_cmp_get_price"),
        "S4": ("QDaK5XAS", "L4_filter_fn_cmp_get_price"),
        "S5": ("BQDaK5XAS", "FULL_TARGET"),
    }

    # Verify stages
    print("\nStage verification:")
    for name, (geno, target_label) in stages.items():
        p = develop(geno)
        labels = classify(p)
        has_target = target_label in labels
        print(f"  {name}: \"{geno}\" -> {p.source} | {target_label}: {'YES' if has_target else 'NO'}")

    # For each stage, try all single-char mutations and insertions
    print("\n--- Single-character mutations ---")
    for stage_name, (geno, _) in stages.items():
        transitions = defaultdict(list)
        total_mutants = 0

        for pos in range(len(geno)):
            for char in ALPHABET:
                if char == geno[pos]:
                    continue
                mutant = geno[:pos] + char + geno[pos + 1:]
                p = develop(mutant)
                labels = classify(p)
                total_mutants += 1

                for target_name, (_, target_label) in stages.items():
                    if target_label in labels and target_name != stage_name:
                        transitions[target_name].append((pos, geno[pos], char, p.source))

        print(f"\n  {stage_name} (\"{geno}\") — {total_mutants} point mutations:")
        for target_name in stages:
            if target_name == stage_name:
                continue
            hits = transitions.get(target_name, [])
            pct = len(hits) / total_mutants * 100 if total_mutants > 0 else 0
            print(f"    → {target_name}: {len(hits)}/{total_mutants} ({pct:.2f}%)")
            for pos, old, new, src in hits[:3]:
                print(f"        pos {pos}: {old}→{new} | {src}")

    # Single-char INSERTIONS (grow the genotype by 1)
    print("\n--- Single-character insertions ---")
    for stage_name, (geno, _) in stages.items():
        transitions = defaultdict(list)
        total = 0

        for pos in range(len(geno) + 1):
            for char in ALPHABET:
                inserted = geno[:pos] + char + geno[pos:]
                p = develop(inserted)
                labels = classify(p)
                total += 1

                for target_name, (_, target_label) in stages.items():
                    if target_label in labels and target_name > stage_name:
                        transitions[target_name].append((pos, char, p.source))

        next_stages = [s for s in stages if s > stage_name]
        for target_name in next_stages:
            hits = transitions.get(target_name, [])
            pct = len(hits) / total * 100 if total > 0 else 0
            if hits:
                print(f"  {stage_name} +1 char → {target_name}: {len(hits)}/{total} ({pct:.2f}%)")
                for pos, char, src in hits[:3]:
                    print(f"    insert '{char}' at pos {pos} | {src}")


# ---------------------------------------------------------------------------
# Analysis 2: S3→S4 specific transition mapping
# ---------------------------------------------------------------------------

def analyze_s3_to_s4():
    """Detailed analysis of the critical S3→S4 transition."""
    print("\n" + "=" * 70)
    print("Analysis 2: S3→S4 Critical Transition")
    print("=" * 70)

    s3_core = "QDaK5"
    s4_core = "QDaK5XAS"

    # What characters need to be added to S3 to get S4?
    # S4 = S3 + "XAS" (if, filter, products)
    # But fold context matters: X turns left, A is filter, S is data/products
    print(f"\n  S3→S4 requires appending 'XAS' (X=if/turn-left, A=filter, S=data/products)")
    print(f"  But the fold must place A(filter) adjacent to both fn-expression and S(data/products)")

    # Try all 3-char extensions of S3
    print(f"\n--- All 3-char extensions of S3 (\"{s3_core}\") ---")
    extensions_found = defaultdict(list)
    total = len(ALPHABET) ** 3

    for c1 in ALPHABET:
        for c2 in ALPHABET:
            for c3 in ALPHABET:
                ext = s3_core + c1 + c2 + c3
                p = develop(ext)
                labels = classify(p)
                if "L4_filter_fn_cmp_get_price" in labels:
                    extensions_found["S4_full"].append((c1 + c2 + c3, p.source, p.bond_count))
                elif "L4_higher_fn" in labels:
                    extensions_found["S4_any_filter_fn"].append((c1 + c2 + c3, p.source, p.bond_count))
                elif "L4_higher" in labels:
                    extensions_found["S4_any_higher"].append((c1 + c2 + c3, p.source, p.bond_count))

    print(f"  Total 3-char extensions: {total:,}")
    for label in ["S4_full", "S4_any_filter_fn", "S4_any_higher"]:
        hits = extensions_found[label]
        pct = len(hits) / total * 100
        print(f"  {label}: {len(hits)} ({pct:.3f}%)")
        for ext, src, bonds in hits[:5]:
            print(f"    +\"{ext}\" → {bonds} bonds: {src}")

    # Also try all 2-char extensions
    print(f"\n--- All 2-char extensions of S3 ---")
    ext2_found = defaultdict(list)
    total2 = len(ALPHABET) ** 2

    for c1 in ALPHABET:
        for c2 in ALPHABET:
            ext = s3_core + c1 + c2
            p = develop(ext)
            labels = classify(p)
            if "L4_filter_fn_cmp_get_price" in labels:
                ext2_found["S4_full"].append((c1 + c2, p.source, p.bond_count))
            elif "L4_higher_fn" in labels:
                ext2_found["S4_any_filter_fn"].append((c1 + c2, p.source, p.bond_count))

    for label in ["S4_full", "S4_any_filter_fn"]:
        hits = ext2_found[label]
        pct = len(hits) / total2 * 100
        print(f"  {label}: {len(hits)}/{total2} ({pct:.3f}%)")
        for ext, src, bonds in hits[:5]:
            print(f"    +\"{ext}\" → {bonds} bonds: {src}")

    # S4→count(S4): try prepending 'B' (count) and other wrappers
    print(f"\n--- S4→count(S4): single-char prepend to \"{s4_core}\" ---")
    count_s4 = 0
    any_wrapper_s4 = 0
    for char in ALPHABET:
        g = char + s4_core
        p = develop(g)
        labels = classify(p)
        if "FULL_TARGET" in labels:
            count_s4 += 1
            print(f"  '{char}' + S4 → FULL TARGET: {p.source}")
        elif "L5_count_filter" in labels:
            any_wrapper_s4 += 1

    print(f"  Full target (count+filter+fn+cmp+get_price): {count_s4}/{len(ALPHABET)}")
    print(f"  Any wrapper+filter: {any_wrapper_s4}/{len(ALPHABET)}")


# ---------------------------------------------------------------------------
# Analysis 3: Padded genotype transitions
# ---------------------------------------------------------------------------

def analyze_padded_transitions(n_genotypes=50, genotype_length=100):
    """Analyze transitions on realistic padded genotypes."""
    print("\n" + "=" * 70)
    print("Analysis 3: Padded Genotype Transitions (length 100)")
    print("=" * 70)

    # Find padded genotypes that express S3 and S4
    rng = random.Random(42)
    s3_genotypes = []
    s4_genotypes = []

    t0 = time.time()
    attempts = 0
    while len(s3_genotypes) < n_genotypes or len(s4_genotypes) < n_genotypes:
        attempts += 1
        if attempts > 100000:
            break

        # Try S3
        if len(s3_genotypes) < n_genotypes:
            core = "QDaK5"
            pad = genotype_length - len(core)
            pre_len = rng.randint(0, pad)
            pre = random_genotype(pre_len, rng) if pre_len > 0 else ""
            post = random_genotype(pad - pre_len, rng) if pad - pre_len > 0 else ""
            g = pre + core + post
            p = develop(g)
            labels = classify(p)
            if "L3_fn_cmp_get_price" in labels and "L4_filter_fn_cmp_get_price" not in labels:
                s3_genotypes.append((g, pre_len, p.source))

        # Try S4
        if len(s4_genotypes) < n_genotypes:
            core = "QDaK5XAS"
            pad = genotype_length - len(core)
            pre_len = rng.randint(0, pad)
            pre = random_genotype(pre_len, rng) if pre_len > 0 else ""
            post = random_genotype(pad - pre_len, rng) if pad - pre_len > 0 else ""
            g = pre + core + post
            p = develop(g)
            labels = classify(p)
            if "L4_filter_fn_cmp_get_price" in labels:
                s4_genotypes.append((g, pre_len, p.source))

    print(f"  Found {len(s3_genotypes)} S3 genotypes, {len(s4_genotypes)} S4 genotypes ({attempts} attempts, {time.time()-t0:.1f}s)")

    # Mutation analysis on S3 padded genotypes
    print(f"\n--- S3 padded: single-char mutations ({len(s3_genotypes)} genotypes × {genotype_length} positions × {len(ALPHABET)} chars) ---")

    s3_mutation_results = Counter()
    s3_transition_positions = defaultdict(list)  # position relative to core -> hits

    t0 = time.time()
    for gi, (geno, core_start, orig_src) in enumerate(s3_genotypes):
        core_end = core_start + 5  # len("QDaK5")
        for pos in range(genotype_length):
            for char in ALPHABET:
                if char == geno[pos]:
                    continue
                mutant = geno[:pos] + char + geno[pos + 1:]
                p = develop(mutant)
                labels = classify(p)

                if "L4_filter_fn_cmp_get_price" in labels:
                    s3_mutation_results["S4_full"] += 1
                    rel_pos = pos - core_start
                    s3_transition_positions[rel_pos].append((gi, pos, char, p.source))
                elif "L4_higher_fn" in labels:
                    s3_mutation_results["S4_any_filter_fn"] += 1
                elif "L3_fn_cmp_get_price" in labels:
                    s3_mutation_results["S3_maintained"] += 1

    total_mutations = len(s3_genotypes) * genotype_length * (len(ALPHABET) - 1)
    elapsed = time.time() - t0
    print(f"  Total mutations tested: {total_mutations:,} ({elapsed:.1f}s)")
    print(f"  S3 maintained:        {s3_mutation_results['S3_maintained']:>8,} ({s3_mutation_results['S3_maintained']/total_mutations*100:.4f}%)")
    print(f"  → S4 (full chain):    {s3_mutation_results['S4_full']:>8,} ({s3_mutation_results['S4_full']/total_mutations*100:.4f}%)")
    print(f"  → S4 (any filter+fn): {s3_mutation_results['S4_any_filter_fn']:>8,} ({s3_mutation_results['S4_any_filter_fn']/total_mutations*100:.4f}%)")

    if s3_transition_positions:
        print(f"\n  Successful S3→S4 transitions by position relative to core:")
        for rel_pos in sorted(s3_transition_positions.keys()):
            hits = s3_transition_positions[rel_pos]
            region = "CORE" if 0 <= rel_pos < 5 else "pre" if rel_pos < 0 else "post"
            print(f"    pos {rel_pos:+4d} ({region:4s}): {len(hits)} transitions")
            for gi, pos, char, src in hits[:2]:
                print(f"      geno[{pos}]→'{char}': {src}")

    # Mutation analysis on S4 padded genotypes: S4→count(S4)
    print(f"\n--- S4 padded: single-char mutations → count(filter(...)) ---")

    s4_mutation_results = Counter()

    t0 = time.time()
    for gi, (geno, core_start, orig_src) in enumerate(s4_genotypes[:n_genotypes]):
        for pos in range(genotype_length):
            for char in ALPHABET:
                if char == geno[pos]:
                    continue
                mutant = geno[:pos] + char + geno[pos + 1:]
                p = develop(mutant)
                labels = classify(p)

                if "FULL_TARGET" in labels:
                    s4_mutation_results["count_filter_full"] += 1
                elif "L5_count_filter" in labels:
                    s4_mutation_results["count_any_filter"] += 1
                elif "L4_filter_fn_cmp_get_price" in labels:
                    s4_mutation_results["S4_maintained"] += 1

    total_s4 = len(s4_genotypes[:n_genotypes]) * genotype_length * (len(ALPHABET) - 1)
    elapsed = time.time() - t0
    print(f"  Total mutations tested: {total_s4:,} ({elapsed:.1f}s)")
    print(f"  S4 maintained:           {s4_mutation_results['S4_maintained']:>8,} ({s4_mutation_results['S4_maintained']/total_s4*100:.4f}%)")
    print(f"  → count(filter full):    {s4_mutation_results['count_filter_full']:>8,} ({s4_mutation_results['count_filter_full']/total_s4*100:.4f}%)")
    print(f"  → count(any filter):     {s4_mutation_results['count_any_filter']:>8,} ({s4_mutation_results['count_any_filter']/total_s4*100:.4f}%)")


# ---------------------------------------------------------------------------
# Analysis 4: Crossover between S3 and S4 genotypes
# ---------------------------------------------------------------------------

def analyze_crossover(n_genotypes=20, genotype_length=100):
    """Test whether crossover can combine partial modules."""
    print("\n" + "=" * 70)
    print("Analysis 4: Crossover Combinations")
    print("=" * 70)

    rng = random.Random(42)

    # Find padded S3 and random genotypes
    s3_genos = []
    s4_genos = []
    random_genos = [random_genotype(genotype_length, random.Random(i)) for i in range(n_genotypes)]

    attempts = 0
    while len(s3_genos) < n_genotypes or len(s4_genos) < n_genotypes:
        attempts += 1
        if attempts > 50000:
            break
        for core, target_label, target_list in [
            ("QDaK5", "L3_fn_cmp_get_price", s3_genos),
            ("QDaK5XAS", "L4_filter_fn_cmp_get_price", s4_genos),
        ]:
            if len(target_list) >= n_genotypes:
                continue
            pad = genotype_length - len(core)
            pre_len = rng.randint(0, pad)
            pre = random_genotype(pre_len, rng) if pre_len > 0 else ""
            post = random_genotype(pad - pre_len, rng) if pad - pre_len > 0 else ""
            g = pre + core + post
            p = develop(g)
            labels = classify(p)
            if target_label in labels:
                target_list.append(g)

    print(f"  Found {len(s3_genos)} S3, {len(s4_genos)} S4, {len(random_genos)} random genotypes")

    # Test crossover at every position
    pairs = [
        ("S3 × random", s3_genos, random_genos),
        ("S4 × random", s4_genos, random_genos),
        ("S3 × S4", s3_genos, s4_genos),
    ]

    for pair_name, list_a, list_b in pairs:
        results = Counter()
        total = 0

        n_a = min(len(list_a), n_genotypes)
        n_b = min(len(list_b), n_genotypes)

        for i in range(n_a):
            for j in range(n_b):
                for cut_a in range(0, genotype_length, 5):  # sample every 5th position
                    for cut_b in range(0, genotype_length, 5):
                        offspring = list_a[i][:cut_a] + list_b[j][cut_b:]
                        if len(offspring) < 5:
                            continue
                        # Truncate or pad to target length
                        if len(offspring) > genotype_length:
                            offspring = offspring[:genotype_length]
                        elif len(offspring) < genotype_length:
                            offspring = offspring + random_genotype(genotype_length - len(offspring), rng)

                        p = develop(offspring)
                        labels = classify(p)
                        total += 1

                        if "FULL_TARGET" in labels:
                            results["full_target"] += 1
                        elif "L4_filter_fn_cmp_get_price" in labels:
                            results["S4_full"] += 1
                        elif "L4_higher_fn" in labels:
                            results["filter_fn"] += 1

        print(f"\n  {pair_name}: {total:,} crossovers tested")
        for label in ["full_target", "S4_full", "filter_fn"]:
            count = results.get(label, 0)
            pct = count / total * 100 if total > 0 else 0
            print(f"    {label}: {count} ({pct:.4f}%)")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary():
    print("\n" + "=" * 70)
    print("TRANSITION PROBABILITY SUMMARY")
    print("=" * 70)
    print("""
    The filter program assembly requires this chain:

    S1: (get x :price)                      — accessor + field_key bond
    S2: (> (get x :price) VALUE)            — comparator bonds to S1 + literal
    S3: (fn x (> (get x :price) VALUE))     — fn wrapper bonds to S2
    S4: (filter (fn ...) data/products)     — filter bonds to S3 + data source
    S5: (count (filter ...))                — count wrapper bonds to S4

    Each step requires specific characters to be spatially adjacent on the
    2D grid. The transition probabilities above quantify exactly how often
    each step succeeds under mutation and crossover.
    """)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    analyze_core_transitions()
    analyze_s3_to_s4()
    analyze_padded_transitions(n_genotypes=30)
    analyze_crossover(n_genotypes=10)
    print_summary()


if __name__ == "__main__":
    main()
