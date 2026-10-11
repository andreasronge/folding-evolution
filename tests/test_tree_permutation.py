"""0524 matching, seed separation, fixed fallback, nested pairing and guards."""

import copy
from types import SimpleNamespace

import pytest

from experiments.chem_tape import gate_sum_run as previous
from experiments.chem_tape import tree_permutation as perm
from experiments.chem_tape import tree_permutation_report as reporting
from experiments.chem_tape.tree_permutation_run import (
    Runner,
    schedules,
    seed_audit,
    snapshot,
    stage_gate,
)


@pytest.mark.parametrize("repeats", [4, 6])
def test_approved_grid_and_disjoint_pairing(repeats):
    schedule = schedules(snapshot("bank.json"), repeats)
    assert seed_audit(schedule)["admitted"]
    assert len(schedule["score"]) == 24 * 18 * repeats * 3
    assert {r["realization"] for r in schedule["score"]} == set(range(repeats // 2))
    # The fallback retains construction seeds and common attempt seeds for the
    # first four repeats, while changing assignment specifically to modulo two.
    for m in schedule["score"]:
        assert m["realization"] == m["repeat"] % (repeats // 2)
    altered = copy.deepcopy(schedule)
    altered["score"][0]["seeds"][0] += 1
    assert not seed_audit(altered)["admitted"]
    altered = copy.deepcopy(schedule)
    for m in altered["score"][:3]:
        m["seeds"][0] = altered["stage"][0]["seeds"][0]
    assert not seed_audit(altered)["admitted"]


def test_every_frozen_pool_matches_and_multiplicity_survives():
    libraries = previous.snapshot("libraries.json")
    for lib in libraries:
        for r in range(3):
            s = perm.seed("construction", lib["build"], r)
            entries, _ = perm.permute(lib["entries"], s)
            assert entries == perm.permute(lib["entries"], s)[0]
            assert perm.signature(entries) == perm.signature(lib["entries"])
    # A fully invariant duplicate pool must not be deduplicated or discarded.
    entries = [dict(prefix=[9, 0, 0], nodes=3, compiled_length=5)] * 3
    result, _ = perm.permute(entries, perm.seed("unit-check"))
    assert len(result) == 3 and result == entries


def test_predicate_audit_respects_gt_order():
    forward = dict(prefix=[10, 9, 0, 1, 9, 2, 3])
    reverse = dict(prefix=[10, 9, 3, 2, 9, 1, 0])
    split = str(perm.PAIRS[0])
    assert perm.motifs([forward])["exact_predicate_counts"][split] == 1
    assert perm.motifs([reverse])["exact_predicate_counts"][split] == 0
    assert perm.motifs([reverse])["predicate_split_counts"][split] == 1


@pytest.mark.parametrize(
    "seconds, repeats, admitted", [(6.0, 6, True), (10.0, 4, True), (50.0, 4, False)]
)
def test_runtime_gate_reduces_all_arms_or_stops(seconds, repeats, admitted):
    rows = [
        dict(
            build=b,
            realization=r,
            worker_seconds=seconds,
            solved=True,
            evaluations=1024,
        )
        for b in range(24)
        for r in range(3)
        for _ in range(4)
    ]
    gate = stage_gate(
        rows,
        dict(worker_seconds=len(rows) * seconds, wall_seconds=len(rows) * seconds / 10),
        snapshot("replay.jsonl"),
    )
    assert gate["repeats"] == repeats and gate["admitted"] == admitted
    assert gate["realizations"] == repeats // 2
    assert gate["scoring_limit_seconds"] == 6000
    assert len(gate["per_construction"]) == 72


def stat(point, low=None, high=None):
    return dict(
        point=point,
        interval95=[point if low is None else low, point if high is None else high],
    )


def test_guard_precedence_and_unresolved_outcomes():
    assert (
        reporting.classify(stat(1), stat(0.35), stat(0.35), stat(0), stat(2))
        == "arrangement_unnecessary_at_this_resolution"
    )
    assert "control_too_weak" in reporting.classify(
        stat(1), stat(0.35), stat(0.35), stat(0), stat(1.5)
    )
    assert "replication_failed" in reporting.classify(
        stat(1), stat(0.6), stat(0.35), stat(0), stat(2)
    )
    assert "reliability_guard_failed" in reporting.classify(
        stat(1), stat(0.35), stat(0.35), stat(-0.03), stat(2)
    )
    assert "intact_information" in reporting.classify(
        stat(1.25, 1.11, 1.4), stat(0.35), stat(0.44), stat(0), stat(2)
    )
    assert reporting.classify(
        stat(1.24, 1.11, 1.4), stat(0.35), stat(0.44), stat(0), stat(2)
    ).startswith("unresolved")
    assert reporting.classify(
        stat(1.25, 1.10, 1.4), stat(0.35), stat(0.44), stat(0), stat(2)
    ).startswith("unresolved")


def fixture(repeats):
    bank = snapshot("bank.json")
    n = repeats // 2
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    rows = []
    for m in schedules(bank, repeats)["score"]:
        matched = tuple(map(tuple, by[m["cell"]]["pairing"])) == perm.PAIRS[0]
        # Vary construction quality markedly. Opposite effects in the paired
        # repeats must cancel, rather than become spurious bootstrap uncertainty.
        cost = 10000 * (m["build"] + 1) * (1, 3, 7)[m["realization"]]
        factor = 1 if m["arm"] == "R-tree" else 0.35
        if m["arm"] == "R-perm":
            factor *= (2 if matched else 1) * (0.5 if m["repeat"] < n else 1.5)
        rows.append(
            m
            | dict(
                evaluations=cost * factor,
                worker_seconds=cost * factor / 10000,
                solved=True,
                attempt_count=1,
                attempts=[
                    dict(
                        operator=dict(mutation=2, library_draws=1, library_insertions=1)
                    )
                ],
            )
        )
    libraries = previous.snapshot("libraries.json")
    for lib in libraries:
        lib["constructions"] = [
            dict(
                entries=perm.permute(
                    lib["entries"], perm.seed("construction", lib["build"], r)
                )[0],
                construction_seconds=0.1,
            )
            for r in range(3)
        ]
    preparation = dict(
        stage_gate=dict(realizations=n), preparation_hash="synthetic-unit-fixture"
    )
    return rows, libraries, bank, preparation


@pytest.mark.parametrize("repeats", [4, 6])
def test_hierarchical_pairing_economics_and_complete_reporting(
    tmp_path, monkeypatch, repeats
):
    monkeypatch.setattr(reporting, "DRAWS", 256)
    rows, libraries, bank, preparation = fixture(repeats)
    result = reporting.summarize(rows, libraries, bank, preparation)
    assert result["primary"]["interval95"] == pytest.approx([1, 1])
    assert result["positive_control"]["interval95"] == pytest.approx([2, 2])
    assert result["decision"] == "arrangement_unnecessary_at_this_resolution"
    assert result["groups"]["B/C"]["jobs_per_arm"] == 24 * 12 * repeats
    assert result["bootstrap"]["builds"] == 24
    acq = result["economics"]["B/C"]["worker_seconds"]
    assert acq["R-perm"]["acquisition"]["point"] - acq["R-lib"]["acquisition"][
        "point"
    ] == pytest.approx(0.1)
    for bad in (rows[:-1], rows + [rows[0]]):
        with pytest.raises(ValueError, match="complete"):
            reporting.summarize(bad, libraries, bank, preparation)
    bad = copy.deepcopy(rows)
    bad[0]["realization"] = 99
    with pytest.raises(ValueError, match="assignment"):
        reporting.summarize(bad, libraries, bank, preparation)
    reporting.report(tmp_path, rows, libraries, bank, preparation, {})
    assert all(
        (tmp_path / name).stat().st_size > 0
        for name in ("result.json", "report.md", "dynamics.png", "economics.png")
    )


def test_smoke_cannot_authorize_scoring(tmp_path):
    from experiments.chem_tape.composition_run import write_json

    runner = Runner.__new__(Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path))
    write_json(tmp_path, "preparation.json", dict(admitted=False, smoke=True))
    with pytest.raises(ValueError, match="admitted production"):
        runner.score()
