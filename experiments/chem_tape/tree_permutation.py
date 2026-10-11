"""0524 source-only, size/arity/width-conditioned label permutations.

Slot ordering is entry order then prefix node order; pool ordering is sorted.
Every pool is shuffled once, including singleton pools. Multiplicity survives.
"""

from collections import Counter, defaultdict
import hashlib
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.tree_gp_search import ARITY, TOKENS, Tree, interpret
from experiments.chem_tape.tree_gp_validate import python_output
from experiments.chem_tape.tree_library import canonical

TASK = "2026-10-11-0524"
PAIRS = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))


def seed(domain, *parts):
    raw = digest([TASK, domain, *parts]).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") & ((1 << 63) - 1)


def signature(entries):
    counts = Counter()
    skeletons = []
    for e in entries:
        t = Tree(tuple(e["prefix"]))
        if (len(t.prefix), len(t.program)) != (e["nodes"], e["compiled_length"]):
            raise ValueError("size metadata mismatch")
        skeletons.append([(ARITY[op], len(TOKENS[op])) for op in t.prefix])
        counts.update((e["nodes"], e["compiled_length"], op) for op in t.prefix)
    return dict(skeletons=skeletons, counts=sorted(counts.items()))


def permute(entries, construction_seed):
    tick = time.monotonic()
    pools = defaultdict(list)
    prefixes = [list(e["prefix"]) for e in entries]
    for ei, e in enumerate(entries):
        for ni, op in enumerate(e["prefix"]):
            pools[e["nodes"], e["compiled_length"], ARITY[op], len(TOKENS[op])].append(
                (ei, ni)
            )
    rng = np.random.default_rng(construction_seed)
    for key in sorted(pools):
        slots = pools[key]
        labels = [prefixes[ei][ni] for ei, ni in slots]
        rng.shuffle(labels)
        for (ei, ni), op in zip(slots, labels):
            prefixes[ei][ni] = op
    result = [
        dict(prefix=p, nodes=e["nodes"], compiled_length=e["compiled_length"])
        for e, p in zip(entries, prefixes)
    ]
    if signature(result) != signature(entries):
        raise ValueError("permutation invariants failed")
    return result, time.monotonic() - tick


def motifs(entries):
    pairs, predicates = [], []
    for e in entries:
        t = Tree(tuple(e["prefix"]))
        for i, op in enumerate(t.prefix):
            sub = t.prefix[i : t.ends[i]]
            if (
                len(sub) == 3
                and op == 9
                and sub[1] < 4
                and sub[2] < 4
                and sub[1] != sub[2]
            ):
                pairs.append(tuple(sorted(sub[1:])))
            if op == 10:
                left = i + 1
                right = t.ends[left]
                children = [t.prefix[j : t.ends[j]] for j in (left, right)]
                if all(
                    len(c) == 3 and c[0] == 9 and c[1] < 4 and c[2] < 4 and c[1] != c[2]
                    for c in children
                ):
                    predicates.append(tuple(tuple(sorted(c[1:])) for c in children))
    return dict(
        pair_counts={str(p): pairs.count(p) for split in PAIRS for p in split},
        split_pair_counts={
            str(split): sum(pairs.count(p) for p in split) for split in PAIRS
        },
        predicate_split_counts={
            str(split): sum(tuple(sorted(p)) == split for p in predicates)
            for split in PAIRS
        },
        exact_predicate_counts={str(split): predicates.count(split) for split in PAIRS},
        ordered_predicate_counts={
            str(order): predicates.count(order)
            for split in PAIRS
            for order in (split, split[::-1])
        },
    )


def build(libraries, inputs):
    result, audit = [], []
    for lib in libraries:
        constructions = []
        original_outputs = outputs(
            [Tree(tuple(e["prefix"])).program for e in lib["entries"]], inputs, ALPHABET
        )
        for realization in range(3):
            s = seed("construction", lib["build"], realization)
            entries, seconds = permute(lib["entries"], s)
            if entries != permute(lib["entries"], s)[0]:
                raise ValueError("construction replay failed")
            trees = [Tree(tuple(e["prefix"])) for e in entries]
            rust = outputs([t.program for t in trees], inputs, ALPHABET)
            for i, t in enumerate(trees):
                if not np.array_equal(
                    rust[i], [interpret(t, x) for x in inputs]
                ) or not np.array_equal(rust[i], [python_output(t, x) for x in inputs]):
                    raise ValueError("compiled/interpreter/Python/Rust disagreement")
            constructions.append(
                dict(
                    realization=realization,
                    seed=s,
                    entries=entries,
                    construction_seconds=seconds,
                )
            )
            audit.append(
                dict(
                    build=lib["build"],
                    realization=realization,
                    seed=s,
                    entries_hash=digest(entries),
                    entry_count=len(entries),
                    invariants_passed=True,
                    semantics_passed=True,
                    changed=sum(
                        canonical(a) != canonical(b)
                        for a, b in zip(
                            trees, [Tree(tuple(e["prefix"])) for e in lib["entries"]]
                        )
                    ),
                    changed_behaviours=int(
                        np.count_nonzero(np.any(rust != original_outputs, axis=1))
                    ),
                    unique_behaviours=len({row.tobytes() for row in rust}),
                    behaviour_hash=digest(rust.tolist()),
                    motifs=motifs(entries),
                    original_motifs=motifs(lib["entries"]),
                    surviving_original_predicate_types=[
                        key
                        for key, count in motifs(lib["entries"])[
                            "ordered_predicate_counts"
                        ].items()
                        if count and motifs(entries)["ordered_predicate_counts"][key]
                    ],
                )
            )
        result.append(lib | dict(constructions=constructions))
    return result, dict(
        passed=True,
        builds=len(result),
        constructions=len(audit),
        verified_entries=sum(r["entry_count"] for r in audit),
        per_construction=audit,
        dependencies="Ordered arity and width skeletons and library-level size-conditioned label counts remain fixed; permutations within pools couple entries. Unchanged entries, duplicates, accidental original motifs and all behaviours retained without filtering. Exact predicates preserve GT operand order; pair-split counts separately ignore orientation.",
    )
