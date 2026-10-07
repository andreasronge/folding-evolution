"""1924 scientific invariants: admission, pairing, fallback replication and outcomes."""

from types import SimpleNamespace

import pytest

from experiments.chem_tape.crossed_learning_run import TRAINING, HOLDOUTS
from experiments.chem_tape.solver_corpus_fit import seed_for, BASE
from experiments.chem_tape.solver_feedback_run import (
    Runner,
    admit_control,
    frozen_parents,
    OWNER_WORK_CUTOFF,
)
from experiments.chem_tape.solver_feedback_report import (
    contrast,
    outcome,
    holdout_label,
    make_report,
)


def test_fixed_admission_and_disjoint_outcomes():
    assert admit_control(125.01, 100) == 16
    assert admit_control(125, 100) == 8
    assert admit_control(62.5, 100) == 0
    yes = dict(interval_95=[1.01, 1.3])
    bound = dict(interval_95=[0.9, 1.09])
    harm = dict(interval_95=[0.7, 0.99])
    wide = dict(interval_95=[0.9, 1.10])
    assert outcome(yes, yes, True)["row"] == 1
    assert outcome(yes, None, True)["row"] == 2
    assert outcome(yes, wide, True)["row"] == 2
    assert outcome(bound, yes, True)["row"] == 3
    assert outcome(harm, yes, True)["row"] == 4
    assert outcome(wide, yes, True)["row"] == 5
    assert outcome(yes, yes, False)["row"] == 0
    assert holdout_label(yes) == "transfers"
    assert holdout_label(harm) == "harms withheld cells"
    assert holdout_label(bound) == "no transfer above 10%"
    assert holdout_label(wide) == "unresolved"
    assert holdout_label(None) == "unresolved"


def test_portable_artifacts_and_full_roster(tmp_path, monkeypatch):
    parents, replay, tapes, provenance = frozen_parents()
    assert len(parents) == 32 and len(replay) == 40 and len(tapes) == 7408
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    r = Runner(
        SimpleNamespace(
            workers=10,
            deadline_seconds=6000,
            work_cutoff=OWNER_WORK_CUTOFF,
            smoke=False,
        )
    )
    for tid, parent in parents.items():
        r.corpora[tid] = dict(
            family=parent["family"],
            index=parent["index"],
            C=parent["table"],
            C2=dict(tables=dict(C=parent["table"])),
            Cprime=dict(tables=dict(C=parent["table"])),
        )
    train, hold = r.evaluation_jobs(), r.evaluation_jobs(holdout=True)
    assert len(train) == 10240 and len(hold) == 6144
    r.admission["roster"] = [f"{f}{k + 1}" for f in TRAINING for k in range(16)]
    assert len(r.evaluation_jobs(control=True)) == 5120
    assert len(r.evaluation_jobs(control=True, holdout=True)) == 3072
    r.admission["roster"] = [f"{f}{k + 1}" for f in TRAINING for k in range(8)]
    ct = r.evaluation_jobs(control=True)
    assert len(ct) == 2560
    keys = {(j[0]["id"], m["corpus"], j[3]) for j, m, _ in train}
    assert all((j[0]["id"], m["corpus"], j[3]) in keys for j, m, _ in ct)
    old = {
        seed_for(p, f, k, c, s)
        for p in range(6)
        for f in TRAINING
        for k in range(16)
        for c in range(6)
        for s in range(128)
    }
    blocks = [
        {
            seed_for(p, f, k, c, s)
            for f in TRAINING
            for k in range(16)
            for c in range(len(TRAINING[f]) if p in (10, 11, 13) else 3)
            for s in range(48 if p in (10, 13) else 32)
        }
        for p in range(10, 14)
    ]
    assert list(map(len, blocks)) == [7680, 5120, 3072, 7680]
    assert all(not a & old for a in blocks)
    assert all(not a & b for i, a in enumerate(blocks) for b in blocks[i + 1 :])
    assert not set.union(*blocks) & set(range(19240000, 19350000))
    smoke = {
        seed_for(p, f, k, c, s, BASE + 300000000)
        for p in range(10, 14)
        for f in TRAINING
        for k in range(1)
        for c in range(6)
        for s in range(8)
    }
    assert not set.union(*blocks) & smoke
    assert all(set(j[0]) == {"id", "labels"} for j, m, _ in train + hold)
    with pytest.raises(ValueError, match="leakage"):
        r.envelope("collection_C", "BE", "BE1", HOLDOUTS["BE"][0], "C", r.g4, 1, True)


