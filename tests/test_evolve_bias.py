"""Endpoint and stopping-rule fidelity for the approved survival experiment."""

import copy
import json
import time

import numpy as np
import pytest

from experiments.chem_tape import evolve_bias as eb
from folding_evolution.chem_tape import tagged
from folding_evolution.chem_tape.evolve import _reproduce_one_island, make_rng


@pytest.fixture
def spec():
    return json.loads(eb.SPEC_PATH.read_text())


def genome(ops, tags=None):
    return np.array(
        ops + [0] * (64 - len(ops)) + (tags or [0] * len(ops)) + [0] * (64 - len(ops)),
        dtype=np.uint8,
    )


def planted(t):
    return genome([20, 1, 5 if t == "sum2" else 18, 15, 8])


def job(t="sum2", cap=8, pop=4):
    return dict(
        phase="smoke",
        task=t,
        arm="uniform",
        seed=eb.MASTER + 20000,
        pop=pop,
        cap=cap,
        probs=[1 / 22] * 22,
        deadline=time.monotonic() + 30,
        out=None,
    )


def survival_row(i, t, event=True, cap=1000):
    return dict(
        seed=i,
        replicate=i,
        time=t,
        event=event,
        complete=True,
        cap=cap,
        pop=4,
        task="sum2",
        arm="uniform",
        seconds=1,
        processed_candidates=t,
    )


def test_frozen_spec_matches_approved_source_and_constant_ids(spec):
    eb.validate_spec(spec)
    assert tagged.N_OPS == 22
    for t in eb.TASKS:
        p = eb.vectors(spec, t)
        assert p["matched"] == spec["vectors"][t[:-1]]
        assert p["mismatched"] == spec["vectors"]["max" if t == "sum2" else "sum"]
        assert p["hand"][15] == 1 / 22
        assert p["hand"][4] != 1 / 22  # CHARS must be among diluted remaining ops.
        cfg = eb.config(t, "hand", 7, 4, 8, p["hand"])
        assert np.allclose(cfg.op_probs(22), p["hand"])
        assert cfg.crossover_rate == 0.7 and cfg.crossover_mate == "selected"


def test_sampler_audit_and_arm_seed_pairing(spec):
    audit = eb.sampler_audit()
    for t, a in audit.items():
        assert a["balance"] == 0.5 and a["both_labels"] and a["n"] == 64
        assert 0 <= a["proxy_train_accuracy"] <= 1
        for arm in eb.ARMS:
            assert (
                eb.config(t, arm, 7, 4, 8, eb.vectors(spec, t)[arm]).seed
                == eb.config(t, "uniform", 7, 4, 8, eb.vectors(spec, t)["uniform"]).seed
            )
    assert audit["sum2"]["distinct_cases"] < 64
    assert not np.array_equal(
        eb.training_indices("sum2", 7), eb.training_indices("sum2", 8)
    )


@pytest.mark.parametrize("t", eb.TASKS)
def test_rust_python_parity_with_special_ops_cycles_and_exact_solver(t):
    rng = np.random.default_rng(6705)
    ops = rng.integers(0, 22, (100, 64), dtype=np.uint8)
    ops[:, ::6] = 20
    ops[:, 2::6] = 21
    tags = rng.integers(0, 4, (100, 64), dtype=np.uint8)
    gs = list(np.concatenate([ops, tags], axis=1)) + [planted(t)]
    task = eb.make_task(t, 19)
    assert np.array_equal(
        eb.predictions(gs, task.inputs), tagged.evaluate_tagged(gs, task)[1]
    )
    assert np.array_equal(
        eb.predictions([planted(t)], eb.DOMAIN_LIST)[0], eb.labels(t, eb.DOMAIN)
    )


def test_gen_zero_position_and_earliest_candidate():
    pop = [genome([0]), planted("sum2"), planted("sum2"), genome([20, 3])]
    r = eb.run_one(job(), initial=pop)
    assert r["complete"] and r["event"] and r["time"] == 2
    assert r["first_gen"] == 0 and r["position"] == 1
    assert r["processed_candidates"] == 4
    assert r["solver"] == planted("sum2").tobytes().hex()


