"""2129 fixed-roster crossing, interaction direction and scope gates."""

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
        SimpleNamespace(smoke=False, preflight=False, workers=10, deadline_seconds=2520)
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
