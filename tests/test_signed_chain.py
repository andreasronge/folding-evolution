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


def test_confirmation_schedule_audit_and_release(saved, monkeypatch):
    b = run.load_bank()
    libs, identities, old_schedule, old_audit = saved
    full, smoke = run.schedules(b, confirm=True), run.schedules(b, True, True)
    assert len(full) == 5184 and len(smoke) == 12
    assert {m["cell"] for m in full} == set(b["split"]["protected"])
    assert {m["cell"] for m in smoke} <= set(b["split"]["development"])
    assert {m["repeat"] for m in full} == set(range(4))
    seeds = {s for m in full for s in m["seeds"]}
    assert seeds == set(range(20461000, 20474824))
    audit = run.seed_audit(b, old_schedule, old_audit, True)
    assert set(audit["published_seed_sets"]["confirmation"]) == seeds
    assert not seeds & set(audit["published_seed_sets"]["smoke"])
    frozen = run.freeze(b, libs, identities, True)
    assert frozen["task"] == run.CONFIRM_TASK and frozen["repeats"] == 4
    jobs = run.envelopes(full[:3], b, libs, frozen, confirm=True)
    assert jobs[0][-1] is None and jobs[1][-1] == [
        e["prefix"] for e in libs[0]["semantic"]
    ]
    assert jobs[2][-1] == frozen["gates"]
    assert all(set(j[1]) == {"id", "labels"} for j in jobs)
    assert len({tuple(m["seeds"]) for m in full[:3]}) == 1
    with pytest.raises(ValueError, match="unapproved/protected"):
        run.envelopes(full[:3], b, libs, frozen, smoke=True, confirm=True)
    with pytest.raises(ValueError, match="unapproved/protected"):
        run.envelopes(smoke[:3], b, libs, frozen, confirm=True)
    # Historical collisions must reject the entire plan before search.
    original = run.schedules

    def collide(bank, smoke=False, confirm=False):
        metas = original(bank, smoke, confirm)
        if confirm:
            for meta in metas[:3]:
                meta["seeds"][0] = 20460000  # 2044 development-only smoke.
        return metas

    monkeypatch.setattr(run, "schedules", collide)
    with pytest.raises(ValueError, match="collision"):
        run.seed_audit(b, old_schedule, old_audit, True)


def test_confirmation_interpretation_boundaries():
    assert run.classify_confirmation([0.7, 0.99]) == "saving"
    assert run.classify_confirmation([1.01, 1.2]) == "harm"
    assert run.classify_confirmation([0.7, 1]) == "unresolved"
    assert run.classify_confirmation([0.8, 1.1], 0.8) == "unresolved"
    arms = {
        "R-tree": dict(first_attempt_rate=0.85, capped_jobs=25, jobs=100),
        "R-gate": dict(solves=95, jobs=100),
    }
    assert run.validity_checks(arms)["intended_interpretation_supported"]
    arms["R-tree"]["first_attempt_rate"] = 0.86
    arms["R-tree"]["capped_jobs"] = 26
    arms["R-gate"]["solves"] = 94
    flags = run.validity_checks(arms)
    assert not flags["hard_tier_supported"] and flags["cap_dominated"]
    assert not flags["supplied_repertoire_reliable"]


