"""0348 fixed bank exposure, restart grid, economics and fail-closed gates."""

import copy
from types import SimpleNamespace

import pytest

from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape import gate_sum_bank as bank_module
from experiments.chem_tape.gate_sum_run import (
    schedules,
    seed_audit,
    snapshot,
    reconstruct,
    stage_gate,
    Runner,
)
from experiments.chem_tape.gate_sum_report import classify, summarize, report
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_library_report import grid


@pytest.fixture(scope="module")
def bank():
    saved, _ = load_saved()
    cells, excluded = bank_module.roster(list(saved["banks.json"].values()))
    return dict(
        screen=dict(cells=cells), split=bank_module.split(cells), exclusions=excluded
    )


def test_roster_fixed_semantics_and_probe_exclusion(bank):
    cells = bank["screen"]["cells"]
    assert [list(c["roles"].values()) for c in cells] == snapshot("planning.json")[
        "greedy_roles"
    ]
    assert len(cells) == 144 and not bank["exclusions"]
    parts = bank["split"]
    assert len(parts["development"]) == 4 and len(parts["protected"]) == 18
    assert not set(parts["development"]) & set(parts["protected"])
    by = {c["id"]: c for c in cells}
    assert set(bank_module.PROBED_ROLES) <= {
        tuple(by[c]["roles"].values()) for c in parts["development"]
    }
    assert sorted(
        [
            sum(bank_module.pairing(by[c]) == p for c in parts["protected"])
            for p in {bank_module.pairing(by[c]) for c in parts["protected"]}
        ]
    ) == [6, 6, 6]
    from experiments.chem_tape.assembly_bank import inputs_for

    for c in cells:
        t = Tree(tuple(c["canonical_tree"]))
        assert len(t.program) == 19
        assert [interpret(t, x) for x in inputs_for("D625")] == c["labels"]
    with pytest.raises(ValueError, match="probe exclusion"):
        bank_module.split(cells[1:])
    with pytest.raises(ValueError, match="six required"):
        bank_module.split(cells[:10])


def test_schedule_complete_paired_disjoint_and_tamper(bank):
    s = schedules(bank)
    audit = seed_audit(s)
    assert audit["admitted"]
    assert len(s["stage"]) == 288 and len(s["score"]) == 5184
    assert {m["cell"] for m in s["stage"]} == set(bank["split"]["development"])
    assert {m["cell"] for m in s["score"]} == set(bank["split"]["protected"])
    assert [
        sum(m["arm"] == a for m in s["score"]) for a in ("R-tree", "R-lib", "R-size")
    ] == [1728] * 3
    bad = copy.deepcopy(s)
    bad["score"][0]["seeds"][0] += 1
    assert not seed_audit(bad)["admitted"]
    bad = copy.deepcopy(s)
    for m in bad["score"][:3]:
        m["seeds"][0] = s["stage"][0]["seeds"][0]
    assert not seed_audit(bad)["admitted"]
    with pytest.raises(ValueError, match="complete"):
        grid([], bank["split"]["protected"], "evaluations", 4, 18)


def test_original_source_reconstruction_includes_failed_attempts():
    saved, _ = load_saved()
    libraries, audit = reconstruct(saved)
    assert audit["passed"] and audit["failed_source_jobs"] == 4
    assert libraries == snapshot("libraries.json")
    assert all(lib["acquisition_evaluations"] > 0 for lib in libraries)


def test_stage_gate_prices_actual_wrapper_all_arms():
    rows = [
        dict(arm=a, solved=True, evaluations=1024, worker_seconds=5.0)
        for a in ("R-tree", "R-lib", "R-size")
        for _ in range(96)
    ]
    gate = stage_gate(rows, dict(worker_seconds=1440, wall_seconds=144))
    assert gate["admitted"]
    assert gate["scoring_projected_seconds"] == pytest.approx(90 + 1.3 * 1728 * 15 / 10)
    assert all(v["projected_protected_solves"] == 1728 for v in gate["arms"].values())
    assert not stage_gate(rows, dict(worker_seconds=1440, wall_seconds=1000))[
        "admitted"
    ]


