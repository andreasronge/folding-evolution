"""Mechanism, episode ordering, exact endpoint, and crossed uncertainty checks."""
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


@pytest.mark.parametrize("arm", ib.ARMS)
@pytest.mark.parametrize("hit", [0, 1, 3, None])
def test_fixed_episode_first_hit_verifier_and_counts(monkeypatch, arm, hit):
    calls = []
    def exact(pop, cases, target, cache):
        gen = len(calls)
        calls.append(gen)
        return (1 if gen == hit else None), 1, 0
    monkeypatch.setattr(ib.eb, "first_exact", exact)
    row = ib.acquire(dict(family="sum", arm=arm, replicate=1, phase="test",
                          pop=4, episodes=1, generations=3))
    assert row["complete"] and row["generations"] == 3
    assert row["censuses"] == 4 and row["evaluations"] == 16
    ep = row["episodes"][0]
    assert ep["shuffles"] == (4 if arm == "broken" else 0)
    assert ep["solved"] == (hit is not None)
    assert len(calls) == (hit + 1 if hit is not None else 4)
    assert ep["verifications"] == len(calls)
    if hit is not None:
        assert ep["first_gen"] == hit and ep["position"] == 1
        assert ep["evaluations_to_exact"] == hit * 4 + 2
    assert len(row["price"]) == 3 and len(row["trajectories"]) == 1
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


def test_crossed_bootstrap_shared_seed_and_paired_runs():
    common = np.arange(20)[:, None, None] / 4
    learned = np.broadcast_to(common, (20, 2, 16)).copy()
    learned[:, :, :8] += np.log(4)
    tensors = dict(family="sum", inherited=learned, broken=learned + np.log(2),
                   uniform=learned[:1] + np.log(2), hand=learned[:1], fit=learned[:1])
    out = ib.crossed_effects(tensors, draws=1000)
    linkage = out["broken_over_inherited"]
    assert linkage["ratio"] == pytest.approx(2)
    assert linkage["lower"] == pytest.approx(2) and linkage["upper"] == pytest.approx(2)
    # A distinct target-specific reference interaction creates seed uncertainty.
    constant = np.zeros((20, 2, 16))
    reference = np.zeros((1, 2, 16))
    reference[:, :, :8] = np.log(4)
    out = ib.crossed_effects(dict(family="sum", inherited=constant, broken=constant,
                                uniform=reference, hand=reference, fit=reference), draws=1000)
    assert out["uniform_over_inherited"]["upper"] > out["uniform_over_inherited"]["lower"]
    assert out["uniform_over_inherited"] == out["fit_over_inherited"]
    sc = out["inherited_over_scaffold"]
    assert sc["lower"] == pytest.approx(1 / out["uniform_over_inherited"]["upper"])


def timing_rows():
    return [dict(task=t, arm=a, seconds=1, complete=True) for t in ib.TARGETS for a in ib.ARMS + ib.REFERENCES]


def test_cost_gate_uses_weighted_means_and_fixed_roster():
    acq = [dict(family=f, arm=a, seconds=10, complete=True) for f in ib.FAMILIES for a in ib.ARMS]
    searches = timing_rows()
    out = ib.projection(acq, searches)
    assert out["feasible"] and out["acquisition_seconds"] == 89
    assert out["scoring_seconds"]["sum"] == pytest.approx(137.6 + .9)
    expensive = [dict(r, seconds=1000) for r in searches]
    assert not ib.projection(acq, expensive)["feasible"]
    reduced = ib.projection(acq, expensive, include_fit=False)
    assert reduced["total_seconds"] < ib.projection(acq, expensive)["total_seconds"]
    assert reduced["reference_arms"] == ("uniform", "hand")
    acq[0]["complete"] = False
    assert not ib.projection(acq, searches)["feasible"]