def test_confirmation_summary_and_repayment(saved):
    # Synthetic completed rows test inference without performing protected search.
    b = run.load_bank()
    libs, identities, _, _ = saved
    frozen = run.freeze(b, libs, identities, True)
    by = {c["id"]: c for c in b["screen"]["cells"]}
    rows = []
    for m in run.schedules(b, confirm=True):
        t = Tree(tuple(by[m["cell"]]["canonical_tree"]))
        cost = 8192 if m["arm"] == "R-gate" else 32768
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
    result = run.summarize(rows, libs, b, frozen, 100, 8, confirm=True)
    assert result["protected_searches"] == 5184
    assert result["decision"] == "unresolved"
    assert result["secondary_20_percent_label"] == "20% saving excluded"
    assert not result["validity_checks"]["hard_tier_supported"]
    assert "confirmation_forecast" not in result
    assert len(result["per_cell"]) == 54 and len(result["per_build"]) == 72
    assert result["contrasts"]["R-gate/R-all"]["evaluations"]["point"] == 0.25
    assert result["contrasts"]["R-all/R-gate"]["evaluations"]["point"] == 4
    e = result["economics"]["evaluations"]
    assert e["repayment_unbounded"] and e["repayment_searches"] is None
    assert e["repayment_interval95"] == [None, None]
    assert all(
        c["acquisition_plus_search_label"] == "higher_total_cost"
        for c in e["cost_curves"]
    )
    with pytest.raises(ValueError, match="incomplete"):
        run.summarize(rows[:-1], libs, b, frozen, 100, 8, confirm=True)
    # A constant known saving preserves all arm pairs/repeats and gives finite repayment.
    for row in rows:
        if row["arm"] == "R-all":
            row["evaluations"] = row["attempts"][0]["evaluations"] = 24576
            row["worker_seconds"] = 24.576
    result = run.summarize(rows, libs, b, frozen, 100, 8, confirm=True)
    assert result["decision"] == "saving"  # Cost verdict survives validity flags.
    assert result["secondary_20_percent_label"] == ">20% saving"
    assert result["contrasts"]["R-all/R-tree"]["evaluations"]["interval95"] == [
        0.75,
        0.75,
    ]
    e = result["economics"]["evaluations"]
    assert not e["repayment_unbounded"]
    assert e["repayment_searches"] == pytest.approx(
        e["historical_acquisition"]["point"] / 8192
    )
    assert e["repayment_interval95"] == pytest.approx(
        [x / 8192 for x in e["historical_acquisition"]["interval95"]]
    )
    horizons = {c["searches"]: c for c in e["cost_curves"]}
    assert horizons[10]["acquisition_plus_search_label"] == "higher_total_cost"
    assert horizons[100]["acquisition_plus_search_label"] == "lower_total_cost"


def test_confirmation_preparation_roundtrip_and_phase_guard(tmp_path, saved):
    from experiments.chem_tape.composition_run import write_json

    b = run.load_bank()
    libs, identities, schedule, audit = saved
    payloads = dict(
        bank=b,
        method_freeze=run.freeze(b, libs, identities, True),
        libraries=libs,
        schedules=run.schedules(b, confirm=True),
        smoke_schedule=run.schedules(b, True, True),
        seed_audit=run.seed_audit(b, schedule, audit, True),
    )
    p = dict(admitted=True)
    for name, value in payloads.items():
        write_json(tmp_path, name + ".json", value)
        p[name + "_hash"] = digest(value)
    p["preparation_hash"] = digest(p)
    write_json(tmp_path, "preparation.json", p)
    assert run.load_prepared(tmp_path, True)[2] == libs
    with pytest.raises(ValueError, match="provenance"):
        run.load_prepared(tmp_path)  # Development cannot consume a confirmation freeze.
    changed = copy.deepcopy(payloads["schedules"])
    changed[0]["seeds"][0] += 1
    write_json(tmp_path, "schedules.json", changed)
    with pytest.raises(ValueError, match="provenance"):
        run.load_prepared(tmp_path, True)


def test_admission_replay_preserves_evidence_across_worktrees():
    b = run.load_bank()
    moved = copy.deepcopy(b)
    marker = "/experiments/chem_tape/data/"

    def relocate(path):
        return "/tmp/another-worktree" + marker + path.split(marker, 1)[1]

    moved["old_bank_hashes"] = {relocate(k): v for k, v in b["old_bank_hashes"].items()}
    for cell in moved["screen"]["cells"]:
        cell["old_bank"] = relocate(cell["old_bank"])
    assert run.admission_identity(b) == run.admission_identity(moved)
    moved["screen"]["cells"][0]["best_old_matches"] += 1
    assert run.admission_identity(b) != run.admission_identity(moved)
    moved["screen"]["cells"][0]["best_old_matches"] -= 1
    moved["old_bank_hashes"][next(iter(moved["old_bank_hashes"]))] = "changed"
    assert run.admission_identity(b) != run.admission_identity(moved)
