"""1831 scientific invariants: replay, terminal checkpoint, exclusion and pairing."""

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape import composition_search as engine
from experiments.chem_tape.comparison_gate_bank import TRAINING, load_training
from experiments.chem_tape.partial_program_collect import Collector, collect_search
from experiments.chem_tape.partial_program_run import ARMS, BASE, Runner, roster
from experiments.chem_tape.partial_program_report import make_report, route
from experiments.chem_tape.solver_corpus_fit import (
    partial_transition_counts,
    transition_counts,
)
from experiments.chem_tape.four_reducer_maps import tables


def scientific(row):
    return {
        k: v
        for k, v in row.items()
        if k
        not in (
            "seconds",
            "decode_seconds",
            "budget_seconds",
            "archive",
            "archive_verification_seconds",
            "worker_seconds",
        )
    }


def test_replay_real_executor_and_deterministic_archive():
    bank, cells = load_training()
    cid = TRAINING["BE"][0]
    job = (
        cells[cid],
        "G4",
        tables()["G4"],
        BASE + 100000000,
        65536,
        256,
        bank["inputs"],
        "v2_rmin_first",
    )
    baseline = engine.search(job)
    a = collect_search((job, {}))
    b = collect_search((job, {}))
    assert scientific(a) == scientific(b) == scientific(baseline)
    assert a["archive"] == b["archive"]
    assert a["archive"] and all(not r["exact"] for r in a["archive"])
    assert (
        all(r["evaluations"] < a["evaluations"] for r in a["archive"])
        if a["solved"]
        else True
    )


def test_terminal_and_solve_checkpoint_boundary(monkeypatch):
    monkeypatch.setattr(
        engine,
        "outputs",
        lambda programs, inputs, alphabet: np.zeros(
            (len(programs), len(inputs)), dtype=int
        ),
    )
    job = (
        {"id": "mock", "labels": [1] * 64},
        "G4",
        tables()["G4"],
        11,
        4 * 8,
        8,
        [[0]] * 64,
        "v2_rmin_first",
    )
    archive = Collector(11, checkpoints=(1, 2, 4))
    before = engine.search(job)
    after = engine.search(job, collector=archive)
    assert scientific(before) == scientific(after)
    assert Counter_checkpoints(archive.rows) == {1: 16, 2: 16, 4: 16}
    terminal = [r for r in archive.rows if r["checkpoint"] == 4]
    assert all(r["terminal"] for r in terminal)
    assert len({r["population_hash"] for r in terminal}) == 1
    # All candidate rows are exact at population1: solve before any archive draw.
    job = ({"id": "mock", "labels": [0] * 64},) + job[1:]
    archive = Collector(11, checkpoints=(1, 2, 4))
    result = engine.search(job, collector=archive)
    assert result["solved"] and result["evaluations"] == 8 and not archive.rows

    calls = 0

    def solve_at_cap(programs, inputs, alphabet):
        nonlocal calls
        calls += 1
        return np.full((len(programs), len(inputs)), int(calls < 4))

    monkeypatch.setattr(engine, "outputs", solve_at_cap)
    archive = Collector(11, checkpoints=(1, 2, 4))
    result = engine.search(job, collector=archive)
    assert result["solved"] and result["evaluations"] == 32
    assert Counter_checkpoints(archive.rows) == {1: 16, 2: 16}


def Counter_checkpoints(rows):
    from collections import Counter

    return dict(Counter(r["checkpoint"] for r in rows))


def partial_source(cell, seed, token, copies):
    return dict(
        cell=cell,
        seed=seed,
        solved=False,
        evaluations=65536,
        archive=[
            dict(
                kind="S",
                cell=cell,
                source_seed=seed,
                exact=False,
                evaluations=16384,
                tape=[token] * 32,
            )
            for _ in range(copies)
        ],
    )


def test_equal_source_then_cell_weight_and_explicit_interface():
    rows = [
        partial_source("a", 1, 1, 8),
        partial_source("a", 2, 2, 24),
        partial_source("b", 3, 3, 8),
    ]
    n, yields = partial_transition_counts(rows, ["a", "b"], "S")
    assert yields == {"a": 2, "b": 1}
    assert n.sum() == pytest.approx(3200)
    assert n[:, 1].sum() == n[:, 2].sum() == pytest.approx(800)
    assert n[:, 3].sum() == pytest.approx(1600)
    with pytest.raises((ValueError, KeyError)):
        transition_counts(rows, ["a", "b"])
    with pytest.raises(ValueError, match="empty partial"):
        partial_transition_counts(rows, ["a", "b", "c"], "S")
    bad = deepcopy(rows)
    bad[0]["archive"][0]["exact"] = True
    with pytest.raises(ValueError, match="provenance"):
        partial_transition_counts(bad, ["a", "b"], "S")
    with pytest.raises(ValueError, match="duplicate source"):
        partial_transition_counts(rows + rows[:1], ["a", "b"], "S")


