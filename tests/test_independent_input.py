"""Language/bank and fixed-recipe invariants for the independent-input probe."""

import numpy as np
import pytest
from _folding_rust import rust_chem_execute

from folding_evolution.chem_tape import alphabet as a, executor as vm
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import _token_max
from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.independent_input_bank import (
    ALPHABET,
    roster,
    maximum_clique,
    validate,
)
from experiments.chem_tape.fragment_library import extract_windows
from experiments.chem_tape.fragment_operator import BlockOperator, trace
from experiments.chem_tape.solver_corpus_fit import small_source_counts, fit_context


@pytest.mark.parametrize("token,index", [(5, 0), (11, 0), (18, 1), (22, 2), (23, 3)])
@pytest.mark.parametrize("xs", [[], [9], [9, -7], [9, -7, 4], [9, -7, 4, -3]])
def test_indexed_python_rust(token, index, xs):
    expected = xs[index] if len(xs) > index else 0
    assert vm.execute_program([1, token], TA, xs, "intlist", ALPHABET) == expected
    assert (
        rust_chem_execute([1, token], "NOP", "NOP", xs, "intlist", ALPHABET) == expected
    )
    for consume in (False, True):
        for program, inp, kind in [
            ([token], xs, "intlist"),
            ([3, token], xs, "intlist"),
            ([1, token], "RE", "str"),
            ([1, 4, token], "RE", "str"),
            ([1, token], 12, "int"),
        ]:
            assert vm.execute_program(
                program, TA, inp, kind, ALPHABET, consume
            ) == rust_chem_execute(
                program, "NOP", "NOP", inp, kind, ALPHABET, 0, consume
            )
    vm._SAFE_POP_CONSUME = False
    stack = [("int", 7)]
    vm.resolve_op(token, TA, ALPHABET)(stack, xs, "intlist", TA)
    assert stack == [("int", 7), ("int", 0)]


def test_generic_prior_masks_and_short_typed_states():
    masses = np.diff(tables()["G4"][1], prepend=0)
    assert masses[5] + masses[11] == masses[18] == masses[22] == masses[23] == 3625
    assert _token_max(ChemTapeConfig(alphabet=ALPHABET)) == 23
    assert [i for i in range(24) if a.is_active(i, ALPHABET)] == list(range(1, 20)) + [
        22,
        23,
    ]
    assert [i for i in range(24) if a.is_separator(i, ALPHABET)] == [20, 21]
    assert validate(random_count=100, depth=2)["passed"]


def test_legacy_golden_replay():
    xs = [9, -7, 4, -3]
    expected = {
        "v1": [3, 3, 0, 0, 0],
        "v2_probe": [3, 3, 9, 0, 0],
        "v2_rmin": [3, 3, 9, -7, 0],
        "v2_rmin_first": [3, 3, 9, -7, 9],
        "v2_split": [3, 3, 9, 2, 1],
        "v2_min": [3, 3, 9, 0, 0],
        "v2_imax": [3, 3, 9, 0, 0],
    }
    for alphabet, values in expected.items():
        for token, answer in zip((5, 11, 18, 22, 23), values):
            assert vm.execute_program([1, token], TA, xs, "intlist", alphabet) == answer
            assert (
                rust_chem_execute([1, token], "NOP", "NOP", xs, "intlist", alphabet)
                == answer
            )


