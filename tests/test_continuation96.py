"""1137 scientific boundaries, independent diagnostics, and fixed budgets."""

from datetime import datetime
import json
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from experiments.chem_tape.continuation96_report import (
    F1_SEEDS,
    ROSTER,
    baseline_check,
    fingerprint,
    gate,
    load_reference,
    outcome,
    selected_diagnostic,
    validate_rows,
)
from experiments.chem_tape.continuation96_run import (
    ContinuationRunner,
    SEEDS,
    internal_seconds,
    reserve,
)
from experiments.chem_tape.crossed_learning_run import HOLDOUTS, TRAINING
from experiments.chem_tape.rank_one_learning import SEEDS as OLD_SEEDS


def runner(tmp_path, monkeypatch, smoke=False):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    # Freeze the local clock so the test does not depend on the wall time.
    monkeypatch.setattr(
        "experiments.chem_tape.continuation96_run.internal_seconds", lambda _: 19800
    )
    return ContinuationRunner(
        SimpleNamespace(workers=10, deadline_seconds=19800, smoke=smoke, probe=False)
    )


def estimate(lo=0.9, hi=1.2, ratio=1):
    return dict(interval_95=[lo, hi], ratio=ratio)


def test_gate_and_all_outcome_boundaries():
    assert not gate(estimate(ratio=1.099999))
    assert gate(estimate(ratio=1.10))
    assert not gate(estimate(ratio=1.2), False)
    counts = dict(BE=8, PA=8)
    minimum = dict(BE=6, PA=6)

    def decide(
        f1=None, token=None, ct=None, cs=None, residual=None, valid=True, nc=minimum
    ):
        return outcome(
            f1 or estimate(ratio=1.1),
            token or estimate(lo=1.01),
            ct or estimate(hi=1.14),
            cs or estimate(),
            residual or estimate(),
            valid,
            counts,
            nc,
        )

    assert decide(valid=False)["row"] == "U"
    assert decide(f1=estimate(hi=1.099, ratio=1.05))["row"] == "1"
    assert decide(f1=estimate(hi=1.10, ratio=1.05))["row"] == "2"
    assert decide(nc=dict(BE=6, PA=5))["row"] == "3"
    relative = decide(token=estimate(), ct=estimate(lo=1.01))
    assert relative["row"] == "4" and not relative["beneficial_adaptation_above_S"]
    assert decide(token=estimate(lo=1), ct=estimate(lo=1, hi=1.14))["row"] == "5"
    assert decide()["row"] == "6"
    assert decide(ct=estimate(hi=1.15))["row"] == "7"


def test_reserve_keeps_confirmation_without_context_and_prospective_cells():
    empty = reserve(ROSTER, [], None, [100], 1, 10)
    assert empty["fresh_searches"] == 8500
    assert empty["trajectory_seconds"] == 0
    first = reserve(ROSTER, [], "BE1", [100, 120], 1, 10)
    assert first["fresh_searches"] == 8900
    assert first["trajectory_seconds"] == 156
    full = reserve(ROSTER, ROSTER[:-1], ROSTER[-1], [100], 1, 10)
    assert full["fresh_searches"] == 16500
    stockholm = ZoneInfo("Europe/Stockholm")
    assert internal_seconds(19800, datetime(2026, 10, 7, 20, tzinfo=stockholm)) == 7200
    assert internal_seconds(21000, datetime(2026, 10, 7, 12, tzinfo=stockholm)) == 19800


def test_diagnostic_tracks_source_not_competitor():
    previous = dict(
        selected_indices=[3, 0],
        scores=[10, 11, 9, 8],
        mutations=[dict(parent=1), dict(parent=0)],
        candidates=[dict(id=f"candidate{i}") for i in range(4)],
    )
    d = selected_diagnostic(previous, [12, 10])
    assert d["covered_pairs"] == 1
    assert d["selected_changes"] == [
        dict(child_id="candidate3", source_parent_id="candidate0", child_minus_parent=2)
    ]
    assert d["winners_curse"][0]["acceptance_minus_rescore"] == -4
    previous["mutations"][1]["parent"] = 1
    d = selected_diagnostic(previous, [12, 10])
    assert d["covered_pairs"] == 0 and d["missing_source_parent"] == 1
    # Both accepted children can have discarded parents; no pair is invented.
    previous["selected_indices"] = [2, 3]
    d = selected_diagnostic(previous, [12, 10])
    assert d["accepted_children"] == d["missing_source_parent"] == 2


