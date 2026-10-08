"""Mechanism, episode ordering, exact endpoint, and crossed uncertainty checks."""
import copy
import time

import numpy as np
import pytest

from experiments.chem_tape import inherited_bias as ib
from folding_evolution.chem_tape import tagged
from folding_evolution.chem_tape.evolve import _reproduce_one_island, make_rng


def test_validation_replays_twenty_legacy_searches():
    audit = ib.validate()
    assert len(audit["sigma_zero_legacy_replay_seeds"]) == 20
    assert set(audit["targets"]) == set(ib.TARGETS)


def test_per_row_draws_and_legacy_rng_state():
    p = np.eye(22)[[1, 5, 8, 18]]
    assert np.array_equal(tagged._draw_ops(np.random.default_rng(5), 22, (4, 100), p),
                          np.array([[op] * 100 for op in (1, 5, 8, 18)]))
    rng = np.random.default_rng(7)
    q = rng.dirichlet(np.ones(22), size=4)
    draws = tagged._draw_ops(rng, 22, (4, 40000), q)
    for i in range(4):
        assert np.max(np.abs(np.bincount(draws[i], minlength=22) / 40000 - q[i])) < 0.007
    a, b = np.random.default_rng(6), np.random.default_rng(6)
    single = np.ones(22) / 22
    assert np.array_equal(tagged._draw_ops(a, 22, (4, 100), single),
                          tagged._draw_ops(b, 22, (4, 100), np.tile(single, (4, 1))))
    assert a.bit_generator.state == b.bit_generator.state
    with pytest.raises(ValueError):
        tagged._draw_ops(a, 22, (4, 100), np.ones((4, 22)))
    with pytest.raises(ValueError):
        tagged._draw_ops(a, 22, (4, 100), np.ones((3, 22)) / 22)


def test_support_bounds_elites_and_recipient_not_mate():
    cfg = ib.eb.config("sum1", "uniform", 55, 16, 32, [1 / 22] * 22, master=ib.MASTER)
    rng = make_rng(cfg)
    pop = ib.eb.build_initial_population(cfg, rng, 16)
    cases = np.random.default_rng(3).integers(0, 2, (16, 64)).astype(bool)
    theta = np.arange(16)[:, None] * np.linspace(0, 0.1, 22)[None, :]
    m = ib.Modifier(16, np.random.default_rng(8), sigma=0, theta=theta)
    lineage = []
    _reproduce_one_island(pop, cases.mean(axis=1), cfg, rng,
                          cases=cases, lineage=lineage, modifier=m)
    assert np.array_equal(m.theta, theta[np.array(lineage)[:, 0]])
    assert (np.array(lineage)[:2, 2] == 0).all()
    assert m.depth[:2].tolist() == [0, 0] and (m.depth[2:] == 1).all()
    counts = np.bincount(np.array(lineage)[:, 0], minlength=16)
    assert np.allclose(m.last_covariance,
                       ((theta - theta.mean(0)) * (counts - counts.mean())[:, None]).mean(0))
    m = ib.Modifier(4, np.random.default_rng(8), sigma=100, theta=np.full((4, 22), 2.9))
    m(np.array([3, 2, 1, 0]), 2)
    assert (m.theta[:2] == 2.9).all() and (np.abs(m.theta[2:]) <= 3).all()
    p = ib.probabilities(m.theta)
    assert np.all(p >= 0.1 / 22) and np.allclose(p.sum(1), 1)


@pytest.mark.parametrize("target", ib.TARGETS)
def test_exact_target_and_position_cost(target):
    pop = [np.zeros(128, dtype=np.uint8), ib.planted(target), ib.planted(target),
           np.zeros(128, dtype=np.uint8)]
    job = ib.frozen_job(target, "test", [1 / 22] * 22, 55)
    job.update(pop=4, cap=8, deadline=time.monotonic() + 30)
    row = ib.eb.run_one(job, initial=pop)
    assert row["event"] and row["time"] == 2 and row["first_gen"] == 0
    assert row["processed_candidates"] == 4


