"""Read-only census of saved sources and input-rebinding support; no search.

Run from repository root with uv run python <this file>. Output is planning
evidence, not a new efficacy experiment or a production-VM validation.
"""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/output/2026-10-11/2026-10-11-1938-prepare"
libraries = json.loads((SOURCE / "libraries.json").read_text())
inputs = np.asarray(json.loads((SOURCE / "bank.json").read_text())["inputs"], dtype=np.int64)
rows = [json.loads(line) for line in (SOURCE / "acquisition.jsonl").read_text().splitlines()]
permutations = tuple(itertools.permutations(range(4)))
cache = {}


def parse(prefix, i=0):
    start = i
    op = prefix[i]
    i += 1
    if op < 4:
        out = inputs[:, op]
    elif op == 4:
        out = np.any(inputs, axis=1).astype(np.int64)
    elif op < 9:
        out = np.full(len(inputs), (0, 1, 2, 5)[op - 5], dtype=np.int64)
    else:
        args = []
        for _ in range(3 if op == 11 else 2):
            arg, i = parse(prefix, i)
            args.append(arg)
        if op == 9:
            out = args[0] + args[1]
        elif op == 10:
            out = (args[0] > args[1]).astype(np.int64)
        else:
            out = np.where(args[2] > 0, args[1], args[0])
    cache[tuple(prefix[start:i])] = out.astype("<i8").tobytes()
    return out, i


helper_keys = {}
for kind in ("p", "n"):
    for a, b in itertools.permutations(range(4), 2):
        active = inputs[:, a] > 0
        values = np.where(active if kind == "p" else ~active, inputs[:, b], 0)
        helper_keys[hashlib.sha256(values.astype("<i8").tobytes()).hexdigest()] = f"{kind}{a}{b}"

classification = Counter()
inadmissible_sizes = Counter()
stats = []
for build, library in enumerate(libraries):
    classes = {}
    for row in rows:
        if row["build"] != build or not row["solved"]:
            continue
        prefix = row["attempts"][-1]["solver_tree"]
        _, end = parse(prefix)
        assert end == len(prefix)

        def collect(i, root=False):
            start = i
            op = prefix[i]
            i += 1
            for _ in range(0 if op < 9 else (3 if op == 11 else 2)):
                i = collect(i)
            form = tuple(prefix[start:i])
            if not root and any(o < 4 for o in form):
                key = hashlib.sha256(cache[form]).hexdigest()
                record = classes.setdefault(key, {"cells": set(), "nodes": 999})
                record["cells"].add(row["cell"])
                record["nodes"] = min(record["nodes"], len(form))
            return i

        collect(0, True)
    one = {k for k, v in classes.items() if 3 <= v["nodes"] <= 9}
    two = {k for k in one if len(classes[k]["cells"]) >= 2}
    assert two == {e["semantic_hash"] for e in library["semantic"]}
    for diagnostic in library["helper_diagnostics"].values():
        d = diagnostic["semantic"]
        category = ("absent" if d["nodes"] is None else "kept" if d["included"]
                    else "admissible_single_cell" if d["admissible"] else "inadmissible")
        classification[category] += 1
        if category == "inadmissible":
            inadmissible_sizes[d["nodes"]] += 1
            classification["inadmissible_recurrent" if d["recurrent"] else "inadmissible_single_cell"] += 1

    rebound_keys = set()
    rebound_helper_draws = 0
    for entry in library["semantic"]:
        prefix = tuple(entry["prefix"])
        parse(prefix)
        assert hashlib.sha256(cache[prefix]).hexdigest() == entry["semantic_hash"]
        for permutation in permutations:
            transformed = tuple(permutation[o] if o < 4 else o for o in prefix)
            parse(transformed)
            key = hashlib.sha256(cache[transformed]).hexdigest()
            rebound_keys.add(key)
            rebound_helper_draws += key in helper_keys
    old_helpers = len(two & helper_keys.keys())
    new_helpers = len(one & helper_keys.keys())
    assert rebound_helper_draws == 24 * old_helpers
    stats.append(dict(
        build=build, old_entries=len(two), singleton_entries=len(one),
        old_helpers=old_helpers, singleton_helpers=new_helpers,
        old_helper_draw_fraction=old_helpers / len(two),
        singleton_helper_draw_fraction=new_helpers / len(one),
        rebound_slots=24 * len(two), rebound_distinct_behaviours=len(rebound_keys),
        rebound_helper_support=len(rebound_keys & helper_keys.keys()),
        rebound_helper_draw_fraction=rebound_helper_draws / (24 * len(two)),
        missing_rebound_helpers=sorted(set(helper_keys.values()) -
                                       {helper_keys[k] for k in rebound_keys & helper_keys.keys()}),
    ))

report = dict(
    scope="Saved-source planning audit only; no new searches, efficacy, or production-VM validation.",
    code_reference="research/main tree_gp_search.py interpret; order_library.py build",
    source_sha256={name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
                   for name in ("libraries.json", "bank.json", "acquisition.jsonl")},
    matched_old_semantic_sets=len(stats), helper_classification=dict(classification),
    inadmissible_minimum_nodes=dict(sorted(inadmissible_sizes.items())), per_build=stats,
    means={key: float(np.mean([s[key] for s in stats])) for key in stats[0]
           if key not in ("build", "missing_rebound_helpers")},
    law="Uniform original entry x uniform all 24 input permutations; retain all duplicate slots.",
)
destination = Path(__file__).with_suffix(".json")
destination.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "per_build"}, indent=2))
