"""Chain probe's admission, source provenance, protected isolation and pricing."""

import copy

import numpy as np
import pytest

from experiments.chem_tape import signed_chain_bank as bank, signed_chain_run as run
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.tree_gp_search import Tree


@pytest.fixture(scope="module")
def saved():
    return run.saved_libraries()


def test_bank_and_pairing(saved):
    b = run.load_bank()
    assert digest(b) == run.BANK_HASH
    assert [len(b["split"][k]) for k in ("development", "protected")] == [6, 18]
    assert b["split"]["development"][:4] == list(bank.SEEN)
    assert len({c["label_hash"] for c in b["screen"]["cells"]}) == 24
    assert all(
        c["retained"] and c["best_matches"] < 625 and c["best_old_matches"] < 500
        for c in b["screen"]["cells"]
    )
    assert max(c["matches"] for c in b["pairwise"]) < 500
    full, smoke = run.schedules(b), run.schedules(b, True)
    assert len(full) == 864 and len(smoke) == 12
    assert all(m["cell"] not in b["split"]["protected"] for m in full + smoke)
    for i in range(0, len(full), 3):
        assert len({tuple(m["seeds"]) for m in full[i : i + 3]}) == 1
    audit = run.seed_audit(b, saved[2], saved[3])
    assert audit["admitted"]
    assert len(audit["published_seed_sets"]["development"]) == 288 * 8
    assert not set(audit["published_seed_sets"]["development"]) & set(
        audit["published_seed_sets"]["smoke"]
    )


def test_archive_identity_and_worker_isolation(saved):
    b = run.load_bank()
    libs, identities, _, _ = saved
    assert len(libs) == 24 and len(identities) == 24
    assert all(
        i["library_hash"] == digest(lib["semantic"]) for i, lib in zip(identities, libs)
    )
    frozen = run.freeze(b, libs, identities)
    metas = run.schedules(b, True)[:3]
    jobs = run.envelopes(metas, b, libs, frozen, True)
    assert jobs[0][-1] is None
    assert jobs[1][-1] == [e["prefix"] for e in libs[0]["semantic"]]
    assert jobs[2][-1] == frozen["gates"] and len(jobs[2][-1]) == 24
    assert all(set(j[1]) == {"id", "labels"} for j in jobs)
    changed = copy.deepcopy(b)
    for c in changed["screen"]["cells"]:
        c["helpers"], c["canonical_tree"] = [], []
    assert run.envelopes(metas, changed, libs, frozen, True) == jobs
    with pytest.raises(ValueError, match="unapproved/protected"):
        run.envelopes(
            [metas[0] | dict(cell=b["split"]["protected"][0])], b, libs, frozen, True
        )
    with pytest.raises(ValueError, match="unapproved/protected"):
        run.envelopes([metas[0] | dict(seeds=[1] * 8)], b, libs, frozen, True)


def test_crossed_variance_and_conditional_pricing():
    # An exactly centered balanced fixture has known ANOVA variances,
    # including search variance distinct from persistent build/cell effects.
    build = np.linspace(-0.2, 0.2, 24)[:, None, None]
    cell = np.linspace(-0.3, 0.3, 6)[None, :, None]
    search = np.array([-0.1, 0.1])[None, None, :]
    z = build + cell + search
    v = run.variance_components(z)
    assert v["search"] == pytest.approx(0.02)
    assert v["build"] == pytest.approx(float(np.var(build, ddof=1)))
    assert v["cell"] == pytest.approx(float(np.var(cell, ddof=1)))
    assert v["build_cell"] == 0
    # Price the actual roster, even when it is smaller than eighteen.
    b = {"split": {"protected": ["x"] * 11}}
    tree = np.ones((24, 6, 2)) * 10000
    arrays = {
        "evaluations": {"R-tree": tree, "R-all": tree * (0.8 + z * 0.2)},
        "worker_seconds": {a: np.ones((24, 6, 2)) * 5 for a in run.ARMS},
    }
    frozen = {
        "forecast": {
            "repeats": [1, 2, 4],
            "effects": [0.60, 0.75, 0.80, 0.85, 1.0],
            "sensitivity_variance_multiplier": 2,
        }
    }
    forecast = run.forecast(arrays, b, {"effective_concurrency": 7.6}, frozen)
    assert forecast["protected_cells"] == 11
    for p in forecast["prices"]:
        assert p["jobs"] == 11 * 24 * 3 * p["repeats"]
        assert p["tail_2x_seconds"] == 2 * p["central_wall_seconds"]
        assert (
            p["summed_timeout_seconds"]
            == p["prepare_timeout_seconds"] + p["scoring_timeout_seconds"]
        )
        central, conservative = p["scenarios"]
        assert conservative["expected_upper_lower"] > central["expected_upper_lower"]
        assert (
            next(
                s
                for s in central["effect_scenarios"]
                if s["hypothetical_effect"] == 0.8
            )["hypothetical_decision"]
            == "unresolved"
        )