def synthetic_acquisitions():
    rows = []
    for f in ib.FAMILIES:
        for a in ib.ARMS:
            for i in range(ib.ACQUISITIONS):
                episodes = [dict(target=f + ("1" if e % 2 == 0 else "5"),
                    generations=128, censuses=129, evaluations=129 * ib.POP,
                    shuffles=129 if a == "broken" else 0) for e in range(48)]
                rows.append(dict(family=f, arm=a, replicate=i, phase="main", master=ib.MASTER,
                    complete=True, seconds=10, verifier_seconds=1, depth=[20], generations=6144,
                    censuses=6192, evaluations=6192 * ib.POP, solves=48, episodes=episodes,
                    trajectories=[dict(mean_p=[1 / 22] * 22)] * 48,
                    price=[{}] * 6144, theta=np.zeros((1,22)).tolist(),
                    probs=ib.probabilities(np.zeros(22)).tolist()))
    return rows


@pytest.mark.parametrize("include_fit,total", [(True, 2752), (False, 2688)])
def test_full_roster_and_pipeline_wiring(tmp_path, include_fit, total):
    acquisitions = synthetic_acquisitions()
    ib.check_acquisitions(acquisitions)
    jobs = [j for f in ib.FAMILIES for j in ib.scoring_jobs(tmp_path, acquisitions, f, include_fit=include_fit)]
    assert len(acquisitions) == 80 and len(jobs) == total
    assert len({(j["task"], j["arm"], j["replicate"]) for j in jobs}) == total
    assert len({j["seed"] for j in jobs}) == 16
    for target in ib.TARGETS:
        assert sum(j["task"] == target for j in jobs) == total // 4
    assert all(str(tmp_path) in j["out"] for j in jobs)
    manifest = ib.manifest(include_fit=include_fit)
    assert manifest["frozen_search_count"] == total
    assert manifest["reference_scoring_indices"] == list(range(16))
    assert ("fit" in manifest["reference_arms"]) == include_fit
    acquisitions[0]["generations"] = 0
    with pytest.raises(RuntimeError, match="schedule"):
        ib.check_acquisitions(acquisitions)


@pytest.mark.parametrize("include_fit", [True, False])
def test_full_roster_cost_and_separate_family_analysis(tmp_path, monkeypatch, include_fit):
    acquisitions = synthetic_acquisitions()
    jobs = [j for f in ib.FAMILIES for j in ib.scoring_jobs(tmp_path, acquisitions, f, include_fit=include_fit)]
    searches = []
    for j in jobs:
        # Sum acquires 2x, max is bounded. Broken looks advantageous in both;
        # it cannot serve as the primary reference or flip the max verdict.
        cost = (100 if j["task"].startswith("sum") else 400) if j["arm"].startswith("inherited/") else 200
        if j["arm"].startswith("broken/"):
            cost = 800
        searches.append(dict(j, complete=True, time=cost, event=True, seconds=cost / 100))
    monkeypatch.setattr(ib, "plot", lambda *a: None)
    result = ib.analyze(tmp_path, acquisitions, searches, draws=50, include_fit=include_fit)
    assert result["families"]["sum"]["primary"]["ratio"] == pytest.approx(2)
    assert result["families"]["sum"]["verdict"] == "acquired"
    assert result["families"]["max"]["primary"]["ratio"] == pytest.approx(.5)
    assert result["families"]["max"]["verdict"] == "bounded"
    assert result["families"]["max"]["effects"]["inherited_over_scaffold"]["ratio"] == pytest.approx(2)
    assert "pooled" not in result and len(result["run_scores"]) == 80
    assert result["reference_extras"] == "none"
    assert ("fit_over_inherited" in result["families"]["sum"]["effects"]) == include_fit
    assert result["families"]["sum"]["break_even"]["uniform"]["searches_by_seconds"] == pytest.approx(10)
    assert (tmp_path / "result.json").exists() and (tmp_path / "COMPLETE").exists()
    searches[0]["complete"] = False
    with pytest.raises(RuntimeError, match="infrastructure"):
        ib.analyze(tmp_path, acquisitions, searches, draws=50, include_fit=include_fit)
    searches[0]["complete"] = True
    with pytest.raises(RuntimeError, match="roster"):
        ib.analyze(tmp_path, acquisitions, searches + searches[:1], draws=50, include_fit=include_fit)
    with pytest.raises(RuntimeError, match="roster"):
        ib.analyze(tmp_path, acquisitions, searches[1:], draws=50, include_fit=include_fit)


