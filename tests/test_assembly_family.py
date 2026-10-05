"""Independent coverage checks for output-only screening and gated inference."""

import itertools

import numpy as np
import pytest

from experiments.chem_tape.assembly_bank import (
    DOMAINS,
    SHAPES,
    inputs_for,
    roster,
    screen_domain,
    choose_pair,
    split_shape,
)
from experiments.chem_tape.assembly_maps import frozen_controls, grammar
from experiments.chem_tape.assembly_report import shape_contrast, report
from experiments.chem_tape.composition_bank import TOKENS, SemanticMachine, TA
from experiments.chem_tape.composition_search import outputs, search, Decoder
from folding_evolution.chem_tape.executor import resolve_op


@pytest.mark.parametrize("domain", DOMAINS)
def test_canonicals_and_full_typed_states(domain):
    inputs = inputs_for(domain)
    cells = roster(domain)
    assert len(cells) == 162
    assert {s: sum(c["shape"] == s for c in cells) for s in SHAPES} == dict(
        GA=18, BT=27, BE=27, PA=54, D1=18, D2=18
    )
    assert np.array_equal(
        outputs([[0] * 22 + c["canonical"] for c in cells], inputs),
        [c["labels"] for c in cells],
    )
    m = SemanticMachine(inputs)
    rng = np.random.default_rng(260609000)
    programs = [rng.choice(TOKENS, rng.integers(1, 33)).tolist() for _ in range(80)]
    observed = outputs(programs, inputs)
    for program, label in zip(programs, observed):
        state = ()
        for token in program:
            state = m.apply(state, token)
        assert np.array_equal(m.values[m.output_id(state)], label)
        for j in rng.choice(len(inputs), 6, replace=False):
            stack = []
            for token in program:
                resolve_op(token, TA, "v2_rmin")(stack, inputs[j], "intlist", TA)
            expected = [
                ("int", int(m.values[v][j]))
                if v >= 0
                else ("intlist", tuple(inputs[j]))
                if v == -1
                else ("intlist", ())
                if v == -2
                else ("charlist", ())
                for v in state
            ]
            assert stack == expected


def test_output_only_screen_vs_raw_rust_through_four():
    domain = "D625"
    labels = np.array([c["labels"] for c in roster(domain)])
    best = np.full(len(labels), -1)
    raw_outputs = set()
    for depth in range(5):
        raw = itertools.product(TOKENS, repeat=depth)
        while batch := list(itertools.islice(raw, 512)):
            observed = outputs(batch, inputs_for(domain))
            raw_outputs.update(r.tobytes() for r in observed)
            # Work on distinct output vectors, independently of semantic machine.
            for row in np.unique(observed, axis=0):
                best = np.maximum(best, np.count_nonzero(labels == row, axis=1))
    screen = screen_domain(domain, 4)
    assert [c["best_matches"] for c in screen["cells"]] == best.tolist()
    assert screen["counts"][-1]["distinct_outputs"] == len(raw_outputs)
    assert screen["counts"][-1]["output_only"]
    assert not screen["complete"]


def test_grammars_and_legacy_hashes():
    tables = frozen_controls()
    assert set(tables) == {"U", "F", "G", "G-marg"}
    for shape in SHAPES:
        table = grammar(shape)
        assert np.all(table[:, -1] == 23000)
        assert np.min(np.diff(table, prepend=0, axis=1)) >= 500
        assert Decoder(table).hash()
    assert np.array_equal(grammar("BT"), grammar("BE"))
    assert not np.array_equal(grammar("PA"), grammar("BT"))


def test_uncovered_roles_fail_split_and_lexicographic_holdouts():
    cells = [
        dict(id=str(i), roles=dict(x=r), token_counts={"1": 2})
        for i, r in enumerate(("S", "S", "M", "M"))
    ]
    assert split_shape(cells)["holdouts"] == ["0", "2"]
    cells[0]["roles"]["x"] = "m"
    assert split_shape(cells) is None
    # Duplicate handling is global, rather than picking a convenient orientation.
    screen = screen_domain("D625", 2)
    for c in screen["cells"]:
        if c["duplicate_ids"]:
            assert not c["retained"]


