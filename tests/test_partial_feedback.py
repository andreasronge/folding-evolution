"""Feedback scientific invariants beyond the reused 1831 collector tests."""

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape.comparison_gate_bank import TRAINING, digest
from experiments.chem_tape.partial_feedback_run import (
    ARMS,
    BASE,
    Runner,
    check_replay,
    replay_source,
    roster,
    source_fingerprint,
)
from experiments.chem_tape.partial_feedback_report import make_report, route
from experiments.chem_tape.solver_corpus_fit import (
    fit,
    partial_transition_counts,
    validate_table,
)
from tests.test_partial_program import partial_source


def test_pooled_source_weights_not_equal_rounds_and_empty_round_retains():
    first = [partial_source("a", 1, 1, 24)]
    second = [partial_source("a", 2, 2, 8), partial_source("a", 3, 2, 8)]
    n, yields = partial_transition_counts(first + second, ["a"], "S")
    assert yields == {"a": 3}
    assert n[:, 2].sum() == pytest.approx(2 * n[:, 1].sum())
    empty = dict(partial_source("a", 4, 3, 1), archive=[])
    pooled, _ = partial_transition_counts(first + second + [empty], ["a"], "S")
    np.testing.assert_array_equal(n, pooled)
    with pytest.raises(ValueError, match="empty partial"):
        partial_transition_counts([empty], ["a"], "S")
    bad = deepcopy(first)
    bad[0].update(solved=True, evaluations=16384)
    with pytest.raises(ValueError, match="provenance"):
        partial_transition_counts(bad, ["a"], "S")


def test_full_roster_allocation_pairing_and_disjoint_seeds():
    full = roster()
    assert len(full) == 2048 + 12288 + 6144
    assert sum(r["phase"] == "training" for r in full) == 6144
    for tid in {r["corpus"] for r in full}:
        for c in TRAINING[tid[:2]]:
            for a in ("F", "TF", "O"):
                assert (
                    sum(
                        r["corpus"] == tid
                        and r["cell"] == c
                        and (r["round"] == 1 or r["round"] in (2, 3) and r["arm"] == a)
                        for r in full
                    )
                    == 96
                )
    smoke = roster(BASE + 100000000, 1, 4, 4)
    assert not {r["seed"] for r in full if r["round"] != 1} & {
        r["seed"] for r in smoke if r["round"] != 1
    }
    assert not {r["seed"] for r in full if r["phase"] == "collection"} & {
        r["seed"] for r in full if r["phase"] == "training"
    }


def test_manifest_and_replay_reject_changed_archive_or_fit():
    saved = replay_source()
    assert len(saved["corpora"]) == 16
    assert all(len(c["sources"]) == 128 for c in saved["corpora"].values())
    row = partial_source("a", 1, 1, 8)
    n, _ = partial_transition_counts([row], ["a"], "S")
    fitted, _ = fit(n)
    expected = dict(
        sources={"1": source_fingerprint(row)},
        counts_hash=digest(n.tolist()),
        tables={a: validate_table(fitted[a]) for a in ("C", "T")},
    )
    assert check_replay([row], n, fitted, expected)["passed"]
    row["seconds"] = 99
    assert check_replay([row], n, fitted, expected)["passed"]
    bad = deepcopy(row)
    bad["archive"][0]["tape"][0] = 2
    with pytest.raises(ValueError, match="archive replay"):
        check_replay([bad], n, fitted, expected)
    with pytest.raises(ValueError, match="table replay"):
        check_replay([row], n + 1, fitted, expected)


def test_payload_uses_updated_source_not_O_fit(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(
        SimpleNamespace(smoke=True, workers=10, deadline_seconds=1800, omit_exact=False)
    )
    first = next(r for r in runner.schedule if r["round"] == 1)
    assert set(runner.envelope(first)[0][0]) == {"id", "labels"}
    tid = first["corpus"]
    from experiments.chem_tape.four_reducer_maps import tables

    C = tables()["G4"].copy()
    C[0, 0] += 1
    runner.corpora[tid] = dict(
        tables={a: C.tolist() for a in ("F", "TF", "O")},
        rounds={"1": {a: dict(table=C.tolist()) for a in ("F", "TF")}},
    )
    for a in ("F", "TF", "O"):
        row = next(
            r
            for r in runner.schedule
            if r["round"] == 2 and r["corpus"] == tid and r["arm"] == a
        )
        job, meta = runner.envelope(row)
        np.testing.assert_array_equal(job[2], runner.g4 if a == "O" else C)
        assert meta["round"] == 2


def test_decision_precedence_and_complete_lineage_only_endpoint():
    def stat(point, lo, hi):
        return dict(speed_ratio=point, interval_95=[lo, hi])

    assert route(stat(0.8, 0.7, 0.9), True)["label"] == "degradation"
    assert route(stat(1.08, 1.02, 1.12), True)["label"] == "small_gain"
    assert route(stat(1.2, 1.02, 1.4), True)["label"] == "adopt_feedback"
    assert not route(stat(1.2, 1.02, 1.4), True)["worthwhile_established"]
    assert route(stat(1.3, 1.2, 1.4), True)["worthwhile_established"]
    assert route(stat(1.1, 1.01, 1.3), True)["label"] == "resolved_small_estimate"
    assert route(stat(1.1, 0.9, 1.3), True)["label"] == "unresolved"
    cfg = dict(
        arms=list(ARMS),
        fresh_n=2,
        workers=10,
        smoke_only=False,
        method_hash="x",
        method=dict(scope="training"),
    )
    rows = []
    for k in range(8):
        for f, cells in TRAINING.items():
            for c in cells:
                for s in range(2):
                    for a in ARMS:
                        rows.append(
                            dict(
                                phase="training",
                                round=4,
                                family=f,
                                corpus=f"{f}{k + 1}",
                                cell=c,
                                seed=s,
                                arm=a,
                                cap=524288,
                                solved=True,
                                evaluations=1024 if a == "F" else 2048,
                                seconds=1,
                                worker_seconds=1,
                            )
                        )
    report = make_report(rows, {}, cfg, 8, None, None, {})
    assert report["sensitivities"]["unsolved_2x_cap"]["F/O"]["n"] == 16
    assert report["sensitivities"]["unsolved_2x_cap"]["F/O"][
        "speed_ratio"
    ] == pytest.approx(2)
    assert report["outcome"]["label"] == "adopt_feedback"
    assert (
        make_report(rows, {}, cfg, 7, "timeout", "x", {})["outcome"]["label"]
        == "incomplete"
    )
    with pytest.raises(ValueError, match="unpaired"):
        make_report(rows[1:], {}, cfg, 8, None, None, {})