def test_empty_fit_library_and_fragment_suffix_preservation():
    ids = ["a", "b", "c", "d"]
    counts, yields = small_source_counts([], ids)
    table = fit_context(counts)
    assert np.array_equal(table, tables()["G4"])
    assert not any(yields.values())
    library = extract_windows(
        "DG0",
        [],
        [[0, 1, 2, 3]] * 96,
        {},
        list(range(96)),
        source_cells=ids,
        alphabet=ALPHABET,
    )
    assert not library["whole_corpus"]["fragments"]
    decoder = Decoder(table)
    original = np.random.default_rng(390002).integers(
        24000, size=(512, 32), dtype=np.int32
    )
    before = decoder.decode(original)
    for fragments in ([], [{"tokens": [1, 5, 1, 18, 7]}]):
        op = BlockOperator(
            "F", fragments, 390002, empty_fallback=True, alphabet=ALPHABET
        )
        edited, info = op.edit(original.copy(), decoder, force=True, boundary=True)
        actual = decoder.decode(edited)
        assert np.array_equal(actual, info["desired"])
        for j, (start, length) in enumerate(zip(info["starts"], info["lengths"])):
            outside = np.ones(32, dtype=bool)
            outside[start : start + length] = False
            assert np.array_equal(actual[j, outside], before[j, outside])
    assert (
        trace([1, 5, 1, 18, 7], [[4, 3, 2, 1]], ALPHABET)["executions"][0]["output"]
        == 7
    )


def test_roster_and_clique_determinism():
    cells = roster()
    assert len(cells) == 492
    assert sum(c["proper"] for c in cells) == 72
    assert all(len(c["canonical"]) == 16 for c in cells)
    assert len({c["label_hash"] for c in cells}) == len(cells)
    # Tiny graph demonstrates strict (not inclusive) 80% threshold.
    tiny = [
        dict(id=str(i), labels=lab)
        for i, lab in enumerate(([0] * 5, [0, 0, 0, 0, 1], [1] * 5))
    ]
    chosen = maximum_clique(tiny)
    assert [c["id"] for c in chosen] == ["0", "2"]


def test_frozen_rosters_old_identities_and_protection():
    from experiments.chem_tape.independent_input_run import load_frozen, schedules

    bank, old = load_frozen()
    source, target = schedules(bank)
    assert len(source) == 256 and len(target) == 192
    assert sum(r["phase"] == "first_G4" for r in source) == 128
    assert sum(r["phase"] == "adaptive" for r in source) == 128
    assert all(r["cell"] not in bank["split"]["protected"] for r in source + target)
    assert [b["identity"] for b in old["builds"]] == [
        f"{f}{i}|A8" for f in ("BE", "PA") for i in range(1, 5)
    ]
    for c in bank["split"]["development"]:
        for arm in ("G4", "A8", "O"):
            rs = [r for r in target if r["cell"] == c and r["arm"] == arm]
            assert len(rs) == 16
            assert {r["seed"] for r in rs} == {
                r["seed"] for r in target if r["cell"] == c and r["arm"] == "G4"
            }
    assert schedules(bank) == schedules(bank)


def test_invalid_bank_or_changed_protected_roster_refused():
    import copy
    from experiments.chem_tape.independent_input_run import load_frozen, validate_bank

    bank, _ = load_frozen()
    for change in ("overlap", "coverage", "shortscreen"):
        altered = copy.deepcopy(bank)
        if change == "overlap":
            altered["split"]["protected"][0] = altered["split"]["source"][0]
        elif change == "coverage":
            altered["split"]["source"] = altered["split"]["development"]
        else:
            altered["screen"]["max_depth"] = 8
        with pytest.raises(ValueError):
            validate_bank(altered)


def test_descriptive_variance_uses_shared_baseline_and_costs_failures():
    from experiments.chem_tape.independent_input_report import (
        summarize,
        precision_price,
    )

    rows = []
    for ci in range(4):
        for i in range(16):
            for arm in ("G4", "A8", "O"):
                rows.append(
                    dict(
                        cell=str(ci),
                        ordinal=i,
                        build=i // 2,
                        arm=arm,
                        cap=524288,
                        evaluations=524288 if i == 0 else (ci + 1) * (i + 1) * 256,
                        solved=i != 0,
                        seconds=20,
                    )
                )
    summary = summarize(rows, 8, draws=128)
    assert summary["ratios"]["G4/A8"]["point"] == 1
    assert all(v["solved"] == 60 for v in summary["solve_counts"].values())
    assert summary["bootstrap"]["G4"].startswith("one shared")
    builds = {
        str(b): dict(
            acquisition=dict(
                evaluations=100000,
                source_worker_seconds=400,
                verification_seconds=1,
                fit_seconds=2,
                extraction_seconds=3,
            )
        )
        for b in range(8)
    }
    prep = dict(
        effective_workers=9,
        source_build_costs={
            b: dict(verification_seconds=1, fit_seconds=2, extraction_seconds=3)
            for b in builds
        },
    )
    price = precision_price(rows, builds, prep, dict(effective_workers=8), summary)
    assert price["effective_workers"] == 8
    assert price["acquisition_mean_worker_seconds"] == 412
    assert price["baseline_fixed16_floor_factor"] > 1
    assert len(price["scenarios"]) == 2


