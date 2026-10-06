"""Scientific invariants for the approved matched continuation design."""

import json
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.contextual_learning import (
    projection,
    start_vector,
    step,
    table,
)
from experiments.chem_tape.contextual_learning_run import Runner, SOURCES
from experiments.chem_tape.contextual_report import classify, contrast, outcome, report
from experiments.chem_tape.map_learning import BOUND, mutate


def test_actual_residual_operator_preserves_saved_starts_and_bounds():
    controls = frozen_controls()
    sources = json.loads(SOURCES.read_text())
    for r in sources["starts"].values():
        v = start_vector(r["vector"], "R")
        assert np.array_equal(table(v, controls), r["table"])
        child, details = step(v, np.random.default_rng(72), row_only=True)
        assert np.array_equal(child[:23], v[:23])
        changed_rows = np.flatnonzero(np.any(child[23:].reshape(24, 23) != 0, axis=1))
        assert changed_rows.tolist() == [details["row"]]
        assert np.diff(table(child, controls), prepend=0, axis=1).min() >= 250
        assert np.max(np.abs(child)) <= BOUND
        # Exactly the inherited M operator, bounded relative to G's zero
        # multipliers, rather than resetting bounds around inherited M.
        m = start_vector(r["vector"], "M+")
        expected, _ = mutate(m, np.zeros(23), np.random.default_rng(4))
        actual, _ = step(m, np.random.default_rng(4))
        np.testing.assert_array_equal(actual, expected)
    with pytest.raises(ValueError):
        table(v + BOUND * 3, controls)


def test_start_clusters_and_shared_seed_bootstrap_are_not_twelve_starts():
    rows, a, b = [], [], []
    for k in range(6):
        ga, gb = [], []
        for rep in ("a", "b"):
            ga.append(f"R{k}{rep}")
            gb.append(f"M+{k}{rep}")
            for seed in range(20):
                for arm, shift in [(ga[-1], 0), (gb[-1], 1)]:
                    rows.append(
                        dict(
                            arm=arm,
                            cell="h",
                            seed=seed,
                            solved=True,
                            evaluations=2 ** (8 + k + seed % 3 + shift),
                        )
                    )
        a.append(ga)
        b.append(gb)
    result = contrast(rows, a, b, ["h"], replicates=500)
    assert result["ratio"] == 2 and result["interval_95"] == [2, 2]
    assert result["start_clusters"] == 6
    assert result["continuations_per_start"] == [2] * 6
    # Compare a nonconstant cluster contrast with an explicitly collapsed
    # one-continuation representation: bootstrap intervals must agree.
    for r in rows:
        if r["arm"].startswith("M+"):
            r["evaluations"] *= 2 ** int(r["arm"][2])
    full = contrast(rows, a, b, ["h"], replicates=500)
    collapsed = contrast(
        rows, [[g[0]] for g in a], [[g[0]] for g in b], ["h"], replicates=500
    )
    assert full["interval_95"] == collapsed["interval_95"]
    with pytest.raises(ValueError, match="unpaired"):
        contrast(rows[:-1], a, b, ["h"], replicates=20)


def test_priority_cuts_and_failed_gate_never_schedule_learning():
    rates = {
        a: dict(train=0.45, test=0.8, off=1.14)
        for a in ("M+", "R", "R_abl", "reference")
    }
    p = projection(rates, 10, 500, 68)
    assert p["selected"]["generations"] == 35 and p["selected"]["sampling"]
    p = projection(rates, 10, 500, 10000)
    assert not p["selected"]["sampling"] and p["selected"]["off_family"]
    p = projection(rates, 10, 500, 68, False)
    assert p["selected"]["generations"] == 0
    assert p["selected"]["learning_seconds"] == p["selected"]["test_seconds"] == 0
    rates["R"]["train"] = 100
    assert not projection(rates, 10, 500, 68)["feasible"]


