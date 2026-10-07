"""Saved-roster crossing, interaction direction and 2156 timing admission."""

import datetime as dt
import json

from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape.context_increment_run import (
    Runner,
    frozen_sources,
    expected_rows,
    timing_admission,
)
from experiments.chem_tape.context_increment_report import (
    outcome,
    phase_report,
    make_report,
)


def test_saved_sources_and_exact_training_holdout_roster(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    r = Runner(
        SimpleNamespace(smoke=False, preflight=False, workers=10, deadline_seconds=4500)
    )
    full = r.evaluation_jobs()
    block = r.evaluation_jobs(timing=True)
    assert len(full) == 10080 and len(block) == 160
    assert len(r.evaluation_jobs("holdout")) == 6144
    assert {m["family"] for j, m, s in block} == {"BE", "PA"}
    keys = {(m["corpus"], j[0]["id"], j[1], j[3]) for j, m, s in full + block}
    assert len(keys) == 10240
    assert all(
        j[4:6] == (524288, 256) and set(j[0]) == {"id", "labels"}
        for j, m, s in full + block
    )
    assert not set((m["corpus"], j[0]["id"], j[1], j[3]) for j, m, s in full) & set(
        (m["corpus"], j[0]["id"], j[1], j[3]) for j, m, s in block
    )
    assert timing_admission(125.001, 100)
    assert not timing_admission(125, 100)
    assert not timing_admission(-1, 0)
    assert len(r.saved_rows) == 16384
    assert r.config["queue_timeout_seconds"] == 4500
    assert r.config["reporting_reserve_seconds"] == 300
    assert "work_cutoff" not in r.config and "autonomous_deadline" not in r.config


def test_holdout_gate_uses_full_primary_cost_and_queue_elapsed(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    started = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=600)
    (tmp_path / "metadata.json").write_text(json.dumps(dict(started_at=started.isoformat())))
    r = Runner(SimpleNamespace(smoke=False, preflight=False, workers=10, deadline_seconds=4500))
    assert r.config["clock_source"] == "run_queue metadata.started_at"
    r.rows = [
        dict(phase=phase, family=f, arm=arm, seconds=seconds)
        for phase, f, arm, seconds in [
            ("training", "BE", "T1", 2), ("training", "PA", "T1", 2),
            ("training", "BE", "T2", 3), ("training", "PA", "T2", 1),
            # Neither holdout timing nor solve rates belong in admission.
            ("holdout", "BE", "T2", 100000),
        ]
    ]
    r.timings = dict(
        timing=dict(worker_seconds=80, wall_seconds=20, rows=160),
        training=dict(worker_seconds=920, wall_seconds=80, rows=10080),
    )
    gate = r.projection()
    assert gate["primary_timing"]["rows"] == 10240
    assert gate["effective_workers"] == 10
    assert gate["primary_mean_worker_seconds"] == dict(T1=2, BE=3, PA=1)
    assert gate["holdout_training_inflation"] == 1
    assert gate["projected_worker_seconds"] == 12288
    assert gate["projected_seconds"] == pytest.approx(1228.8)
    assert gate["elapsed_since_queue_start_seconds"] >= 600
    assert 3590 < gate["remaining_seconds"] <= 3600
    assert gate["admitted"]
    # Primary used too much time: same scientific roster, whole holdout skipped.
    r.work_deadline -= 2200
    assert not r.projection()["admitted"]


def test_primary_snapshot_precedes_holdout_even_if_block_is_slow(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    r = Runner(SimpleNamespace(smoke=True, preflight=False, workers=1, deadline_seconds=600))
    training, _, _ = synthetic("training")
    keys = set(expected_rows(r.corpora, r.roster, "training", ("T1", "T2"), 2))
    r.rows = [row for row in training if tuple(row[k] for k in
              ("phase", "family", "corpus", "cell", "arm", "seed")) in keys]

    class Pool:
        def terminate(self):
            pass

        def join(self):
            pass

    monkeypatch.setattr("experiments.chem_tape.context_increment_run.mp.get_context",
                        lambda _: SimpleNamespace(Pool=lambda _: Pool()))
    monkeypatch.setattr(r, "replay_sources", lambda: r.complete.update(replay=True))
    stages = []

    def jobs(_, stage):
        stages.append(stage)
        # This block would have rejected primary in 2129. Primary is unconditional.
        r.timings[stage] = dict(worker_seconds=10000, wall_seconds=1, rows=1)

    def gate():
        assert (tmp_path / "primary" / "result.json").exists()
        assert (tmp_path / "primary" / "report.md").exists()
        assert (tmp_path / "primary" / "diagnostics.png").exists()
        primary = json.loads((tmp_path / "primary" / "result.json").read_text())
        assert primary["stages"]["training"] and not primary["stages"]["holdout"]
        return dict(admitted=False)

    monkeypatch.setattr(r, "jobs", jobs)
    monkeypatch.setattr(r, "projection", gate)
    assert r.run() == 0
    assert stages == ["timing", "training"]
    assert r.complete["training"] and not r.complete["holdout"]


def synthetic(phase):
    corpora, _, _ = frozen_sources()
    roster = list(corpora)
    # C1/T1=2, C2/T2=4 => interaction=2. Family-cell offsets cancel.
    offsets = {"C1": 2, "T1": 3, "C2": 1, "T2": 3}
    rows = []
    for ph, f, tid, cid, arm, seed in expected_rows(corpora, roster, phase, offsets, 2):
        rows.append(
            dict(
                phase=ph,
                family=f,
                corpus=tid,
                cell=cid,
                arm=arm,
                seed=seed,
                cap=524288,
                pop_size=256,
                solved=True,
                evaluations=256 * 2 ** offsets[arm],
                training_indices=np.random.default_rng([seed, 0])
                .choice(1331, 64, replace=False)
                .tolist(),
                table_hash=corpora[tid]["hashes"][arm],
                initial_source_hash=corpora[tid]["hashes"][arm],
                initial_reencoded=False,
            )
        )
    return rows, corpora, dict(roster=roster, fresh_n=2, smoke_only=False)


@pytest.mark.parametrize("phase,df", [("training", 15), ("holdout", 31)])
def test_paired_difference_of_differences_and_incomplete_refusal(phase, df):
    rows, corpora, config = synthetic(phase)
    report = phase_report(rows, corpora, config, phase)
    estimate = report["interaction"].get("pooled", report["interaction"])
    assert estimate["speed_ratio"] == 2
    assert estimate["df"] == df
    assert report["outcome"]["row"] == 1
    assert report["T2/T1"].get("pooled", report["T2/T1"])["speed_ratio"] == 1
    for bad in [rows[:-1], rows + [rows[0]]]:
        with pytest.raises(ValueError, match="roster"):
            phase_report(bad, corpora, config, phase)
    rows[0]["training_indices"][0] = -1
    with pytest.raises(ValueError, match="mismatch"):
        phase_report(rows, corpora, config, phase)


def test_disjoint_outcomes_and_smoke_never_claims():
    for bounds, row in [
        ([1.01, 1.2], 1),
        ([0.8, 0.99], 2),
        ([0.92, 1.09], 3),
        ([1 / 1.1, 1.09], 4),
        ([0.95, 1.1], 4),
        ([0.8, 1.09], 4),
    ]:
        assert outcome(dict(interval_95=bounds))["row"] == row
    assert outcome(dict(interval_95=[1.1, 1.2]), False)["row"] == 0
    rows, corpora, config = synthetic("training")
    config["smoke_only"] = True
    report = make_report(
        rows,
        corpora,
        config,
        dict(training=True, holdout=False),
        dict(passed=True),
        {},
        None,
    )
    assert report["outcome"]["row"] == 0 and report["transfer"] == "unresolved"
    report = make_report(
        rows[:-1],
        corpora,
        config,
        dict(training=False, holdout=False),
        dict(passed=True),
        {},
        None,
    )
    assert not report["training"] and report["outcome"]["row"] == 0