def test_classification_boundaries():
    assert ib.classify(dict(ratio=1.5, lower=1.01, upper=2)) == "acquired"
    assert ib.classify(dict(ratio=1.5, lower=1.01, upper=1.49)) == "acquired"
    assert ib.classify(dict(ratio=1.4, lower=1.1, upper=1.49)) == "bounded"
    assert ib.classify(dict(ratio=1.5, lower=1, upper=2)) == "unresolved"
    assert ib.classify(dict(ratio=1, lower=.7, upper=1.5)) == "unresolved"


def test_staged_manifest_guard_and_saved_acquisitions(tmp_path, monkeypatch):
    import json
    import sys
    source = tmp_path / "acq"
    target = tmp_path / "sum"
    rows = synthetic_acquisitions()
    def fake_parallel(function, jobs, workers):
        assert function is ib.acquire and len(jobs) == 80
        for j in jobs:
            row = next(r for r in rows if (r["family"], r["arm"], r["replicate"]) ==
                       (j["family"], j["arm"], j["replicate"]))
            ib.eb.write_json(j["out"], row)
        return rows
    monkeypatch.setattr(ib, "parallel", fake_parallel)
    monkeypatch.setattr(ib, "validate", lambda: {})
    monkeypatch.setattr(sys, "argv", ["inherited_bias", "--mode", "acquire", "--out", str(source)])
    assert ib.main() == 0 and (source / "ACQUISITIONS_COMPLETE").exists()
    assert len(ib.load_acquisitions(source)) == 80
    manifest = json.loads((source / "manifest.json").read_text())
    manifest["master"] -= 1
    ib.eb.write_json(source / "manifest.json", manifest)
    monkeypatch.setattr(sys, "argv", ["inherited_bias", "--mode", "score", "--family", "sum",
                                    "--acquisitions", str(source), "--out", str(target)])
    with pytest.raises(RuntimeError, match="manifest"):
        ib.main()


def test_fit_omission_preserves_shared_bootstrap_draws():
    rng = np.random.default_rng(51)
    tensors = dict(family="sum", inherited=rng.normal(size=(20, 2, 16)),
                   broken=rng.normal(size=(20, 2, 16)))
    tensors.update({arm: rng.normal(size=(1, 2, 16)) for arm in ib.REFERENCES})
    full = ib.crossed_effects(dict(tensors), draws=100)
    reduced = ib.crossed_effects({k: v for k, v in tensors.items() if k != "fit"}, draws=100)
    assert reduced == {k: v for k, v in full.items() if k != "fit_over_inherited"}


