"""Confirmation roster and uncertainty checks against deliberately structured data."""

import numpy as np
import pytest

from experiments.chem_tape.independent_input_run import (
    load_frozen,
    schedules,
    score_projection,
)
from experiments.chem_tape.independent_input_protected_report import (
    summarize,
    decision,
    economics,
)


def test_confirmation_roster_freshness_and_smoke_protection():
    bank, _ = load_frozen()
    source, target = schedules(bank, protected=True)
    pilot_source, pilot_target = schedules(bank)
    assert len(source) == 768 and len(target) == 896
    assert {r["cell"] for r in target} == set(bank["split"]["protected"])
    assert not {r["cell"] for r in source} & {r["cell"] for r in target}
    assert not {r["seed"] for r in source + target} & {
        r["seed"] for r in pilot_source + pilot_target
    }
    for ci, cid in enumerate(bank["split"]["source"]):
        for phase, base in (("first_G4", 500000), ("adaptive", 600000)):
            rs = [r for r in source if r["phase"] == phase and r["cell"] == cid]
            assert {r["seed"] for r in rs} == {
                base + 1000 * b + 10 * ci + a for b in range(24) for a in range(4)
            }
    for ci, cid in enumerate(bank["split"]["protected"]):
        for arm, n in (("G4", 48), ("A8", 48), ("O", 16)):
            rs = [r for r in target if r["cell"] == cid and r["arm"] == arm]
            assert [r["seed"] for r in rs] == [700000 + 1000 * ci + i for i in range(n)]
            assert all(r["build"] == r["ordinal"] // 2 for r in rs)
    ss, st = schedules(bank, smoke=True, protected=True)
    assert not {r["cell"] for r in ss + st} & set(bank["split"]["protected"])
    assert not {r["seed"] for r in ss + st} & {
        r["seed"] for r in source + target + pilot_source + pilot_target
    }
    assert np.isclose(
        score_projection(target, 30, 9.2, 30, 9.2),
        1.3 * (384 * 30 + 384 * 9.2 + 128 * 30) / 9.2 + 90,
    )


def structured_rows(variable_build=False, variable_baseline=False):
    rows = []
    for c in range(8):
        for a, n in (("G4", 48), ("A8", 48), ("O", 16)):
            for i in range(n):
                # Entire builds vary together; uncertainty must not be divided by 8 cells.
                ev = 32768 if a == "G4" else 4096
                if variable_build and a == "A8":
                    ev = 256 * 2 ** (i // 2 % 10)
                if variable_baseline and a == "G4":
                    ev = 256 * 2 ** (i % 10)
                rows.append(
                    dict(
                        cell=str(c),
                        arm=a,
                        ordinal=i,
                        build=i // 2,
                        seed=700000 + 1000 * c + i,
                        evaluations=ev,
                        cap=524288,
                        solved=True,
                        seconds=1,
                    )
                )
    return rows


def test_interval_keeps_between_build_and_baseline_uncertainty():
    fixed = summarize(structured_rows(), 24, draws=512)
    assert np.allclose(fixed["ratios"]["G4/A8"]["interval95"], [8, 8])
    for kwargs in (dict(variable_build=True), dict(variable_baseline=True)):
        s = summarize(structured_rows(**kwargs), 24, draws=512)
        lo, hi = s["ratios"]["G4/A8"]["interval95"]
        assert hi / lo > 1.2
        assert s["bootstrap"]["G4"].startswith("one shared")
    with pytest.raises(ValueError, match="roster"):
        summarize(structured_rows()[:-1], 24, draws=8)


def test_penalty_sensitive_label_and_all_capped_interpretation():
    rows = structured_rows()
    for r in rows:
        if r["arm"] == "G4":
            r.update(evaluations=r["cap"], solved=False)
        else:
            r["evaluations"] = 400000
    two, one = summarize(rows, 24, draws=64), summarize(rows, 24, penalty=1, draws=64)
    assert two["decision"].startswith("useful protected-cell replication")
    assert one["decision"] == "not worthwhile at this margin"
    for r in rows:
        r.update(evaluations=r["cap"], solved=False)
    capped = summarize(rows, 24, draws=64)
    assert np.isclose(capped["ratios"]["G4/A8"]["point"], 1)
    assert decision([1.5, 2]) == decision([1, 1.5]) == "unresolved"


def test_acquisition_charged_once_and_no_finite_repayment_for_no_savings():
    rows = structured_rows()
    builds = {
        str(b): dict(
            acquisition=dict(
                evaluations=1000,
                source_worker_seconds=10,
                verification_seconds=1,
                fit_seconds=2,
                extraction_seconds=3,
            )
        )
        for b in range(24)
    }
    intermediate = {
        b: dict(
            acquisition=dict(
                verification_seconds=1, fit_seconds=2, extraction_seconds=3
            ),
            yields=dict(a=int(b)),
            library=dict(fragments=[]),
        )
        for b in builds
    }
    costs = economics(rows, builds, intermediate, summarize(rows, 24, draws=8))
    assert costs["acquisition_total_evaluations"] == 24000
    assert costs["acquisition_mean_worker_seconds"] == 22
    assert np.isclose(costs["repayment_searches"], 1000 / (32768 - 4096))
    assert all(v["target_searches"] == 16 for v in costs["per_build"].values())
    for r in rows:
        r["evaluations"] = 32768
    costs = economics(rows, builds, intermediate, summarize(rows, 24, draws=8))
    assert costs["repayment_searches"] is None


def test_full_report_handles_24_fresh_and_8_old_builds(tmp_path, monkeypatch):
    import json
    from experiments.chem_tape import independent_input_protected_report as module

    bank, old = load_frozen()
    _, schedule = schedules(bank, protected=True)
    rows = [
        dict(
            r,
            evaluations=32768 if r["arm"] == "G4" else 4096,
            cap=524288,
            solved=True,
            seconds=1,
        )
        for r in schedule
    ]
    builds = {
        str(b): dict(
            acquisition=dict(
                evaluations=1000,
                source_worker_seconds=10,
                verification_seconds=1,
                fit_seconds=2,
                extraction_seconds=3,
            )
        )
        for b in range(24)
    }
    intermediate = {
        b: dict(
            acquisition=dict(
                verification_seconds=1, fit_seconds=2, extraction_seconds=3
            ),
            yields=dict(a=int(b)),
            library=dict(fragments=[]),
        )
        for b in builds
    }
    (tmp_path / "bank.json").write_text(json.dumps(bank))
    (tmp_path / "seed_builds.json").write_text(json.dumps(intermediate))
    monkeypatch.setattr(module, "plot", lambda *args, **kwargs: None)
    module.report(
        tmp_path,
        rows,
        builds,
        old,
        dict(prepare_seconds=100),
        dict(effective_workers=9),
    )
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == "protected_confirmation_complete"
    assert result["summary"]["solve_counts"]["A8"]["attempts"] == 384
    assert result["summary"]["solve_counts"]["O"]["attempts"] == 128
    assert len(result["subgroups"]["unseen_pairing"]["cells"]) == 3
    assert len(result["subgroups"]["source_seen_pairing"]["cells"]) == 5
    assert result["summary"]["decision"].startswith("useful protected-cell replication")
    assert result["protected_performance_scored"] is True
    assert (tmp_path / "report.md").is_file()
