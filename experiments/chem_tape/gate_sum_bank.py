"""0348 performance-blind gate-sum bank and fixed development/protected split."""

import hashlib
import itertools
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from experiments.chem_tape.independent_input_bank import ALPHABET, XMachine
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_gp_validate import python_output
from experiments.chem_tape.composition_search import outputs

BANK = "x4-gate-sum-v1"
PROBED_ROLES = ((1, 3, 0, 2, 0, 1, 3), (0, 1, 2, 3, 0, 3, 0))


def pairing(cell):
    return tuple(map(tuple, cell["pairing"]))


def roster(old_banks):
    xs = np.asarray(inputs_for("D625"))
    old = {c["label_hash"] for b in old_banks for c in b["screen"]["cells"]}
    unique, excluded = {}, []
    for A, B in itertools.combinations(range(4), 2):
        C, D = sorted(set(range(4)) - {A, B})
        for E, F in itertools.combinations(range(4), 2):
            for G in range(4):
                roles = (A, B, C, D, E, F, G)
                tree = Tree((11, G, 9, E, F, 10, 9, A, B, 9, C, D))
                gate = xs[:, A] + xs[:, B] > xs[:, C] + xs[:, D]
                then, other = xs[:, E] + xs[:, F], xs[:, G]
                labels = np.where(gate, then, other).astype("<i8")
                sha = hashlib.sha256(labels.tobytes()).hexdigest()
                cid = f"GS:(X{A}+X{B})>(X{C}+X{D})?(X{E}+X{F}):X{G}"
                cell = dict(
                    id=cid,
                    shape="GS",
                    roles=dict(zip("ABCDEFG", roles)),
                    proper=True,
                    labels=labels.tolist(),
                    label_hash=sha,
                    canonical=list(tree.program),
                    canonical_tree=list(tree.prefix),
                    pairing=sorted([sorted((A, B)), sorted((C, D))]),
                )
                reason = (
                    "inactive_gate_or_branch"
                    if gate.all()
                    or not gate.any()
                    or np.array_equal(labels, then)
                    or np.array_equal(labels, other)
                    else "old_DG_TS_exact_alias"
                    if sha in old
                    else "duplicate_label"
                    if sha in unique
                    else None
                )
                if reason:
                    excluded.append(dict(id=cid, label_hash=sha, reason=reason))
                else:
                    unique[sha] = cell
    candidates = sorted(unique.values(), key=lambda c: (c["label_hash"], c["id"]))
    separated = []
    for c in candidates:
        if any(
            5 * np.count_nonzero(np.array(c["labels"]) == p["labels"]) >= 4 * 625
            for p in separated
        ):
            excluded.append(
                dict(
                    id=c["id"],
                    label_hash=c["label_hash"],
                    reason="pairwise_agreement_at_least_80_percent",
                )
            )
        else:
            separated.append(c)
    return separated, excluded


def split(cells):
    development = cells[:4]
    probed = {tuple(c["roles"].values()) for c in development}
    if not set(PROBED_ROLES) <= probed or len({pairing(c) for c in development}) != 3:
        raise ValueError(
            "fixed first-four development split fails probe exclusion/coverage"
        )
    pairs = sorted({pairing(c) for c in cells})
    protected = []
    if len(pairs) != 3:
        raise ValueError("missing predicate pair split")
    for p in pairs:
        group = [c for c in cells[4:] if pairing(c) == p]
        if len(group) < 6:
            raise ValueError(
                f"only {len(group)} protected survivors for {p}; six required"
            )
        protected.extend(group[:6])
    return dict(
        development=[c["id"] for c in development],
        protected=[c["id"] for c in protected],
    )


def build(old_banks, planning, deadline=None):
    tick = time.monotonic()
    candidates, excluded = roster(old_banks)
    if [list(c["roles"].values()) for c in candidates] != planning["greedy_roles"]:
        raise ValueError("candidate roster disagrees with planning audit")
    screen = screen_domain(
        "D625",
        9,
        deadline,
        cells=candidates,
        tokens=EXECUTABLE,
        machine_type=XMachine,
        alphabet=ALPHABET,
    )
    # The proposal admits iff no <=9-token exact solution exists. The reused
    # screen also reports near aliases; retain their diagnostics without adding
    # a stricter, unapproved admission criterion.
    for c in screen["cells"]:
        c["retained"] = c["best_matches"] < 625 and not c["duplicate_ids"]
        c["exclusion_reason"] = None if c["retained"] else "short_exact_alias"
    admitted = [c for c in screen["cells"] if c["retained"]]
    bank = dict(
        name=BANK,
        alphabet=ALPHABET,
        inputs=inputs_for("D625"),
        screen=screen,
        exclusions=excluded,
        split=split(admitted),
        admission="no exact executable program through nine tokens; pairwise agreement <80%",
        tie_break="ascending label SHA256/id; first four development; first six remaining per sorted pair split",
        seconds=time.monotonic() - tick,
    )
    validate_bank(bank, old_banks, planning)
    return bank


def validate_bank(bank, old_banks, planning):
    candidates, excluded = roster(old_banks)
    cells = bank["screen"]["cells"]
    if (
        bank["name"] != BANK
        or bank["alphabet"] != ALPHABET
        or bank["inputs"] != inputs_for("D625")
        or not bank["screen"]["complete"]
        or bank["screen"]["max_depth"] != 9
        or bank["screen"]["token_ids"] != list(EXECUTABLE)
        or len(cells) != 144
        or bank["exclusions"] != excluded
        or [list(c["roles"].values()) for c in candidates] != planning["greedy_roles"]
    ):
        raise ValueError("incomplete or changed gate-sum bank")
    for c, expected in zip(cells, candidates):
        if any(c[k] != v for k, v in expected.items()):
            raise ValueError("candidate semantics/roster changed")
        if c["retained"] != (c["best_matches"] < 625 and not c["duplicate_ids"]):
            raise ValueError("short exact alias admission changed")
    if bank["split"] != split([c for c in cells if c["retained"]]):
        raise ValueError("fixed split changed")


def verify(bank):
    """Validate every canonical and screen witness, without evolutionary search."""
    tick = time.monotonic()
    for c in bank["screen"]["cells"]:
        t = Tree(tuple(c["canonical_tree"]))
        if len(t.program) != 19 or list(t.program) != c["canonical"]:
            raise ValueError("canonical compilation changed")
        if (
            [interpret(t, x) for x in bank["inputs"]] != c["labels"]
            or [python_output(t, x) for x in bank["inputs"]] != c["labels"]
            or outputs([t.program], bank["inputs"], ALPHABET)[0].tolist() != c["labels"]
        ):
            raise ValueError("canonical interpreter/Python/Rust mismatch")
        from experiments.chem_tape.independent_input_bank import semantic_outputs

        witness = outputs([c["witness"]], bank["inputs"], ALPHABET)
        if (
            not np.array_equal(
                witness, semantic_outputs([c["witness"]], bank["inputs"])
            )
            or np.count_nonzero(witness[0] == c["labels"]) != c["best_matches"]
        ):
            raise ValueError("screen witness verification failed")
    return dict(
        passed=True,
        cells=len(bank["screen"]["cells"]),
        seconds=time.monotonic() - tick,
        protected_searches=0,
    )