def test_shortcut_does_not_terminate_and_later_generation_position(monkeypatch):
    shortcut = genome([20, 3])
    zero = genome([0])
    pop = [shortcut] * 4
    # Force a training shortcut, without changing exhaustive ground truth.
    monkeypatch.setattr(
        eb,
        "make_task",
        lambda t, seed: type(
            "Training", (), {"inputs": [[9, 9, 9, 9]] * 64, "labels": np.ones(64)}
        )(),
    )
    monkeypatch.setattr(
        eb,
        "_reproduce_one_island",
        lambda *a, **kw: [shortcut, zero, planted("sum2"), zero],
    )
    r = eb.run_one(job(), initial=pop)
    assert r["event"] and r["time"] == 7 and r["first_gen"] == 1 and r["position"] == 2
    assert r["shortcut_candidates"] == 5 and r["verifications"] == 2


def test_cap_counts_gen_zero_and_incomplete_is_missing():
    r = eb.run_one(job(cap=12), initial=[genome([0])] * 4)
    assert r["complete"] and not r["event"] and r["time"] == 12
    assert r["processed_candidates"] == 12
    j = job()
    j["deadline"] = time.monotonic() - 1
    r = eb.run_one(j)
    assert not r["complete"] and r["time"] is None and "deadline" in r["error"]
    assert eb.km_curve([r]) == ([], [], None)


def test_standard_reproduction_is_retained_with_rust_training_predictions():
    t = eb.make_task("sum2", 17)
    cfg = eb.config("sum2", "uniform", 17, 4, 8, [1 / 22] * 22)
    pop = [planted("sum2"), genome([20, 3]), genome([0]), genome([20, 1, 18, 15, 8])]
    rust = eb.predictions(pop, t.inputs)
    fits, python = tagged.evaluate_tagged(pop, t)
    want = _reproduce_one_island(
        pop, fits, cfg, make_rng(cfg), cases=python == t.labels
    )
    got = _reproduce_one_island(
        pop, (rust == t.labels).mean(axis=1), cfg, make_rng(cfg), cases=rust == t.labels
    )
    assert all(np.array_equal(a, b) for a, b in zip(want, got))


def test_km_medians_ties_and_bootstrap_exactly_half_events():
    rows = [survival_row(i, 10, i < 25, cap=10) for i in range(50)]
    assert eb.km_curve(rows)[2] == 10
    draws = np.arange(50)[None, :]
    assert eb.bootstrap_medians(rows, draws)[0] == 10
    rows[24]["event"] = False
    assert eb.km_curve(rows)[2] is None
    assert np.isinf(eb.bootstrap_medians(rows, draws)[0])


def test_bootstrap_faster_equivalent_reverse_unestimable():
    a = [survival_row(i, 500 + i) for i in range(50)]
    b = [{**r, "time": r["time"] / 5} for r in a]
    assert eb.compare(a, b, 12, 10000)["verdict"] == "F"
    assert eb.compare(a, a, 12, 10000)["verdict"] == "E"
    assert eb.compare(b, a, 12, 10000)["verdict"] == "R"
    c = [
        {**r, "event": i < 27, "time": r["time"] if i < 27 else 1000}
        for i, r in enumerate(a)
    ]
    result = eb.compare(c, a, 12, 10000)
    assert result["finite_fraction"] < 0.99 and result["verdict"] == "U"
    c[0]["complete"] = False
    assert eb.compare(c, a, 12, 10000)["verdict"] == "U"
    with pytest.raises(ValueError, match="unpaired"):
        eb.compare(a, [{**r, "seed": r["seed"] + 1} for r in a], 12, 1000)


def test_stopped_contrast_immutable_when_shared_cells_grow():
    comps = {
        f"{t}/{a}/{b}": dict(verdict="E", n=50, look=1, ratio=1)
        for t in eb.TASKS
        for a, b in eb.PAIRS
    }
    comps["sum2/mismatched/matched"]["verdict"] = "U"
    before = copy.deepcopy(comps["sum2/uniform/matched"])
    assert eb.next_cells(comps) == {("sum2", "mismatched"), ("sum2", "matched")}
    rows = [
        {**survival_row(i, 10), "arm": a}
        for i in range(100)
        for a in ("mismatched", "matched")
    ]
    eb.look(rows, comps, 2, 1000)
    assert comps["sum2/uniform/matched"] == before
    assert comps["sum2/mismatched/matched"]["n"] == 100