def test_gen_zero_solve_still_shuffles_and_final_extract_has_no_reset(monkeypatch):
    calls = []
    def reset(m, rng):
        m.theta = np.arange(4)[:, None] * np.arange(22)[None, :] / 100
        calls.append("reset")
        return [ib.planted("sum1")] * 4
    original = ib.Modifier.shuffle
    def shuffle(m):
        calls.append("shuffle")
        return original(m)
    monkeypatch.setattr(ib, "reset_population", reset)
    monkeypatch.setattr(ib.Modifier, "shuffle", shuffle)
    row = ib.acquire(dict(family="sum", arm="broken", replicate=1, phase="test",
                          pop=4, episodes=1, generations=128))
    assert calls == ["reset", "shuffle"]
    assert row["complete"] and row["solves"] == 1 and row["generations"] == 0
    assert row["episodes"][0]["shuffles"] == 1
    assert np.allclose(row["probs"], ib.probabilities(np.array(row["theta"])).mean(0))


def test_broken_permutation_after_evaluation_before_elite_selection(monkeypatch):
    initial = np.arange(4)[:, None] * np.arange(22)[None, :] / 100
    recipient = np.array([3, 2, 1, 0])
    stages = []
    def reset(m, rng):
        m.theta = initial.copy()
        return [np.zeros(128, dtype=np.uint8)] * 4
    def predict(pop, inputs):
        stages.append("evaluate")
        return np.zeros((4, len(inputs)), dtype=int)
    def shuffle(m):
        stages.append("shuffle")
        m.theta = m.theta[::-1].copy()
        m.depth = m.depth[::-1].copy()
    def reproduce(pop, fits, cfg, rng, cases, modifier):
        stages.append("select")
        assert np.array_equal(modifier.theta, initial[::-1])
        modifier.sigma = 0
        modifier(recipient, 2)
        return pop
    monkeypatch.setattr(ib, "reset_population", reset)
    monkeypatch.setattr(ib.eb, "predictions", predict)
    monkeypatch.setattr(ib.Modifier, "shuffle", shuffle)
    monkeypatch.setattr(ib, "_reproduce_one_island", reproduce)
    row = ib.acquire(dict(family="sum", arm="broken", replicate=0, phase="test",
                          pop=4, episodes=1, generations=1))
    assert stages == ["evaluate", "shuffle", "select", "evaluate", "shuffle"]
    assert row["episodes"][0]["shuffles"] == 2
    # Final shuffle is included, but final extraction does not mutate/reset.
    assert np.array_equal(row["theta"], initial[::-1][recipient][::-1])


def test_crossed_bootstrap_contains_shared_seed_uncertainty():
    # No acquisition variance, large target-specific seed interaction.
    a = np.zeros((2, 16, 2, 16))
    b = np.zeros_like(a)
    a[:, :, :, :8] = np.log(4)
    out = ib.crossed_effect(a, b, np.random.default_rng(8), draws=1000)
    assert out["pooled"]["ratio"] == pytest.approx(2)
    assert out["pooled"]["upper"] > out["pooled"]["lower"]
    exact = ib.crossed_effect(a, a, np.random.default_rng(8), draws=1000)
    assert exact["pooled"] == dict(ratio=1.0, lower=1.0, upper=1.0)


def test_cost_gate_does_not_use_arm_advantage():
    acq = [dict(family=f, arm=a, seconds=10, complete=True) for f in ib.FAMILIES for a in ib.ARMS]
    searches = [dict(task=t, seconds=1, complete=True) for t in ib.TARGETS]
    assert ib.projection(acq, searches)["feasible"]
    costly = copy.deepcopy(searches)
    costly[0]["seconds"] = 1000
    assert not ib.projection(acq, costly)["feasible"]
    acq[0]["complete"] = False
    assert not ib.projection(acq, searches)["feasible"]


