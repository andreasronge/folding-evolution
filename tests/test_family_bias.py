"""Fidelity checks for the sum/max sampling experiment and its decision gates."""

import itertools
from dataclasses import replace

import numpy as np
import pytest
from _folding_rust import rust_tag_outputs, rust_tag_screen
from experiments.chem_tape.family_bias import (
    DOMAIN,
    FLOOR,
    FITS,
    TASKS,
    UNIFORM,
    Deadline,
    Experiment,
    constrained,
    executed_counts,
    knockout,
    labels,
    ratio_record,
    swap,
    verdict,
)
from folding_evolution.chem_tape import tagged
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.tasks import build_task


def genome(ops, tags=None):
    return np.array(
        ops + [0] * (64 - len(ops)) + (tags or [0] * len(ops)) + [0] * (64 - len(ops)),
        dtype=np.uint8,
    )


def planted(task):
    family = "sum" if task.startswith("sum") else "max"
    threshold = int(task[len(family) :])
    # Construct any threshold by adding CONST_1; every task has a planted exact solver.
    return genome(
        [20, 1, 5 if family == "sum" else 18, 3] + [3, 7] * (threshold - 1) + [8]
    )


def python_task(inputs):
    task = build_task(
        ChemTapeConfig(task="mb_max_gt_5", alphabet="tagged", arm="TAG"), 0
    )
    return replace(
        task, inputs=inputs.tolist(), labels=np.zeros(len(inputs), dtype=np.int64)
    )


def test_rust_python_random_and_cyclic_parity():
    rng = np.random.default_rng(191)
    # Enrich SEP/RECV and small tags to exercise same-tag merges, cycles and depth.
    weights = np.ones(22)
    weights[[20, 21]] = 5
    g = np.concatenate(
        [
            rng.choice(22, (500, 64), p=weights / weights.sum()),
            rng.integers(0, 4, (500, 64)),
        ],
        axis=1,
    ).astype(np.uint8)
    xs = DOMAIN[rng.choice(len(DOMAIN), 32, replace=False)]
    want = tagged.evaluate_tagged(list(g), python_task(xs))[1]
    got = np.array(rust_tag_outputs(g.tobytes(), 64, xs.tolist()))
    assert np.array_equal(got, want)
    y = [labels(t, xs).tolist() for t in TASKS]
    candidates = dict(rust_tag_screen(g.tobytes(), 64, xs.tolist(), y))
    for i in range(len(g)):
        mask = sum(1 << j for j in range(len(TASKS)) if np.array_equal(want[i], y[j]))
        assert candidates.get(i, 0) == mask


def test_every_planted_solver_exact_and_knockout():
    gs = np.array([planted(t) for t in TASKS])
    x = DOMAIN.tolist()
    predictions = np.array(rust_tag_outputs(gs.tobytes(), 64, x))
    for i, t in enumerate(TASKS):
        assert np.array_equal(predictions[i], labels(t, DOMAIN)), t
        op = 5 if t.startswith("sum") else 18
        ko = knockout(gs[i], {op})
        bad = np.array(rust_tag_outputs(ko.tobytes(), 64, x))[0]
        assert not np.array_equal(bad, labels(t, DOMAIN)), t
    mask = dict(
        rust_tag_screen(
            gs.tobytes(), 64, x, [labels(t, DOMAIN).tolist() for t in TASKS]
        )
    )
    assert mask == {i: 1 << i for i in range(len(TASKS))}


def test_executed_cells_exclude_leader_unused_runs_and_depth():
    g = genome([1, 20, 1, 5, 16, 8, 20, 18], [0, 0, 0, 0, 0, 0, 9, 0])
    c = executed_counts(g)
    assert c[1] == 1 and c[18] == 0 and c[20] == 1 and c.sum() == 5
    # Cyclic recv returns default; each visited cell counted once.
    g = genome([20, 21, 20, 21], [0, 1, 1, 0])
    c = executed_counts(g)
    assert c[20] == c[21] == 2 and c[0] == 60


def test_floor_and_exact_swap_mass():
    q = constrained(np.arange(22, dtype=float))
    assert q.min() >= FLOOR - 1e-15 and q.sum() == pytest.approx(1)
    r = swap(q)
    assert r[18] == pytest.approx(q[5] + q[11])
    assert r[5] + r[11] == pytest.approx(q[18])
    assert np.array_equal(
        r[[i for i in range(22) if i not in (5, 11, 18)]],
        q[[i for i in range(22) if i not in (5, 11, 18)]],
    )


def pool(n, **hits):
    return {"n": n, "counts": hits}


