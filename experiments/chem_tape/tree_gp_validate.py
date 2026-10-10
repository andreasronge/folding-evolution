"""Bounded 2214 semantic/initialization smoke; never calibrates or scores targets.

Usage: RUN_DIR=... RAYON_NUM_THREADS=1 .venv/bin/python -m
experiments.chem_tape.tree_gp_validate. Expected failed initialization is reported
as admitted=false, not converted into a different initialization procedure.
"""

import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.tree_gp_search import (
    GRAMMAR, Tree, from_postfix, initialize, interpret, random_tree,
)
from folding_evolution.chem_tape import executor as vm

SEED = 22160000


def full_acceptance_probability(depth, limit=32):
    """Exact generating-function calculation for independent uniform draws.

    Terminal polynomial: 4/9 one-token constants, 5/9 two-token readouts.
    Each function contributes one token; ADD/GT have two children (2/3),
    IF_GT three (1/3). Truncation is exact for the low-degree coefficients.
    """
    p = np.zeros(limit + 1)
    p[1:3] = [4 / 9, 5 / 9]
    for _ in range(depth):
        two = np.convolve(p, p)[:limit + 1]
        three = np.convolve(two, p)[:limit + 1]
        p = np.concatenate(([0.0], (2 * two / 3 + three / 3)[:limit]))
    return float(p.sum())


def python_output(tree, inp):
    stack = []
    for token in tree.program:
        vm.resolve_op(token, TA, ALPHABET)(stack, inp, "intlist", TA)
    if len(stack) != 1 or stack[0][0] != "int":
        raise ValueError("compiled tree failed Python closure")
    return stack[0][1]


def validate():
    start = time.monotonic()
    saved, targets = load_saved()  # existing full provenance audit; no refit
    fixtures = []
    for family in ("DG", "TS"):
        bank = saved["banks.json"][family]
        by = {c["id"]: c for c in bank["screen"]["cells"]}
        for cid in targets[family]:
            c = by[cid]
            t = from_postfix(c["canonical"])
            if list(t.program) != c["canonical"] or len(t.program) > 32:
                raise ValueError("fixture compilation changed")
            independent = [interpret(t, x) for x in bank["inputs"]]
            py = [python_output(t, x) for x in bank["inputs"]]
            rust = outputs([t.program], bank["inputs"], ALPHABET)[0].tolist()
            if independent != rust or independent != py or independent != c["labels"]:
                raise ValueError("target fixture semantics changed")
            fixtures.append(dict(family=family, cell=cid, nodes=len(t.prefix), tokens=len(t.program)))
    checks = 0
    inputs = [[], [9], [9, -7], [9, -7, 4, -3]]
    extreme = [[2**63 - 1, 1, -2**63, -1]]
    rng = np.random.default_rng(SEED)
    for _ in range(1000):
        t = random_tree(rng, 3)
        donor = random_tree(rng, 3)
        # Rejection assumes parent is valid, as every search population is.
        if len(t.program) > 32:
            continue
        child, _ = t.insert(int(rng.integers(len(t.prefix))), donor,
                            int(rng.integers(len(donor.prefix))))
        for candidate in (t, child):
            if len(candidate.program) > 32:
                raise ValueError("operator escaped size limit")
            expected = [interpret(candidate, x) for x in inputs]
            if expected != outputs([candidate.program], inputs, ALPHABET)[0].tolist():
                raise ValueError("random Rust semantics")
            if expected != [python_output(candidate, x) for x in inputs]:
                raise ValueError("random Python semantics")
            if [interpret(candidate, x) for x in extreme] != outputs([candidate.program], extreme, ALPHABET)[0].tolist():
                raise ValueError("signed overflow semantics")
            checks += 1
    # A deterministic overflow fixture ensures wrapping is actually exercised.
    wrapping = Tree((9, 0, 1))
    if interpret(wrapping, extreme[0]) != -2**63 or outputs([wrapping.program], extreme, ALPHABET)[0, 0] != -2**63:
        raise ValueError("overflow fixture failed")
    tick = time.monotonic()
    try:
        _, stats = initialize(np.random.default_rng([SEED, 1]), 256)
        initialization = dict(passed=True, stats=stats)
    except ValueError as exc:
        initialization = dict(passed=False, seed=SEED, population=256,
                              error=str(exc), seconds=time.monotonic() - tick)
    bins = []
    for depth in (2, 3, 4):
        gen = np.random.default_rng([SEED, depth, 9])
        tick = time.monotonic()
        lengths = [len(random_tree(gen, depth, full=True).program) for _ in range(10000)]
        seconds = time.monotonic() - tick
        p = full_acceptance_probability(depth)
        bins.append(dict(depth_edges=depth, draws=len(lengths),
                         accepted=sum(x <= 32 for x in lengths), rejected=sum(x > 32 for x in lengths),
                         min_tokens=min(lengths), median_tokens=float(np.median(lengths)), max_tokens=max(lengths),
                         seconds=seconds, exact_acceptance_probability=p,
                         expected_draws_per_accepted=1 / p,
                         projected_seconds_per_accepted=seconds / len(lengths) / p,
                         chance_accepted_within_10000=float(-np.expm1(10000 * np.log1p(-p))) if p < 1 else 1.0))
    return dict(task="2026-10-10-2214", seed=SEED, grammar=GRAMMAR,
                git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                fixtures=fixtures, interpreter_python_rust_checks=checks,
                overflow_fixture=True, initialization=initialization,
                full_bins=bins, seconds=time.monotonic() - start,
                admitted=initialization["passed"], targets_scored=False,
                deferred=["calibration", "native replay", "search replay", "scoring", "inference and economics"])


def main():
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    result = validate()
    write_json(out, "validation.json", result)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