@pytest.mark.parametrize("include_fit", [True, False])
def test_staged_cli_synthetic_score_analysis_and_plots(tmp_path, monkeypatch, include_fit):
    """Exercise both approved rosters without inspecting new frozen performance."""
    import json
    import sys
    acquisitions = synthetic_acquisitions()
    roots = {name: tmp_path / name for name in ("acq", "sum", "max", "analysis")}
    flags = [] if include_fit else ["--omit-fit"]

    def fake_parallel(function, jobs, workers):
        rows = []
        for job in jobs:
            if function is ib.acquire:
                row = next(r for r in acquisitions if (r["family"], r["arm"], r["replicate"]) ==
                           (job["family"], job["arm"], job["replicate"]))
            else:
                assert function is ib.score
                row = dict(job, complete=True, time=ib.CAP, event=False, seconds=1,
                           history=[dict(gen=0, best=.5, distinct=32)])
            ib.eb.write_json(job["out"], row)
            rows.append(row)
        return rows

    monkeypatch.setattr(ib, "parallel", fake_parallel)
    monkeypatch.setattr(ib, "validate", lambda: {})
    def run(mode, root, extra=(), roster_flags=None):
        monkeypatch.setattr(sys, "argv", ["inherited_bias", "--mode", mode, "--out", str(root),
                                        *(flags if roster_flags is None else roster_flags), *extra])
        return ib.main()

    assert run("acquire", roots["acq"]) == 0
    # Every stage must use the same reference arms, even acquisition.
    with pytest.raises(RuntimeError, match="manifest"):
        run("score", tmp_path / "mismatch", ["--family", "sum", "--acquisitions", str(roots["acq"])],
            roster_flags=["--omit-fit"] if include_fit else [])
    for family in ib.FAMILIES:
        assert run("score", roots[family], ["--family", family, "--acquisitions", str(roots["acq"])]) == 0
        assert (roots[family] / "SCORING_COMPLETE").exists()
    assert run("analyze", roots["analysis"], ["--acquisitions", str(roots["acq"]),
               "--sum-scores", str(roots["sum"]), "--max-scores", str(roots["max"])]) == 0
    result = json.loads((roots["analysis"] / "result.json").read_text())
    assert all(r["linkage_unidentified_by_both_censored"] for r in result["families"].values())
    assert all(r["verdict"] == "bounded" for r in result["families"].values())
    for name in ("trajectories.png", "search_trajectories.png", "report.md", "COMPLETE"):
        assert (roots["analysis"] / name).stat().st_size > 0


def test_job_deadlines_are_explicit_only(monkeypatch):
    seen = []
    monkeypatch.setattr(ib.eb, "run_one", lambda job: seen.append(job) or job)
    ib.score(ib.frozen_job("sum1", "uniform", [1 / 22] * 22, 0))
    assert seen[-1]["deadline"] == float("inf")
    ib.score(dict(task="sum1", deadline=123))
    assert seen[-1]["deadline"] == 123
    ib.score(dict(task="sum1", seconds=10))
    assert time.monotonic() < seen[-1]["deadline"] <= time.monotonic() + 10
    row = ib.acquire(dict(family="sum", arm="inherited", replicate=0, phase="test",
                          pop=4, episodes=1, generations=1, deadline=0))
    assert not row["complete"] and "not censoring" in row["error"]


def test_recovery_timing_roster_and_weighted_tail_price(tmp_path):
    from experiments.chem_tape import inherited_bias_recovery as rec
    jobs = rec.timing_jobs(tmp_path, synthetic_acquisitions())
    assert len(jobs) == 92
    assert {j["replicate"] for j in jobs} == {2000, 2001, 2002}
    assert len({(j["task"], j["arm"], j["replicate"]) for j in jobs}) == 92
    rows = [dict(j, seconds=10 if j["arm"].startswith("inherited/") else 20,
                 verifier_seconds=0, complete=True) for j in jobs]
    rows[0].update(seconds=110, verifier_seconds=100)
    p = rec.scoring_price(rows, 10)
    # 320 searches/cell, with the tail retained in its cell mean.
    assert p["sum"]["worker_seconds"] == (20 + 10 + 20 + 20) * 320 + 6 * 20 * 16
    assert p["sum"]["expected_seconds"] == p["sum"]["worker_seconds"] / 10 + .9 * 110
    assert p["sum"]["verifier_tail_count"] == 1
    assert p["sum"]["observed_tail_rate"] == 1 / 46
    assert p["sum"]["projected_verifier_tail_worker_seconds"] == 3200
    with pytest.raises(RuntimeError, match="roster"):
        rec.scoring_price(rows[:-1], 10)


