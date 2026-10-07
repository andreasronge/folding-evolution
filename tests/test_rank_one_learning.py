"""0821 scientific invariants: budgets, seed pairing, inference and admission."""

import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.stats import t

from experiments.chem_tape.crossed_learning_run import HOLDOUTS, TRAINING
from experiments.chem_tape.map_learning import BOUND, mutate
from experiments.chem_tape.rank_one_learning import (
    SEEDS,
    calibration_estimate,
    calibration_point,
    choose_effort,
    diagnostics,
    reservation,
    start_vector,
    step,
    table,
)
from experiments.chem_tape.rank_one_report import (
    balanced,
    make_report,
    outcome,
    validate_fresh,
)
from experiments.chem_tape.rank_one_run import Runner, load_sources


def runner(tmp_path, monkeypatch, smoke=False):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    return Runner(
        SimpleNamespace(workers=10, deadline_seconds=13680, smoke=smoke, probe=False)
    )


def test_saved_starts_token_operator_and_rank_one_constraints():
    _, starts, g4 = load_sources()
    for si, source in enumerate(starts.values()):
        v = start_vector(source["vector"], np.random.default_rng(si))
        np.testing.assert_array_equal(table(v, g4), source["table"])
        expected, _ = mutate(v[:24], np.zeros(24), np.random.default_rng(si))
        child, mutation = step(v, np.random.default_rng(si), g4, "T")
        assert mutation["operator"] == "token"
        np.testing.assert_array_equal(child[:24], expected)
        np.testing.assert_array_equal(child[24:], v[24:])
        child, record = step(v, np.random.default_rng(si), g4, force="b")
        assert record["operator"] == "b" and abs(child[49:].mean()) < 1e-15
        assert not np.array_equal(table(child, g4), table(v, g4))
        np.testing.assert_allclose(
            np.outer(child[24:49], child[49:]).mean(0), 0, atol=1e-15
        )
        later, _ = step(child, np.random.default_rng(si), g4, force="a")
        assert np.mean(later[24:49] ** 2) == pytest.approx(1)
        assert np.diff(table(later, g4), prepend=0, axis=1).min() >= 250
    child[49:] *= 100
    d = diagnostics(child, g4, np.array(source["table"]))
    assert d["clipped_elements"] > 0
    assert np.max(np.abs(d["residual_log_weights"])) <= BOUND
    assert np.max(np.abs(d["post_clipping_column_means"])) > 0.001


def test_unchanged_a_step_redraws_as_b():
    _, starts, g4 = load_sources()
    v = start_vector(starts["BE1"]["vector"], np.random.default_rng(1))
    # Even forced a at b=0 must redraw to a genuinely changing b step.
    child, record = step(v, np.random.default_rng(7), g4, force="a")
    assert record["operator"] == "b" and record["redraws"] == 1
    assert np.any(child[49:])


def test_signed_covariance_plugin_and_bootstrap_reselection():
    effects = np.array([[i, -i, i] for i in range(24)], dtype=float)
    unit = dict(effects=effects, variances=np.ones((24, 2)))
    p = calibration_point([unit])
    assert p["raw_covariance"] < 0
    assert p["mean_effect"] == 0
    effort = choose_effort(p)
    assert effort["n"] == 24 and effort["nonnegative_variance"] == 0
    assert p["selected"]["48"]["parent_effect"] == -2.5
    assert p["selected"]["48"]["selected_minus_all"] == 9
    estimate = calibration_estimate([unit], np.random.default_rng(1), 100)
    # Independent manual bootstrap, including selection again on resampled A.
    rng = np.random.default_rng(1)
    gains = []
    for _ in range(100):
        records = effects[rng.integers(24, size=24)]
        choices = np.argsort(records[:, 0], kind="stable")[:6]
        gains.append(records[choices, 1].mean() - records[:, 1].mean())
    assert estimate["selected"]["48"][
        "selected_minus_all_interval_95"
    ] == pytest.approx(np.quantile(gains, [0.025, 0.975]))
    # A unit-specific parent offset cancels from covariance and relative gain.
    shifted = dict(effects=effects + [100, 200, 100], variances=np.ones((24, 2)))
    pp = calibration_point([unit, shifted])
    assert pp["raw_covariance"] == p["raw_covariance"]
    assert (
        pp["selected"]["24"]["selected_minus_all"]
        == p["selected"]["24"]["selected_minus_all"]
    )


def fake_job_rows(jobs, phase):
    return [
        dict(
            arm=j[1],
            cell=j[0]["id"],
            seed=j[3],
            cap=j[4],
            solved=True,
            evaluations=256 * (1 + j[3] % 32),
            seconds=0.001,
            phase=phase,
        )
        for j in jobs
    ], 0.01