def test_pair_selection_is_semantic_and_domain_ties_are_frozen():
    cells = [
        dict(
            id=shape + str(i),
            shape=shape,
            retained=True,
            roles=dict(role=r),
            token_counts={"1": 4, "7": 1, "17": 1},
        )
        for shape in ("BE", "BT")
        for i, r in enumerate(("S", "S", "M", "M"))
    ]
    pair = choose_pair({d: dict(cells=cells) for d in reversed(DOMAINS)})["selected"]
    assert pair["domain"] == "D625"
    assert pair["shapes"] == ["BE", "BT"]
    assert pair["split"]["BE"]["holdouts"] == ["BE0", "BE2"]


def rows_for(cells=("a", "b"), censored=False):
    return [
        dict(
            cell=cid,
            arm=arm,
            seed=i,
            evaluations=(8192 if arm == "swap" else 4096),
            solved=not censored or i < 20,
        )
        for cid in cells
        for arm in ("swap", "match")
        for i in range(50)
    ]


def test_joint_paired_bootstrap_and_censoring():
    rows = rows_for()
    contrast = shape_contrast(rows, ["a", "b"], "swap", "match")
    assert contrast["resolved"] and contrast["median_ratio"] == 2
    assert contrast["interval_95"] == [2.0, 2.0]
    censored = shape_contrast(rows_for(censored=True), ["a", "b"], "swap", "match")
    assert not censored["resolved"] and censored["median_ratio"] is None
    assert censored["capped_time_ratio"] == 2
    # Seed pairing is mandatory, not a zip of two unrelated samples.
    for row in rows:
        if row["arm"] == "match":
            row["seed"] += 1000
    assert shape_contrast(rows, ["a", "b"], "swap", "match")["n_paired_seeds"] == 0


def test_completed_semantics_survives_incomplete_calibration():
    screens = {d: dict(complete=True, cells=[]) for d in DOMAINS}
    result = report(screens, dict(selected=None), [], False, True, True)
    assert result["outcome"] == "U"
    assert result["semantic_verdict"] == "no eligible enumerated pair"
    assert result["stage_a_complete"]


def test_expanded_domain_search_case_pairing_and_exact_check():
    domain = "D1331"
    cell = roster(domain)[0]
    rows = [
        search((cell, arm, table, 260609020, 512, 256, inputs_for(domain)))
        for arm, table in frozen_controls().items()
    ]
    assert all(r["evaluations"] <= 512 for r in rows)
    assert all(r["training_indices"] == rows[0]["training_indices"] for r in rows)
    assert max(rows[0]["training_indices"]) >= 625


def test_both_shape_advantages_are_required_for_go():
    cells = [
        dict(
            id=shape + str(i),
            shape=shape,
            retained=True,
            alias_kind=None,
            duplicate_ids=[],
            roles=dict(role=r),
            token_counts={"1": 4, "7": 1, "17": 1},
        )
        for shape in ("BE", "PA")
        for i, r in enumerate(("S", "S", "M", "M"))
    ]
    screens = {d: dict(complete=True, cells=cells) for d in DOMAINS}
    pairing = choose_pair(screens)
    rows = []
    for c in cells:
        for arm in ("U", "F", "G", "G-marg", "BE", "PA", "BE-marg", "PA-marg"):
            t = 8192 if arm.split("-")[0] == c["shape"] else 16384
            if arm in ("U", "F", "G", "G-marg"):
                t = 32768
            for seed in range(50):
                rows.append(
                    dict(
                        cell=c["id"],
                        arm=arm,
                        seed=seed,
                        solved=True,
                        evaluations=t,
                        seconds=t / 1000000,
                        cap=524288,
                        budget_seconds={
                            str(b): t / 1000000
                            for b in (32768, 65536, 131072, 262144, 524288)
                        },
                        shortcuts=0,
                        decode_seconds=0,
                        generations=t // 256,
                    )
                )
    result = report(screens, pairing, rows, True, True, True)
    assert result["outcome"] == "5"
    assert result["costs"]["transfer_searches"] == 10400
    # G is faster than the matched diagnostic in one shape: row 3 cannot
    # pass merely because the other shape has a well-supported improvement.
    for row in rows:
        if row["cell"].startswith("PA") and row["arm"] == "G":
            row["evaluations"] = 4096
    assert report(screens, pairing, rows, True, True, True)["outcome"] == "3"