def test_reference_pin_and_timing_exclusion():
    ref = load_reference()
    assert len(ref["records"]) == 8000
    assert "seconds" not in ref["scientific_fields"]
    row = dict(
        arm="BE1:S",
        cell=TRAINING["BE"][0],
        seed=F1_SEEDS[0],
        evaluations=256,
        solved=True,
        seconds=1,
    )
    fields = ["evaluations", "solved"]
    tiny_ref = dict(
        scientific_fields=fields,
        records=[
            dict(
                start="BE1",
                arm="S",
                cell=c,
                seed=F1_SEEDS[0],
                scientific_sha256=fingerprint(row, fields),
            )
            for c in TRAINING["BE"]
        ],
    )
    rows = [dict(row, cell=c) for c in TRAINING["BE"]]
    assert baseline_check(rows, tiny_ref, ["BE1"], F1_SEEDS[:1])["passed"]
    rows[0]["seconds"] = 999
    assert baseline_check(rows, tiny_ref, ["BE1"], F1_SEEDS[:1])["passed"]
    rows[0]["evaluations"] = 512
    assert not baseline_check(rows, tiny_ref, ["BE1"], F1_SEEDS[:1])["passed"]
    assert not baseline_check(rows[1:], tiny_ref, ["BE1"], F1_SEEDS[:1])["passed"]


def test_full_budget_midpoint_pairing_and_seed_disjointness(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch)
    batches = []

    def fake_jobs(jobs, phase):
        batches.append((jobs, phase))
        return [
            dict(
                arm=j[1],
                cell=j[0]["id"],
                seed=j[3],
                cap=j[4],
                solved=True,
                evaluations=256 * (1 + j[3] % 32),
                seconds=0.001,
            )
            for j in jobs
        ], 0.01

    monkeypatch.setattr(r, "jobs", fake_jobs)
    r.evolve_arm("PA1", "T")
    r.evolve_arm("PA1", "C")
    assert sum(len(j) for j, _ in batches) == 19200
    assert r.config["searches_per_trajectory"] == 9600
    assert all(f["search_costs"]["searches"] == 9600 for f in r.finals.values())
    assert r.finals["PA1:T"]["step_mix"]["token"]["proposed"] == 72
    assert "PA1" in r.midpoints
    t_batches, c_batches = batches[:13], batches[13:]
    used = set()
    for (tj, phase), (cj, _) in zip(t_batches, c_batches):
        streams = [
            [(j[0]["id"], j[3]) for j in jobs if j[1] == name]
            for jobs in (tj, cj)
            for name in dict.fromkeys(j[1] for j in jobs)
        ]
        assert all(s == streams[0] for s in streams)
        unique = {j[3] for j in tj}
        assert not used & unique
        used.update(unique)
        assert len(tj) == (8 * 96 if phase.startswith("learn") else 2 * 192)
        assert all(
            sum(c == cell for c, _ in streams[0]) == len(streams[0]) // 6
            for cell in TRAINING["PA"]
        )
    old_rng_namespaces = {
        v + off for v in OLD_SEEDS.values() for off in (0, 10_000_000, 20_000_000)
    }
    assert not set(SEEDS.values()) - {SEEDS["fresh"]} & old_rng_namespaces
    assert not used & set(F1_SEEDS)
    generations = [
        json.loads(line)
        for line in (tmp_path / "generations.jsonl").read_text().splitlines()
    ]
    assert len(generations) == 24
    assert (
        r.midpoints["PA1"]["vector"]
        == generations[5]["candidates"][generations[5]["selected_indices"][0]]["vector"]
    )
    for c in sum(HOLDOUTS.values(), []):
        with pytest.raises(ValueError, match="non-training"):
            r.job("bad", r.g4, c, 1, 65536)


def test_deadline_refusal_stops_at_first_and_retains_reserve(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch)
    r.token_times = [100]
    r.deadline = 0
    monkeypatch.setattr(r, "evolve_arm", lambda *_: pytest.fail("should not admit"))
    r.context_stage()
    assert len(r.schedule) == 1 and not r.schedule[0]["admitted"]
    assert r.schedule[0]["fresh_searches"] == 8900
    assert r.context_starts == []