@pytest.mark.parametrize("n", [24, 48])
def test_full_equal_budgets_and_seed_pairing(tmp_path, monkeypatch, n):
    r = runner(tmp_path, monkeypatch)
    r.n, r.generations = n, 3840 // (8 * n)
    batches = []

    def jobs(js, phase):
        batches.append((js, phase))
        return fake_job_rows(js, phase)

    monkeypatch.setattr(r, "jobs", jobs)
    r.evolve_pair("BE1", 0)
    assert sum(len(js) for js, _ in batches) == 8080
    inner_seeds, final_seeds = set(), set()
    for js, phase in batches:
        names = sorted({j[1] for j in js})
        streams = [[(j[0]["id"], j[3]) for j in js if j[1] == name] for name in names]
        assert all(s == streams[0] for s in streams)
        assert len(js) == (16 * n if phase.startswith("learn") else 400)
        (inner_seeds if phase.startswith("learn") else final_seeds).update(
            j[3] for j in js
        )
    assert not inner_seeds & final_seeds
    for rec in r.finals.values():
        assert rec["search_costs"]["searches"] == 4040
    assert (
        sum(x["proposed"] for x in r.finals["BE1:C"]["step_mix"].values())
        == 6 * r.generations
    )
    assert r.finals["BE1:T"]["step_mix"]["token"]["proposed"] == 6 * r.generations
    generations = [
        json.loads(line)
        for line in (tmp_path / "generations.jsonl").read_text().splitlines()
    ]
    assert len(generations) == 2 * r.generations


def test_calibration_counts_disjoint_mutant_seeds_and_no_variance_gate(
    tmp_path, monkeypatch
):
    r = runner(tmp_path, monkeypatch)
    batches = []

    def jobs(js, phase):
        batches.append(js)
        return fake_job_rows(js, phase)

    monkeypatch.setattr(r, "jobs", jobs)
    # Keep bootstrap short; inspect the full approved search roster.
    import experiments.chem_tape.rank_one_run as module

    original = module.calibration_estimate
    monkeypatch.setattr(
        module, "calibration_estimate", lambda us, rng, _: original(us, rng, 10)
    )
    # The fake path bypasses real cost recording.
    r.costs["calibration"] = dict(searches=29184)
    r.calibration()
    assert sum(len(js) for js in batches) == 29184
    assert len(r.units) == 12
    assert sum(u["operator"] == "context" for u in r.units) == 8
    streams = {}
    for batch in batches:
        for j in batch:
            streams.setdefault(j[1], set()).add(j[3])
    all_seeds = [seed for stream in streams.values() for seed in stream]
    assert len(all_seeds) == len(set(all_seeds)) == 29184
    assert all(len(stream) in (48, 192) for stream in streams.values())
    assert r.calibration_result["stage_b_always_runs"]
    assert r.generations * 8 * r.n == 3840


def test_reserves_prospective_pair_and_anchor_and_updates_from_b():
    first = reservation([], "BE1", [], 0.66, 0, 9.5)
    assert first["fresh_searches"] == 50 * (10 + 16)
    assert first["pair_seconds"] == pytest.approx(1.3 * 8080 * 0.66 / 9.5)
    nextpair = reservation(["BE1"], "PA1", [600], 0.66, 1.32, 9.5)
    assert nextpair["fresh_searches"] == 50 * (10 + 16 + 24)
    assert nextpair["fresh_worker_seconds_per_search"] == 2.04
    assert nextpair["pair_seconds"] == 780
    final = reservation(
        [f"{f}{k}" for k in range(1, 8) for f in TRAINING] + ["BE8"],
        "PA8",
        [500],
        0.66,
        0,
        9.5,
    )
    assert final["fresh_searches"] == 16500


def test_family_balance_and_outcome_order():
    values = dict(BE=[0, 1, 2], PA=[3, 4])
    p = balanced(values)
    assert p["log2_mean"] == 2.25  # unequal n still gets equal family weight
    expected_se = 0.5 * np.sqrt(1 / 3 + 0.5 / 2)
    assert p["standard_error_log2"] == pytest.approx(expected_se)
    assert p["df"] == 3
    assert p["half_width_log2"] == pytest.approx(t.ppf(0.975, 3) * expected_se)

    def est(lo, hi, ratio=1):
        return dict(interval_95=[lo, hi], ratio=ratio)

    ns = dict(BE=6, PA=7)
    assert (
        outcome(
            est(1.01, 1.1, 1.05), est(0.9, 1.2), est(0.9, 1.3), est(0.9, 1.2), True, ns
        )["row"]
        == "1"
    )
    assert (
        outcome(
            est(0.9, 1.14), est(1.01, 1.2), est(1.01, 1.2), est(0.9, 1.2), True, ns
        )["row"]
        == "2"
    )
    o = outcome(est(0.9, 1.14), est(0.9, 1.2), est(1.01, 1.3), est(0.9, 1.2), True, ns)
    assert o["row"] == "3" and not o["neither_arm_resolved_learning"]
    assert (
        outcome(est(0.9, 1.15), est(0.9, 1.2), est(0.9, 1.2), est(0.9, 1.2), True, ns)[
            "row"
        ]
        == "4"
    )
    assert outcome({}, {}, {}, {}, False, ns)["row"] == "U"