def test_routing_all_comparison_classes_and_incomplete():
    comps = {f"{t}/{a}/{b}": dict(verdict="F") for t in eb.TASKS for a, b in eb.PAIRS}
    assert eb.overall(comps) == "A'"
    comps["sum2/matched/hand"]["verdict"] = "U"
    assert eb.overall(comps) == "A"
    comps["max2/uniform/matched"]["verdict"] = "U"
    assert eb.overall(comps) == "Partial"
    for t in eb.TASKS:
        comps[f"{t}/uniform/matched"]["verdict"] = "E"
    assert eb.overall(comps) == "B"
    assert eb.overall(comps, screen=True) == "Unresolved"
    assert eb.overall(comps, incomplete=True) == "Unresolved"
    comps["max2/uniform/matched"]["verdict"] = "U"
    assert eb.overall(comps) == "Unresolved"


def pilot_fixture():
    return [
        {
            **survival_row(i, 10000 if a == "uniform" else 5000),
            "task": t,
            "arm": a,
            "pop": p,
            "cap": eb.CAPS[-1],
            "seconds": 0.1,
            "processed_candidates": 10000,
        }
        for t in eb.TASKS
        for a in ("uniform", "hand")
        for p in eb.SIZES
        for i in range(10)
    ]


def test_pilot_selection_budget_and_fallback():
    pilot = pilot_fixture()
    d = eb.select_design(pilot, 100000, 4)
    assert d["feasible"] and d["max_look"] == 2
    assert d["tasks"]["sum2"] == dict(pop=256, cap=eb.CAPS[0], pilot_passed=True)
    d = eb.select_design(pilot, d["look1_seconds"] + 1, 4)
    assert d["feasible"] and d["max_look"] == 1 and d["large_effect_screen"]
    assert not eb.select_design(pilot, 1, 4)["feasible"]
    for r in pilot:
        r.update(event=False, time=eb.CAPS[-1], processed_candidates=eb.CAPS[-1])
    d = eb.select_design(pilot, 100000, 4)
    assert d["tasks"]["sum2"]["pop"] == 1024
    assert not d["tasks"]["sum2"]["pilot_passed"]
    pilot[0]["complete"] = False
    assert not eb.select_design(pilot, 100000, 4)["feasible"]


def test_binomial_zero_and_random_baseline_stable_at_large_n():
    assert eb.binomial(0, 100)["lower"] == 0
    assert eb.binomial(100, 100)["upper"] == 1
    p = 1e-6
    assert np.isclose(
        eb.random_cdf(math_log_half := np.log(0.5) / np.log1p(-p), p), 0.5
    )
    assert math_log_half > 100000
    assert np.all(np.diff(eb.random_cdf([0, 1, 1000000000], p)) >= 0)


def test_full_orchestrator_two_looks_without_full_compute(tmp_path, monkeypatch):
    """Exercise the full stage wiring and immutable look files with toy runs."""
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["evolve_bias", "--seconds", "100000"])
    calls = []

    def fake_jobs(jobs, workers, out):
        calls.append(jobs)
        if jobs[0]["phase"] == "pilot":
            return pilot_fixture()
        return [
            {
                **j,
                "out": None,
                "complete": True,
                "event": j["replicate"] < 24 or j["replicate"] >= 50,
                "time": 100
                if j["replicate"] < 24 or j["replicate"] >= 50
                else j["cap"],
                "seconds": 1,
                "history": [],
                "processed_candidates": j["cap"],
            }
            for j in jobs
        ]

    def fake_sampling(spec, out, n, deadline):
        assert n == 125000000
        data = {t: eb.binomial(10, n) for t in eb.TASKS}
        eb.write_json(out / "sampling.json", data)
        return data

    monkeypatch.setattr(eb, "run_jobs", fake_jobs)
    monkeypatch.setattr(eb, "sample_hand", fake_sampling)
    monkeypatch.setattr(eb, "plot_results", lambda *a: None)
    assert eb.main() == 0
    assert [len(c) for c in calls] == [80, 400, 400]
    assert {j["replicate"] for j in calls[1]} == set(range(50))
    assert {j["replicate"] for j in calls[2]} == set(range(50, 100))
    one = json.loads((tmp_path / "look1.json").read_text())
    result = json.loads((tmp_path / "result.json").read_text())
    assert all(c["verdict"] == "U" and c["n"] == 50 for c in one.values())
    assert all(
        c["verdict"] == "E" and c["n"] == 100 and c["look"] == 2
        for c in result["comparisons"].values()
    )
    assert result["outcome"] == "B" and (tmp_path / "COMPLETE").exists()
    report = (tmp_path / "report.md").read_text()
    assert "| verdict |\n|---" in report
    assert result["product_model_predictions"]["sum2"] == pytest.approx(17.05, abs=0.1)