def test_descriptive_summary_pairing_and_caps(saved):
    b = run.load_bank()
    libs, identities, _, _ = saved
    frozen = run.freeze(b, libs, identities)
    rows = []
    by = {c["id"]: c for c in b["screen"]["cells"]}
    for m in run.schedules(b):
        t = Tree(tuple(by[m["cell"]]["canonical_tree"]))
        cost = (
            256 * (2 + m["build"]) if m["arm"] == "R-tree" else 256 * (1 + m["build"])
        )
        rows.append(
            m
            | dict(
                solved=True,
                cap=524288,
                cutoff=65536,
                pop_size=256,
                evaluations=cost,
                worker_seconds=cost / 1000,
                attempts=[
                    dict(
                        seed=m["seeds"][0],
                        solved=True,
                        evaluations=cost,
                        solver_tree=list(t.prefix),
                        solver=list(t.program),
                    )
                ],
            )
        )
    result = run.summarize(rows, libs, b, frozen, 100, 8)
    assert (
        result["decision"] == "descriptive_no_efficacy_verdict"
        and result["protected_searches"] == 0
    )
    assert result["contrasts"]["R-all/R-tree"]["evaluations"]["point"] == pytest.approx(
        12.5 / 13.5
    )
    assert len(result["per_build"]) == 72 and len(result["per_cell"]) == 18
    assert result["confirmation_forecast"]["protected_cells"] == 18
    assert not result["strategy_recommendation"]["hard"]
    with pytest.raises(ValueError, match="incomplete"):
        run.summarize(rows[:-1], libs, b, frozen, 100, 8)
    bad = copy.deepcopy(rows)
    bad[0]["attempts"][0]["evaluations"] = 65535
    with pytest.raises(ValueError):
        run.summarize(bad, libs, b, frozen, 100, 8)


def test_preparation_json_roundtrip_and_tampering(tmp_path, saved):
    from experiments.chem_tape.composition_run import write_json

    b = run.load_bank()
    libs, identities, schedule, audit = saved
    payloads = dict(
        bank=b,
        method_freeze=run.freeze(b, libs, identities),
        libraries=libs,
        schedules=run.schedules(b),
        smoke_schedule=run.schedules(b, True),
        seed_audit=run.seed_audit(b, schedule, audit),
    )
    p = dict(admitted=True)
    for name, value in payloads.items():
        write_json(tmp_path, name + ".json", value)
        p[name + "_hash"] = digest(value)
    p["preparation_hash"] = digest(p)
    write_json(tmp_path, "preparation.json", p)
    assert run.load_prepared(tmp_path)[2] == libs
    changed = copy.deepcopy(libs)
    changed[0]["semantic"].pop()
    write_json(tmp_path, "libraries.json", changed)
    with pytest.raises(ValueError, match="provenance"):
        run.load_prepared(tmp_path)
    (tmp_path / "failure.json").write_text("{}")
    with pytest.raises(ValueError, match="recorded failure"):
        run.load_prepared(tmp_path)