def test_paired_acquisition_bootstrap_preserves_common_run_effects():
    common = np.arange(16)[None, :, None, None] / 4
    a = np.broadcast_to(common, (2, 16, 2, 16)).copy() + np.log(2)
    b = np.broadcast_to(common, (2, 16, 2, 16)).copy()
    result = ib.crossed_effect(a, b, np.random.default_rng(3), draws=500, paired_runs=True)
    assert result["pooled"]["ratio"] == pytest.approx(2)
    assert result["pooled"]["lower"] == pytest.approx(2)
    assert result["pooled"]["upper"] == pytest.approx(2)


def test_full_roster_and_pipeline_wiring(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["inherited_bias", "--mode", "full", "--out", str(tmp_path)])
    monkeypatch.setattr(ib, "stage_zero", lambda out, workers: {"projection": {"feasible": True}})
    calls = []
    def fake_parallel(function, jobs, workers):
        calls.append((function, jobs))
        if function is ib.acquire:
            return [{**j, "probs": [1 / 22] * 22, "complete": True} for j in jobs]
        return jobs
    monkeypatch.setattr(ib, "parallel", fake_parallel)
    checked = []
    monkeypatch.setattr(ib, "analyze", lambda out, acq, searches: checked.append((acq, searches)))
    assert ib.main() == 0
    acquisitions, jobs = checked[0]
    assert len(acquisitions) == 64 and len(jobs) == 2816
    assert all(j["task"] in ib.TARGETS for j in jobs)
    assert len({(j["task"], j["arm"], j["replicate"]) for j in jobs}) == 2816
    assert len({j["seed"] for j in jobs}) == 64
    for target in ib.TARGETS:
        assert sum(j["task"] == target for j in jobs) == 704
        for ref in ("uniform", "hand", "fit"):
            assert len([j for j in jobs if j["task"] == target and j["arm"] == ref]) == 64
    assert all(str(tmp_path) in j["out"] for j in jobs)


def test_full_roster_cost_and_analysis(tmp_path, monkeypatch):
    # Synthetic data test the endpoint algebra and output shape, not significance.
    rows = []
    for f in ib.FAMILIES:
        for a in ib.ARMS:
            for i in range(16):
                rows.append(dict(family=f, arm=a, replicate=i, complete=True,
                                 seconds=10, depth=[20], generations=20, solves=48))
    searches = []
    for t in ib.TARGETS:
        for arm in ib.ARMS:
            for i in range(16):
                for s in range(16):
                    searches.append(dict(task=t, arm=f"{arm}/{i}", replicate=s,
                                         complete=True, time=100 if arm == "inherited" else 200,
                                         event=True, seconds=1 if arm == "inherited" else 2))
        for ref in ("uniform", "hand", "fit"):
            for s in range(64):
                searches.append(dict(task=t, arm=ref, replicate=s, complete=True,
                                     time=200, event=True, seconds=2))
    original = ib.crossed_effect
    monkeypatch.setattr(ib, "crossed_effect", lambda *a, **kw: original(*a, **(kw | {"draws": 50})))
    monkeypatch.setattr(ib, "plot", lambda *a: None)
    result = ib.analyze(tmp_path, rows, searches)
    assert result["primary"]["pooled"]["ratio"] == pytest.approx(2)
    assert result["inherited_over_reference"]["uniform"]["pooled"]["ratio"] == pytest.approx(0.5)
    assert result["endpoint_rule"] == "linkage advantage" and result["useful_interval"]
    assert len(result["run_scores"]) == 64
    assert result["break_even"]["sum"]["uniform"]["searches"] == pytest.approx(10)
    assert (tmp_path / "result.json").exists() and (tmp_path / "COMPLETE").exists()
    searches[0]["complete"] = False
    with pytest.raises(RuntimeError, match="infrastructure"):
        ib.analyze(tmp_path, rows, searches)
