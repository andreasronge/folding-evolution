"""0652 frozen controls, admission fallback and paired realization weights."""

import copy
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape import tree_uniform as uniform
from experiments.chem_tape import tree_uniform_run as run
from experiments.chem_tape import tree_uniform_report as report
from experiments.chem_tape import tree_permutation as permutation
from experiments.chem_tape.comparison_gate_bank import digest


def test_uniform_grammar_invariants_and_replay():
    libs = run.snapshot("libraries.json")
    for lib in libs:
        for r in range(3):
            s = uniform.seed("construction", lib["build"], r)
            entries, _ = uniform.relabel(lib["entries"], s)
            assert entries == uniform.relabel(lib["entries"], s)[0]
            assert (
                permutation.signature(entries)["skeletons"]
                == permutation.signature(lib["entries"])["skeletons"]
            )
            assert len(entries) == len(lib["entries"])
            # Independently check each slot against the complete grammar.
            for before, after in zip(lib["entries"], entries):
                for a, b in zip(before["prefix"], after["prefix"]):
                    assert (
                        b
                        in uniform.CLASSES[
                            permutation.ARITY[a], len(permutation.TOKENS[a])
                        ]
                    )
    terminals = [
        dict(prefix=[op], nodes=1, compiled_length=len(permutation.TOKENS[op]))
        for op in range(9)
    ] * 1000
    entries, _ = uniform.relabel(terminals, uniform.seed("unit-check"))
    counts = np.bincount([e["prefix"][0] for e in entries], minlength=9)
    # In particular ANY must be sampled, and labels of either width stay uniform.
    assert np.all((counts[:5] > 700) & (counts[:5] < 1300))
    assert np.all((counts[5:9] > 700) & (counts[5:9] < 1300))


def test_full_seed_grid_and_explicit_fallback():
    bank = run.prior_run.snapshot("bank.json")
    schedule = run.schedules(bank)
    assert run.seed_audit(schedule)["admitted"]
    assert len(schedule["stage"]) == 288
    assert len(schedule["score"]) == 8640
    damaged = copy.deepcopy(schedule)
    damaged["score"][0]["seeds"][0] += 1
    assert not run.seed_audit(damaged)["admitted"]
    for n, arms, count in ((6, run.ARMS[:-1], 6912), (4, run.ARMS[:-1], 4608)):
        selected = run.schedules(bank, n, arms)
        assert len(selected["score"]) == count
        assert {m["realization"] for m in selected["score"]} == {0, 1, 2}
        common = {
            (m["build"], m["cell"], m["repeat"], m["arm"]): m for m in schedule["score"]
        }
        assert all(
            m == common[m["build"], m["cell"], m["repeat"], m["arm"]]
            for m in selected["score"]
        )
    with pytest.raises(ValueError, match="fallback"):
        run.schedules(bank, 4, run.ARMS)


@pytest.mark.parametrize(
    "seconds,n,arms,admit",
    [(6, 6, 5, True), (12, 6, 4, True), (20, 4, 4, True), (40, 4, 4, False)],
)
def test_runtime_gate_orders_fallback_and_stops(seconds, n, arms, admit):
    rows = [
        dict(
            build=b,
            realization=r,
            worker_seconds=seconds,
            solved=True,
            evaluations=1024,
            cap=524288,
            attempt_count=1,
        )
        for b in range(24)
        for r in range(3)
        for _ in range(4)
    ]
    gate = run.stage_gate(
        rows,
        dict(worker_seconds=seconds * 288, wall_seconds=seconds * 288 / 10),
        run.snapshot("replay.jsonl"),
    )
    assert (gate["repeats"], len(gate["active_arms"]), gate["admitted"]) == (
        n,
        arms,
        admit,
    )
    assert gate["realizations"] == 3
    assert len(gate["per_construction"]) == 72


def stat(x, low=None, high=None):
    return dict(
        point=x, interval95=[x if low is None else low, x if high is None else high]
    )


def test_decision_boundaries_and_intact_cannot_be_chained():
    guards = dict(R_lib=stat(0.35), R_perm=stat(0.36))
    assert "retains_acquired" in report.classify(
        stat(1), stat(1), stat(0.4), stat(0), guards
    )
    assert (
        report.classify(stat(1), stat(1.2, 0.8, 1.3), stat(0.4), stat(0), guards)
        == "matches_R_perm_relation_to_intact_unresolved"
    )
    assert "unresolved_price" in report.classify(
        stat(1.1, 0.9, 1.25), stat(1), stat(0.4), stat(0), guards
    )
    assert "unresolved_price" in report.classify(
        stat(1), stat(1), stat(0.8), stat(0), guards
    )
    assert "unresolved_price" in report.classify(
        stat(1), stat(1), stat(0.4), stat(-0.03), guards
    )
    assert "worthwhile" in report.classify(
        stat(1.25, 1.11, 1.4), stat(2), stat(0.8), stat(-0.1), guards
    )
    assert "validity_failed" in report.classify(
        stat(2), stat(2), stat(0.8), stat(0), dict(R_lib=stat(0.6), R_perm=stat(0.35))
    )


