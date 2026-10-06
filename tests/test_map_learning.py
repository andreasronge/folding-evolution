"""Scientific invariants for PA map learning and censored paired inference."""

import numpy as np
import pytest

from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.map_learning import (
    BOUND,
    initial,
    log_cost,
    mutate,
    normalize,
    schedule_projection,
    table_for,
)
from experiments.chem_tape.map_learning_report import (
    classify,
    contrast,
    make_report,
    outcome,
)
from experiments.chem_tape.map_learning_run import Runner, load_bank


def test_starts_are_exact_and_restricted_maps_have_correct_context():
    controls = frozen_controls()
    for a in ("C", "M", "T"):
        start = initial(a, controls)
        table = table_for(a, start, controls)
        assert np.array_equal(table, controls["G-marg" if a == "T" else "G"])
        rng = np.random.default_rng(52)
        for _ in range(100):
            vector, mutation = mutate(start, start, rng)
            assert len(set(mutation["coordinates"])) == 3
            assert np.count_nonzero(vector != start) == 3
            table = table_for(a, vector, controls)
            Decoder(table)
            assert np.diff(table, prepend=0, axis=1).min() >= 250
            assert Decoder(table).tied == (a == "T")
        with pytest.raises(ValueError):
            table_for(a, start + BOUND + 0.001, controls)


def test_support_enforcement_with_extreme_imbalances_and_stable_rounding():
    w = np.full((24, 23), 1e-30)
    w[:, 0] = 1e30
    counts = np.diff(normalize(w), prepend=0, axis=1)
    assert np.all(counts[:, 1:] == 250)
    assert np.all(counts[:, 0] == 17500)
    assert np.all(normalize(np.ones((24, 23))) == np.arange(1, 24) * 1000)
    controls = frozen_controls()
    for a in ("C", "M", "T"):
        start = initial(a, controls)
        vector = start + np.where(np.arange(len(start)) % 2, BOUND, -BOUND)
        assert np.diff(table_for(a, vector, controls), prepend=0, axis=1).min() >= 250


def test_bank_is_verified_and_canonicals_do_not_enter_search_cells():
    bank = load_bank()
    assert len(bank["split"]["training"]) == 6
    assert bank["split"]["holdouts"] == ["PA:(S?M:S)+M", "PA:(S?M:S)+m"]


def test_cost_derivation_censors_solutions_past_training_cap():
    assert log_cost(dict(solved=True, evaluations=131072), 65536) == 17
    assert log_cost(dict(solved=False, evaluations=524288), 524288) == 20
    assert log_cost(dict(solved=True, evaluations=32768), 65536) == 15


def test_matched_trajectory_and_frozen_control_bootstrap():
    rows = []
    for k in range(6):
        for seed in range(10):
            # Each trajectory has a large common offset, canceled only by
            # paired block draws. Seeds also share a large common offset.
            for a, extra in [("C", 0), ("M", 1)]:
                rows.append(
                    dict(
                        arm=f"{a}{k + 1}",
                        cell="hold",
                        seed=seed,
                        solved=True,
                        evaluations=2 ** (9 + k + seed % 3 + extra),
                    )
                )
    ids_c = [f"C{k + 1}" for k in range(6)]
    ids_m = [f"M{k + 1}" for k in range(6)]
    result = contrast(rows, ids_c, ids_m, ["hold"], replicates=1000)
    assert result["ratio"] == 2
    assert result["interval_95"] == [2, 2]
    for seed in range(10):
        rows.append(
            dict(
                arm="G",
                cell="hold",
                seed=seed,
                solved=True,
                evaluations=2 ** (13 + seed % 3),
            )
        )
    expected = contrast(rows, ids_c, ["G"], ["hold"], replicates=1000)
    assert expected["ratio"] == pytest.approx(2**1.5)
    assert expected["interval_95"][0] < expected["ratio"] < expected["interval_95"][1]
    with pytest.raises(ValueError, match="unpaired"):
        contrast(rows[:-1], ids_c, ["G"], ["hold"], replicates=20)


