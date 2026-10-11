"""0833 roster/seed gates, source provenance, and decision/inference checks."""

import copy
import json
from types import SimpleNamespace

import pytest

from experiments.chem_tape import tree_source_run as run
from experiments.chem_tape import tree_source_report as report
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape import tree_uniform_run as prior


def test_fixed_rosters_pairing_and_seed_disjointness():
    saved, targets = load_saved()
    gs = prior.prior_run.snapshot("bank.json")
    schedules = run.schedules(saved["banks.json"]["TS"], gs, targets["TS"])
    assert {k: len(v) for k, v in schedules.items()} == dict(
        source=768,
        stage_source=64,
        gate=6912,
        native=2304,
        stage_gate=96,
        stage_native=48,
    )
    audit = run.seed_audit(schedules, saved, targets, gs)
    assert audit["admitted"] and not any(audit["overlaps"].values())
    assert all(m["family"] == "TS" for m in schedules["source"])
    assert not {m["cell"] for m in schedules["source"]} & {
        m["cell"] for m in schedules["native"] + schedules["gate"]
    }
    bad = copy.deepcopy(schedules)
    bad["gate"][0]["seeds"][0] += 1
    assert not run.seed_audit(bad, saved, targets, gs)["admitted"]


def test_source_family_is_never_relabelled_and_empty_fallback():
    saved, targets = load_saved()
    meta = dict(
        family="TS",
        cell=targets["TS"][0],
        arm="R-TS",
        build=0,
        repeat=0,
        seeds=[run.seed("test", k) for k in range(8)],
    )
    e = run.envelope(meta, saved, {"TS": [dict(entries=[], controls=[])]})
    assert e["meta"] == meta
    assert e["first"]["meta"]["family"] == "TS"
    assert e["donors"] == []
    with pytest.raises(ValueError, match="exactly 32 TS-source"):
        run.build_libraries(
            [dict(build=0, family="DG")] * 32, 1, saved["banks.json"]["TS"]
        )


@pytest.mark.parametrize(
    "ratio,guard,expected",
    [
        ([0.4, 0.79], [0, 0], "worthwhile_saving_supported"),
        ([0.81, 0.95], [0, 0], "saving_at_least_20pct_excluded"),
        ([0.7, 0.85], [0, 0], "usefulness_unresolved"),
        ([0.4, 0.7], [-0.04, 0], "reliability_unresolved"),
        ([0.4, 0.7], [-0.05, -0.04], "reliability_inferior"),
        ([0.4, 0.7], [-0.03, 0], "reliability_unresolved"),
    ],
)
def test_decision_and_native_reliability(ratio, guard, expected):
    assert report.classify(ratio, guard) == expected


def synthetic():
    targets = dict(
        GS=["GS" + str(i) for i in range(12)], TS=["TS" + str(i) for i in range(8)]
    )
    libs = {
        owner: [
            dict(
                build=b,
                entries=[],
                controls=[],
                source_solves=32,
                source_by_cell={},
                acquisition_evaluations=25600 if owner == "TS" else 51200,
                acquisition_worker_seconds=100.0 if owner == "TS" else 200.0,
                extraction_seconds=1.0,
                verification_seconds=3.0,
                control_seconds=2.0,
            )
            for b in range(24)
        ]
        for owner in ("TS", "DG")
    }
    rows = []
    for f, cells in targets.items():
        for b in range(24):
            for c in cells:
                for r in range(6 if f == "GS" else 4):
                    for a, factor in zip(
                        run.ARMS if f == "GS" else run.NATIVE_ARMS,
                        (1.0, 0.5, 0.4, 0.75),
                    ):
                        cost = (b + 1) * 256 * factor
                        rows.append(
                            dict(
                                family=f,
                                cell=c,
                                build=b,
                                repeat=r,
                                arm=a,
                                seeds=[b, r],
                                evaluations=cost,
                                worker_seconds=cost / 256,
                                solved=True,
                                attempt_count=1,
                                attempts=[
                                    dict(
                                        evaluations=cost,
                                        operator=dict(mutation=1),
                                        curve=[[cost, 64, 1, 10]],
                                        phenotype_diversity_curve=[[cost, 1]],
                                    )
                                ],
                            )
                        )
    return rows, libs, targets


def test_full_report_block_inference_costs_and_plots(tmp_path):
    rows, libs, targets = synthetic()
    report.report(tmp_path, rows, libs, targets, dict(preparation_hash="test"), {})
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["routing"] == "portable_complete_procedure_return_to_strategy"
    for f in ("GS", "TS"):
        d = result["destinations"][f]
        assert d["contrasts"]["R-TS/R-tree"]["evaluations"]["interval95"] == [0.5, 0.5]
        assert d["contrasts"]["R-TS/R-DG"]["evaluations"]["point"] == pytest.approx(
            1.25
        )
        # DG acquisitions are independently sampled, so unlike the paired primary
        # the varying-build TS/DG interval must not collapse to its point.
        dg_interval = d["contrasts"]["R-TS/R-DG"]["evaluations"]["interval95"]
        assert dg_interval[0] < 1.25 < dg_interval[1]
        assert d["economics"]["worker_seconds"]["R-TS"]["acquisition"]["point"] == 104
        assert d["economics"]["worker_seconds"]["R-DG"]["acquisition"]["point"] == 204
    assert (
        result["destinations"]["GS"]["economics"]["worker_seconds"]["R-sizeTS"][
            "acquisition"
        ]["point"]
        == 106
    )
    for name in ("report.md", "dynamics.png", "economics.png"):
        assert (tmp_path / name).stat().st_size > 0
    with pytest.raises(ValueError, match="all 9,216"):
        report.summarize(rows[:-1], libs, targets)


def test_smoke_cannot_authorize_scoring(tmp_path):
    p = dict(admitted=True, smoke=True, freeze={}, seed_audit={})
    p["preparation_hash"] = run.digest(p)
    (tmp_path / "preparation.json").write_text(json.dumps(p))
    runner = object.__new__(run.Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path))
    runner.freeze, runner.audit = {}, {}
    with pytest.raises(ValueError, match="admitted production"):
        runner.score()


def test_timing_gate_does_not_change_design_for_yield_or_effect():
    rows, libs, _ = synthetic()
    source = [
        dict(cell="source", worker_seconds=0.5, evaluations=1024, solved=False)
    ] * 64
    stages = {
        phase: [
            r for r in rows if r["family"] == f and r["build"] < 2 and r["repeat"] == 0
        ]
        for phase, f in (("stage_gate", "GS"), ("stage_native", "TS"))
    }
    batches = {
        k: dict(
            worker_seconds=sum(r["worker_seconds"] for r in rs),
            wall_seconds=sum(r["worker_seconds"] for r in rs) / 10,
        )
        for k, rs in ([("stage_source", source)] + list(stages.items()))
    }
    gate = run.stage_gate(source, stages, batches, libs, 90)
    assert gate["admitted"]
    # Empty libraries and zero solves are accepted; only timing decides admission.
    slow = copy.deepcopy(stages)
    for rs in slow.values():
        for r in rs:
            r["worker_seconds"] = 10000.0
    assert not run.stage_gate(source, slow, batches, libs, 90)["admitted"]
