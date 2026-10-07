"""1707 scientific invariants: search compatibility, controls, seeds and inference."""

from types import SimpleNamespace

import numpy as np
import pytest
from scipy.stats import t

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_search import Decoder, outputs, search
from experiments.chem_tape.crossed_learning_run import TRAINING, HOLDOUTS
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.solver_corpus_fit import (
    seed_for,
    transition_counts,
    emitted,
    fit,
    validate_table,
    admit_holdouts,
)
from experiments.chem_tape.solver_corpus_run import Runner, scientific_fields
from experiments.chem_tape.solver_corpus_report import (
    pooled,
    welch,
    outcome,
    cost,
    contrast,
    make_report,
)


def test_solver_return_consumes_no_randomness_or_changes_fields():
    table = tables()["G4"]
    inputs = inputs_for("D1331")
    seed = 1234
    # Ensure a solve at generation zero with a target made from the first sampled tape.
    pop = np.random.default_rng([seed, 1]).integers(
        24000, size=(16, 32), dtype=np.int32
    )
    labels = outputs(Decoder(table).decode(pop)[:1], inputs, ALPHABET)[0].tolist()
    job = (
        dict(id="synthetic", labels=labels),
        "G4",
        table,
        seed,
        256,
        16,
        inputs,
        ALPHABET,
    )
    old = search(job)
    new = search(job, return_solver=True)
    assert "solver" not in old and new["solved"]
    assert scientific_fields(old) == scientific_fields(new)
    assert np.array_equal(outputs([new["solver"]], inputs, ALPHABET)[0], labels)
    # Deliberately unreachable labels exercise None handling without a full-cap run.
    job = (dict(id="none", labels=[999999999] * 1331), *job[1:])
    row = search(job, return_solver=True)
    assert not row["solved"] and row["solver"] is None


def test_equal_cell_weight_start_and_exact_emitted_control():
    cells = ["a", "b"]
    rows = [dict(cell="a", solved=True, solver=[1] * 32)] + [
        dict(cell="b", solved=True, solver=[7] * 32) for _ in range(3)
    ]
    rows.append(dict(cell="b", solved=False, solver=None))
    n, yields = transition_counts(rows, cells)
    assert yields == dict(a=1, b=3)
    assert n.sum() == 3200 and n[24, 1] == 50 and n[24, 7] == 50
    assert n[1, 1] == 1550 and n[7, 7] == 1550
    fitted, d = fit(n)
    assert d["T_success"] and d["K_valid"]
    assert max(abs(emitted(fitted["K"]) - emitted(fitted["C"]))) <= 0.001
    assert all(validate_table(tab) for tab in fitted.values())
    # T and K preserve G4's row template before support projection; C differs by row.
    assert np.isclose(emitted(fitted["C"]).sum(), 1)
    with pytest.raises(ValueError, match="non-training"):
        transition_counts(rows, ["a"])


def runner(tmp_path, monkeypatch, smoke=False, probe=False):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    return Runner(
        SimpleNamespace(workers=10, deadline_seconds=7920, smoke=smoke, probe=probe)
    )