def test_unresolved_training_and_incomplete_study_never_become_negative():
    assert classify([0.9, 1.6]) == "unresolved"
    assert classify([1.01, 1.1]) == "faster"
    assert outcome({"training524:C/G": dict(classification="unresolved")})["row"] == 5
    result = make_report(
        [],
        dict(training=["a"], holdouts=["b", "c"]),
        dict(trajectories=dict(C=6, M=6, T=6)),
        False,
    )
    assert not result["complete"] and result["outcome"] is None
    assert "C6" in result["missing_map_ids"]


def test_seed_bootstrap_is_joint_even_with_four_T_trajectories():
    rows = []
    for seed in range(20):
        for a, n in [("C", 6), ("T", 4), ("G", 1)]:
            for k in range(n):
                rows.append(
                    dict(
                        arm=f"{a}{k + 1}" if a != "G" else a,
                        cell="hold",
                        seed=seed,
                        solved=True,
                        evaluations=2 ** (10 + (seed % 5 if a == "G" else 0)),
                    )
                )
    c = contrast(rows, [f"C{k + 1}" for k in range(6)], ["G"], ["hold"], replicates=500)
    t = contrast(rows, [f"T{k + 1}" for k in range(4)], ["G"], ["hold"], replicates=500)
    assert c["ratio"] == t["ratio"]
    assert c["interval_95"] == t["interval_95"]


def test_runtime_gate_drops_sampling_before_learning_and_refuses_overbudget():
    rates = {a: dict(train=1.0, test500=500.0) for a in ("C", "M", "T", "G-marg")}
    rates.update(U=dict(holdout200=1000), F=dict(holdout200=1000))
    decision = schedule_projection(
        rates, workers=10, elapsed=600, marginal_seconds=1, sample_seconds=10000
    )
    assert decision["feasible"]
    assert not decision["selected"]["sampling"]
    assert decision["selected"]["trajectories"] == dict(C=6, M=6, T=6)
    assert decision["selected"]["generations"] == 25
    rates["T"]["train"] = 100
    decision = schedule_projection(
        rates, workers=10, elapsed=600, marginal_seconds=1, sample_seconds=10000
    )
    assert not decision["feasible"] and decision["selected"] is None


def test_reservation_stops_before_starting_a_trajectory_and_reports_missing_ids(
    tmp_path, monkeypatch
):
    import json
    from types import SimpleNamespace
    import experiments.chem_tape.map_learning_run as module

    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(SimpleNamespace(smoke=False, workers=10, deadline_seconds=600))
    fake_pool = SimpleNamespace(terminate=lambda: None, join=lambda: None)
    monkeypatch.setattr(
        module.mp, "get_context", lambda *_: SimpleNamespace(Pool=lambda *_: fake_pool)
    )
    schedule = dict(
        trajectories=dict(C=6, M=6, T=6),
        generations=25,
        sampling=False,
        learning_seconds=dict(C=6000, M=6000, T=6000),
        test_seconds={"C": 300, "M": 300, "T": 300, "C-marg": 300},
    )
    monkeypatch.setattr(
        runner,
        "calibration",
        lambda: dict(projection=dict(selected=schedule), marginal_seconds=1),
    )
    monkeypatch.setattr(runner, "evaluate", lambda *_: None)
    monkeypatch.setattr(runner, "searches", lambda *_: ([], 0))
    monkeypatch.setattr(module, "plots", lambda *_: None)

    def forbidden(*_args, **_kwargs):
        pytest.fail(
            "A trajectory must not start when its evaluation time cannot be reserved"
        )

    monkeypatch.setattr(runner, "evolve", forbidden)
    runner.run()
    result = json.loads((tmp_path / "result.json").read_text())
    assert not result["complete"] and result["outcome"] is None
    assert "C1" in result["missing_map_ids"] and "T6" in result["missing_map_ids"]
    assert "reserved time" in result["stop_reason"]