def test_interval_zero_counts_adjustment_one_holdout_and_reversal():
    a, b = pool(1_000_000, a=0), pool(1_000_000, a=0)
    assert ratio_record(a, b, ["a"], 0.05 / 64)["class"] == "U"
    a, b = pool(1_000_000, a=4000), pool(1_000_000, a=1000)
    d = ratio_record(a, b, ["a"], 0.05 / 64)
    nominal = ratio_record(a, b, ["a"], 0.05 / 2)
    assert d["class"] == "G" and d["one_holdout"]
    assert d["lower"] < nominal["lower"] and d["upper"] > nominal["upper"]
    assert ratio_record(pool(1_000_000, a=1000), b, ["a"], 0.05 / 64)["class"] == "N"
    d = ratio_record(
        pool(1_000_000, a=500, b=100_000),
        pool(1_000_000, a=1000, b=1000),
        ["a", "b"],
        0.05 / 64,
    )
    assert d["member_reversal"] and d["class"] == "G"


def comparisons(s1, g1, s2, g2):
    return {
        "sum": {"specificity": {"class": s1}, "gain": {"class": g1}},
        "max": {"specificity": {"class": s2}, "gain": {"class": g2}},
    }


def test_verdict_all_combinations_and_critique_example():
    for s1, g1, s2, g2 in itertools.product("GNU", repeat=4):
        c = comparisons(s1, g1, s2, g2)
        v = verdict(c)
        if "U" in (s1, g1, s2, g2):
            assert v == "inconclusive"
        if v == "D":
            assert g1 == g2 == "N"
        if v == "C":
            assert s1 == s2 == "N" and "G" in (g1, g2)
        assert verdict(c, False) == "inconclusive"
    assert verdict(comparisons("G", "N", "N", "G")) == "mixed/unresolved"
    assert verdict(comparisons("G", "G", "G", "G")) == "A"
    assert verdict(comparisons("G", "G", "N", "G")) == "partial A"


def test_training_balanced_shared_and_deterministic(tmp_path):
    a = Experiment(tmp_path / "a", smoke=True)
    b = Experiment(tmp_path / "b", smoke=True)
    assert a.training == b.training and a.screen == b.screen
    for t, indices in a.training.items():
        assert len(indices) == 64 and labels(t, DOMAIN[indices]).sum() == 32
    assert np.array_equal(
        a.draw(a.rng("x"), 10, UNIFORM), b.draw(b.rng("x"), 10, UNIFORM)
    )
    assert not np.array_equal(
        a.draw(a.rng("x"), 10, UNIFORM), b.draw(b.rng("y"), 10, UNIFORM)
    )


def test_prune_observed_support_joint_and_under_supported(tmp_path):
    e = Experiment(tmp_path, smoke=True)
    fits = {f: ts[:2] for f, ts in FITS.items()}
    elites = {t: [planted(t)] * 10 for t in TASKS}
    p = e.prune(elites, fits)
    r = e.results["pruning"]
    assert r["under_supported"]
    assert 18 not in r["floored"] and 5 not in r["floored"]
    assert 0 in r["floored"]  # visited NOPs have adequate support
    assert 4 in r["low_support_kept"]  # absent ops cannot be pruned
    assert p[0] / p[5] == pytest.approx(0.05)


def empty_fit_pool(name, n, weights, collect=False, previous=None):
    return pool(n, **dict.fromkeys(TASKS, 0)), {t: [] for t in TASKS}


def test_calibration_bootstrap_is_one_iteration_with_equal_retained_task_weight(
    tmp_path, monkeypatch
):
    e = Experiment(tmp_path, smoke=True)
    tasks = FITS["sum"][:2]
    counts = {t: 20 for t in TASKS}
    counts[tasks[1]] = 9  # Unsupported contribution stays uniform.
    e.results["calibration"] = pool(30_000_000, **counts)
    elites = {t: [planted(t)] * counts[t] for t in TASKS}
    calls = []

    def fresh(name, n, weights, collect=False, previous=None):
        calls.append((name, n, weights.copy()))
        return empty_fit_pool(name, n, weights, collect, previous)

    monkeypatch.setattr(e, "pool", fresh)
    starts = e.fit("sum", tasks, 1, calibration_elites=elites)
    r = e.results["fitting"]["sum"]
    freq = executed_counts(planted(tasks[0])).astype(float)
    freq /= freq.sum()
    expected = constrained(0.5 * UNIFORM + 0.5 * np.mean([freq, UNIFORM], axis=0))
    assert np.allclose(r["iterations"][0]["next_weights"], expected)
    assert r["iterations"][0]["source"] == "uniform calibration"
    assert r["bootstrap"]["updated_tasks"] == tasks[:1]
    assert set(r["bootstrap"]["counts"]) == set(tasks)  # Holdouts cannot enter.
    assert len(r["iterations"]) == 18 and len(calls) == 17
    assert sum(n for _, n, _ in calls) <= 18 * 2000
    assert calls[0][0] == "fit/sum/0/1"
    assert r["start_updates"][0]["status"] == "updated"
    assert not r["start_updates"][0]["fresh_updated_tasks"]
    for start in (1, 2):
        assert r["start_updates"][start]["status"] == "no task updated"
        initial = next(w for name, _, w in calls if name == f"fit/sum/{start}/0")
        assert np.allclose(starts[start], initial)
    assert np.min(starts[0]) >= FLOOR


