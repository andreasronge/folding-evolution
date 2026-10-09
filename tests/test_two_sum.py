"""2303 semantic split, fallback accounting and inference safety checks."""

from collections import Counter
import math
import time

import numpy as np
import pytest

from experiments.chem_tape.two_sum_bank import choose, load, roster
from experiments.chem_tape.two_sum_run import (
    ARMS,
    CAP,
    CORPORA,
    admission,
    fitted_roster,
    g4_roster,
    methods,
)
from experiments.chem_tape.two_sum_report import bootstrap, acquisition_cost, report


def test_frozen_bank_reproduces_semantic_selection_and_separation():
    bank, cells = load()
    raw = roster()
    assert sum(not c["constant_gate"] for c in raw) == 333
    assert len({c["label_hash"] for c in raw if not c["constant_gate"]}) == 289
    assert choose(bank["cells"]) == (bank["selected_ids"], bank["timing_ids"])
    assert len(bank["selected_ids"]) == 16 and len(bank["timing_ids"]) == 4
    assert (
        bank["canonical_validation"]["Python"] and bank["canonical_validation"]["Rust"]
    )
    selected = [c for c in bank["cells"] if c["id"] in cells]
    assert max(Counter(c["gate_pair"] for c in selected).values()) <= 4
    for i, c in enumerate(selected):
        assert c["old_max_agreement"] < 0.8 and c["agreement"] < 0.8
        for d in selected[i + 1 :]:
            assert np.mean(np.asarray(c["labels"]) == d["labels"]) < 0.8
    assert all(set(c) == {"id", "labels"} for c in cells.values())