def test_leakage_rejected_and_fresh_pair_validation(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch, smoke=True)
    for c in sum(HOLDOUTS.values(), []):
        with pytest.raises(ValueError, match="non-training"):
            r.job("bad", r.g4, c, 1, 4096)
    r.config["searches_per_trajectory"] = 10
    pairs = ["BE1", "PA1"]
    finals = {
        tid + ":" + a: dict(search_costs=dict(searches=10))
        for tid in pairs
        for a in ("T", "C")
    }
    maps = {"G4": dict(table_hash="g")}
    rows = []
    for name in [
        "G4",
        *[tid + ":" + a for tid in pairs for a in ("S", "T", "C", "C0")],
    ]:
        maps[name] = dict(table_hash=name)
        for c in sum(TRAINING.values(), []) if name == "G4" else TRAINING[name[:2]]:
            for s in r.config["fresh_seeds"]:
                rows.append(
                    dict(
                        arm=name,
                        cell=c,
                        seed=s,
                        phase="fresh",
                        cap=8192,
                        pop_size=256,
                        table_hash=name,
                        training_indices=list(range(64)),
                    )
                )
    assert validate_fresh(r.config, pairs, rows, finals, maps)["passed"]
    assert not validate_fresh(r.config, pairs, rows[:-1], finals, maps)["passed"]
    assert not validate_fresh(r.config, pairs, [*rows, rows[0]], finals, maps)["passed"]
    altered = copy.deepcopy(rows)
    altered[-1]["training_indices"].reverse()
    assert not validate_fresh(r.config, pairs, altered, finals, maps)["passed"]
    altered = copy.deepcopy(rows)
    altered[-1]["cell"] = HOLDOUTS["PA"][0]
    assert not validate_fresh(r.config, pairs, altered, finals, maps)["passed"]
    assert SEEDS["learning"] - SEEDS["calibration"] == 1000000


def test_primary_cost_sign_full_report_and_missingness(tmp_path, monkeypatch):
    r = runner(tmp_path, monkeypatch)
    r.config.update(
        searches_per_trajectory=4040, fresh_seeds=[r.seed("fresh"), r.seed("fresh", 1)]
    )
    pairs = [f"{f}{k}" for k in range(1, 7) for f in TRAINING]
    finals, maps, rows = {}, {}, []
    maps["G4"] = dict(table_hash="G4")
    for tid in pairs:
        for arm in ("T", "C"):
            finals[tid + ":" + arm] = dict(
                selected_score=14,
                search_costs=dict(searches=4040),
                diagnostics=dict(residual_log_weights=np.zeros((25, 24)).tolist()),
                step_mix={
                    op: dict(proposed=0, survived=0, clipped_elements=0, redraws=0)
                    for op in ("token", "b", "a")
                },
            )
        for arm in ("S", "T", "C", "C0"):
            maps[tid + ":" + arm] = dict(table_hash=tid + ":" + arm)
    for name in maps:
        cells = sum(TRAINING.values(), []) if name == "G4" else TRAINING[name[:2]]
        evals = (
            65536
            if name == "G4"
            else {"S": 32768, "T": 16384, "C": 8192, "C0": 16384}[name.split(":")[1]]
        )
        for cid in cells:
            for seed in r.config["fresh_seeds"]:
                rows.append(
                    dict(
                        arm=name,
                        cell=cid,
                        seed=seed,
                        solved=name != "G4",
                        evaluations=evals,
                        seconds=1,
                        cap=524288,
                        pop_size=256,
                        table_hash=name,
                        training_indices=list(range(64)),
                        phase="fresh",
                    )
                )
    report = make_report(r.config, pairs, rows, finals, maps)
    assert report["validation"]["passed"]
    assert report["outcome"]["row"] == "1"
    assert report["outcome"]["residual_removal_resolved"]
    assert report["contrasts"]["C/T"]["pooled"]["interval_95"] == [2, 2]
    assert report["contrasts"]["T/S"]["pooled"]["ratio"] == 2
    assert report["contrasts"]["C/S"]["pooled"]["ratio"] == 4
    assert report["contrasts"]["C0/T"]["pooled"]["ratio"] == 1
    assert report["fresh_stats"]["G4|" + TRAINING["BE"][0]]["mean_log2_cost"] == 20
    incomplete = make_report(r.config, pairs, rows[:-1], finals, maps)
    assert incomplete["outcome"]["row"] == "U"
    assert not incomplete["validation"]["passed"]
    broken_finals = copy.deepcopy(finals)
    del broken_finals["BE1:C"]
    assert (
        make_report(r.config, pairs, rows, broken_finals, maps)["outcome"]["row"] == "U"
    )