def test_outcome_language_and_incomplete_coverage():
    assert classify([0.9, 1.24]) == "no practical gain"
    assert classify([0.9, 1.25]) == "unresolved"
    assert classify([1.01, 1.1]) == "faster"
    contrasts = {
        f"{label}:R/M+": dict(classification="no practical gain")
        for label in ("training524", "holdout0", "holdout1")
    }
    contrasts["training524:R/R_abl"] = dict(classification="unresolved")
    assert "unresolved" in outcome(contrasts)["residual_reading"]
    result = report(
        [], dict(training=["t"], holdouts=["h1", "h2"]), [], [], 12, False, False
    )
    assert result["outcome"] is None
    assert result["coverage_by_start"] == {str(k): [] for k in range(1, 7)}


def test_complete_flag_cannot_override_missing_or_duplicated_test_seeds():
    result = report(
        [], dict(training=["t"], holdouts=["h1", "h2"]), [], [], 12, True, False
    )
    assert not result["complete"] and result["outcome"] is None
    assert result["test_counts"]["G:t"]["expected"] == 50


def test_learning_and_selection_seed_sets_match_between_arms(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(SimpleNamespace(smoke=True, workers=10, deadline_seconds=600))
    runner.schedule = dict(generations=2)
    seen = {}

    def fake_searches(tables, cells, seeds, cap, phase):
        seen[phase] = list(seeds)
        return (
            [
                dict(arm=a, cell=c, seed=s, solved=True, evaluations=256)
                for a in tables
                for c in cells
                for s in seeds
            ],
            0.1,
        )

    monkeypatch.setattr(runner, "searches", fake_searches)
    for arm in ("M+", "R"):
        runner.evolve(arm, 1, "a", 0)
    for g in (1, 2):
        assert seen[f"learn:M+1a:g{g}"] == seen[f"learn:R1a:g{g}"]
    assert seen["selection:M+1a"] == seen["selection:R1a"]
    assert not set(seen["selection:M+1a"]).intersection(seen["learn:M+1a:g1"])
    abl = runner.finals["R_abl1a"]
    np.testing.assert_array_equal(abl["vector"], runner.finals["R1a"]["vector"][:23])
    np.testing.assert_array_equal(
        abl["table"], table(np.array(abl["vector"]), runner.controls)
    )


def test_reserved_pair_and_gate_failure_routing(tmp_path, monkeypatch):
    import experiments.chem_tape.contextual_learning_run as module

    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(SimpleNamespace(smoke=False, workers=10, deadline_seconds=600))
    fake = SimpleNamespace(terminate=lambda: None, join=lambda: None)
    monkeypatch.setattr(
        module.mp, "get_context", lambda *_: SimpleNamespace(Pool=lambda *_: fake)
    )
    monkeypatch.setattr(module, "plots", lambda *_: None)
    monkeypatch.setattr(
        runner,
        "calibration",
        lambda: dict(
            harness_mismatch=False,
            contextual_gate_passed=True,
            projection=dict(
                selected=dict(
                    generations=35, pair_seconds=10000, off_family=True, sampling=True
                )
            ),
        ),
    )
    monkeypatch.setattr(runner, "evaluate", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        runner,
        "evolve",
        lambda *_: pytest.fail(
            "No partial pair may be admitted without its test reservation"
        ),
    )
    runner.run()
    result = json.loads((tmp_path / "result.json").read_text())
    assert not result["complete"] and result["outcome"] is None
    assert "reserved time" in result["stop_reason"]

    # Gate failure must keep only frozen maps and never invoke evolve.
    other = tmp_path / "gate"
    monkeypatch.setenv("RUN_DIR", str(other))
    runner = Runner(SimpleNamespace(smoke=False, workers=10, deadline_seconds=600))
    monkeypatch.setattr(
        runner,
        "calibration",
        lambda: dict(
            harness_mismatch=False,
            contextual_gate_passed=False,
            projection=dict(
                selected=dict(
                    generations=0, pair_seconds=0, off_family=False, sampling=True
                )
            ),
        ),
    )
    monkeypatch.setattr(runner, "evaluate", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        runner, "evolve", lambda *_: pytest.fail("Gate failure must not learn")
    )
    called = []
    monkeypatch.setattr(runner, "sampling", lambda names: called.extend(names) or True)
    runner.run()
    assert called == [f"M{k}" for k in range(1, 7)]
    assert json.loads((other / "result.json").read_text())["outcome"]["row"] == 0