def test_rosters_retain_all_corpora_equal_blocks_and_unchanged_g4():
    bank, _ = load()
    timing = fitted_roster(bank["timing_ids"], 4, timing=True) + g4_roster(
        bank["timing_ids"], True
    )
    assert len(timing) == 112
    assert {r["family"] for r in timing} == {"BE", "PA", "G4"}
    assert set(
        Counter((r["arm"], r["block"]) for r in timing if r["arm"] != "G4").values()
    ) == {8}
    g4 = g4_roster(bank["selected_ids"])
    for n, arms, total in (
        (8, ARMS, 6400),
        (4, ARMS, 3328),
        (4, ("A8", "full_F"), 2304),
    ):
        fitted = fitted_roster(bank["selected_ids"], n, arms)
        assert len(fitted + g4) == total
        assert {r["corpus"] for r in fitted} == set(CORPORA)
        assert set(
            Counter(
                (r["corpus"], r["block"], r["cell"], r["arm"]) for r in fitted
            ).values()
        ) == {n // 4}
        assert not {r["seed"] for r in timing} & {r["seed"] for r in fitted + g4}
    assert len({r["seed"] for r in g4}) == 256


@pytest.mark.parametrize(
    "seconds,expected", [(5, (8, 3)), (16, (4, 3)), (28, (4, 2)), (40, None)]
)
def test_timing_selects_first_affordable_option_and_deadline(seconds, expected):
    bank, _ = load()
    timing = fitted_roster(bank["timing_ids"], 4, timing=True) + g4_roster(
        bank["timing_ids"], True
    )
    rows = [dict(r, seconds=seconds) for r in timing]
    a = admission(rows, 112 * seconds / 10, 300, 10, time.time() + 20000)
    if expected:
        assert (a["selected"]["seeds"], len(a["selected"]["arms"])) == expected
    else:
        assert not a["admitted"]
    assert not admission(rows, 112 * seconds / 10, 300, 10, time.time() - 1)["admitted"]
    assert not admission(rows, 112 * seconds / 10, 2700, 10, time.time() + 20000)[
        "admitted"
    ]


def synthetic_rows(unsolved=False):
    bank, _ = load()
    schedule = fitted_roster(bank["selected_ids"], 4) + g4_roster(bank["selected_ids"])
    rows = []
    for r in schedule:
        ev = {"A8": 256, "full_F": 512, "S8": 512, "G4": 1024}[r["arm"]]
        solved = not unsolved or r["arm"] == "G4"
        rows.append(
            dict(
                r,
                cap=CAP,
                evaluations=ev if solved else CAP,
                solved=solved,
                seconds=1,
                curve=[[256, 32, 0.5]],
                operator=dict(edited_children=0, eligible_children=0, changed_tokens=0),
            )
        )
    return schedule, rows


def test_g4_seed_uncertainty_is_nonzero_and_shared_across_methods():
    _, rows = synthetic_rows()
    for r in rows:
        if r["arm"] == "G4":
            r["evaluations"] = 256 if r["seed_ordinal"] < 8 else 16384
    fit, draws, _, _, baseline = bootstrap(rows, ARMS, "log_cost")
    assert baseline.std() > 0
    a = baseline - draws["A8"]
    f = baseline - draws["full_F"]
    assert np.allclose(a - f, math.log(2))
    assert all(v.std() < 1e-12 for v in draws.values())
    assert all(len(v) == 16 for v in fit.values())


def test_complete_report_known_ratio_timeout_guard_and_incomplete_refusal(tmp_path):
    saved, _ = methods()
    accounting = dict(
        full=saved["preparation.json"]["full_acquisition"],
        cheap={k: b["acquisition"] for k, b in saved["builds.json"].items()},
    )
    prep = dict(
        admission=dict(selected=dict(arms=ARMS, projected_seconds=100)),
        validation=dict(calibration={a: 1 for a in (*ARMS, "G4")}),
    )
    schedule, rows = synthetic_rows()
    result = report(tmp_path, rows, schedule, accounting, prep)
    assert result["decision"] == "useful_retention"
    assert result["primary"]["cost_ratio"] == pytest.approx(0.5)
    assert result["primary"]["df"] == 15
    assert result["sigma"]["cost_ratio"] == pytest.approx(2)
    assert result["economics"]["evaluations"]["arithmetic_search_mean"]["A8"] == 256
    assert (tmp_path / "cost_curves.png").is_file()
    _, rows = synthetic_rows(unsolved=True)
    result = report(tmp_path, rows, schedule, accounting, prep)
    assert result["primary"]["cost_ratio"] == pytest.approx(1)
    assert not result["full_F_solve_guard"] and not result["A8_useful_against_G4"]
    assert result["decision"] != "useful_retention"
    with pytest.raises(ValueError, match="incomplete"):
        report(tmp_path, rows[:-1], schedule, accounting, prep)


def test_historical_price_calibrates_continuation_and_charges_all_overheads():
    a = dict(
        evaluations=100,
        historical_source_seconds=30,
        current_source_seconds=20,
        source_worker_seconds=50,
        verification_seconds=2,
        fit_seconds=3,
        extraction_seconds=4,
        continuation_verification_seconds=6,
        intermediate_overhead_seconds=5,
    )
    accounting = dict(current_calibration=dict(G4=2, A8=3, full_F=4))
    assert acquisition_cost(a, "evaluations", accounting, "A8") == 100
    assert acquisition_cost(a, "worker_seconds", accounting, "A8") == 180
    assert acquisition_cost(a, "worker_seconds", accounting, "full_F") == 180


def test_smoke_and_changed_method_handoffs_refused_before_search(tmp_path, monkeypatch):
    import hashlib
    import json
    from pathlib import Path
    from types import SimpleNamespace
    from experiments.chem_tape.two_sum_run import Runner

    monkeypatch.setenv("RUN_DIR", str(tmp_path / "run"))
    handoff = tmp_path / "preparation.json"
    args = SimpleNamespace(
        workers=10,
        deadline_seconds=600,
        preparation=str(handoff),
        prepare=False,
        smoke=False,
    )
    runner = Runner(args)
    code = Path("experiments/chem_tape/two_sum_run.py").read_bytes()
    assert (
        runner.freeze["implementation_hashes"]["two_sum_run.py"]
        == hashlib.sha256(code).hexdigest()
    )
    monkeypatch.setattr(
        runner, "jobs", lambda *a, **k: pytest.fail("invalid handoff reached search")
    )
    handoff.write_text(json.dumps(dict(admitted=False)))
    with pytest.raises(ValueError, match="handoff"):
        runner.score()
    handoff.write_text(json.dumps(dict(admitted=True, method_freeze={})))
    with pytest.raises(ValueError, match="handoff"):
        runner.score()
