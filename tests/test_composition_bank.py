"""Checks for the new reducer and exhaustive-screen implementation."""

import itertools

import numpy as np
import pytest
from _folding_rust import rust_chem_execute

from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program, resolve_op
from experiments.chem_tape.composition_bank import (
    INPUTS,
    TOKENS,
    TA,
    SemanticMachine,
    cells,
    rust_outputs,
)
from experiments.chem_tape.composition_search import Decoder, base_tables


@pytest.mark.parametrize("inp", [[], [-2, -1], [3, 5], [-2, 1, 0, 2]])
def test_reduce_min_and_legacy(inp):
    tokens = [a.INPUT, a.REDUCE_MIN]
    expected = min(inp) if inp else 0
    assert execute_program(tokens, TA, inp, "intlist", "v2_rmin") == expected
    assert (
        rust_chem_execute(tokens, "NOP", "NOP", inp, "intlist", "v2_rmin", 0)
        == expected
    )
    assert (
        execute_program([a.CONST_1, a.CONST_2, 22], TA, inp, "intlist", "v2_min") == 1
    )
    assert (
        execute_program([a.CONST_1, a.CONST_2, 22], TA, inp, "intlist", "v2_imax") == 2
    )


def test_machine_full_stacks_and_rust_differential():
    m = SemanticMachine()
    rng = np.random.default_rng(224700)
    programs = [
        rng.choice(TOKENS, size=rng.integers(0, 33)).tolist() for _ in range(160)
    ]
    observed = rust_outputs(programs)
    for program, outputs in zip(programs, observed):
        state = ()
        for token in program:
            state = m.apply(state, token)
        assert np.array_equal(m.values[m.output_id(state)], outputs)
        # Compare complete typed stack to the independently implemented
        # production reference, on every domain input.
        for j, inp in enumerate(INPUTS):
            stack = []
            for token in program:
                resolve_op(token, TA, "v2_rmin")(stack, inp, "intlist", TA)
            expected = []
            for value in state:
                expected.append(
                    ("int", int(m.values[value][j]))
                    if value >= 0
                    else ("intlist", tuple(inp))
                    if value == -1
                    else ("intlist", ())
                    if value == -2
                    else ("charlist", ())
                )
            assert stack == expected


def test_exact_semantic_dedup_vs_bruteforce_through_four():
    m = SemanticMachine()
    seen = {()}
    frontier = {()}
    dedup_outputs = {m.values[m.zero].tobytes()}
    for _ in range(4):
        nxt = {m.apply(state, t) for state in frontier for t in TOKENS} - seen
        seen |= nxt
        frontier = nxt
        dedup_outputs |= {m.values[m.output_id(s)].tobytes() for s in frontier}
    raw_outputs = set()
    raw_states = set()
    # Compare raw enumeration to the Rust executor, including every invalid
    # prefix, not to the same semantic-machine implementation.
    for depth in range(5):
        raw = itertools.product(TOKENS, repeat=depth)
        while batch := list(itertools.islice(raw, 1024)):
            raw_outputs.update(row.tobytes() for row in rust_outputs(batch))
            for program in batch:
                state = ()
                for token in program:
                    state = m.apply(state, token)
                raw_states.add(state)
    assert raw_outputs == dedup_outputs
    assert raw_states == seen