def test_fresh_missing_duplicate_and_shared_case_checks():
    maps = {"BE1:S": dict(table_hash="s")}
    seeds = [1]
    rows = [
        dict(
            arm="BE1:S",
            cell=c,
            seed=1,
            cap=524288,
            phase="F1",
            pop_size=256,
            table_hash="s",
            training_indices=[0, 1],
        )
        for c in TRAINING["BE"]
    ]
    assert validate_rows(rows, maps, seeds, 524288, "F1")["passed"]
    assert not validate_rows(rows[:-1], maps, seeds, 524288, "F1")["passed"]
    assert not validate_rows([*rows, rows[0]], maps, seeds, 524288, "F1")["passed"]
    rows[-1]["training_indices"] = [1, 0]
    assert not validate_rows(rows, maps, seeds, 524288, "F1")["passed"]


@pytest.mark.parametrize(
    "pass_gate,context_limit,expected_row",
    [(False, 0, "1"), (True, 16, "4"), (True, 12, "4"), (True, 0, "3")],
)
def test_full_stage_flow_fresh_counts_and_matched_confirmation(
    tmp_path, monkeypatch, pass_gate, context_limit, expected_row
):
    r = runner(tmp_path, monkeypatch)
    captured = {}

    class FakePool:
        def terminate(self):
            pass

        def join(self):
            pass

    monkeypatch.setattr(
        "experiments.chem_tape.continuation96_run.mp.get_context",
        lambda _: SimpleNamespace(Pool=lambda _: FakePool()),
    )
    monkeypatch.setattr(
        "experiments.chem_tape.continuation96_run.baseline_check",
        lambda *_: dict(passed=True, simulated=True),
    )

    def evolve(tid, arm):
        from experiments.chem_tape.rank_one_learning import start_vector

        v = start_vector(r.starts[tid]["vector"], np.random.default_rng(0))
        r.finals[tid + ":" + arm] = dict(
            table=r.starts[tid]["table"], vector=v.tolist()
        )
        if arm == "T":
            r.midpoints[tid] = dict(table=r.starts[tid]["table"])
            r.pairs.append(tid)
            r.token_times.append(100)
        else:
            r.context_starts.append(tid)

    monkeypatch.setattr(r, "evolve_arm", evolve)

    def context_stage():
        for tid in ROSTER[:context_limit]:
            evolve(tid, "C")

    monkeypatch.setattr(r, "context_stage", context_stage)
    batches = {}

    def jobs(js, phase):
        batches[phase] = len(js)
        rows = []
        for j in js:
            label = j[1].split(":")[-1]
            evals = {
                "S": 4096,
                "T": 2048 if pass_gate else 4096,
                "T_mid": 4096,
                "C": 1024,
                "C0": 2048,
                "G4": 8192,
            }[label]
            rows.append(
                dict(
                    arm=j[1],
                    cell=j[0]["id"],
                    seed=j[3],
                    cap=j[4],
                    solved=True,
                    evaluations=evals,
                    seconds=0.001,
                    phase=phase,
                    pop_size=256,
                    training_indices=list(range(64)),
                    table_hash=r.config["g4_hash"]
                    if j[1] == "G4"
                    else r.starts[j[1].split(":")[0]]["table_hash"],
                )
            )
        return rows, 0.01

    monkeypatch.setattr(r, "jobs", jobs)
    monkeypatch.setattr(r, "save_report", lambda result: captured.update(result))
    r.run()
    assert batches["F1"] == 12000
    assert captured["gate_passed"] is pass_gate
    assert captured["outcome"]["row"] == expected_row
    if pass_gate:
        cells = sum(len(TRAINING[tid[:2]]) for tid in ROSTER[:context_limit])
        assert batches["F2"] == 8500 + 100 * cells
        assert len(captured["pair_effects"]["T/S(F2,all)"]) == 16
        if context_limit:
            assert set(captured["pair_effects"]["T/S(F2)"]) == set(
                ROSTER[:context_limit]
            )
            assert captured["contrasts"]["T/S(F2)"]["pooled"]["df"] == context_limit - 2
    else:
        assert "F2" not in batches and not r.context_starts
        assert json.loads((tmp_path / "f2_scores.json").read_text()) == []
