"""Prospective bank, frozen source, timeout-prefix and statistical-unit checks."""

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape.comparison_gate_bank import TRAINING, load_training
from experiments.chem_tape.then_addition_bank import load, roster
from experiments.chem_tape.then_addition_run import (
    Runner,
    frozen_source,
    fresh_schedule,
    smoke_schedule,
    check_seeds,
)
from experiments.chem_tape.then_addition_report import make_report, route


def test_bank_counts_full_reference_and_exclusion_audit():
    bank, payload = load()
    raw = roster()
    v1, _ = load_training()
    assert len(raw) == 240
    assert bank["counts"] == dict(
        raw=240,
        nonconstant=162,
        distinct=86,
        nine_token_survivors=37,
        fresh_before_old_exclusion=16,
        final=16,
    )
    assert bank["reference_v1_ids"] == [c["id"] for c in v1["cells"]]
    assert all(set(c) == {"id", "labels"} for c in payload.values())
    assert set(payload) == set(bank["selected_ids"])
    by = {r["id"]: r for r in raw}
    for cell in bank["cells"]:
        assert cell["labels"] == by[cell["id"]]["labels"]
        assert cell["id"] == min(cell["alias_ids"])
        matches = np.count_nonzero(
            np.asarray([c["labels"] for c in v1["cells"]]) == cell["labels"], axis=1
        )
        assert matches.max() == cell["v1_best_matches"]
        assert cell["retained"] == (not cell["exclusion_reasons"])
        if cell["retained"]:
            assert cell["best_matches"] * 5 < 1331 * 4
            assert cell["v1_best_matches"] * 5 < 1331 * 4
    assert sum(not c["constant_gate"] for c in raw) == 162
    assert bank["probe_order_reducer_counts"] == dict(S=3, M=5, m=4, F=4)
    for cell in bank["cells"]:
        aliases = [by[cid] for cid in cell["alias_ids"]]
        assert (
            cell["probe_repeated_reducer"]
            == min(aliases, key=lambda c: ("SMmF".index(c["repeated"]), c["id"]))[
                "repeated"
            ]
        )


def test_frozen_rosters_seed_pairing_and_source_tamper(tmp_path):
    saved, _ = frozen_source()
    bank, _ = load()
    f = fresh_schedule(bank["selected_ids"])
    d = [r for r in saved["schedule.json"] if r["phase"] == "holdout"]
    smoke = smoke_schedule()
    assert [len(s) for s in (f, d, smoke)] == [4352, 4352, 48]
    check_seeds(f + d + smoke)
    assert not {r["seed"] for r in f + d + smoke} & {
        r["seed"] for r in saved["search.jsonl"]
    }
    assert {r["cell"] for r in smoke} == set(sum(TRAINING.values(), []))
    bad = deepcopy(f)
    bad[0]["seed"] = bad[-1]["seed"]
    with pytest.raises(ValueError, match="seed collision"):
        check_seeds(bad)
    (tmp_path / "provenance.json").write_text("{}")
    with pytest.raises(ValueError, match="provenance SHA"):
        frozen_source(tmp_path)


@pytest.mark.parametrize("row", ["F", "D"])
def test_runner_search_payload_and_exact_D_roster(tmp_path, monkeypatch, row):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(
        SimpleNamespace(row=row, smoke=False, workers=1, deadline_seconds=300)
    )
    if row == "D":
        assert runner.schedule == [
            r for r in runner.saved["schedule.json"] if r["phase"] == "holdout"
        ]
    for r in (runner.schedule[0], runner.schedule[-1]):
        job, meta, save = runner.envelope(r)
        assert set(job[0]) == {"id", "labels"}
        assert not save
        assert job[4:6] == (524288, 256)
    with pytest.raises(ValueError, match="outside frozen roster"):
        runner.envelope(dict(runner.schedule[0], seed=0))


