"""Frozen provenance, leakage, inference and incomplete-run safeguards."""

import copy
import hashlib
import json
import shutil
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape.crossed_holdout_run import (
    SOURCE,
    SOURCE_HASHES,
    Runner,
    frozen_source,
)
from experiments.chem_tape.crossed_learning_run import (
    DEFAULT_BANK,
    G4_HASH,
    HOLDOUTS,
    TRAINING,
)
from experiments.chem_tape.crossed_holdout_report import (
    estimate,
    future_sizing,
    gain_matrix,
    make_report,
    outcome,
)


@pytest.fixture(scope="module")
def source():
    return frozen_source(SOURCE)


def test_frozen_source_and_corruption(tmp_path, source, monkeypatch):
    trajectories, g4, gains, validation = source
    assert len(trajectories) == 20 and g4.shape == (25, 24)
    assert validation["passed"] and validation["actual_rows"] == 10500
    assert min(gains.values()) > 0
    shutil.copytree(SOURCE, tmp_path / "source")
    path = tmp_path / "source" / "trajectories.json"
    path.write_text(path.read_text() + " ")
    with pytest.raises(ValueError, match="SHA256"):
        frozen_source(tmp_path / "source")
    raw = json.loads(path.read_text())
    raw["BE1"]["table"][0][0] += 1
    path.write_text(json.dumps(raw))
    monkeypatch.setitem(
        SOURCE_HASHES,
        "trajectories.json",
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    with pytest.raises(ValueError, match="vector/table"):
        frozen_source(tmp_path / "source")


def runner(tmp_path, monkeypatch, smoke=False):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    return Runner(
        SimpleNamespace(
            bank=str(DEFAULT_BANK),
            source=str(SOURCE),
            workers=10,
            deadline_seconds=6300,
            smoke=smoke,
            probe=False,
        )
    )


def test_job_set_all_frozen_maps_no_training_or_learning(tmp_path, monkeypatch):
    import experiments.chem_tape.map_learning as learning
    import experiments.chem_tape.crossed_learning_run as training

    def forbidden(*_):
        pytest.fail("outer learning invoked")

    monkeypatch.setattr(learning, "mutate", forbidden)
    monkeypatch.setattr(training.Runner, "evolve", forbidden)
    r = runner(tmp_path, monkeypatch)
    jobs = [
        r.job(c, m, s) for m in r.maps for c in r.cells for s in r.config["fresh_seeds"]
    ]
    assert len(jobs) == 25200
    assert r.config["fresh_seeds"] == list(range(2229000, 2229400))
    assert r.config["learning_calls"] == 0 and not r.config["learning_permitted"]
    assert len(r.maps) == 21 and all(set(j[0]) == {"id", "labels"} for j in jobs)
    assert all(j[4:6] == (524288, 256) and len(j[6]) == 1331 for j in jobs)
    for c in sum(TRAINING.values(), []):
        with pytest.raises(ValueError, match="non-holdout"):
            r.job(c, "G4", 2229000)
    with pytest.raises(ValueError, match="non-holdout"):
        r.job(next(iter(r.cells)), "BE11", 2229000)


def synthetic(source):
    trajectories, _, training_gains, _ = source
    config = dict(
        holdouts=HOLDOUTS,
        fresh_seeds=[2229000, 2229001],
        fresh_cap=524288,
        g4_hash=G4_HASH,
        smoke_only=False,
        probe_only=False,
    )
    rows = []
    for arm in ["G4", *trajectories]:
        for cid in sum(HOLDOUTS.values(), []):
            for seed in config["fresh_seeds"]:
                # Known preference: matched maps faster, with nonzero spread.
                if arm == "G4":
                    evaluations = 262144
                else:
                    matched = cid.startswith(trajectories[arm]["family"])
                    evaluations = (100 + 5 * int(arm[2:])) * 256 * (1 if matched else 2)
                rows.append(
                    dict(
                        arm=arm,
                        cell=cid,
                        seed=seed,
                        table_hash=G4_HASH
                        if arm == "G4"
                        else trajectories[arm]["table_hash"],
                        phase="fresh_holdout",
                        cap=524288,
                        pop_size=256,
                        solved=True,
                        evaluations=evaluations,
                        training_indices=np.random.default_rng([seed, 0])
                        .choice(1331, 64, replace=False)
                        .tolist(),
                        shortcuts=0,
                        unique_shortcuts=0,
                        seconds=1,
                        curve=[],
                    )
                )
    return rows, trajectories, config, training_gains


def test_complete_and_interaction_trajectory_inference(source):
    rows, tr, config, train = synthetic(source)
    r = make_report(rows, tr, config, train)
    assert r["complete"] and r["outcome"]["row"] == "1"
    assert len(r["per_map"]) == 20 and all(len(v) == 3 for v in r["generic"].values())
    assert r["crossed"]["BE"]["ratio"] == pytest.approx(2)
    assert r["crossed"]["PA"]["ratio"] == pytest.approx(2)
    assert r["interaction"]["ratio"] == pytest.approx(4)
    assert all(
        v["useful_improvement"] and not v["via_mismatched_harm"]
        for v in r["damage"].values()
    )
    for f in HOLDOUTS:
        assert r["aggregate_gains"][f]["PA"]["interval_95"] is not None
        for tid in tr:
            if tr[tid]["family"] == f:
                assert r["per_map"][tid]["transfer_loss_log2"] == pytest.approx(
                    train[tid] - r["per_map"][tid]["aggregate_log2"][f]
                )


@pytest.mark.parametrize(
    "problem",
    ["missing", "duplicate", "extra", "hash", "phase", "cases", "cap", "unsolved"],
)
def test_validation_never_analyses_selected_subset(source, problem):
    rows, tr, config, train = synthetic(source)
    if problem == "missing":
        rows.pop()
    elif problem == "duplicate":
        rows.append(rows[0])
    elif problem == "extra":
        rows[-1]["cell"] = TRAINING["BE"][0]
    else:
        field, value = {
            "hash": ("table_hash", "wrong"),
            "phase": ("phase", "learning"),
            "cases": ("training_indices", [1, 2]),
            "cap": ("cap", 65536),
            "unsolved": ("solved", False),
        }[problem]
        rows[-1][field] = value
    r = make_report(rows, tr, config, train)
    assert not r["complete"] and r["outcome"]["row"] == "U"
    assert r["per_map"] == {} and r["crossed"] == {} and r["interaction"] is None


def test_unsolved_cost_is_cap_and_g4_gate(source):
    rows, tr, config, train = synthetic(source)
    cid = HOLDOUTS["BE"][0]
    for row in rows:
        if row["arm"] == "G4" and row["cell"] == cid:
            row.update(solved=False, evaluations=524288)
    gains, validation = gain_matrix(
        rows,
        tr,
        sum(HOLDOUTS.values(), []),
        config["fresh_seeds"],
        524288,
        G4_HASH,
        "fresh_holdout",
    )
    assert validation["passed"]
    assert gains["BE1"][cid] == pytest.approx(np.log2(524288 / (105 * 256)))
    r = make_report(rows, tr, config, train)
    assert r["complete"] and not r["g4_solve_gate"][cid]["passed"]
    assert r["outcome"]["row"] == "U"


def test_no_learning_or_map_exclusion(source):
    rows, tr, config, train = synthetic(source)
    config["learning_calls"] = 1
    assert make_report(rows, tr, config, train)["outcome"]["row"] == "U"
    config["learning_calls"] = 0
    tr = dict(tr)
    tr.pop("BE10")
    rows = [row for row in rows if row["arm"] != "BE10"]
    r = make_report(rows, tr, config, train)
    assert not r["complete"] and r["outcome"]["row"] == "U"
    assert r["crossed"] == {}


def test_reversed_small_and_unresolved_labels():
    reverse = estimate([-1.1, -1, -0.9], [0, 0, 0], crossed=True)
    assert reverse["label"] == "B" and reverse["reversed_preference"]
    small = estimate([0.1, 0.101, 0.099], [0, 0, 0], crossed=True)
    assert small["label"] == "W" and small["upper_below_1_25"]
    gain = {"BE": {"cell": dict(resolved_gain=True)}}
    cross = {f: reverse for f in HOLDOUTS}
    assert outcome(cross, gain, dict(resolved_gain=True), True)["row"] == "4"
    assert (
        outcome(cross, {"BE": {"cell": dict(resolved_gain=False)}}, {}, True)["row"]
        == "3"
    )
    cross["BE"] = small
    assert outcome(cross, gain, {}, True)["row"] == "2"
    unresolved = estimate([-1, 0, 1], [0, 0, 0], crossed=True)
    cross = {f: unresolved for f in HOLDOUTS}
    assert outcome(cross, gain, dict(resolved_gain=True), True)["subreading"] == "5a"
    assert outcome(cross, gain, dict(resolved_gain=False), True)["subreading"] == "5b"


def test_sizing_distinguishes_width_and_detection():
    r = future_sizing(np.linspace(-0.6, 0.6, 10), np.linspace(-0.8, 0.8, 10))
    assert (
        r["n_per_family_approx_80_percent_detection"]
        > r["n_per_family_expected_half_width_below_effect"]
    )
    assert r["width_cost"]["additional_learning_hours"][0] > 0


def test_smoke_seed_block_is_separate(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch, smoke=True)
    assert r.cap == 8192 and r.config["expected_searches"] == 126
    assert r.config["fresh_seeds"] == [2229400, 2229401]
    assert not set(r.config["fresh_seeds"]) & set(range(2229000, 2229400))


def test_deadline_persists_partial_rows_and_has_no_inference(
    tmp_path, monkeypatch, source
):
    import experiments.chem_tape.crossed_holdout_run as module

    r = runner(tmp_path, monkeypatch)
    rows, _, _, _ = synthetic(source)
    fake_pool = SimpleNamespace(terminate=lambda: None, join=lambda: None)
    monkeypatch.setattr(
        module.mp, "get_context", lambda *_: SimpleNamespace(Pool=lambda *_: fake_pool)
    )

    def partial(pool, fn, jobs, deadline, save):
        assert len(jobs) == 25200 and deadline == r.work_deadline
        save(copy.deepcopy(rows[0]))
        return False

    monkeypatch.setattr(module, "run_jobs", partial)
    monkeypatch.setattr(module, "save_report", lambda *_: None)
    r.run()
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["outcome"]["row"] == "U" and result["crossed"] == {}
    assert len(json.loads((tmp_path / "fresh_scores.json").read_text())) == 1
    assert len((tmp_path / "search.jsonl").read_text().splitlines()) == 1
    assert "deadline" in result["stop_reason"]
    assert not json.loads((tmp_path / "validation.json").read_text())["passed"]