@pytest.mark.parametrize(
    "n,arms", [(6, run.ARMS), (6, run.ARMS[:-1]), (4, run.ARMS[:-1])]
)
def test_equal_realizations_paired_intervals_and_reporting(
    tmp_path, monkeypatch, n, arms
):
    monkeypatch.setattr(report, "DRAWS", 128)
    bank = run.prior_run.snapshot("bank.json")
    rows = []
    # Deliberately heterogeneous paired construction cost. First realization's
    # two repeats cancel; singleton realizations keep equal weight with n=4.
    for m in run.schedules(bank, n, arms)["score"]:
        factor = 1 if m["arm"] in ("R-tree", "R-size") else 0.35
        base = 1000 * (m["build"] + 1) * (1, 3, 7)[m["realization"]]
        if m["arm"] == "R-unif":
            factor *= 0.5 if m["repeat"] == 0 else 1.5 if m["repeat"] == 3 else 1
        rows.append(
            m
            | dict(
                evaluations=base * factor,
                worker_seconds=base * factor / 1000,
                solved=True,
                attempt_count=1,
                attempts=[
                    dict(
                        operator=dict(mutation=2, library_draws=1, library_insertions=1)
                    )
                ],
            )
        )
    libs = run.snapshot("libraries.json")
    for lib in libs:
        lib["uniform_constructions"] = [
            dict(entries=lib["entries"], construction_seconds=0.1)
        ] * 3
    prep = dict(
        stage_gate=dict(repeats=n, active_arms=list(arms)),
        construction_audit={},
        preparation_hash="synthetic",
    )
    result = report.summarize(rows, libs, bank, prep)
    assert result["primary"]["interval95"] == pytest.approx([1, 1])
    assert result["groups"]["B/C"]["means"]["evaluations"]["R-lib"][
        "point"
    ] == pytest.approx(1000 * 12.5 * 11 / 3 * 0.35)
    assert (
        result["economics"]["B/C"]["evaluations"]["R-unif"]["acquisition"]["point"]
        == 2880000
    )
    assert "retains_acquired" in result["decision"]
    report.report(tmp_path, rows, libs, bank, prep, {})
    assert all(
        (tmp_path / f).stat().st_size
        for f in ("result.json", "report.md", "dynamics.png", "economics.png")
    )
    with pytest.raises(ValueError, match="complete"):
        report.summarize(rows[:-1], libs, bank, prep)
    damaged = copy.deepcopy(rows)
    damaged[0]["realization"] = 4
    with pytest.raises(ValueError, match="assignment"):
        report.summarize(damaged, libs, bank, prep)


def test_smoke_never_authorizes_scoring(tmp_path):
    from experiments.chem_tape.composition_run import write_json

    runner = run.Runner.__new__(run.Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path))
    write_json(tmp_path, "preparation.json", dict(admitted=False, smoke=True))
    with pytest.raises(ValueError, match="admitted production"):
        runner.score()


def test_archived_0524_constructions_match_reconstruction():
    for lib in run.snapshot("libraries.json"):
        for c in lib["constructions"]:
            entries, _ = permutation.permute(
                lib["entries"],
                permutation.seed("construction", lib["build"], c["realization"]),
            )
            assert digest(entries) == digest(c["entries"])


def test_all_arm_routes_keep_exact_frozen_donors():
    saved, _ = run.load_saved()
    bank = run.prior_run.snapshot("bank.json")
    saved["banks.json"]["GS"] = bank
    libs = run.snapshot("libraries.json")
    uniform_entries, _ = uniform.relabel(
        libs[0]["entries"], uniform.seed("construction", 0, 2)
    )
    libs[0]["uniform_constructions"] = [dict(entries=uniform_entries)] * 3
    meta = dict(
        family="GS",
        cell=run.score_cells(bank)[0],
        build=0,
        repeat=2,
        realization=2,
        seeds=[uniform.seed("unit-engine", k) for k in range(8)],
    )
    expected = {
        "R-tree": None,
        "R-lib": libs[0]["entries"],
        "R-size": libs[0]["controls"],
        "R-perm": libs[0]["constructions"][2]["entries"],
        "R-unif": uniform_entries,
    }
    for arm, entries in expected.items():
        envelope = run.envelope(meta | dict(arm=arm), saved, libs, 1024)
        assert envelope["meta"]["arm"] == arm
        assert (
            envelope["donors"] is None
            if entries is None
            else [list(t.prefix) for t in envelope["donors"]]
            == [e["prefix"] for e in entries]
        )
    with pytest.raises(ValueError, match="unknown"):
        run.envelope(meta | dict(arm="R-other"), saved, libs, 1024)