def test_exact_timing_is_opt_in_and_preserves_search_streams():
    from experiments.chem_tape.composition_search import search

    inputs = [[0, 1, 2, 3]] * 80
    job = (
        dict(id="unreachable", labels=[99999] * 80),
        "G4",
        tables()["G4"],
        390005,
        768,
        256,
        inputs,
        ALPHABET,
    )
    old = search(job)
    measured = search(job, measure_exact=True)
    newkeys = {"exact_check_seconds", "exact_check_max_seconds", "exact_checks"}
    assert not set(old) & newkeys
    assert newkeys <= set(measured)
    timing = {"seconds", "budget_seconds", "decode_seconds"} | newkeys
    assert {k: v for k, v in old.items() if k not in timing} == {
        k: v for k, v in measured.items() if k not in timing
    }


def test_score_refuses_changed_admission_before_search(tmp_path):
    import argparse
    import json
    from experiments.chem_tape.independent_input_run import Runner
    from experiments.chem_tape.comparison_gate_bank import digest

    p = dict(smoke=False, admitted=True, median_first_yield=0)
    p["preparation_hash"] = digest(p)
    p["admitted"] = False
    path = tmp_path / "preparation.json"
    path.write_text(json.dumps(p))
    runner = Runner.__new__(Runner)
    runner.args = argparse.Namespace(preparation=str(path), smoke=False)
    with pytest.raises(ValueError, match="admission/timing record changed"):
        runner.score()
    assert not (tmp_path / "search.jsonl").exists()


def test_source_provenance_requires_complete_frozen_attempts():
    from experiments.chem_tape.independent_input_run import (
        load_frozen,
        schedules,
        validate_source_rows,
        CAP,
    )

    bank, _ = load_frozen()
    schedule, _ = schedules(bank)
    rows = [dict(r, cap=CAP, pop_size=256, solver=None, solved=False) for r in schedule]
    validate_source_rows(rows, schedule, CAP)
    for changed in (rows[:-1], rows + [rows[0]], [dict(rows[0], seed=1)] + rows[1:]):
        with pytest.raises(ValueError):
            validate_source_rows(changed, schedule, CAP)


