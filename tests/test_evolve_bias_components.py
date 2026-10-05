"""Scientific gate, event, diagnostic and fixed one-look orchestration fidelity."""

import itertools
import json
import time

import numpy as np
import pytest

from experiments.chem_tape import evolve_bias as eb
from experiments.chem_tape import evolve_bias_components as ec
from tests.test_evolve_bias import genome, planted, job, survival_row


def estimate(lo, hi, ratio=None, finite=1):
    return dict(
        lower=lo,
        upper=hi,
        ratio=ratio if ratio is not None else (lo + hi) / 2,
        finite_fraction=finite,
    )


def comps_for(task="sum2"):
    return {
        f"{task}/{a}/{b}": estimate(2, 4) if a == "U" else estimate(0.9, 1.2)
        for a, b in ec.PAIRS
    }


def test_factorial_vectors_reconstruct_and_coupled_config():
    spec = json.loads(eb.SPEC_PATH.read_text())
    ec.validate_vectors(spec)
    for t in ec.TASKS:
        v = {a: np.array(p) for a, p in ec.vectors(spec, t).items()}
        rest = [i for i in range(22) if i not in (1, 8)]
        assert np.array_equal(v["X"], spec["vectors"]["max" if t == "sum2" else "sum"])
        assert np.allclose(v["IG"][rest], (1 - v["X"][[1, 8]].sum()) / 20)
        assert np.allclose(
            v["R"][rest] / v["R"][rest].sum(), v["X"][rest] / v["X"][rest].sum()
        )
        for a in ec.ARMS:
            cfg = eb.config(
                t, a, ec.MASTER + 100000, ec.POP, ec.CAP, v[a], master=ec.MASTER
            )
            assert np.allclose(cfg.op_probs(22), v[a])
            assert cfg.pop_size == 1024 and cfg.generations == 255
            assert cfg.crossover_mate == "selected" and cfg.mutation_rate == 0.015


@pytest.mark.parametrize(
    "sx,fu", itertools.product(("within", "short", "open"), (True, False))
)
def test_exclusive_grid_and_strict_gates(sx, fu):
    comps = comps_for()
    comps["sum2/IG/X"] = {
        "within": estimate(0.8, 1.4),
        "short": estimate(1.6, 2),
        "open": estimate(1.2, 1.8),
    }[sx]
    comps["sum2/U/IG"] = estimate(1.01, 2) if fu else estimate(0.9, 2)
    a = ec.labels_for_task(comps, "sum2")["arms"]["IG"]
    expected = (
        "carries"
        if sx == "within" and fu
        else "falls short"
        if sx == "short"
        else "unresolved"
    )
    assert a["label"] == expected and a["vs_X"] == sx
    comps["sum2/IG/X"] = estimate(1.5, 1.5)
    assert ec.labels_for_task(comps, "sum2")["arms"]["IG"]["vs_X"] == "open"
    comps["sum2/U/X"] = estimate(1, 2)
    assert not ec.labels_for_task(comps, "sum2")["X_replicated"]


def test_reliability_guard_does_not_resolve():
    comps = comps_for()
    comps["sum2/IG/X"] = estimate(0.9, 1.2, finite=0.9899)
    assert ec.labels_for_task(comps, "sum2")["arms"]["IG"]["label"] == "unresolved"
    comps["sum2/U/X"]["upper"] = None
    assert ec.labels_for_task(comps, "sum2")["arms"]["R"]["label"].startswith(
        "not applicable"
    )


def test_cross_task_closure_never_upgrades_unresolved_or_nonreplication():
    by = {t: ec.labels_for_task(comps_for(t), t) for t in ec.TASKS}
    assert ec.closure(by) == "close: IG+R"
    by["sum2"]["arms"]["R"]["label"] = "falls short"
    assert ec.closure(by) == "park"
    by["max2"]["arms"]["R"]["label"] = "unresolved"
    assert ec.closure(by) == "close: IG"
    by["max2"]["X_replicated"] = False
    assert ec.closure(by) == "park"
    by["max2"]["X_replicated"] = True
    assert ec.closure(by, incomplete=True) == "park"
    for t in ec.TASKS:
        by[t]["arms"]["IG"]["label"] = "falls short"
    assert ec.closure(by) == "park"