def test_roster_full_counts_smoke_disjoint_and_training_payload(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(SimpleNamespace(smoke=False, workers=10, deadline_seconds=14220))
    full = runner.schedule
    assert len(full) == 7168
    assert sum(r["phase"] == "collection" for r in full) == 2048
    assert sum(r["phase"] == "training" for r in full) == 5120
    assert len({r["seed"] for r in full}) == 2048 + 1024
    assert not {r["seed"] for r in full} & {
        r["seed"] for r in roster(BASE + 100000000, 1, 4, 2)
    }
    collect = [r for r in full if r["phase"] == "collection"]
    assert all(set(runner.envelope(r)[0][0]) == {"id", "labels"} for r in collect)
    bad = dict(collect[0], cell="holdout")
    with pytest.raises(ValueError, match="training-only"):
        runner.envelope(bad)
    for tid, tr in runner.saved["corpora.json"].items():
        assert tr["family"] == tid[:2] and tr["index"] == int(tid[2:]) - 1


def synthetic(pairs=8):
    rows = []
    for k in range(pairs):
        for f, cells in TRAINING.items():
            for cid in cells:
                for seed in range(2):
                    for arm in ARMS:
                        rows.append(
                            dict(
                                phase="training",
                                family=f,
                                corpus=f"{f}{k + 1}",
                                cell=cid,
                                seed=seed,
                                arm=arm,
                                cap=524288,
                                solved=True,
                                evaluations=1024 if arm == "C_S" else 2048,
                                seconds=1,
                                worker_seconds=1,
                            )
                        )
    cfg = dict(
        smoke_only=False,
        fresh_n=2,
        nc=8,
        workers=10,
        method_hash="test",
        method=dict(scope="test"),
    )
    return rows, cfg


def test_prefix_endpoint_pairing_precedence_errors_and_caps():
    rows, cfg = synthetic()
    report = make_report(rows, {}, cfg, 6, "timeout", "deadline", {})
    ct = report["sensitivities"]["unsolved_2x_cap"]["C_S/T_S"]
    assert ct["n"] == 12 and ct["speed_ratio"] == pytest.approx(2)
    assert report["outcome"]["label"] == "useful"
    changed = deepcopy(rows)
    for r in changed:
        if r["corpus"] in ("BE7", "PA7", "BE8", "PA8"):
            r["evaluations"] = 524288
    assert (
        make_report(changed, {}, cfg, 6, "timeout", "deadline", {})["sensitivities"]
        == report["sensitivities"]
    )
    for pairs, kind in ((5, "timeout"), (6, "error"), (6, None)):
        assert (
            make_report(rows, {}, cfg, pairs, kind, "failure", {})["outcome"]["label"]
            == "incomplete"
        )
    assert (
        route(dict(interval_95=[1.03, 1.19]), dict(interval_95=[1.01, 1.5]), True)[
            "label"
        ]
        == "bounded_gain"
    )
    assert (
        route(dict(interval_95=[1.01, 1.5]), dict(interval_95=[0.9, 1.5]), True)[
            "label"
        ]
        == "relative_only"
    )
    assert (
        route(dict(interval_95=[0.9, 1.5]), dict(interval_95=[1.01, 1.5]), True)[
            "label"
        ]
        == "unresolved"
    )
    for r in rows:
        if r["arm"] in ("C_S", "T_S"):
            r.update(solved=False, evaluations=r["cap"])
    result = make_report(rows, {}, cfg, 8, None, None, {})
    assert result["almost_all_primary_capped"]
    assert result["sensitivities"]["unsolved_2x_cap"]["C_S/T_S"]["speed_ratio"] == 1
    assert result["sensitivities"]["both_solved"]["C_S/T_S"]["n"] == 0
    with pytest.raises(ValueError, match="missing scored"):
        make_report(rows[1:], {}, cfg, 6, "timeout", "deadline", {})


def test_archive_samples_current_parent_slots_and_population():
    programs = np.tile(np.arange(32) % 24, (8, 1)).astype(np.uint8)
    programs[:, 0] = np.arange(8)
    correct = np.zeros((8, 64), dtype=bool)
    parents = np.array([[6] * 6, [3] * 6])
    collector = Collector(47, checkpoints=(64,))
    collector(64, programs, correct, parents, False)
    for row in collector.rows:
        assert row["tape"] == programs[row["population_index"]].tolist()
        if row["kind"] == "S":
            assert row["population_index"] == int(parents.ravel()[row["slot"]])
        else:
            assert row["population_index"] == row["slot"]


def test_archive_independent_exact_validation_refuses_hidden_solver(monkeypatch):
    import experiments.chem_tape.partial_program_collect as collect

    def fake_search(job, collector):
        tape = np.zeros((4, 32), dtype=np.uint8)
        collector(
            64, tape, np.zeros((4, 64), dtype=bool), np.zeros((2, 2), dtype=int), False
        )
        return dict(cell="mock", seed=1, solved=False, evaluations=65536)

    monkeypatch.setattr(collect, "search", fake_search)
    monkeypatch.setattr(
        collect,
        "outputs",
        lambda tapes, inputs, alphabet: np.zeros((len(tapes), len(inputs)), dtype=int),
    )
    job = (
        {"id": "mock", "labels": [0] * 1331},
        "G4",
        tables()["G4"],
        1,
        65536,
        256,
        [[0]] * 1331,
        "v2_rmin_first",
    )
    with pytest.raises(ValueError, match="exact tape entered"):
        collect.collect_search((job, {}))