@pytest.mark.parametrize("protected", [False, True])
@pytest.mark.parametrize(
    "first_yield, projection, elapsed, admitted",
    [
        (0, 100.0, 10.0, True),
        (3, 1770.0, 1470.0, True),
        (0, 1770.01, 10.0, False),
        (3, 100.0, 1470.01, False),
    ],
)
def test_full_admission_reports_sparse_yield_and_stops_only_for_runtime(
    tmp_path, monkeypatch, first_yield, projection, elapsed, admitted, protected
):
    import argparse
    import json
    from experiments.chem_tape.comparison_gate_bank import digest
    from experiments.chem_tape.independent_input_run import (
        Runner,
        load_frozen,
        schedules,
        CAP,
    )

    if protected:
        if projection >= 1770:
            projection += 2400
        if elapsed >= 1470:
            elapsed += 1500
    bank, _ = load_frozen()
    schedule, development = schedules(bank, protected=protected)
    nbuild = 24 if protected else 8
    rows = [dict(r, cap=CAP, pop_size=256, solver=None, solved=False) for r in schedule]
    for b in range(nbuild):
        selected = [r for r in rows if r["build"] == b and r["phase"] == "first_G4"]
        for row in selected[:first_yield]:
            row.update(solved=True, solver=[1])

    def order(r):
        return (r["build"], r["cell"], r["seed"], r["arm"])

    first = sorted([r for r in rows if r["phase"] == "first_G4"], key=order)
    adaptive = sorted([r for r in rows if r["phase"] == "adaptive"], key=order)
    builds = {
        str(b): dict(
            empty_cells=bank["split"]["source"],
            yields={c: 0 for c in bank["split"]["source"]},
            library=dict(fragments=[]),
            acquisition={},
        )
        for b in range(nbuild)
    }
    source = tmp_path / "source"
    source.mkdir()
    out = tmp_path / "score"
    out.mkdir()
    for name, data in [("builds.json", builds), ("seed_builds.json", builds)]:
        (source / name).write_text(json.dumps(data))
    for name, data in [("first.jsonl", first), ("adaptive.jsonl", adaptive)]:
        (source / name).write_text("".join(json.dumps(r) + "\n" for r in data))
    validation = dict(passed=True)
    freeze = dict(frozen_before_search=True)
    p = dict(
        smoke=False,
        freeze=freeze,
        validation=validation,
        validation_hash=digest(validation),
        builds_hash=digest(builds),
        seed_builds_hash=digest(builds),
        first_hash=digest(first),
        adaptive_hash=digest(adaptive),
        median_first_yield=float(first_yield),
        admitted=admitted,
        score_projected_seconds=projection,
        prepare_seconds=elapsed,
        reasons=["discovery obstacle"] + ([] if admitted else ["runtime obstacle"]),
    )
    p["preparation_hash"] = digest(p)
    path = source / "preparation.json"
    path.write_text(json.dumps(p))
    runner = Runner.__new__(Runner)
    runner.args = argparse.Namespace(
        preparation=str(path), smoke=False, protected=protected
    )
    runner.out = out
    runner.freeze = freeze
    runner.source_schedule = schedule
    runner.score_schedule = development
    runner.cap = CAP
    runner.config = {}
    if admitted:
        # Exercise the full scoring dispatch without paying for 192 searches.
        def jobs(actual, filename, phase):
            assert actual == development and len(actual) == (896 if protected else 192)
            assert filename == "search.jsonl" and phase == (
                "protected" if protected else "development"
            )
            runner.batches = {phase: {}}
            return actual

        def report(actual_out, actual_rows, *args):
            assert actual_out == out and actual_rows == development
            (out / "report.md").write_text("Development scoring reached")

        runner.jobs = jobs
        runner.old = {}
        monkeypatch.setattr(
            "experiments.chem_tape.independent_input_protected_report.report"
            if protected
            else "experiments.chem_tape.independent_input_run.report",
            report,
        )
    # A rejected preparation has no pool/jobs: any search would fail.
    runner.score()
    summary = json.loads((out / "source_summary.json").read_text())
    assert summary["median_first_yield"] == first_yield
    assert summary["discovery_obstacle"] is True
    assert all(b["final_empty_library"] for b in summary["builds"].values())
    if admitted:
        assert (out / "report.md").read_text() == "Development scoring reached"
        assert not (out / "result.json").exists()
        return
    result = json.loads((out / "result.json").read_text())
    assert result["status"] == "feasibility_stop"
    assert result["protected_performance_scored"] is False
    assert (out / "report.md").exists() and not (out / "search.jsonl").exists()


def test_bank_validation_preserves_safe_pop_mode(monkeypatch):
    from experiments.chem_tape import independent_input_bank as bank

    monkeypatch.setattr(vm, "_SAFE_POP_CONSUME", True)
    assert bank.validate(random_count=1, depth=0)["passed"]
    assert vm._SAFE_POP_CONSUME is True

    def fail(*args):
        assert vm._SAFE_POP_CONSUME is False
        raise ValueError("validation failed")

    monkeypatch.setattr(bank, "_validate", fail)
    with pytest.raises(ValueError, match="validation failed"):
        bank.validate(random_count=1, depth=0)
    assert vm._SAFE_POP_CONSUME is True