def test_full_search_roster_counts_disjoint_blocks_and_holdout_payload(
    tmp_path, monkeypatch
):
    r = runner(tmp_path, monkeypatch)
    for f in TRAINING:
        for k in range(16):
            r.corpora[f"{f}{k + 1}"] = dict(
                family=f,
                index=k,
                fit=dict(K_valid=True),
                tables=dict.fromkeys(("T", "C", "K"), r.g4.tolist()),
            )
    jobs = r.evaluation_jobs()
    hold = r.evaluation_jobs(True)
    assert len(jobs) == 17920 and len(hold) == 9600
    assert sum(j[1] == "M" for j, _, _ in jobs) == 1600
    assert sum(j[1] == "G4" for j, _, _ in jobs) == 960
    train_seeds = {j[3] for j, _, _ in jobs}
    hold_seeds = {j[3] for j, _, _ in hold}
    assert len(train_seeds) == 5120 + 960 + 1600
    assert len(hold_seeds) == 3072 + 384
    collect = {
        seed_for(0, f, k, c, s)
        for f in TRAINING
        for k in range(16)
        for c in range(len(TRAINING[f]))
        for s in range(48)
    }
    assert (
        len(collect) == 7680
        and not collect & train_seeds
        and not hold_seeds & train_seeds
    )
    assert len({j[3] for j, m, _ in jobs if j[1] == "C"}) == 5120
    assert len({j[3] for j, m, _ in hold if j[1] == "C"}) == 3072
    assert all(set(j[0]) == {"id", "labels"} for j, _, _ in jobs + hold)
    assert all(j[4:6] == (524288, 256) and len(j[6]) == 1331 for j, _, _ in jobs + hold)
    with pytest.raises(ValueError, match="leakage"):
        r.envelope("training", "BE", "BE1", HOLDOUTS["BE"][0], "C", r.g4, 1)
    r.corpora["BE1"]["fit"]["K_valid"] = False
    assert len(r.evaluation_jobs()) == 17920 - 4 * 32
    assert len(r.evaluation_jobs(True)) == 9600 - 3 * 32


def test_deadline_and_estimator_family_weights_and_outcome_rules():
    import json

    assert json.dumps(admit_holdouts(151, np.float64(100))) == "true"
    assert not admit_holdouts(150, 100)
    assert admit_holdouts(150.01, 100)
    be = [0, 1, 2, 3]
    pa = [0, 2, 4, 6]
    r = pooled(dict(BE=be, PA=pa))["pooled"]
    se = 0.5 * np.sqrt(np.var(be, ddof=1) / 4 + np.var(pa, ddof=1) / 4)
    assert r["delta_log2"] == 2.25 and r["df"] == 3
    assert r["half_width_log2"] == pytest.approx(t.ppf(0.975, 3) * se)
    assert welch([0, 0, 0], [1, 1, 1])["speed_ratio"] == 2
    yes = dict(interval_95=[1.01, 1.3])
    null = dict(interval_95=[0.9, 1.09])
    wide = dict(interval_95=[0.9, 1.1])
    assert outcome(yes, yes, yes, True)["row"] == 1
    assert outcome(yes, null, yes, True)["row"] == 2
    assert outcome(yes, yes, wide, True)["row"] == 2
    assert outcome(null, null, yes, True)["row"] == 3
    assert outcome(wide, wide, yes, True)["row"] == 4
    assert outcome(yes, yes, yes, False)["row"] == 0
    assert cost(dict(solved=False, evaluations=100, cap=100)) == 200
    assert cost(dict(solved=False, evaluations=100, cap=100), 1) == 100


def test_k_valid_subset_changes_both_attribution_contrasts():
    corpora = {}
    scores = {}
    for f in TRAINING:
        for k in range(3):
            tid = f + str(k)
            corpora[tid] = dict(family=f, fit=dict(K_valid=k != 0))
            scores[tid] = dict(
                C=dict(cell=1 if k == 0 else 2), T=dict(cell=4), K=dict(cell=3)
            )
    all_ct = contrast(scores, corpora, "C", "T")
    sub = contrast(scores, corpora, "C", "T", subset=True)
    ck = contrast(scores, corpora, "C", "K")
    assert all_ct["families"]["BE"]["n"] == 3
    assert sub["families"]["BE"]["n"] == ck["families"]["BE"]["n"] == 2
    assert all_ct["pooled"]["delta_log2"] != sub["pooled"]["delta_log2"]


def test_report_incomplete_stage_cannot_claim_transfer():
    cfg = dict(smoke_only=False, probe_only=False)
    report = make_report([], {}, cfg, False, False, dict(passed=False), "deadline")
    assert report["outcome"]["row"] == 0 and not report["sensitivities"]