@pytest.mark.parametrize("mismatch,over_budget", [(False, False), (True, False), (True, True)])
def test_selective_recovery_and_full_replay_fallback(tmp_path, monkeypatch, mismatch, over_budget):
    import copy
    import json
    from experiments.chem_tape import inherited_bias_recovery as rec
    source, out = tmp_path / "source", tmp_path / "out"
    source.mkdir()
    out.mkdir()
    # An old success sentinel must not survive a failed recovery.
    (out / "ACQUISITIONS_COMPLETE").write_text("stale")
    (source / "manifest.json").write_text('{}')
    originals = synthetic_acquisitions()
    complete = {rec.key(r): copy.deepcopy(r) for r in originals}
    paths = {}
    for row in originals:
        if rec.key(row) == rec.CUT:
            row.update(complete=False, trajectories=row["trajectories"][:30],
                       episodes=row["episodes"][:31])
        f, a, i = rec.key(row)
        p = source / "acquisition" / "main" / f / a / f"{i}.json"
        ib.eb.write_json(p, row)
        paths[rec.key(row)] = p
    monkeypatch.setattr(rec, "source_rows", lambda root: (originals, paths))
    monkeypatch.setattr(ib, "validate", lambda: {})
    calls = []
    def fake_parallel(function, jobs, workers):
        calls.append((len(jobs), workers))
        assert all(j["phase"] == "main" and "deadline" in j for j in jobs)
        result = []
        for j in jobs:
            row = copy.deepcopy(complete[rec.key(j)])
            row["seconds"] = 9999  # never compared for determinism
            if mismatch and len(jobs) == 3 and rec.key(j) == rec.REPLAYS[0]:
                row["theta"][0][0] = 1
            ib.eb.write_json(j["out"], row)
            result.append(row)
        return result
    monkeypatch.setattr(ib, "parallel", fake_parallel)
    if over_budget:
        monkeypatch.setattr(rec, "recovery_estimate", lambda rows: dict(full_replay_expected_seconds=20000))
        with pytest.raises(RuntimeError, match="remaining cumulative"):
            rec.recover(out, source)
        assert calls == [(3, 3)]
        assert not (out / "ACQUISITIONS_COMPLETE").exists()
        assert json.loads((out / "recovery.json").read_text())["fallback"]
        return
    record = rec.recover(out, source)
    assert calls == ([(3, 3), (80, 10)] if mismatch else [(3, 3)])
    assert record["fallback"] == mismatch
    assert sum(r["reused"] for r in record["source_rows"]) == (0 if mismatch else 79)
    assert len(ib.load_acquisitions(out)) == 80
    assert (out / "ACQUISITIONS_COMPLETE").exists()
    for r in record["source_rows"]:
        if r["reused"]:
            f, a, i = rec.key(r)
            assert rec.digest(out / "acquisition" / "main" / f / a / f"{i}.json") == r["sha256"]
    assert json.loads((out / "recovery.json").read_text())["complete"]


def test_replay_equality_excludes_runtime_but_checks_all_episode_endpoints():
    import copy
    from experiments.chem_tape import inherited_bias_recovery as rec
    row = synthetic_acquisitions()[0]
    row["episodes"][0].update(solved=True, first_gen=2, evaluations_to_exact=2050)
    new = copy.deepcopy(row)
    new["seconds"] = 2000
    new["episodes"][0]["seconds"] = 1000
    assert rec.replay_checks({rec.key(row): row}, [new])[0]["passed"]
    for field in ("solved", "first_gen", "evaluations_to_exact"):
        bad = copy.deepcopy(new)
        bad["episodes"][0][field] = None
        assert not rec.replay_checks({rec.key(row): row}, [bad])[0]["passed"]
    bad = copy.deepcopy(new)
    bad["probs"][0] += 1e-15
    assert not rec.replay_checks({rec.key(row): row}, [bad])[0]["passed"]
