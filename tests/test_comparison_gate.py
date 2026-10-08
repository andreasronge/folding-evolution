"""Scientific checks for protected split, phase seeds, endpoint and timeout unit."""

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.stats import t

from experiments.chem_tape.comparison_gate_bank import (
    load_training,
    roster,
    TRAINING,
    PROBED,
    roles,
)
from experiments.chem_tape.comparison_gate_run import (
    Runner,
    roster as search_roster,
    corpus_diagnostics,
)
from experiments.chem_tape.comparison_gate_report import interval, route, make_report
from experiments.chem_tape.solver_corpus_fit import transition_counts


def test_semantic_bank_and_performance_blind_protected_split():
    bank, payload = load_training()
    raw = roster()
    assert len(raw) == 480
    assert {
        f: sum(c["shape"] == f and not c["constant_gate"] for c in raw)
        for f in TRAINING
    } == {"BE": 162, "PA": 162}
    assert bank["retained_counts"] == {"BE": 37, "PA": 56}
    by = {c["id"]: c for c in bank["cells"]}
    for family in TRAINING:
        covered = set().union(*(roles(by[c]) for c in TRAINING[family]))
        assert len(bank["split"]["holdouts"][family]) == 4
        assert {by[c]["repeated"] for c in bank["split"]["holdouts"][family]} == set(
            "SMmF"
        )
        for cid in bank["split"]["holdouts"][family]:
            c = by[cid]
            assert c["retained"] and roles(c) <= covered
            assert not set(c["alias_ids"]) & set(PROBED)
            candidates = bank["split"]["candidates"][family][c["repeated"]]
            assert candidates[0]["id"] == cid
            assert [r["selection_hash"] for r in candidates] == sorted(
                r["selection_hash"] for r in candidates
            )
    assert (
        bank["split"]["holdout_token_totals"]["BE"]
        == bank["split"]["holdout_token_totals"]["PA"]
    )
    assert set(payload) == set(sum(TRAINING.values(), []))
    assert all(set(c) == {"id", "labels"} for c in payload.values())
    expected = {c["id"]: c for c in raw}
    assert all(expected[c["id"]]["labels"] == c["labels"] for c in bank["cells"])


