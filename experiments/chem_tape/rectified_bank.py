"""1315 performance-blind rectified-sum bank; canonical trees are validation only."""

import hashlib
import itertools
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from experiments.chem_tape.order_bank import overlap
from experiments.chem_tape.independent_input_bank import ALPHABET, XMachine, semantic_outputs
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_gp_validate import python_output

BANK = "x4-rectified-sum-v1"
SEEN = ("O:pos01+neg02", "O:pos13+neg23", "O:pos01+neg23", "O:pos12+neg03")


def helper(kind, a, b):
    if kind not in ("pos", "neg") or not 0 <= a < b < 4:
        raise ValueError("invalid rectifier helper")
    summed = (9, a, b)
    # IF_GT children are [else, then, condition].
    return Tree((11, 5) + summed + summed if kind == "pos"
                else (11,) + summed + (5,) + summed)


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

    for kind in ("pos", "neg"):
        for a, b in pairs:
            labels = np.maximum(xs[:, a] + xs[:, b], 0) if kind == "pos" else np.minimum(xs[:, a] + xs[:, b], 0)
            for c in sorted(set(range(4)) - {a, b}):
                emit(f"S:{kind}{a}{b}+X{c}", "source", Tree((9,) + helper(kind, a, b).prefix + (c,)),
                     labels + xs[:, c], [f"{kind}{a}{b}"])
    for a, b in pairs:
        for c, d in pairs:
            if (a, b) == (c, d):
                continue
            emit(f"O:pos{a}{b}+neg{c}{d}", "destination",
                 Tree((9,) + helper("pos", a, b).prefix + helper("neg", c, d).prefix),
                 np.maximum(xs[:, a] + xs[:, b], 0) + np.minimum(xs[:, c] + xs[:, d], 0),
                 [f"pos{a}{b}", f"neg{c}{d}"], disjoint=len({a, b, c, d}) == 4)
    return sorted(cells, key=lambda c: (c["label_hash"], c["id"]))


def verify(cells):
    inputs = inputs_for("D625")
    for c in cells:
        tree = Tree(tuple(c["canonical_tree"]))
        expected_length = 15 if c["shape"] == "source" else 25
        if list(tree.program) != c["canonical"] or len(tree.program) != expected_length:
            raise ValueError("canonical compilation changed")
        if ([interpret(tree, x) for x in inputs] != c["labels"]
                or [python_output(tree, x) for x in inputs] != c["labels"]
                or outputs([tree.program], inputs, ALPHABET)[0].tolist() != c["labels"]):
            raise ValueError("rectifier canonical interpreter/Python/VM disagreement")
        if "witness" in c:
            witness = outputs([c["witness"]], inputs, ALPHABET)
            if (not np.array_equal(witness, semantic_outputs([c["witness"]], inputs))
                    or int(np.count_nonzero(witness[0] == c["labels"])) != c["best_matches"]):
                raise ValueError("alias witness semantics changed")
    if any(len(set(c["labels"])) < 2 for c in cells):
        raise ValueError("constant rectifier fixture")
    return dict(passed=True, cells=len(cells), protected_searches=0,
                engines=["numpy labels", "recursive interpreter", "Python executor", "production VM", "screen machine witnesses"])


def split(cells):
    source = [c for c in cells if c["shape"] == "source"]
    destinations = [c for c in cells if c["shape"] == "destination"]
    by = {c["id"]: c for c in destinations}
    if len(source) != 24 or not set(SEEN) <= set(by):
        raise ValueError("approved source allocation or seen development cells excluded")
    development = list(SEEN) + [c["id"] for c in destinations if c["id"] not in SEEN and not c["disjoint"]][:2]
    protected = [c for c in destinations if c["id"] not in development]
    if (len(development) != 6 or len(protected) < 8
            or sum(c["disjoint"] for c in protected) < 2
            or not any(not c["disjoint"] for c in protected)):
        raise ValueError("insufficient protected coverage")
    opportunities = {f"{kind}{a}{b}": sum(f"{kind}{a}{b}" in c["helpers"] for c in source)
                     for kind in ("pos", "neg") for a, b in itertools.combinations(range(4), 2)}
    if any(n != 2 for n in opportunities.values()):
        raise ValueError("canonical source opportunities changed")
    return dict(source=[c["id"] for c in source], development=development,
                protected=[c["id"] for c in protected])


def build(deadline=None):
    started = time.monotonic()
    executable_check()
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
                tie_break="label SHA256/id; four stage-0 seen plus lowest two remaining overlapping development; all remaining protected")
    try:
        bank["split"] = split(admitted)
        bank["admitted"] = True
    except ValueError as error:
        bank["admitted"], bank["failure"] = False, str(error)
    return bank


def executable_check():
    import importlib
    backend = importlib.import_module("_folding_rust._folding_rust")
    extension = Path(backend.__file__).resolve()
    root = Path(__file__).resolve().parents[2]
    if not extension.is_relative_to(root / ".venv"):
        raise ValueError("production extension is not from this worktree: " + str(extension))
    return dict(path=str(extension), sha256=hashlib.sha256(extension.read_bytes()).hexdigest())
