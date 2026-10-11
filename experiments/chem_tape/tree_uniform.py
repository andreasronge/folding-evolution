"""0652 independent uniform compatible labels on frozen acquired skeletons."""

from collections import Counter
import hashlib
import json
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.tree_gp_search import ARITY, TOKENS, Tree, interpret
from experiments.chem_tape.tree_gp_validate import python_output
from experiments.chem_tape import tree_permutation as permutation

TASK = "2026-10-11-0652"
CLASSES = {
    (2, 1): (9, 10),
    (3, 1): (11,),
    (0, 2): (0, 1, 2, 3, 4),
    (0, 1): (5, 6, 7, 8),
}


def seed(domain, *parts):
    raw = json.dumps(
        [TASK, domain, *parts], sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") & ((1 << 63) - 1)


def relabel(entries, construction_seed):
    tick = time.monotonic()
    rng = np.random.default_rng(construction_seed)
    result = [
        dict(
            prefix=[
                int(rng.choice(CLASSES[ARITY[op], len(TOKENS[op])]))
                for op in e["prefix"]
            ],
            nodes=e["nodes"],
            compiled_length=e["compiled_length"],
        )
        for e in entries
    ]
    # signature also parses every tree and verifies node/compiled metadata.
    if (
        permutation.signature(result)["skeletons"]
        != permutation.signature(entries)["skeletons"]
    ):
        raise ValueError(
            "uniform skeleton/width/size/order/multiplicity invariants failed"
        )
    return result, time.monotonic() - tick


def build(libraries, inputs):
    result, audit = [], []
    for lib in libraries:
        constructions = []
        original = outputs(
            [Tree(tuple(e["prefix"])).program for e in lib["entries"]], inputs, ALPHABET
        )
        for realization in range(3):
            s = seed("construction", lib["build"], realization)
            entries, seconds = relabel(lib["entries"], s)
            if entries != relabel(lib["entries"], s)[0]:
                raise ValueError("uniform construction replay failed")
            trees = [Tree(tuple(e["prefix"])) for e in entries]
            rust = outputs([t.program for t in trees], inputs, ALPHABET)
            for i, t in enumerate(trees):
                if not np.array_equal(
                    rust[i], [interpret(t, x) for x in inputs]
                ) or not np.array_equal(rust[i], [python_output(t, x) for x in inputs]):
                    raise ValueError(
                        "uniform interpreter/compiler/Python/Rust disagreement"
                    )
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
                    label_counts=dict(
                        sorted(
                            Counter(
                                str(op) for e in entries for op in e["prefix"]
                            ).items()
                        )
                    ),
                    original_label_counts=dict(
                        sorted(
                            Counter(
                                str(op) for e in lib["entries"] for op in e["prefix"]
                            ).items()
                        )
                    ),
                    changed=sum(
                        a["prefix"] != b["prefix"]
                        for a, b in zip(entries, lib["entries"])
                    ),
                    changed_behaviours=int(
                        np.count_nonzero(np.any(rust != original, axis=1))
                    ),
                    unique_behaviours=len({row.tobytes() for row in rust}),
                    behaviour_hash=digest(rust.tolist()),
                    motifs=permutation.motifs(entries),
                    original_motifs=permutation.motifs(lib["entries"]),
                )
            )
        result.append(lib | dict(uniform_constructions=constructions))
    return result, dict(
        passed=True,
        builds=len(result),
        constructions=len(audit),
        verified_entries=sum(r["entry_count"] for r in audit),
        per_construction=audit,
        dependencies="Independent uniform labels within whole-grammar arity/width classes. Acquired ordered skeletons, widths, sizes, entry order and multiplicity fixed; counts and finite-library dependencies change. No filtering, deduplication or target-dependent selection.",
    )
