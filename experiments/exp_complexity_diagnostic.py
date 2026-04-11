"""
Diagnostic C1 + C2: Complexity ceiling investigation.

C1: Random genotype bond-count survey at lengths 50, 80, 100, 150, 200.
    Generate 100K random genotypes per length, measure bond-count distribution.

C2: Reverse-engineer 4+ bond genotypes.
    Starting from the known 4-bond genotype "QDaK5XASBw", explore variants
    and random search for genotypes producing 4+ bonds.
"""

import random
import time
from collections import Counter

from folding_evolution.alphabet import random_genotype, ALPHABET
from folding_evolution.phenotype import develop


def c1_bond_count_survey(lengths=(50, 80, 100, 150, 200), n_samples=100_000, seed=42):
    """Survey bond-count distribution for random genotypes at various lengths."""
    print("=" * 70)
    print("C1: Random Genotype Bond-Count Survey")
    print("=" * 70)
    print(f"Samples per length: {n_samples:,}")
    print()

    results = {}
    for length in lengths:
        rng = random.Random(seed)
        counts = Counter()
        max_bond = 0
        max_genotype = ""
        max_source = ""
        examples_4plus = []

        t0 = time.time()
        for i in range(n_samples):
            g = random_genotype(length, rng=rng)
            p = develop(g)
            bc = p.bond_count
            counts[bc] += 1
            if bc > max_bond:
                max_bond = bc
                max_genotype = g
                max_source = p.source
            if bc >= 4 and len(examples_4plus) < 10:
                examples_4plus.append((bc, g, p.source))
        elapsed = time.time() - t0

        results[length] = {
            "counts": counts,
            "max_bond": max_bond,
            "max_genotype": max_genotype,
            "max_source": max_source,
            "examples_4plus": examples_4plus,
            "elapsed": elapsed,
        }

        total = sum(counts.values())
        avg_bonds = sum(k * v for k, v in counts.items()) / total
        pct_0 = counts[0] / total * 100
        pct_1 = counts[1] / total * 100
        pct_2 = counts[2] / total * 100
        pct_3 = counts[3] / total * 100
        pct_4plus = sum(v for k, v in counts.items() if k >= 4) / total * 100

        print(f"Length {length}:")
        print(f"  Time: {elapsed:.1f}s ({n_samples/elapsed:.0f} evals/sec)")
        print(f"  Avg bonds: {avg_bonds:.2f}")
        print(f"  Max bonds: {max_bond}")
        print(f"  Distribution: 0={pct_0:.1f}%  1={pct_1:.1f}%  2={pct_2:.1f}%  3={pct_3:.1f}%  4+={pct_4plus:.1f}%")

        # Detailed distribution
        for bc in sorted(counts.keys()):
            bar = "#" * max(1, int(counts[bc] / total * 100))
            print(f"    {bc:2d} bonds: {counts[bc]:6d} ({counts[bc]/total*100:5.1f}%) {bar}")

        if examples_4plus:
            print(f"  First 4+ bond examples:")
            for bc, g, src in examples_4plus[:5]:
                print(f"    {bc} bonds: {src}")
                print(f"      genotype: {g}")
        print()

    return results