def synthetic(n=16):
    rows, corpora = [], {}
    for family in TRAINING:
        for k in range(n):
            tid = f"{family}{k + 1}"
            corpora[tid] = dict(family=family, index=k)
            for phase, cells in [
                ("training", TRAINING[family]),
                ("holdout", sum(HOLDOUTS.values(), [])),
            ]:
                for c, cid in enumerate(cells):
                    for arm in ("C2", "C", "Cprime"):
                        # Unequal numbers of cells and family shifts test mean ordering.
                        evaluations = 256 * 2 ** (k % 3 + c + (1 if arm == "C" else 0))
                        rows.append(
                            dict(
                                phase=phase,
                                corpus=tid,
                                family=family,
                                cell=cid,
                                arm=arm,
                                seed=1000 + k * 20 + c,
                                training_indices=[1, 2],
                                solved=True,
                                evaluations=evaluations,
                                cap=524288,
                                seconds=1,
                            )
                        )
    return rows, corpora


def test_fixed_subset_df_and_pairing():
    rows, corpora = synthetic()
    full = list(corpora)
    half = [tid for tid, tr in corpora.items() if tr["index"] < 8]
    for roster, df in [(full, 15), (half, 7)]:
        estimate = contrast(rows, corpora, roster, "training", "C2", "C", 1)
        assert estimate["pooled"]["df"] == df
        assert estimate["pooled"]["speed_ratio"] == 2
        assert all(v["n"] == df + 1 for v in estimate["families"].values())
        hold = contrast(rows, corpora, roster, "holdout", "C2", "Cprime", 1)
        assert hold["df"] == 2 * (df + 1) - 1
        assert hold["speed_ratio"] == 1
    partial = [r for r in rows if not (r["corpus"] == "PA8" and r["arm"] == "Cprime")]
    with pytest.raises(ValueError, match="incomplete"):
        contrast(partial, corpora, half, "training", "C2", "Cprime", 1)
    duplicate = rows + [rows[0]]
    with pytest.raises(ValueError, match="duplicate"):
        contrast(duplicate, corpora, full, "training", "C2", "C", 1)
    rows[0]["training_indices"] = [3]
    with pytest.raises(ValueError, match="unpaired"):
        contrast(rows, corpora, full, "training", "C2", "C", 1)


def test_incomplete_primary_cannot_claim():
    report = make_report(
        [],
        {},
        dict(roster=[], fresh_n=32, smoke_only=False),
        dict(
            A=False,
            B=False,
            C=False,
            D_collection=False,
            D_training=False,
            D_holdout=False,
        ),
        dict(passed=False),
        dict(roster=[]),
        True,
        "deadline",
        None,
    )
    assert report["outcome"]["row"] == 0
    assert not report["source_attributed_transfer"]
    assert all(v == "unresolved" for v in report["holdout"].values())


def test_control_failure_and_phase_completion_do_not_shrink_inference():
    from experiments.chem_tape.four_reducer_maps import tables

    rows, corpora = synthetic(8)
    for tr in corpora.values():
        tr["C"] = tables()["G4"].tolist()
        tr["C2"] = dict(
            tables=dict(C=tr["C"]),
            collection_evaluations=100,
            collection_seconds=1,
            fit_seconds=0.1,
        )
    cfg = dict(roster=list(corpora), fresh_n=1, smoke_only=False)
    done = dict(
        A=True, B=True, C=True, D_collection=True, D_training=True, D_holdout=False
    )
    admission = dict(roster=list(corpora))
    # Complete training control remains usable after holdout timeout.
    result = make_report(
        rows,
        corpora,
        cfg,
        done,
        dict(passed=True),
        admission,
        True,
        None,
        "TimeoutError",
    )
    assert result["contrasts"]["training"]["C2/Cprime"]["pooled"]["df"] == 7
    assert "C2/Cprime" not in result["contrasts"]["holdout"]
    assert result["holdout"]["C2/Cprime"] == "unresolved"
    assert not result["source_attributed_transfer"]
    # A control scientific validation failure removes both source contrasts,
    # while retaining the valid complete primary.
    result = make_report(
        rows,
        corpora,
        cfg,
        done,
        dict(passed=True),
        admission,
        False,
        None,
        "ValueError",
    )
    assert result["outcome"]["row"] == 2
    assert set(result["contrasts"]["training"]) == {"C2/C"}
    assert set(result["contrasts"]["holdout"]) == {"C2/C"}
