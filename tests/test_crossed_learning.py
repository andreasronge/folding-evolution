"""Leakage, budget, accounting, and trajectory-level inference invariants."""

import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.stats import t

from experiments.chem_tape.crossed_learning_run import (
    DEFAULT_BANK,
    G4_HASH,
    HOLDOUTS,
    TRAINING,
    Runner,
    early_stop,
    load_bank,
    reservation,
)
from experiments.chem_tape.crossed_learning_report import (
    flags,
    interval,
    make_report,
    outcome,
    sizing,
)


def runner(tmp_path, monkeypatch, smoke=False):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    return Runner(
        SimpleNamespace(
            bank=str(DEFAULT_BANK),
            workers=10,
            deadline_seconds=27000,
            smoke=smoke,
            probe=False,
        )
    )


def test_frozen_bank_and_search_payload(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch)
    assert len(r.cells) == 10
    assert all(set(c) == {"id", "labels"} for c in r.cells.values())
    for cid in sum(HOLDOUTS.values(), []):
        with pytest.raises(ValueError, match="non-training"):
            r.job(cid, "G4", r.controls["G"], 1, 65536)
    broken = tmp_path / "broken.json"
    broken.write_text(DEFAULT_BANK.read_text() + " ")
    with pytest.raises(ValueError, match="SHA256"):
        load_bank(broken)


def test_full_learner_search_accounting_and_fresh_selection(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch)
    batches = []

    def fake_jobs(jobs, phase):
        batches.append((jobs, phase))
        return [dict(arm=j[1], solved=False, evaluations=j[4]) for j in jobs]

    monkeypatch.setattr(r, "jobs", fake_jobs)
    r.evolve("BE", 0)
    assert sum(len(jobs) for jobs, _ in batches[:-1]) == 9696
    assert len(batches[-1][0]) == 600
    selection = batches[-1][0]
    for arm in {j[1] for j in selection}:
        jobs = [j for j in selection if j[1] == arm]
        assert len(jobs) == 120
        assert {
            cid: sum(j[0]["id"] == cid for j in jobs) for cid in TRAINING["BE"]
        } == dict.fromkeys(TRAINING["BE"], 30)
        assert [j[3] for j in jobs] == list(
            range(1723200 * 10000 + 5000, 1723200 * 10000 + 5120)
        )
    inner_seeds = {j[3] for jobs, _ in batches[:-1] for j in jobs}
    assert not inner_seeds & {j[3] for j in selection}
    tr = r.trajectories["BE1"]
    assert tr["evaluations"] == 10296 * 65536
    assert tr["selection_gain_log2"] == 0
    assert len(tr["vector"]) == 24 and tr["table_hash"] == G4_HASH
    generations = [
        json.loads(s) for s in (tmp_path / "generations.jsonl").read_text().splitlines()
    ]
    assert len(generations) == 26
    assert len(generations[0]["candidates"]) == 4
    assert all(
        len(g["candidates"]) == 16 and len(g["mutations"]) == 12
        for g in generations[1:]
    )
    r.evolve("PA", 0)
    selection = batches[-1][0]
    assert all(
        sum(j[0]["id"] == cid for j in selection) == 100 for cid in TRAINING["PA"]
    )
    assert r.trajectories["PA1"]["seed"] == 1723201


def test_deadline_reserve_and_operational_gate(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch)
    r.pair_times = [100, 200]
    r.deadline = 0
    assert not r.admit()
    assert r.schedule[-1]["reserve"]["pair_seconds"] == 260
    reserve = reservation(100, 2, 4, 10)
    assert reserve["fresh_seconds"] == 1.3 * 7 * 10 * 50 * 2 / 10
    ts = {str(i): dict(selection_gain_log2=0.01) for i in range(4)}
    assert early_stop(ts)
    ts["3"]["selection_gain_log2"] = np.log2(1.1)
    assert not early_stop(ts)
    assert not early_stop(dict(list(ts.items())[:2]))


def test_early_stop_runs_fresh_training_for_all_saved_maps(tmp_path, monkeypatch):
    import experiments.chem_tape.crossed_learning_run as module

    r = runner(tmp_path, monkeypatch)
    fake_pool = SimpleNamespace(terminate=lambda: None, join=lambda: None)
    monkeypatch.setattr(
        module.mp, "get_context", lambda *_: SimpleNamespace(Pool=lambda *_: fake_pool)
    )
    monkeypatch.setattr(r, "admit", lambda: True)

    def evolve(family, k):
        r.trajectories[f"{family}{k + 1}"] = dict(
            family=family, selection_gain_log2=0, table=r.controls["G"].tolist()
        )

    monkeypatch.setattr(r, "evolve", evolve)
    batches = []
    monkeypatch.setattr(
        r, "jobs", lambda jobs, phase: batches.append((jobs, phase)) or []
    )
    monkeypatch.setattr(module, "make_report", lambda *_: {})
    monkeypatch.setattr(module, "save_report", lambda *_: None)
    r.run()
    assert r.gate_stopped and len(r.trajectories) == 4
    assert len(r.pair_times) == 2
    assert len(batches) == 5
    assert all(
        len(jobs) == 500 and phase == "fresh_training" for jobs, phase in batches
    )
    assert {j[1] for jobs, _ in batches for j in jobs} == {
        "G4",
        "BE1",
        "BE2",
        "PA1",
        "PA2",
    }