def test_nop_tokens_canonical_tapes_and_decoder():
    for t in (0, 12, 13, 20, 21):
        assert resolve_op(t, TA, "v2_rmin") is resolve_op(0, TA, "v2_rmin")
    cs = cells()
    assert np.array_equal(
        rust_outputs([[0] * (32 - len(c["canonical"])) + c["canonical"] for c in cs]),
        np.array([c["labels"] for c in cs]),
    )
    alleles = np.random.default_rng(224700).integers(23000, size=(1024, 32))
    for table in base_tables().values():
        d = Decoder(table)
        assert np.array_equal(d.decode(alleles), d.decode(alleles.copy()))
    assert np.array_equal(Decoder(base_tables()["U"]).decode(alleles), alleles // 1000)


def test_latent_executor_and_invalid_tables():
    from _folding_rust import rust_chem_execute_alleles
    from experiments.chem_tape.composition_search import outputs

    alleles = np.random.default_rng(224700).integers(23000, size=(80, 32))
    for table in base_tables().values():
        d = Decoder(table)
        observed = np.array(
            rust_chem_execute_alleles(alleles.tolist(), table.tolist(), INPUTS)
        ).reshape(80, 625)
        assert np.array_equal(observed, outputs(d.decode(alleles), INPUTS))
    with pytest.raises(ValueError):
        rust_chem_execute_alleles([[23000]], base_tables()["U"].tolist(), INPUTS)
    with pytest.raises(ValueError):
        Decoder(np.zeros((24, 23)))


def test_censored_statistics_and_split_routing():
    from experiments.chem_tape.composition_calibrate import select_bank
    from experiments.chem_tape.composition_bank import screen
    from experiments.chem_tape.composition_report import (
        median,
        summarize,
        decision,
        splits,
        summaries,
        CAP,
    )

    def row(cid, arm, seed, solved=True, cost=16384, seconds=0.1):
        return dict(
            cell=cid,
            arm=arm,
            seed=seed,
            solved=solved,
            evaluations=cost if solved else CAP,
            seconds=seconds,
            budget_seconds={
                str(b): seconds for b in (32768, 65536, 131072, 262144, CAP)
            },
            shortcuts=0,
            decode_seconds=0.001,
            generations=64,
        )

    censored = [row("x", "U", i, i < 24) for i in range(50)]
    assert median(censored) is None
    stat = summarize(censored, np.random.default_rng(1))
    assert stat["km_median"] is None
    assert stat["km_median_95_interval"][1] is None
    assert stat["ranking_value"] == CAP
    assert stat["budgets"]["32768"]["objective_sd"] > 0
    bank = select_bank(screen(6))
    retained = [c for c in bank if not c["rejects"]]
    rows = [
        row(c["id"], arm, i)
        for c in retained
        for arm in ("U", "F", "G", "G-marg")
        for i in range(50)
    ]
    result = decision(bank, rows, True)
    assert result["outcome"] == "5"
    assert len(result["transversals"]) == 6
    assert result["all_split_costs"][0]["inner_budget"] == 32768
    cost = result["all_split_costs"][0]["budgets"]["32768"]["trajectories"]["8"]
    assert cost["mismatched_adaptation_cpu_hours"] == cost["adaptation_cpu_hours"]
    assert decision(bank, rows, False)["outcome"] == "U"
    assert decision(bank, rows, True, False)["outcome"] == "U"
    hard = [{**r, "solved": False, "evaluations": CAP} for r in rows]
    assert decision(bank, hard, True)["outcome"] == "2"
    fast = [{**r, "evaluations": 256} if r["arm"] == "F" else r for r in rows]
    assert decision(bank, fast, True)["outcome"] == "3"
    slower = [{**r, "evaluations": 262144} for r in rows]
    result = decision(bank, slower, True)
    assert result["outcome"] == "4a"
    assert result["all_split_costs"][0]["budgets"]["262144"]["feasible"]
    expensive = [
        {
            **r,
            "seconds": 100000,
            "budget_seconds": {
                str(b): 100000 for b in (32768, 65536, 131072, 262144, CAP)
            },
        }
        for r in rows
    ]
    assert decision(bank, expensive, True)["outcome"] == "4"
    failed_bank = [
        {**c, "rejects": c["rejects"] or c["id"] in ("SM-ADD", "Sm-ADD")} for c in bank
    ]
    assert decision(failed_bank, [], True)["outcome"] == "1"
    # F fast on one and G fast on another is insufficient for no headroom.
    summary = summaries(rows)
    split = next(s for s in splits(bank, summary) if s["eligible"])
    summary[split["holdouts"][0] + "|F"]["km_median"] = 256
    summary[split["holdouts"][1] + "|G"]["km_median"] = 256
    check = next(s for s in splits(bank, summary) if s["holdouts"] == split["holdouts"])
    assert check["headroom"]


def test_seed_pairing_and_reproducibility():
    from experiments.chem_tape.composition_search import search

    c = cells()[0]
    tables = base_tables()
    first = search((c, "U", tables["U"], 22471000, 1024, 32))
    again = search((c, "U", tables["U"], 22471000, 1024, 32))
    grammar = search((c, "G", tables["G"], 22471000, 1024, 32))
    assert first["training_indices"] == grammar["training_indices"]
    for key in ("solved", "evaluations", "curve", "shortcuts", "training_indices"):
        assert first[key] == again[key]


def test_inner_budget_borderline_topups_and_pooled_routing():
    from experiments.chem_tape.composition_calibrate import select_bank
    from experiments.chem_tape.composition_bank import screen
    from experiments.chem_tape.composition_report import (
        BUDGETS,
        CAP,
        decision,
        summaries,
        topup_requests,
    )

    bank = select_bank(screen(6))
    retained = [c for c in bank if not c["rejects"]]

    def row(cid, arm, seed, at_budget):
        return dict(
            cell=cid,
            arm=arm,
            seed=seed,
            solved=True,
            evaluations=16384 if at_budget else 262144,
            seconds=0.01,
            budget_seconds={str(b): 0.01 for b in (*BUDGETS, 262144, CAP)},
            shortcuts=3,
            unique_shortcuts=1,
            decode_seconds=0.001,
            generations=64,
        )

    rows = [
        row(c["id"], arm, seed, arm != "U" or seed < 24)
        for c in retained
        for arm in ("U", "F", "G", "G-marg")
        for seed in range(50)
    ]
    # All cells solve by the cap, so this isolates the new inner-budget gate.
    requests = topup_requests(bank, summaries(rows))
    assert len(requests) == len(retained)
    assert all(r["arm"] == "U" and len(r["reasons"]) == 3 for r in requests)
    result = decision(bank, rows, True)
    assert result["outcome"] == "U"
    assert result["pending_inner_budgets"] == list(BUDGETS)

    for extra_hits, expected in ((50, "4a"), (51, "5")):
        pooled = rows + [
            row(c["id"], "U", 22472000 + seed, seed < extra_hits)
            for c in retained
            for seed in range(100)
        ]
        result = decision(bank, pooled, True)
        assert result["outcome"] == expected
        assert not topup_requests(bank, summaries(pooled))
        s = result["summaries"][retained[0]["id"] + "|U"]
        assert s["budgets"]["131072"]["solves"] == 24 + extra_hits
        assert s["unique_shortcuts"] == 150
        assert s["shortcuts"] == 450

    # The same U seed block satisfies both gates; no duplicate job request.
    both = [
        {
            **r,
            "solved": r["seed"] < 35,
            "evaluations": (16384 if r["seed"] < 24 else CAP),
        }
        if r["arm"] == "U"
        else r
        for r in rows
    ]
    requests = topup_requests(bank, summaries(both))
    assert len(requests) == len(retained)
    assert all("tractability" in r["reasons"] for r in requests)


def test_row_two_keeps_structural_headroom_diagnostics():
    from experiments.chem_tape.composition_calibrate import select_bank
    from experiments.chem_tape.composition_bank import screen
    from experiments.chem_tape.composition_report import BUDGETS, CAP, decision

    bank = select_bank(screen(6))
    rows = [
        dict(
            cell=c["id"],
            arm=arm,
            seed=seed,
            solved=arm != "U",
            evaluations=CAP if arm == "U" else 256,
            seconds=0.01,
            budget_seconds={str(b): 0.01 for b in (*BUDGETS, 262144, CAP)},
            shortcuts=0,
            decode_seconds=0.001,
            generations=64,
        )
        for c in bank
        if not c["rejects"]
        for arm in ("U", "F", "G", "G-marg")
        for seed in range(50)
    ]
    result = decision(bank, rows, True)
    assert result["outcome"] == "2"
    assert result["deciding_cap"] == CAP
    structural = [s for s in result["structural_transversals"] if s["eligible"]]
    assert len(structural) == 4
    assert all(s["holdout_medians"]["G"] == [256] * 3 for s in structural)
    assert result["all_structural_candidates_lack_headroom"]
    assert result["structural_headroom_complete"]
    assert not decision(bank, rows, True, False)["structural_headroom_complete"]