def synthetic_report_rows():
    corpora = {}
    rows = []
    for family in TRAINING:
        for k in range(3):
            tid = f"{family}{k + 1}"
            corpora[tid] = dict(
                family=family,
                index=k,
                fit=dict(K_valid=k != 2),
                collection_evaluations=100000,
                collection_seconds=10,
                fit_seconds=1,
            )
            for phase, cells in [
                ("training", TRAINING[family]),
                ("holdout", sum(HOLDOUTS.values(), [])),
            ]:
                for cid in cells:
                    for arm in ("T", "C", "K"):
                        if arm == "K" and k == 2:
                            continue
                        for s in range(2):
                            rows.append(
                                dict(
                                    phase=phase,
                                    corpus=tid,
                                    family=family,
                                    cell=cid,
                                    arm=arm,
                                    seed=s,
                                    cap=524288,
                                    solved=True,
                                    evaluations=1024 if arm == "C" else 4096,
                                    seconds=1,
                                )
                            )
        for phase, cells in [
            ("training", TRAINING[family]),
            ("holdout", HOLDOUTS[family]),
        ]:
            for cid in cells:
                for s in range(2):
                    rows.append(
                        dict(
                            phase=phase,
                            corpus="G4",
                            family=family,
                            cell=cid,
                            arm="G4",
                            seed=s,
                            cap=524288,
                            solved=True,
                            evaluations=8192,
                            seconds=4,
                        )
                    )
        for k in range(3):
            for cid in TRAINING[family]:
                rows.append(
                    dict(
                        phase="training",
                        corpus=f"M:{family}{k}",
                        family=family,
                        cell=cid,
                        arm="M",
                        seed=0,
                        cap=524288,
                        solved=True,
                        evaluations=4096,
                        seconds=1,
                    )
                )
    return rows, corpora


def test_report_subset_scope_amortization_sensitivity_and_partial_holdouts():
    import json
    from experiments.chem_tape.solver_corpus_report import versus_g4, corpus_scores

    rows, corpora = synthetic_report_rows()
    cfg = dict(smoke_only=False, probe_only=False)
    report = make_report(rows, corpora, cfg, True, True, dict(passed=True), None)
    json.dumps(report, allow_nan=False)
    assert report["outcome"]["row"] == 1
    assert report["K_exclusions"] == dict(BE=["BE3"], PA=["PA3"])
    main = report["sensitivities"]["unsolved_2x_cap"]
    assert main["C_T"]["families"]["BE"]["n"] == 3
    assert main["K_valid_C_T"]["families"]["BE"]["n"] == 2
    assert main["holdout"]["C_T"]["n"] == 6 and main["holdout"]["C_K"]["n"] == 4
    assert main["holdout"]["interpreted"]
    assert main["amortization"]["BE1"]["C"]["break_even_searches_evaluations"] == 14
    assert main["amortization"]["BE1"]["C"]["break_even_searches_seconds"] == 4
    assert "unsolved_1x_cap" in report["sensitivities"]
    # A skipped/interrupted holdout grid must not produce any transfer readout.
    partial = make_report(
        rows, corpora, cfg, True, False, dict(passed=True), "stage2 deadline"
    )
    assert "holdout" not in partial["sensitivities"]["unsolved_2x_cap"]
    for r in rows:
        if r["arm"] == "G4":
            r.update(evaluations=256, seconds=0.5)
    harm = make_report(rows, corpora, cfg, True, False, dict(passed=True), None)
    assert harm["outcome"]["row"] == 1
    assert (
        harm["sensitivities"]["unsolved_2x_cap"]["amortization"]["BE1"]["C"][
            "break_even_searches_evaluations"
        ]
        is None
    )
    # Shared holdout G4 reference uncertainty must not be averaged down twice.
    for r in rows:
        if r["arm"] == "G4":
            r["evaluations"] = 256 if r["seed"] == 0 else 1024
    scores, grouped = corpus_scores(rows, corpora, "holdout", 2)
    ref = versus_g4(scores, grouped, corpora, "holdout", 2)["C/G4"]
    assert ref["pooled"]["se_log2"] == pytest.approx(ref["families"]["BE"]["se_log2"])
