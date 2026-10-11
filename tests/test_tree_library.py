"""Source leakage, recurrence, support, off-path RNG and inference-unit checks."""

import pytest
from experiments.chem_tape.tree_gp_search import Tree, search
from experiments.chem_tape.tree_library import (
    canonical,
    extract,
    controls,
    donor_support,
)
from experiments.chem_tape.tree_library_report import classify, grid
from experiments.chem_tape.restart_gp_run import deterministic


def source_row(cell, prefix, solved=True):
    return dict(
        cell=cell,
        arm="R-tree",
        solved=solved,
        attempts=[dict(solver_tree=list(prefix))],
    )


def test_source_recurrence_root_exclusion_and_literal_forms():
    a = source_row("a", (11, 0, 1, 10, 9, 0, 1, 9, 2, 3))
    b = source_row("b", (11, 2, 3, 10, 9, 1, 0, 9, 3, 2))
    entries, _ = extract([a, a, b, source_row("b", (), False)], ["a", "b"])
    assert [e["nodes"] for e in entries] == [3, 3, 7]
    assert all(e["solver_count"] == 3 and len(e["source_cells"]) == 2 for e in entries)
    assert entries[0]["prefix"] == [9, 0, 1]
    assert canonical(Tree((10, 9, 0, 1, 9, 2, 3))) == canonical(
        Tree((10, 9, 1, 0, 9, 3, 2))
    )
    assert canonical(Tree((10, 0, 1))) != canonical(Tree((10, 1, 0)))
    # Repeated copies in one solver never inflate solver recurrence.
    repeats = source_row("a", (9, 9, 0, 1, 9, 0, 1))
    e, _ = extract([repeats, b], ["a", "b"])
    assert next(x for x in e if x["canonical"] == [9, 0, 1])["solver_count"] == 2
    assert extract([a], ["a"])[0] == []
    with pytest.raises(ValueError, match="source"):
        extract([a], ["other"])


def test_size_controls_support_bounded_and_reproducible():
    entries = [dict(nodes=3, compiled_length=5), dict(nodes=7, compiled_length=11)]
    a, _ = controls(entries, 32000001)
    b, _ = controls(entries, 32000001)
    assert a == b
    for e, c in zip(entries, a):
        t = Tree(tuple(c["prefix"]))
        assert (len(t.prefix), len(t.program)) == (e["nodes"], e["compiled_length"])
    assert (2, 2) not in donor_support()
    with pytest.raises(ValueError, match="no support"):
        controls([dict(nodes=2, compiled_length=2)], 32000001)
    with pytest.raises(ValueError, match="exhausted"):
        controls(entries, 32000001, max_draws=0)


def test_empty_library_preserves_rng_and_hook_statistics():
    inputs = [
        [a, b, c, d]
        for a in range(5)
        for b in range(5)
        for c in range(5)
        for d in range(5)
    ]
    # Never training-perfect: enforce a full small budget for operator checks.
    cell = dict(id="test", labels=[1234567] * 625)
    job = (cell, 32000002, 1024, 256, inputs, 0.5)
    off = search(job)
    empty = search(job, donor_library=[])
    empty_compare = empty | dict(
        operator={k: empty["operator"][k] for k in off["operator"]}
    )
    assert deterministic(off) == deterministic(empty_compare)
    donors = search(job, donor_library=[Tree((9, 0, 1))])
    s = donors["operator"]
    assert s["library_draws"] > 0
    assert s["library_draws"] + s["ordinary_donors"] == s["mutation"]
    assert s["library_insertions"] + s["rejected_library"] == s["library_draws"]
    assert donors["initial_tokens_hash"] == off["initial_tokens_hash"]


def test_outcome_precedence_and_resolved_control_loss():
    assert (
        classify([0.86, 0.89], [0.8, 0.99], [0, 0])
        == "useful_search_content_increment_consider_fresh_bank"
    )
    assert (
        classify([0.86, 0.89], [0.9, 1.1], [0, 0])
        == "baseline_gain_content_increment_unresolved"
    )
    assert (
        classify([0.8, 0.89], [1.01, 1.1], [0, 0])
        == "baseline_gain_random_control_better"
    )
    assert (
        classify([0.9, 1.1], [1.01, 1.1], [0, 0])
        == "learned_content_loses_to_size_control"
    )
    assert classify([0.9, 1.1], [0.9, 1.1], [0, 0]) == "end_saving_above_15pct_excluded"
    assert classify([0.8, 0.89], [0.8, 0.99], [-0.04, 0]) == "reliability_unresolved"
    with pytest.raises(ValueError, match="complete"):
        grid([], ["c"] * 8, "evaluations")


