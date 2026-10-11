"""0150 source-only proper-subtree extraction and ordinary size-matched donors."""

from collections import Counter
from itertools import product
import time

import numpy as np

from experiments.chem_tape.tree_gp_search import ARITY, Tree, interpret, random_tree
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET

MAX_DRAWS = 1_000_000


def canonical(tree):
    def visit(i):
        children, point = [], i + 1
        for _ in range(ARITY[tree.prefix[i]]):
            children.append(visit(point))
            point = tree.ends[point]
        if tree.prefix[i] == 9:
            children.sort()
        return (tree.prefix[i],) + sum(children, ())

    return visit(0)


def donor_support(depth=3):
    """Exact support in (nodes, compiled length), restricted to extractor sizes."""
    support = {(1, 1), (1, 2)}
    for _ in range(depth):
        previous = support
        support = {(1, 1), (1, 2)}
        for arity in (2, 3):
            for children in product(previous, repeat=arity):
                nodes = 1 + sum(c[0] for c in children)
                length = 1 + sum(c[1] for c in children)
                if nodes <= 9:
                    support.add((nodes, length))
    return support


def extract(rows, source_cells):
    tick = time.monotonic()
    cells, solvers, literals = {}, Counter(), {}
    for row in rows:
        if row["cell"] not in source_cells or row["arm"] != "R-tree":
            raise ValueError("extractor accepts new source R-tree jobs only")
        if not row["solved"]:
            continue
        tree = Tree(tuple(row["attempts"][-1]["solver_tree"]))
        seen = {}
        for point in range(1, len(tree.prefix)):
            prefix = tree.prefix[point : tree.ends[point]]
            if 3 <= len(prefix) <= 9 and any(op < 4 for op in prefix):
                subtree = Tree(prefix)
                seen.setdefault(canonical(subtree), set()).add(prefix)
        for key, forms in seen.items():
            cells.setdefault(key, set()).add(row["cell"])
            solvers[key] += 1
            counts = literals.setdefault(key, Counter())
            for form in forms:
                counts[form] += 1
    ranked = sorted(
        (k for k in cells if len(cells[k]) >= 2),
        key=lambda k: (-len(cells[k]), -solvers[k], len(k), k),
    )[:16]
    entries = []
    for key in ranked:
        literal = min(literals[key], key=lambda p: (-literals[key][p], p))
        tree = Tree(literal)
        entries.append(
            dict(
                prefix=list(literal),
                canonical=list(key),
                source_cells=sorted(cells[key]),
                solver_count=solvers[key],
                literal_solver_count=literals[key][literal],
                nodes=len(literal),
                compiled_length=len(tree.program),
            )
        )
    return entries, time.monotonic() - tick


def controls(entries, seed, max_draws=MAX_DRAWS):
    tick = time.monotonic()
    rng, support, result = np.random.default_rng(seed), donor_support(), []
    for entry in entries:
        pair = entry["nodes"], entry["compiled_length"]
        if pair not in support:
            raise ValueError(f"ordinary depth-3 donor has no support for {pair}")
        for draws in range(1, max_draws + 1):
            donor = random_tree(rng, 3)
            if (len(donor.prefix), len(donor.program)) == pair:
                result.append(
                    dict(
                        prefix=list(donor.prefix),
                        nodes=pair[0],
                        compiled_length=pair[1],
                        draws=draws,
                    )
                )
                break
        else:
            raise ValueError(f"size control exhausted {max_draws} draws for {pair}")
    return result, time.monotonic() - tick


def verify_entries(entries, inputs):
    for entry in entries:
        tree = Tree(tuple(entry["prefix"]))
        if (len(tree.prefix), len(tree.program)) != (
            entry["nodes"],
            entry["compiled_length"],
        ):
            raise ValueError("library size metadata mismatch")
        if not np.array_equal(
            [interpret(tree, x) for x in inputs],
            outputs([tree.program], inputs, ALPHABET)[0],
        ):
            raise ValueError("library interpreter/VM disagreement")
    return len(entries)