def test_independent_welch_and_small_resolved_gain_precedence():
    x, y = [1, 2, 3], [0, 0, 0, 0]
    r = interval(x, y)
    assert r["ratio"] == 4
    assert r["df"] == 2
    assert r["half_width_log2"] == pytest.approx(t.ppf(0.975, 2) * np.sqrt(1 / 3))
    small = dict(interval_95=[1.05, 1.2])
    assert flags(small) == dict(resolved_gain=True, upper_below_1_25=True, label="L")
    assert flags(small, crossed=True)["label"] == "W"
    own = {f: dict(label="L") for f in TRAINING}
    cross = {f: dict(label="B") for f in TRAINING}
    assert outcome(own, cross, True, 10, False)["row"] == "3"
    cross["BE"]["label"] = "X"
    assert outcome(own, cross, True, 10, False)["row"] == "4"
    assert outcome(own, cross, True, 2, True)["row"] == "1"
    assert outcome(own, cross, True, 2, False)["row"] == "U"


def synthetic():
    config = dict(
        training=TRAINING,
        fresh_seeds=[1723300, 1723301],
        fresh_cap=524288,
        g4_hash=G4_HASH,
        smoke_only=False,
    )
    trs = {}
    rows = []
    for f in TRAINING:
        for k in range(6):
            tid = f"{f}{k + 1}"
            trs[tid] = dict(
                family=f,
                table_hash=tid,
                vector=[k * 0.1 + (f == "PA")] * 24,
                final_in_loop_selected_score=16 - k * 0.1,
                selection_scores=[16 - k * 0.1] * 4,
                within_generation_spearman=[None, 0.5],
                seconds=100,
                evaluations=65536,
            )
    for tid in ["G4", *trs]:
        for cid in sum(TRAINING.values(), []):
            for seed in config["fresh_seeds"]:
                gain = (
                    0
                    if tid == "G4"
                    else (
                        0.5
                        + int(tid[2:]) * 0.1
                        + (cid.startswith(trs[tid]["family"]) * 0.5)
                    )
                )
                rows.append(
                    dict(
                        arm=tid,
                        cell=cid,
                        seed=seed,
                        solved=True,
                        cap=524288,
                        evaluations=2 ** (18 - gain),
                        phase="fresh_training",
                        table_hash=G4_HASH if tid == "G4" else tid,
                        training_indices=[1, 2],
                    )
                )
    return rows, trs, config


def test_exact_fresh_cross_product_and_case_pairing():
    rows, trs, config = synthetic()
    good = make_report(rows, trs, config, False)
    assert good["complete"] and good["outcome"]["row"] == "4"
    assert good["crossed"]["BE"]["ratio"] == pytest.approx(np.sqrt(2))
    assert good["own"]["BE"]["estimated_n_for_half_width_below_log2_1_25"] == 4
    assert good["spreads"][TRAINING["BE"][0]]["contrast_proxy"] == pytest.approx(
        np.std(np.arange(6) * 0.1, ddof=1)
    )
    assert make_report(rows[:-1], trs, config, False)["outcome"]["row"] == "U"
    assert make_report(rows + [rows[0]], trs, config, False)["outcome"]["row"] == "U"
    wrong = copy.deepcopy(rows)
    wrong[-1]["training_indices"] = [2, 3]
    assert make_report(wrong, trs, config, False)["outcome"]["row"] == "U"
    wrong[-1]["table_hash"] = "bad"
    assert not make_report(wrong, trs, config, False)["complete"]


def test_sizing_never_turns_missing_precision_into_generic_transfer():
    spreads = {c: dict(contrast_proxy=2) for c in sum(TRAINING.values(), [])}
    r = sizing(spreads, 10)
    assert r["no_candidate_reaches_target"] and r["selected_n_per_family"] == 10
    assert r["achieved_half_width_log2"] > 0.5
    own = {f: dict(label="L") for f in TRAINING}
    cross = {f: dict(label="X") for f in TRAINING}
    assert outcome(own, cross, True, 10, False)["row"] == "4"