def synthetic(row="F", pairs=6):
    ids = ["TA:a", "TA:b"] if row == "F" else ["BE:h", "PA:h"]
    schedule = fresh_schedule(ids)
    if row == "D":
        schedule = [dict(r, phase="holdout") for r in schedule]
    prefix = {f"{f}{k + 1}" for k in range(pairs) for f in TRAINING}
    rows = []
    for r in schedule:
        if r["corpus"] not in prefix and r["arm"] != "G4":
            continue
        # D has a 4x own-family gain and a 1x cross-family gain.
        matched = r["cell"].startswith(r["family"] + ":")
        ev = (512 if row == "F" or matched else 2048) if r["arm"] == "C" else 2048
        rows.append(dict(r, cap=524288, evaluations=ev, solved=True, seconds=1))
    source = []
    for tid in prefix:
        for cid in TRAINING[tid[:2]]:
            for arm in ("C", "T"):
                for s in range(2):
                    source.append(
                        dict(
                            phase="training",
                            corpus=tid,
                            family=tid[:2],
                            cell=cid,
                            arm=arm,
                            seed=s,
                            cap=524288,
                            evaluations=1024 if arm == "C" else 2048,
                            solved=True,
                            seconds=1,
                        )
                    )
    config = dict(nc=8, row=row, smoke_only=False, method_hash="synthetic")
    return rows, schedule, source, config


def test_corpus_endpoint_missingness_and_no_error_fallback():
    rows, schedule, source, config = synthetic()

    def report(rs=rows, pairs=6, kind="timeout"):
        return make_report(rs, schedule, source, config, pairs, True, kind, "test", {})

    r = report()
    assert r["sensitivities"]["unsolved_2cap"]["C_T"]["speed_ratio"] == pytest.approx(4)
    assert r["completed_corpora"] == 12
    assert r["outcome"]["label"] == "resolved_relative_gain"
    assert report(kind="error")["outcome"]["label"] == "incomplete"
    # Trailing fastest rows cannot enter the completed initial pair prefix.
    extra = dict(
        next(r for r in schedule if r["corpus"] == "BE7"),
        cap=524288,
        evaluations=256,
        solved=True,
        seconds=1,
    )
    trailing = report(rows + [extra])
    assert trailing["trailing_corpora"] == ["BE7"]
    assert (
        trailing["sensitivities"]["unsolved_2cap"]["C_T"]
        == r["sensitivities"]["unsolved_2cap"]["C_T"]
    )
    with pytest.raises(ValueError, match="roster missing"):
        report(rows[:-1])
    five_rows, s, src, cfg = synthetic(pairs=5)
    assert (
        make_report(five_rows, s, src, cfg, 5, True, "timeout", "test", {})["outcome"][
            "label"
        ]
        == "incomplete"
    )


def test_matched_shrinkage_does_not_mix_family_mismatch():
    args = synthetic("D")
    report = make_report(*args, 6, True, "timeout", "test", {})
    secondary = report["sensitivities"]["unsolved_2cap"]["secondaries"]
    assert secondary["matched_C_T"]["speed_ratio"] == pytest.approx(4)
    assert secondary["mismatched_C_T"]["speed_ratio"] == pytest.approx(1)
    assert secondary["matched_minus_mismatched"]["difference_log"] == pytest.approx(
        np.log(4)
    )
    assert secondary["own_family_holdout_minus_training"][
        "difference_log"
    ] == pytest.approx(np.log(2))
    assert secondary["target_minus_own_family_training"][
        "difference_log"
    ] == pytest.approx(0)


def test_precedence_and_shared_censoring_guard():
    both = dict(interval_95=[1.03, 1.08])
    assert route(both, True, False, "F")["label"] == "resolved_gain_below_10_percent"
    assert route(both, True, True, "F")["label"] == "capped_endpoint"
    assert route(both, False, True, "F")["label"] == "incomplete"
    assert (
        route(dict(interval_95=[0.96, 1.08]), True, False, "F")["label"]
        == "bounded_small_gain"
    )
    assert (
        route(dict(interval_95=[0.96, 1.3]), True, False, "F")["label"] == "unresolved"
    )
    rows, schedule, source, config = synthetic()
    for r in rows:
        if r["arm"] in ("C", "T"):
            r.update(solved=False, evaluations=524288)
    r = make_report(rows, schedule, source, config, 6, True, "timeout", "test", {})
    assert r["outcome"]["label"] == "capped_endpoint"
    assert r["sensitivities"]["unsolved_2cap"]["arms"]["C"]["solved"] == 0
    assert r["sensitivities"]["unsolved_1cap"]["C_T"]["speed_ratio"] == pytest.approx(1)