def test_all_cells_pair_fresh_seeds_and_sampler(tmp_path):
    spec = json.loads(eb.SPEC_PATH.read_text())
    jobs = ec.jobs_for(spec, tmp_path, 350, time.monotonic() + 1)
    assert len(jobs) == 2800
    assert {j["replicate"] for j in jobs} == set(range(350))
    for t in ec.TASKS:
        by = [j for j in jobs if j["task"] == t and j["replicate"] == 0]
        assert len(by) == 4 and len({j["seed"] for j in by}) == 1
        hashes = {
            eb.make_task(t, j["seed"], master=j["master"]).labels.tobytes()
            + np.array(eb.make_task(t, j["seed"], master=j["master"]).inputs).tobytes()
            for j in by
        }
        assert len(hashes) == 1
        assert not np.array_equal(
            eb.training_indices(t, by[0]["seed"], ec.MASTER),
            eb.training_indices(t, by[0]["seed"]),
        )
        assert (
            len(
                {
                    eb.config(
                        t,
                        j["arm"],
                        j["seed"],
                        j["pop"],
                        j["cap"],
                        j["probs"],
                        master=j["master"],
                    ).seed
                    for j in by
                }
            )
            == 1
        )
    assert all(
        v["balance"] == 0.5 and v["both_labels"] for v in ec.sampler_audit().values()
    )


def test_alpha_is_new_family_not_inherited_old_labels():
    a = [survival_row(i, 100 + i) for i in range(50)]
    b = [{**r, "time": r["time"] / 2} for r in a]
    c = eb.compare(a, b, 1, 10000, alpha=ec.ALPHA)
    assert c["alpha"] == 0.005 and c["lower"] == 2 and c["upper"] == 2
    rows = [
        {**r, "task": t, "arm": arm} for t in ec.TASKS for arm in ec.ARMS for r in a
    ]
    cs = ec.comparisons(rows, 1000)
    assert len(cs) == 10 and all(
        c["alpha"] == 0.005 and c["look"] == 1 and "verdict" not in c
        for c in cs.values()
    )


def test_shortcut_capture_order_cap_and_other_family_agreement():
    # Exactly matches max2 and is nonexact on sum2; all listed training cases positive.
    shortcut = planted("max2")
    cases = np.ones((4, 64), dtype=bool)
    saved = {}
    pos, checked, count = eb.first_exact(
        [shortcut, shortcut, planted("sum2"), genome([20, 3])],
        cases,
        "sum2",
        {},
        saved,
        7,
    )
    assert pos == 2 and checked == 2 and count == 2
    assert len(saved) == 1
    s = next(iter(saved.values()))
    assert (
        s["first_gen"] == 7
        and s["other_family_agreement"] == 1
        and s["target_agreement"] == 0.9934
    )
    # 30 distinct nonexact, training-perfect candidate byte strings.
    gs = [genome([20, 3], [i] + [0]) for i in range(30)]
    saved = {}
    eb.first_exact(gs, np.ones((30, 64), bool), "sum2", {}, saved, 0)
    assert len(saved) == 20
    assert list(saved) == [g.tobytes().hex() for g in gs[:20]]


def test_diagnostics_do_not_change_evolution_endpoint_and_log_every_generation(
    monkeypatch,
):
    # Keep preexisting default loop identical, compare opt-in diagnostics.
    j = job(cap=16)
    j["master"] = ec.MASTER
    plain = eb.run_one(j, initial=[genome([0])] * 4)
    j["component_diagnostics"] = True
    logged = eb.run_one(j, initial=[genome([0])] * 4)
    for key in (
        "time",
        "event",
        "solver",
        "verifications",
        "shortcut_candidates",
        "processed_candidates",
        "training_sha256",
    ):
        assert plain[key] == logged[key]
    assert [v["gen"] for v in logged["training_history"]] == list(range(4))
    assert logged["first_training_100"] is None
    r = eb.run_one(j, initial=[planted("sum2")] * 4)
    assert r["first_training_075"] == 0 and r["first_training_100"] == 0