def test_no_fitting_updates_distinct_from_failed_adaptation(tmp_path, monkeypatch):
    e = Experiment(tmp_path, smoke=True)
    monkeypatch.setattr(e, "pool", empty_fit_pool)
    starts = e.fit("sum", FITS["sum"], 1)
    r = e.results["fitting"]["sum"]
    assert r["status"] == "no task updated"
    assert not r["bootstrap"]["used"]
    assert np.allclose(starts[0], UNIFORM)
    assert not e.results["gates"][-1]["passed"]
    assert (
        e.validate(
            "sum", FITS["sum"], starts, pool(30_000_000, **dict.fromkeys(TASKS, 20)), 1
        )
        is None
    )
    assert r["status"] == "no task updated"


def test_deadline_before_decisive_completion_is_inconclusive(tmp_path):
    e = Experiment(tmp_path, smoke=True)
    # A provisional early look does not survive a timeout in an unresolved pool.
    e.results["transfer"] = {"outcome": "A"}
    e.stage = "transfer"
    e.handle_deadline(Deadline("transfer/uniform/look2"))
    assert e.results["outcome"] == "inconclusive"
    assert "look2" in e.results["reason"]
    assert not e.results["gates"][-1]["decisive_complete"]


@pytest.mark.parametrize(
    "transfer_hits", ["gain", "zero", "diagnostic_deadline", "prune_deadline"]
)
def test_all_stages_with_synthetic_counts(tmp_path, monkeypatch, transfer_hits):
    """Exercise gates/pool scheduling without turning tiny smoke into evidence."""
    e = Experiment(tmp_path, smoke=True)
    calls = []

    def fake_pool(name, n, weights, collect=False, previous=None):
        if (
            transfer_hits == "diagnostic_deadline"
            and name == "transfer/both/descriptive"
        ):
            raise Deadline(name)
        if transfer_hits == "prune_deadline" and name == "transfer/prune/side2":
            raise Deadline(name)
        calls.append(name)
        p = previous or {
            "n": 0,
            "counts": dict.fromkeys(TASKS, 0),
            "seconds": 0.0,
            "screen_seconds": 0.0,
            "exact_seconds": 0.0,
            "candidates": 0,
        }
        p["n"] += max(n, 100000) if name.startswith("calibration") else n
        p["seconds"] += 0.01
        hit = 20 if name.startswith("calibration") else 100
        for t in TASKS:
            if name.startswith("transfer/max") and t.startswith("sum"):
                k = 20
            elif name.startswith("transfer/sum") and t.startswith("max"):
                k = 20
            elif name.startswith("transfer/uniform") or name.startswith(
                "transfer/prune"
            ):
                k = 20
            else:
                k = hit
            if name.startswith("transfer/") and transfer_hits == "zero":
                k = 0
            if name.startswith("transfer/prune") and transfer_hits == "prune_deadline":
                k = 35  # Side comparison is U; primary comparisons already G.
            p["counts"][t] += k
        e.results["pools"][name] = p
        return p, {t: [planted(t)] * hit if collect else [] for t in TASKS}

    monkeypatch.setattr(e, "pool", fake_pool)
    if transfer_hits.endswith("deadline"):
        with pytest.raises(Deadline) as error:
            e.run()
        e.handle_deadline(error.value)
        assert "remaining diagnostics incomplete" in e.results["diagnostics_status"]
        assert e.results["transfer"]["decisive_complete"]
        assert e.results["gates"][-1]["decisive_complete"]
        assert set(e.results["fitting_recheck"]) == set(FITS)
    else:
        e.run()
    e.finish()
    assert e.results["outcome"] == ("inconclusive" if transfer_hits == "zero" else "A")
    if transfer_hits == "zero":
        assert len(e.results["transfer"]["looks"]) == 4
        assert all(
            e.results["transfer"]["pools"][k]["n"] == 16000
            for k in ("uniform", "sum", "max", "prune")
        )
    assert len(e.results["validation"]) == 3
    expected_pools = {
        "uniform",
        "sum",
        "max",
        "prune",
        "both",
        "sum_swap",
        "max_swap",
    }
    if transfer_hits.endswith("deadline"):
        expected_pools -= {"both", "sum_swap", "max_swap"}
    assert set(e.results["transfer"]["pools"]) == expected_pools
    assert all(e.results["validation"][f]["selected"] is not None for f in FITS)
    assert (tmp_path / "COMPLETE").exists()
