"""2044 performance-blind linked signed-chain bank; no search in this module."""

import hashlib
import itertools
import json
import time

import numpy as np

from experiments.chem_tape import signed_gate_bank as gates
from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from experiments.chem_tape.independent_input_bank import (
    ALPHABET,
    XMachine,
    semantic_outputs,
)
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_gp_validate import python_output

BANK = "x4-signed-chain-v1"
SEEN = ("C:p30+n01+p12", "C:p30+n02+p21", "C:p13+n30+p02", "C:p01+n12+p23")


def roster():
    xs = np.asarray(inputs_for("D625"))
    cells = []
    for a, b, c, d in itertools.permutations(range(4)):
        helpers = [f"p{a}{b}", f"n{b}{c}", f"p{c}{d}"]
        tree = Tree(
            (9, 9)
            + gates.helper("p", a, b).prefix
            + gates.helper("n", b, c).prefix
            + gates.helper("p", c, d).prefix
        )
        labels = (
            np.where(xs[:, a] > 0, xs[:, b], 0)
            + np.where(xs[:, b] > 0, 0, xs[:, c])
            + np.where(xs[:, c] > 0, xs[:, d], 0)
        ).astype("<i8")
        cells.append(
            dict(
                id="C:" + "+".join(helpers),
                shape="destination",
                helpers=helpers,
                canonical_tree=list(tree.prefix),
                canonical=list(tree.program),
                labels=labels.tolist(),
                label_hash=hashlib.sha256(labels.tobytes()).hexdigest(),
            )
        )
    return sorted(cells, key=lambda c: (c["label_hash"], c["id"]))


def verify(cells):
    inputs = inputs_for("D625")
    expected = {c["id"]: c for c in roster()}
    for cell in cells:
        original = expected[cell["id"]]
        if any(cell[k] != v for k, v in original.items()):
            raise ValueError("chain labels/canonical/hash changed")
        tree = Tree(tuple(cell["canonical_tree"]))
        if len(tree.prefix) != 14 or len(tree.program) != 20:
            raise ValueError("chain canonical accounting changed")
        if (
            [interpret(tree, x) for x in inputs] != cell["labels"]
            or [python_output(tree, x) for x in inputs] != cell["labels"]
            or outputs([tree.program], inputs, ALPHABET)[0].tolist() != cell["labels"]
        ):
            raise ValueError("chain interpreter/Python/VM disagreement")
        if "witness" in cell:
            observed = outputs([cell["witness"]], inputs, ALPHABET)
            if (
                not np.array_equal(
                    observed, semantic_outputs([cell["witness"]], inputs)
                )
                or int(np.count_nonzero(observed[0] == cell["labels"]))
                != cell["best_matches"]
            ):
                raise ValueError("chain short witness disagreement")
    return dict(
        passed=True,
        cells=len(cells),
        nodes=14,
        compiled_tokens=20,
        protected_searches=0,
    )


def overlap(cells):
    from experiments.chem_tape.order_bank import old_banks
    from experiments.chem_tape.rectified_run import DATA as rectified
    from experiments.chem_tape.signed_gate_run import DATA as signed

    old = old_banks()
    for directory in (rectified, signed):
        path = directory / "manifest.json"
        old.append((str(path), json.loads(path.read_text())))
    labels = np.asarray([c["labels"] for _, b in old for c in b["screen"]["cells"]])
    refs = [(path, c["id"]) for path, b in old for c in b["screen"]["cells"]]
    audit = []
    for cell in cells:
        counts = np.count_nonzero(labels == cell["labels"], axis=1)
        i = int(np.argmax(counts))
        audit.append(
            dict(
                id=cell["id"],
                best_old_matches=int(counts[i]),
                old_bank=refs[i][0],
                old_cell=refs[i][1],
                old_excluded=5 * int(counts[i]) >= 4 * 625,
            )
        )
    hashes = {
        path: hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest()
        for path, b in old
    }
    return audit, hashes


def split(cells):
    cells = sorted(cells, key=lambda c: (c["label_hash"], c["id"]))
    if not set(SEEN) <= {c["id"] for c in cells}:
        raise ValueError("seen development cells excluded")
    development = list(SEEN) + [c["id"] for c in cells if c["id"] not in SEEN][:2]
    protected = [c["id"] for c in cells if c["id"] not in development]
    if len(development) != 6 or len(protected) < 8:
        raise ValueError("insufficient protected roster")
    return dict(development=development, protected=protected)


def build(deadline=None):
    start = time.monotonic()
    executor = gates.executor_check()
    cells = roster()
    verify(cells)
    audit, hashes = overlap(cells)
    screen = screen_domain(
        "D625",
        9,
        deadline,
        cells=cells,
        tokens=EXECUTABLE,
        machine_type=XMachine,
        alphabet=ALPHABET,
    )
    by = {c["id"]: c for c in audit}
    admitted = []
    for cell in screen["cells"]:
        cell.update(by[cell["id"]])
        reason = (
            "old_agreement_at_least_80_percent"
            if cell["old_excluded"]
            else "short_exact_alias"
            if cell["best_matches"] == 625
            else "duplicate_label"
            if cell["duplicate_ids"]
            else None
        )
        if reason is None and any(
            5 * np.count_nonzero(np.asarray(cell["labels"]) == c["labels"]) >= 4 * 625
            for c in admitted
        ):
            reason = "pairwise_agreement_at_least_80_percent"
        cell.update(retained=reason is None, exclusion_reason=reason)
        if reason is None:
            admitted.append(cell)
    pairwise = [
        dict(
            left=a["id"],
            right=b["id"],
            matches=int(np.count_nonzero(np.asarray(a["labels"]) == b["labels"])),
        )
        for a, b in itertools.combinations(cells, 2)
    ]
    bank = dict(
        name=BANK,
        alphabet=ALPHABET,
        inputs=inputs_for("D625"),
        screen=screen,
        overlap=audit,
        old_bank_hashes=hashes,
        pairwise=pairwise,
        verification=verify(screen["cells"]),
        executor_check=executor,
        seconds=time.monotonic() - start,
        split=None,
        admission="no exact alias through nine executable tokens; old/admitted pairwise agreement <80%; near-aliases descriptive",
        screen_scope="D625 only; exhaustive <=9 executable tokens, no claim about longer aliases",
        tie_break="label SHA256/id; four seen stage-0 cells plus lowest remaining two; no replacement",
    )
    try:
        bank["split"], bank["admitted"] = split(admitted), True
    except ValueError as error:
        bank["admitted"], bank["failure"] = False, str(error)
    return bank