def test_full_roster_counts_and_holdout_search_refusal(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    runner = Runner(SimpleNamespace(smoke=False, workers=10, deadline_seconds=10680))
    schedule = runner.schedule
    collect = [r for r in schedule if r["phase"] == "collection"]
    train = [r for r in schedule if r["phase"] == "training"]
    hold = [r for r in schedule if r["phase"] == "holdout"]
    assert (len(collect), len(train), len(hold)) == (3072, 2304, 4352)
    assert sum(r["arm"] == "C" for r in train) == 1024
    assert sum(r["arm"] == "T" for r in train) == 1024
    assert sum(r["arm"] == "G4" for r in train) == 256
    blocks = [{r["seed"] for r in rows} for rows in (collect, train, hold)]
    assert (
        not blocks[0] & blocks[1]
        and not blocks[1] & blocks[2]
        and not blocks[0] & blocks[2]
    )
    assert runner.config["pair_order"] == [
        [f"BE{k + 1}", f"PA{k + 1}"] for k in range(8)
    ]
    for row in hold:
        with pytest.raises(ValueError, match="holdout leakage"):
            runner.envelope(row)
    assert all(set(runner.envelope(row)[0][0]) == {"id", "labels"} for row in collect)
    # Smoke phases cannot reuse any full-run or future holdout seed.
    smoke = search_roster(runner.bank, runner.base + 100000000, 1, 8, 2, 2)
    assert not {r["seed"] for r in smoke} & set.union(*blocks)


def test_low_yield_normalization_distinct_tapes_and_empty_cell_refusal():
    rows = [dict(cell="a", solved=True, solver=[1] * 32)] + [
        dict(cell="b", solved=True, solver=[7] * 32)
    ] * 12
    counts, yields = transition_counts(rows, ["a", "b"])
    assert yields == {"a": 1, "b": 12}
    assert counts.sum() == 3200 and counts[:, 1].sum() == counts[:, 7].sum() == 1600
    diag = corpus_diagnostics(rows, ["a", "b"])
    assert diag["b"]["solved"] == 12 and diag["b"]["distinct_tapes"] == 1
    with pytest.raises(ValueError, match="empty corpus cell"):
        transition_counts(rows, ["a", "b", "empty"])


def synthetic(pairs=6):
    config = dict(
        nc=8, fresh_n=2, g4_n=2, smoke_only=False, method_hash="synthetic", workers=10
    )
    rows, corpora = [], {}
    for family, cells in TRAINING.items():
        for c, cid in enumerate(cells):
            for s in range(2):
                rows.append(
                    dict(
                        phase="training",
                        family=family,
                        corpus="G4",
                        cell=cid,
                        arm="G4",
                        seed=s,
                        cap=524288,
                        evaluations=8192,
                        solved=True,
                        seconds=1,
                    )
                )
        for k in range(pairs):
            tid = f"{family}{k + 1}"
            corpora[tid] = dict(
                cells={c: dict(solved=2, attempts=2, distinct_tapes=2) for c in cells},
                collection_evaluations=10000,
                collection_worker_seconds=10,
                fit_seconds=1,
            )
            for cid in cells:
                for s in range(2):
                    rows.append(
                        dict(
                            phase="collection",
                            family=family,
                            corpus=tid,
                            cell=cid,
                            arm="G4",
                            seed=s,
                            cap=524288,
                            evaluations=8192,
                            solved=True,
                            seconds=1,
                        )
                    )
                    for arm in ("C", "T"):
                        rows.append(
                            dict(
                                phase="training",
                                family=family,
                                corpus=tid,
                                cell=cid,
                                arm=arm,
                                seed=s,
                                cap=524288,
                                evaluations=1024 if arm == "C" else 2048,
                                solved=True,
                                seconds=1,
                            )
                        )
    return rows, corpora, config


def test_endpoint_sign_corpus_interval_and_routing_precedence():
    x = np.log([1, 2, 3, 4])
    estimate = interval(x)
    assert estimate["speed_ratio"] == pytest.approx(np.exp(x.mean()))
    width = t.ppf(0.975, 3) * x.std(ddof=1) / 2
    assert estimate["interval_95"] == pytest.approx(
        np.exp([x.mean() - width, x.mean() + width])
    )
    overlap = dict(interval_95=[1.03, 1.08])
    assert route(overlap, 0.4, True)["label"] == "recommend_stage2"
    assert route(overlap, 0.39, True)["label"] == "acquisition_obstacle"
    assert (
        route(dict(interval_95=[0.95, 1.08]), 0.6, True)["label"]
        == "bounded_small_gain"
    )
    assert route(dict(interval_95=[0.9, 1.2]), 0.6, True)["label"] == "unresolved"
    assert route(overlap, 0.6, False)["label"] == "incomplete"


def test_timeout_keeps_only_balanced_completed_prefix_and_error_has_no_decision():
    rows, corpora, config = synthetic(8)
    report = make_report(rows, corpora, config, 6, True, "timeout", "deadline", {})
    primary = report["sensitivities"]["unsolved_2x_cap"]["C_T"]
    assert primary["n"] == 12 and primary["speed_ratio"] == pytest.approx(2)
    assert report["analysed_corpora"] == [
        f"{f}{k + 1}" for k in range(6) for f in TRAINING
    ]
    assert report["outcome"]["label"] == "recommend_stage2"
    # Arbitrarily fast/slow trailing jobs do not change the endpoint or yield gate.
    changed = deepcopy(rows)
    for r in changed:
        if r["corpus"] in ("BE7", "PA7", "BE8", "PA8"):
            r["evaluations"] = 256 if r["arm"] == "T" else 524288
            if r["phase"] == "collection":
                r["solved"] = False
    other = make_report(changed, corpora, config, 6, True, "timeout", "deadline", {})
    assert other["sensitivities"]["unsolved_2x_cap"]["C_T"] == primary
    assert other["collection_yield_pooled"] == report["collection_yield_pooled"]
    for pairs, kind in ((5, "timeout"), (6, "error"), (6, None)):
        result = make_report(rows, corpora, config, pairs, True, kind, "failure", {})
        assert result["outcome"]["label"] == "incomplete"
    # A partially scored cell cannot accidentally be labelled a complete block.
    changed = [
        r
        for r in rows
        if not (r["corpus"] == "BE1" and r["arm"] == "T" and r["seed"] == 0)
    ]
    with pytest.raises(ValueError, match="missing a scored corpus cell"):
        make_report(changed, corpora, config, 6, True, "timeout", "deadline", {})


def test_no_zero_hits_relabelled_as_absence_and_penalty_sensitivity():
    rows, corpora, config = synthetic(6)
    for r in rows:
        if r["arm"] == "C":
            r.update(solved=False, evaluations=r["cap"])
    result = make_report(rows, corpora, config, 6, True, "timeout", "deadline", {})
    primary = result["sensitivities"]["unsolved_2x_cap"]["C_T"]["speed_ratio"]
    sensitivity = result["sensitivities"]["unsolved_1x_cap"]["C_T"]["speed_ratio"]
    assert primary == pytest.approx(sensitivity / 2)
    assert result["outcome"]["label"] == "bounded_small_gain"
    assert (
        result["sensitivities"]["unsolved_2x_cap"]["per_family"]["BE"]["C"][
            "solve_rate"
        ]
        == 0
    )