def test_library_schedule_seed_audit_and_changed_pairing():
    import copy
    from experiments.chem_tape.tree_library_run import schedules, seed_audit
    from experiments.chem_tape.component_transfer_run import load_saved

    saved, targets = load_saved()
    s = schedules(saved["banks.json"]["DG"], targets["DG"])
    audit = seed_audit(s)
    assert audit["admitted"] and not any(audit["overlaps"].values())
    assert [
        sum(m["arm"] == a for m in s["score"]) for a in ("R-tree", "R-lib", "R-size")
    ] == [1536] * 3
    bad = copy.deepcopy(s)
    bad["score"][0]["seeds"][0] += 1
    assert not seed_audit(bad)["admitted"]
    bad = copy.deepcopy(s)
    bad["source"][0]["seeds"][0] = bad["stage_source"][0]["seeds"][0]
    assert not seed_audit(bad)["admitted"]


def test_acquisition_block_statistics_economics_and_render(tmp_path):
    from experiments.chem_tape.tree_library_report import report, coverage

    cells = [str(i) for i in range(8)]
    bank = dict(
        split=dict(source=["source"]),
        screen=dict(
            cells=[
                dict(id=c, pairing=[[0, 1], [2, 3]] if i < 4 else [[0, 2], [1, 3]])
                for i, c in enumerate(cells)
            ]
            + [dict(id="source", pairing=[[0, 1], [2, 3]])]
        ),
    )
    assert sum(coverage(bank, cells).values()) == 4
    rows = []
    for b in range(24):
        for c in cells:
            for r in range(8):
                for a, factor in [("R-tree", 1.0), ("R-lib", 0.5), ("R-size", 0.75)]:
                    cost = 256 * (b + 1) * factor
                    rows.append(
                        dict(
                            build=b,
                            cell=c,
                            repeat=r,
                            arm=a,
                            seeds=[1000 * int(c) + 8 * r + k for k in range(8)],
                            evaluations=cost,
                            worker_seconds=cost / 256,
                            solved=True,
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
            acquisition_evaluations=25600,
            acquisition_worker_seconds=100.0,
            extraction_seconds=1.0,
            control_seconds=2.0,
            verification_seconds=3.0,
        )
        for b in range(24)
    ]
    report(tmp_path, rows, libraries, bank, cells, dict(preparation_hash="test"), {})
    import json

    result = json.loads((tmp_path / "result.json").read_text())
    assert result["contrasts"]["R-lib/R-tree"]["evaluations"]["interval95"] == [
        0.5,
        0.5,
    ]
    assert result["contrasts"]["R-lib/R-size"]["evaluations"][
        "interval95"
    ] == pytest.approx([2 / 3, 2 / 3])
    assert result["economics"]["worker_seconds"]["R-lib"]["acquisition"]["point"] == 104
    assert (
        result["economics"]["worker_seconds"]["R-size"]["acquisition"]["point"] == 106
    )
    assert result["economics"]["evaluations"]["R-lib"]["repayment_searches"] == 16
    for file in ("dynamics.png", "economics.png", "report.md"):
        assert (tmp_path / file).stat().st_size > 0
    with pytest.raises(ValueError, match="complete"):
        grid(rows[:-1], cells, "evaluations")


def test_stage_and_smoke_cannot_admit_scoring(tmp_path):
    import json
    from types import SimpleNamespace
    from experiments.chem_tape.tree_library_run import Runner
    from experiments.chem_tape.comparison_gate_bank import digest

    for flags in (
        dict(admitted=False, smoke=True),
        dict(admitted=True, smoke=False, stage_only=True),
    ):
        p = flags | dict(freeze={}, seed_audit={})
        p["preparation_hash"] = digest(p)
        (tmp_path / "preparation.json").write_text(json.dumps(p))
        runner = object.__new__(Runner)
        runner.args = SimpleNamespace(preparation=str(tmp_path))
        runner.freeze = {}
        runner.audit = {}
        with pytest.raises(ValueError, match="admitted unchanged full"):
            runner.score()


@pytest.mark.parametrize("solve_on,expected", [(0, 1), (3, 4), (None, 8)])
def test_library_retained_through_restarts_and_failure_cost(
    monkeypatch, solve_on, expected
):
    from experiments.chem_tape import tree_library_run as run

    donors = [Tree((9, 0, 1))]
    seeds = list(range(32000008, 32000016))
    seen = []

    def fake_search(job, donor_library):
        seen.append((job[1], donor_library))
        solved = len(seen) - 1 == solve_on
        return dict(
            solved=solved,
            solver=[2] if solved else None,
            evaluations=256 if solved else 65536,
        )

    monkeypatch.setattr(run, "search", fake_search)
    meta = dict(
        family="DG", cell="fixture", arm="R-lib", build=0, repeat=0, seeds=seeds
    )
    e = dict(
        meta=meta,
        cutoff=65536,
        donors=donors,
        first=dict(
            kind="tree",
            meta=dict(seed=seeds[0]),
            job=(None, seeds[0], 65536, 256, [], 0.5),
        ),
    )
    row = run.execute(e)
    assert len(seen) == expected and [s for s, _ in seen] == seeds[:expected]
    assert all(d is donors for _, d in seen)
    assert row["evaluations"] == (
        524288 if solve_on is None else solve_on * 65536 + 256
    )