@pytest.mark.parametrize(
    "ratio,guard,outcome",
    [
        ([0.86, 0.89], [0, 0], "search_cost_transfers_return_to_strategy"),
        ([1.01, 1.1], [0, 0], "harm_end_route_expansion"),
        ([0.9, 1.1], [0, 0], "small_or_none_end_route_expansion"),
        ([0.8, 1.1], [0, 0], "unresolved_price_resolution_return_to_strategy"),
        ([0.86, 0.89], [-0.04, 0], "reliability_unresolved_price_resolution"),
        ([0.86, 0.89], [-0.05, -0.04], "reliability_inferior"),
    ],
)
def test_decision_precedence(ratio, guard, outcome):
    assert classify(ratio, [0.5, 1.1], guard) == outcome


def fake_rows(bank):
    rows = []
    for b in range(24):
        for ci, c in enumerate(bank["split"]["protected"]):
            for r in range(4):
                for a, factor in [("R-tree", 2), ("R-lib", 1), ("R-size", 2)]:
                    cost = 256 * (b + ci + r + 1) * factor
                    rows.append(
                        dict(
                            build=b,
                            cell=c,
                            repeat=r,
                            arm=a,
                            seeds=[
                                100000 * ci + 1000 * b + 8 * r + k for k in range(8)
                            ],
                            solved=True,
                            cap=524288,
                            evaluations=cost,
                            worker_seconds=cost / 256,
                            attempt_count=1,
                            attempts=[
                                dict(
                                    evaluations=cost,
                                    curve=[[cost, 64, 1, 10]],
                                    phenotype_diversity_curve=[[cost, 1]],
                                    operator=dict(crossover=1, mutation=1),
                                    shortcuts=0,
                                    training_perfect_individuals=1,
                                )
                            ],
                        )
                    )
    libraries = [
        dict(
            build=b,
            entries=[],
            controls=[],
            source_solves=32,
            acquisition_evaluations=25600 * (b + 1),
            acquisition_worker_seconds=100.0 * (b + 1),
            extraction_seconds=1,
            control_seconds=2,
            verification_seconds=3,
        )
        for b in range(24)
    ]
    return rows, libraries


def test_full_grid_inference_joint_economics_and_render(bank, tmp_path):
    rows, libraries = fake_rows(bank)
    targets = bank["split"]["protected"]
    result = summarize(rows, libraries, bank, targets)
    assert result["contrasts"]["R-lib/R-tree"]["evaluations"]["interval95"] == [
        0.5,
        0.5,
    ]
    assert result["solve_counts"] == {a: 1728 for a in ("R-tree", "R-lib", "R-size")}
    assert len(result["pair_split"]) == 3
    assert all(len(g["cells"]) == 6 for g in result["pair_split"].values())
    assert set(result["economics"]["evaluations"]["R-lib"]["horizons"]) == {
        "1",
        "10",
        "50",
        "100",
        "500",
        "1000",
    }
    assert result["economics"]["worker_seconds"]["R-lib"]["acquisition"][
        "point"
    ] == pytest.approx(1254)
    assert summarize(list(reversed(rows)), libraries, bank, targets) == result
    with pytest.raises(ValueError, match="complete"):
        summarize(rows[:-1], libraries, bank, targets)
    bad = copy.deepcopy(rows)
    bad[0]["seeds"][0] += 1
    with pytest.raises(ValueError, match="pairing"):
        summarize(bad, libraries, bank, targets)
    report(tmp_path, rows, libraries, bank, targets, dict(preparation_hash="test"), {})
    assert (tmp_path / "dynamics.png").stat().st_size > 10000
    assert (tmp_path / "economics.png").stat().st_size > 10000
    assert "Two cells probed before freeze" in (tmp_path / "report.md").read_text()


def test_nonpositive_savings_retains_unbounded_repayment(bank):
    rows, libraries = fake_rows(bank)
    for row in rows:
        if row["arm"] == "R-lib":
            row["evaluations"] *= 2
            row["worker_seconds"] *= 2
    result = summarize(rows, libraries, bank, bank["split"]["protected"])
    for metric in ("evaluations", "worker_seconds"):
        econ = result["economics"][metric]["R-lib"]
        assert econ["repayment_searches"] is None
        assert econ["repayment_unbounded"]
        assert econ["repayment_interval95"] == [None, None]


def test_smoke_preparation_cannot_authorize_protected_jobs(tmp_path):
    # The scoring gate must reject before any job is submitted.
    import json

    (tmp_path / "preparation.json").write_text(
        json.dumps(dict(admitted=False, smoke=True))
    )
    runner = object.__new__(Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path))
    runner.freeze = {}
    runner.audit = {}
    runner.jobs = lambda *a, **kw: pytest.fail("protected jobs were submitted")
    with pytest.raises(ValueError, match="fully admitted"):
        runner.score()
