"""1129 semantic pooling and reporting-only helper census; no helper-aware fitting."""

from collections import Counter
import hashlib
import time

import numpy as np

from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.order_bank import helper
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_library import canonical, extract, verify_entries

RECIPE = dict(proper=True, contains_input=True, pooling_sizes="all including one node",
              key="exact D625 int64 output vector", per_solver="one count per semantic class",
              representative="minimum (nodes, canonical, literal) observed prefix",
              recurrence_cells=2, ranking="-cells,-solvers,nodes,canonical,literal",
              emission_nodes=[3, 9], filter_before_cap=True, cap=16)


def helpers(inputs):
    import itertools
    return {f"{kind}{a}{b}": outputs([helper(kind, a, b).program], inputs, ALPHABET)[0].astype('<i8').tobytes()
            for kind in ("lo", "hi") for a, b in itertools.combinations(range(4), 2)}


def build(rows, source_cells, inputs):
    start = time.monotonic()
    literal_entries, literal_seconds = extract(rows, source_cells)
    forms, row_forms = set(), []
    for row in rows:
        if row["cell"] not in source_cells or row["arm"] != "R-tree":
            raise ValueError("semantic extractor accepts source R-tree jobs only")
        own = set()
        if row["solved"]:
            tree = Tree(tuple(row["attempts"][-1]["solver_tree"]))
            for point in range(1, len(tree.prefix)):
                prefix = tree.prefix[point:tree.ends[point]]
                if any(op < 4 for op in prefix):
                    own.add(prefix)
        row_forms.append(own)
        forms.update(own)
    trees = [Tree(p) for p in sorted(forms)]
    cache = {}
    if trees:
        vectors = outputs([t.program for t in trees], inputs, ALPHABET)
        for tree, vector in zip(trees, vectors):
            if not np.array_equal([interpret(tree, x) for x in inputs], vector):
                raise ValueError("semantic pooling interpreter/VM disagreement")
            cache[tree.prefix] = vector.astype('<i8').tobytes()
    cells, solvers, reps = {}, Counter(), {}
    literal_cells, literal_solvers, literal_forms = {}, Counter(), {}
    helper_vectors = helpers(inputs)
    census = []
    for row, own in zip(rows, row_forms):
        seen = {}
        literal_seen = {}
        found = {h: sorted({len(p) for p in own if cache[p] == vector})
                 for h, vector in helper_vectors.items()}
        census.append(dict(cell=row['cell'], build=row['build'], repeat=row['repeat'],
                           solved=row['solved'], helpers=found))
        for prefix in own:
            tree = Tree(prefix)
            key = cache[prefix]
            seen.setdefault(key, []).append(prefix)
            if 3 <= len(prefix) <= 9:
                literal_seen.setdefault(canonical(tree), set()).add(prefix)
        for key, prefixes in seen.items():
            cells.setdefault(key, set()).add(row['cell'])
            solvers[key] += 1
            candidate = min(prefixes, key=lambda p: (len(p), canonical(Tree(p)), p))
            if key not in reps or (len(candidate), canonical(Tree(candidate)), candidate) < (len(reps[key]), canonical(Tree(reps[key])), reps[key]):
                reps[key] = candidate
        for key, prefixes in literal_seen.items():
            literal_cells.setdefault(key, set()).add(row['cell'])
            literal_solvers[key] += 1
            literal_forms.setdefault(key, Counter()).update(prefixes)
    pooled_ranked = sorted((key for key in cells if len(cells[key]) >= 2),
                           key=lambda key: (-len(cells[key]), -solvers[key], len(reps[key]), canonical(Tree(reps[key])), reps[key]))
    ranked = [key for key in pooled_ranked if 3 <= len(reps[key]) <= 9]
    entries = []
    for key in ranked[:16]:
        tree = Tree(reps[key])
        entries.append(dict(prefix=list(tree.prefix), canonical=list(canonical(tree)),
                            source_cells=sorted(cells[key]), solver_count=solvers[key],
                            nodes=len(tree.prefix), compiled_length=len(tree.program),
                            semantic_hash=hashlib.sha256(key).hexdigest()))
    literal_ranked = sorted((key for key in literal_cells if len(literal_cells[key]) >= 2),
                            key=lambda key: (-len(literal_cells[key]), -literal_solvers[key], len(key), key))
    literal_reps = {k: min(counts, key=lambda p: (-counts[p], p)) for k, counts in literal_forms.items()}
    diagnostics = {}
    for name, vector in helper_vectors.items():
        prefix = reps.get(vector)
        matching = [k for k in literal_cells if cache[literal_reps[k]] == vector]
        diagnostics[name] = dict(
            semantic=dict(source_cells=sorted(cells.get(vector, set())), solver_count=solvers[vector],
                          smallest_prefix=None if prefix is None else list(prefix),
                          nodes=None if prefix is None else len(prefix),
                          admissible=prefix is not None and 3 <= len(prefix) <= 9,
                          recurrent=len(cells.get(vector, set())) >= 2,
                          pooling_rank=pooled_ranked.index(vector) + 1 if vector in pooled_ranked else None,
                          uncapped_rank=ranked.index(vector) + 1 if vector in ranked else None,
                          included=vector in ranked[:16]),
            literal=[dict(canonical=list(k), source_cells=sorted(literal_cells[k]), solver_count=literal_solvers[k],
                          representative=list(literal_reps[k]), nodes=len(k), admissible=True,
                          uncapped_rank=literal_ranked.index(k) + 1 if k in literal_ranked else None,
                          included=k in literal_ranked[:16]) for k in sorted(matching)],
        )
    verify_entries(literal_entries, inputs)
    verify_entries(entries, inputs)
    return dict(literal=literal_entries, semantic=entries, helper_diagnostics=diagnostics,
                census=census, eligible_semantic_classes=len(ranked),
                eligible_literal_classes=len(literal_ranked),
                literal_seconds=literal_seconds, extraction_census_seconds=time.monotonic() - start,
                acquisition_evaluations=sum(r['evaluations'] for r in rows),
                acquisition_worker_seconds=sum(r['worker_seconds'] for r in rows),
                source_jobs=len(rows), source_solves=sum(r['solved'] for r in rows))
