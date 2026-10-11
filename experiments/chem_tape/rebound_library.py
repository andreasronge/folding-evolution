"""Uniform input symmetry supplied to frozen donors, with duplicate slots retained."""

from collections import Counter
import itertools
import time

import numpy as np

from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.signed_gate_bank import helper
from experiments.chem_tape.tree_gp_search import Tree, interpret

PERMUTATIONS = tuple(itertools.permutations(range(4)))


def rename(prefix, permutation):
    if tuple(sorted(permutation)) != (0, 1, 2, 3):
        raise ValueError("rebinding requires a bijection on all four inputs")
    return tuple(permutation[op] if op < 4 else op for op in prefix)


def expand(entries):
    """No domain, target, helper labels, or semantic deduplication in construction."""
    return [
        dict(
            prefix=list(rename(entry["prefix"], permutation)),
            nodes=entry["nodes"],
            compiled_length=entry["compiled_length"],
            original_entry=i,
            permutation=list(permutation),
        )
        for i, entry in enumerate(entries)
        for permutation in PERMUTATIONS
    ]


def validate(libraries, rebound, inputs, deadline):
    """Every slot's semantics and accounting; cached calculations retain slot mass."""
    start = time.monotonic()
    x = np.asarray(inputs, dtype=np.int64)
    if x.shape != (625, 4) or len({tuple(row) for row in x}) != 625:
        raise ValueError("expected exact D625 input domain")
    positions = {tuple(row): i for i, row in enumerate(x)}
    column_maps = {
        p: np.asarray([positions[tuple(row[list(p)])] for row in x])
        for p in PERMUTATIONS
    }
    # Fixtures explicitly cover repeated occurrences, ANY and IF_GT's
    # production operand order, including non-Boolean/negative branches.
    fixtures = [(9, 0, 0), (11, 0, 1, 2), (11, 4, 0, 1), (11, 9, 0, 1, 2, 10, 0, 3)]
    pairs = [(prefix, p) for prefix in fixtures for p in PERMUTATIONS]
    for lib in libraries:
        pairs.extend(
            (tuple(e["prefix"]), p) for e in lib["semantic"] for p in PERMUTATIONS
        )
    forms = sorted(
        {prefix for prefix, _ in pairs} | {rename(prefix, p) for prefix, p in pairs}
    )
    cache = {}
    for offset in range(0, len(forms), 256):
        if time.monotonic() > deadline:
            raise TimeoutError("rebinding validation deadline exceeded")
        batch = [Tree(prefix) for prefix in forms[offset : offset + 256]]
        vectors = outputs([t.program for t in batch], inputs, "v2_x4")
        for tree, vector in zip(batch, vectors):
            if not np.array_equal(vector, [interpret(tree, row) for row in inputs]):
                raise ValueError("rebinding interpreter/production VM disagreement")
            cache[tree.prefix] = vector
    for prefix, p in pairs:
        if not np.array_equal(cache[rename(prefix, p)], cache[prefix][column_maps[p]]):
            raise ValueError("renaming/column permutation disagreement")
    helper_trees = {
        f"{kind}{a}{b}": helper(kind, a, b)
        for kind in ("p", "n")
        for a, b in itertools.permutations(range(4), 2)
    }
    helper_vectors = outputs(
        [t.program for t in helper_trees.values()], inputs, "v2_x4"
    )
    helper_keys = {
        v.astype("<i8").tobytes(): name for name, v in zip(helper_trees, helper_vectors)
    }
    diagnostics = []
    if len(libraries) != len(rebound):
        raise ValueError("rebound build count mismatch")
    for build, (lib, expanded) in enumerate(zip(libraries, rebound)):
        entries = lib["semantic"]
        if expanded != expand(entries) or len(expanded) != 24 * len(entries):
            raise ValueError("rebound construction/multiplicity mismatch")
        for slot in expanded:
            tree = Tree(tuple(slot["prefix"]))
            original = entries[slot["original_entry"]]
            if (len(tree.prefix), len(tree.program)) != (
                slot["nodes"],
                slot["compiled_length"],
            ):
                raise ValueError("rebound primitive size changed")
            if (
                slot["permutation"] == [0, 1, 2, 3]
                and slot["prefix"] != original["prefix"]
            ):
                raise ValueError("identity permutation changed original entry")
        counts = {}
        for arm, ee in (("R-all", entries), ("R-bind", expanded)):
            counts[arm] = Counter(
                helper_keys.get(cache[tuple(e["prefix"])].astype("<i8").tobytes())
                for e in ee
            )
        if sum(v for k, v in counts["R-bind"].items() if k is not None) != 24 * sum(
            v for k, v in counts["R-all"].items() if k is not None
        ):
            raise ValueError("rebinding changed total signed-helper draw mass")
        diagnostics.append(
            dict(
                build=build,
                arms={
                    arm: dict(
                        slots=len(ee),
                        helper_slots=sum(
                            v for k, v in counts[arm].items() if k is not None
                        ),
                        helper_counts={
                            k: v for k, v in counts[arm].items() if k is not None
                        },
                        distinct_behaviours=len(
                            {
                                cache[tuple(e["prefix"])].astype("<i8").tobytes()
                                for e in ee
                            }
                        ),
                    )
                    for arm, ee in (("R-all", entries), ("R-bind", expanded))
                },
            )
        )
    return dict(
        complete=True,
        mappings=24,
        slots=sum(map(len, rebound)),
        semantic_slot_checks=len(pairs),
        unique_forms=len(forms),
        domain="D625, including negative inputs and zero",
        identity_replay="syntax identity; production search replay recorded separately",
        seconds=time.monotonic() - start,
        per_build=diagnostics,
    )