@pytest.mark.parametrize(
    "ops,tags,inp,gt",
    [
        ([1, 8, 20, 3], None, False, False),  # leader ops are inert
        ([20, 1, 5, 15, 8], None, True, True),
        ([20, 1, 5, 15, 8, 3], None, False, False),  # overwritten
        ([20, 1, 5, 15, 8, 20, 21], [1, 0, 0, 0, 0, 0, 1], True, True),  # RECV
        (
            [20, 1, 5, 15, 8, 20, 21],
            [1, 0, 0, 0, 0, 0, 2],
            False,
            False,
        ),  # disconnected
        ([20, 1, 3, 5, 15, 8], None, False, True),  # list can't be popped through int
        (
            [20, 21, 1, 5, 15, 8],
            [0, 0, 0, 0, 0, 0],
            True,
            True,
        ),  # ignored cyclic receive
        ([20, 1], None, False, False),  # nonint output defaults to0
    ],
)
def test_decoder_distinguishes_tape_presence_from_output_dependencies(
    ops, tags, inp, gt
):
    d = ec.decode(genome(ops, tags).tobytes().hex())
    assert d["tape_INPUT"] == (1 in ops) and d["tape_GT"] == (8 in ops)
    assert d["output_dependency_INPUT"] == inp and d["output_dependency_GT"] == gt
    assert "Conservative" in d["qualification"]


def test_fixed_one_look_orchestration(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["components", "--seconds", "9900"])
    calls = []

    def jobs(js, workers, out):
        calls.append(js)
        return [
            {
                **{k: v for k, v in j.items() if k not in ("deadline", "out")},
                "time": 100,
                "complete": True,
                "event": True,
                "history": [],
                "training_history": [],
                "shortcuts": [],
                "solver": None,
            }
            for j in js
        ]

    def sampling(spec, out, n, deadline):
        assert n == 125000000
        return {t: {a: eb.binomial(10, n) for a in ("IG", "R")} for t in ec.TASKS}

    monkeypatch.setattr(eb, "run_jobs", jobs)
    monkeypatch.setattr(ec, "sample_components", sampling)
    monkeypatch.setattr(ec, "decode_all", lambda *a: None)
    monkeypatch.setattr(ec, "plot_results", lambda *a: None)
    monkeypatch.setattr(
        ec,
        "comparisons",
        lambda rows, boot: {
            f"{t}/{a}/{b}": {**estimate(1, 1), "n": len(rows) // 8, "look": 1}
            for t in ec.TASKS
            for a, b in ec.PAIRS
        },
    )
    assert ec.main() == 0
    n = json.loads(ec.DESIGN.read_text())["n"]
    assert len(calls) == 1 and len(calls[0]) == 8 * n
    assert {j["replicate"] for j in calls[0]} == set(range(n))
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["decision"] == "park" and len(result["comparisons"]) == 10
    assert (tmp_path / "COMPLETE").exists()


def test_missingness_fails_queue_and_never_completes(tmp_path, monkeypatch):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["components", "--smoke"])

    def fail(*a):
        raise eb.Deadline("sampling timeout")

    monkeypatch.setattr(ec, "sample_components", fail)
    monkeypatch.setattr(ec, "decode_all", lambda *a: None)
    monkeypatch.setattr(ec, "plot_results", lambda *a: None)
    assert ec.main() == 1
    assert not (tmp_path / "COMPLETE").exists()
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["incomplete"] and all(
        c["ratio"] is None for c in result["comparisons"].values()
    )


def test_precision_rule_raises_n_before_any_new_data(tmp_path, monkeypatch):
    prior = dict(
        runs=[
            {**survival_row(i, 100), "task": t, "arm": "mismatched", "cap": ec.CAP}
            for t in ec.TASKS
            for i in range(10)
        ]
    )

    def compare(a, b, seed, boot, alpha):
        # n250 exact matching fails, n300 passes both checks.
        return estimate(0.8, 1.6 if len(a) == 250 else 1.2)

    monkeypatch.setattr(eb, "compare", compare)
    r = ec.precision(prior, tmp_path, trials=2, boot=10)
    assert r["n"] == 300 and r["precision_passed"]
    assert set(r["sizes"]) == {"250", "300"}