def c2_reverse_engineer(seed=42):
    """Try to construct and find 4+ bond genotypes."""
    print("=" * 70)
    print("C2: Reverse-Engineering 4+ Bond Genotypes")
    print("=" * 70)
    print()

    # --- Part 1: Verify the known 4-bond genotype ---
    print("Part 1: Known 4-bond genotype")
    known = "QDaK5XASBw"
    p = develop(known)
    print(f"  Genotype: {known}")
    print(f"  Bonds: {p.bond_count}")
    print(f"  Source: {p.source}")
    print()

    # --- Part 2: Systematic single-char mutations of the known genotype ---
    print("Part 2: Mutant survey of known 4-bond genotype")
    print("  Testing all single-character mutations...")
    bond_distribution = Counter()
    improved = []
    maintained = []

    for pos in range(len(known)):
        for char in ALPHABET:
            if char == known[pos]:
                continue
            mutant = known[:pos] + char + known[pos + 1:]
            mp = develop(mutant)
            bond_distribution[mp.bond_count] += 1
            if mp.bond_count > p.bond_count:
                improved.append((mp.bond_count, mutant, mp.source))
            elif mp.bond_count == p.bond_count:
                maintained.append((mutant, mp.source))

    total_mutants = sum(bond_distribution.values())
    print(f"  Total mutants tested: {total_mutants}")
    for bc in sorted(bond_distribution.keys()):
        pct = bond_distribution[bc] / total_mutants * 100
        print(f"    {bc} bonds: {bond_distribution[bc]:4d} ({pct:5.1f}%)")

    if improved:
        print(f"  IMPROVED beyond 4 bonds ({len(improved)} found):")
        for bc, g, src in improved[:10]:
            print(f"    {bc} bonds: {src}")
            print(f"      genotype: {g}")
    else:
        print(f"  No mutants exceeded 4 bonds.")

    print(f"  Maintained 4 bonds: {len(maintained)} ({len(maintained)/total_mutants*100:.1f}%)")
    print()

    # --- Part 3: Extension — append/prepend characters to known 4-bond genotype ---
    print("Part 3: Extending the known 4-bond genotype")
    best_extended = (4, known, p.source)
    rng = random.Random(seed)

    # Try appending 1-20 random characters
    for ext_len in [5, 10, 20, 40]:
        extended_counts = Counter()
        best_this_len = (0, "", "")
        for _ in range(10_000):
            suffix = "".join(rng.choice(ALPHABET) for _ in range(ext_len))
            g = known + suffix
            ep = develop(g)
            extended_counts[ep.bond_count] += 1
            if ep.bond_count > best_this_len[0]:
                best_this_len = (ep.bond_count, g, ep.source)
            if ep.bond_count > best_extended[0]:
                best_extended = (ep.bond_count, g, ep.source)

        total = sum(extended_counts.values())
        avg = sum(k * v for k, v in extended_counts.items()) / total
        pct_4plus = sum(v for k, v in extended_counts.items() if k >= 4) / total * 100
        print(f"  +{ext_len} chars: avg={avg:.2f} bonds, 4+={pct_4plus:.1f}%, max={best_this_len[0]}")
        if best_this_len[0] >= 5:
            print(f"    Best: {best_this_len[0]} bonds: {best_this_len[2]}")

    print(f"\n  Overall best extended: {best_extended[0]} bonds")
    print(f"    Source: {best_extended[2]}")
    print(f"    Genotype: {best_extended[1]}")
    print()

    # --- Part 4: Targeted construction ---
    # Try to build genotypes that should produce 5+ bond programs
    # Target: (filter (fn x (> (get x :price) 500)) (map (fn x (get x :name)) data/products))
    # This needs: filter + fn + comparator + get + field + literal + map + fn + get + field + data
    print("Part 4: Targeted construction attempts")
    print("  Trying hand-crafted genotypes for complex programs...")

    # These are educated guesses based on fold mechanics:
    # Need characters adjacent in the right order across passes
    candidates = [
        # Try to get filter+fn+predicate on one arm, data on another
        "QDaK5XASBwCDeST",
        "QDaK5ZASCebT",
        "BASQDaK5CeTb",
        # Try different fold topologies
        "AQDaK5STBCeR",
        "QKDa5ASBCeTw",
        # Longer with spacers to control topology
        "QDaK5ZZZASBwZZZCDeTb",
        "QDaK5XASBwQCeTS",
        # Really long to let complexity emerge
        "QDaK5XASBwZZZQCeTSZZZBIU",
    ]

    for g in candidates:
        cp = develop(g)
        if cp.bond_count >= 3:
            print(f"  {cp.bond_count} bonds | {g:30s} | {cp.source}")

    # --- Part 5: Random search specifically for high-bond genotypes ---
    print()
    print("Part 5: Random search for 5+ bond genotypes")
    rng = random.Random(seed)
    high_bond_examples = {}  # bond_count -> (genotype, source)

    for length in [20, 30, 50, 80, 100, 150]:
        t0 = time.time()
        local_max = 0
        for i in range(50_000):
            g = random_genotype(length, rng=rng)
            gp = develop(g)
            bc = gp.bond_count
            if bc >= 5 and bc not in high_bond_examples:
                high_bond_examples[bc] = (length, g, gp.source)
            if bc > local_max:
                local_max = bc
        elapsed = time.time() - t0
        print(f"  Length {length:3d}: max found = {local_max} bonds ({elapsed:.1f}s)")

    if high_bond_examples:
        print(f"\n  High-bond examples found:")
        for bc in sorted(high_bond_examples.keys()):
            length, g, src = high_bond_examples[bc]
            print(f"    {bc} bonds (length {length}): {src}")
            print(f"      genotype: {g}")
    else:
        print(f"\n  No 5+ bond genotypes found in random search.")


if __name__ == "__main__":
    results = c1_bond_count_survey()
    print()
    c2_reverse_engineer()
