"""1129 performance-blind order-helper bank; canonical trees are validation only."""

import gzip
import hashlib
import itertools
import json
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from experiments.chem_tape.independent_input_bank import ALPHABET, XMachine, semantic_outputs
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_gp_validate import python_output

BANK = "x4-order-v1"
SEEN = ("O:lo01+hi23", "O:lo01+hi12", "O:lo02+hi13")


def helper(kind, a, b):
    if kind not in ("lo", "hi") or not 0 <= a < b < 4:
        raise ValueError("invalid helper")
    return Tree((11, a, b, 10, a, b) if kind == "lo" else (11, b, a, 10, a, b))


def roster():
    xs = np.asarray(inputs_for("D625"))
    pairs = list(itertools.combinations(range(4), 2))
    cells = []

    def emit(cid, shape, tree, labels, helpers, **extra):
        labels = labels.astype("<i8")
        cells.append(dict(id=cid, shape=shape, canonical_tree=list(tree.prefix),
                          canonical=list(tree.program), labels=labels.tolist(),
                          label_hash=hashlib.sha256(labels.tobytes()).hexdigest(),
                          helpers=helpers, **extra))

    for kind in ("lo", "hi"):
        for a, b in pairs:
            labels = np.minimum(xs[:, a], xs[:, b]) if kind == "lo" else np.maximum(xs[:, a], xs[:, b])
            for c in sorted(set(range(4)) - {a, b}):
                emit(f"S:{kind}{a}{b}+X{c}", "source", Tree((9,) + helper(kind, a, b).prefix + (c,)),
                     labels + xs[:, c], [f"{kind}{a}{b}"])
    for a, b in pairs:
        for c, d in pairs:
            if (a, b) == (c, d):
                continue
            emit(f"O:lo{a}{b}+hi{c}{d}", "destination",
                 Tree((9,) + helper("lo", a, b).prefix + helper("hi", c, d).prefix),
                 np.minimum(xs[:, a], xs[:, b]) + np.maximum(xs[:, c], xs[:, d]),
                 [f"lo{a}{b}", f"hi{c}{d}"], disjoint=len({a, b, c, d}) == 4)
    return sorted(cells, key=lambda c: (c["label_hash"], c["id"]))


def old_banks():
    """All saved independent-input banks, including all screened candidates."""
    found = []

    def visit(value, path):
        if not isinstance(value, dict):
            return
        if value.get("alphabet") == ALPHABET and "screen" in value:
            if value["inputs"] != inputs_for("D625"):
                raise ValueError("old independent-input bank has changed domain")
            found.append((path, value))
        else:
            for key, child in value.items():
                visit(child, path + ":" + key)

    data = Path(__file__).with_name("data")
    for path in sorted(data.rglob("*bank*.json*")):
        raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
        visit(json.loads(raw), str(path))
    if not found:
        raise ValueError("no historical independent-input banks found")
    return found


def overlap(cells):
    old = old_banks()
    labels = np.asarray([c["labels"] for _, bank in old for c in bank["screen"]["cells"]])
    refs = [(path, c["id"]) for path, bank in old for c in bank["screen"]["cells"]]
    result = []
    for cell in cells:
        counts = np.count_nonzero(labels == cell["labels"], axis=1)
        point = int(np.argmax(counts))
        result.append(dict(id=cell["id"], best_old_matches=int(counts[point]),
                           old_bank=refs[point][0], old_cell=refs[point][1],
                           old_excluded=5 * int(counts[point]) >= 4 * 625))
    return result, {path: hashlib.sha256(json.dumps(bank, sort_keys=True).encode()).hexdigest()
                    for path, bank in old}


def verify(cells):
    inputs = inputs_for("D625")
    for c in cells:
        tree = Tree(tuple(c["canonical_tree"]))
        expected_length = 13 if c["shape"] == "source" else 21
        if list(tree.program) != c["canonical"] or len(tree.program) != expected_length:
            raise ValueError("canonical compilation changed")
        if ([interpret(tree, x) for x in inputs] != c["labels"]
                or [python_output(tree, x) for x in inputs] != c["labels"]
                or outputs([tree.program], inputs, ALPHABET)[0].tolist() != c["labels"]):
            raise ValueError("order canonical interpreter/Python/VM disagreement")
        if "witness" in c:
            witness = outputs([c["witness"]], inputs, ALPHABET)
            if (not np.array_equal(witness, semantic_outputs([c["witness"]], inputs))
                    or int(np.count_nonzero(witness[0] == c["labels"])) != c["best_matches"]):
                raise ValueError("alias witness semantics changed")
    return dict(passed=True, cells=len(cells), protected_searches=0)


def split(cells):
    source = [c for c in cells if c["shape"] == "source"]
    destinations = [c for c in cells if c["shape"] == "destination"]
    by = {c["id"]: c for c in destinations}
    if len(source) != 24 or not set(SEEN) <= set(by):
        raise ValueError("approved source allocation or seen development cells excluded")
    development = list(SEEN) + [c["id"] for c in destinations if c["id"] not in SEEN and not c["disjoint"]][:3]
    protected = [c for c in destinations if c["id"] not in development]
    if (len(development) != 6 or len(protected) < 8
            or sum(c["disjoint"] for c in protected) < 2
            or not any(not c["disjoint"] for c in protected)):
        raise ValueError("insufficient protected coverage")
    return dict(source=[c["id"] for c in source], development=development,
                protected=[c["id"] for c in protected])


def build(deadline=None):
    started = time.monotonic()
    cells = roster()
    verification = verify(cells)
    audit, old_hashes = overlap(cells)
    screen = screen_domain("D625", 9, deadline, cells=cells, tokens=EXECUTABLE,
                           machine_type=XMachine, alphabet=ALPHABET)
    by = {x["id"]: x for x in audit}
    admitted = []
    for c in screen["cells"]:
        c.update(by[c["id"]])
        c["retained"] = c["best_matches"] < 625 and not c["duplicate_ids"] and not c["old_excluded"]
        c["exclusion_reason"] = ("old_agreement_at_least_80_percent" if c["old_excluded"]
                                 else "short_exact_alias" if c["best_matches"] == 625
                                 else "duplicate_label" if c["duplicate_ids"] else None)
        if c["retained"]:
            if any(5 * np.count_nonzero(np.asarray(c["labels"]) == p["labels"]) >= 4 * 625 for p in admitted):
                c["retained"], c["exclusion_reason"] = False, "pairwise_agreement_at_least_80_percent"
            else:
                admitted.append(c)
    verification = verify(screen["cells"])
    bank = dict(name=BANK, alphabet=ALPHABET, inputs=inputs_for("D625"), screen=screen,
                overlap=audit, old_bank_hashes=old_hashes, verification=verification,
                split=None, seconds=time.monotonic() - started,
                admission="no exact alias through nine executable tokens; all old and admitted pairwise agreements <80%",
                tie_break="label SHA256/id; three seen plus lowest three remaining overlapping development; all remaining protected")
    try:
        bank["split"] = split(admitted)
        bank["admitted"] = True
    except ValueError as error:
        bank["admitted"], bank["failure"] = False, str(error)
    return bank
