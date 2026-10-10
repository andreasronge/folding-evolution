"""Component isolation, pair-block inference and pre-score cost admission."""

import copy
import numpy as np
import pytest
from experiments.chem_tape.component_transfer_run import (
    ARMS,
    load_saved,
    schedules,
    envelope,
    execute,
    validate_rows,
    project,
)
from experiments.chem_tape.component_transfer_report import summarize, economics
from experiments.chem_tape.composition_search import search


@pytest.fixture(scope="module")
def frozen():
    return load_saved()


def test_complete_crossing_and_seed_identity(frozen):
    saved, targets = frozen
    permutation, cal, score = schedules(saved["banks.json"], targets)
    assert sorted(permutation) == list(range(24))
    assert len(cal) == 96 and len(score) == 4608
    assert {r["pair"] for r in cal} == {0, 12}
    assert not {r["seed"] for r in cal} & {r["seed"] for r in score}
    assert not {r["cell"] for r in cal} & {r["cell"] for r in score}
    for pair in range(24):
        for table in ("D", "T"):
            rs = [r for r in score if r["pair"] == pair and r["table_owner"] == table]
            assert {r["table_build"] for r in rs} == {
                pair if table == "D" else permutation[pair]
            }
            assert len({r["seed"] for r in rs}) == 32
            assert len(rs) == 96


def test_explicit_off_uses_fitted_table_and_native_ordinary_search(frozen):
    saved, targets = frozen
    _, _, score = schedules(saved["banks.json"], targets, smoke=True)
    rs = []
    for m in score[:6]:
        e = envelope(m, saved, 512)
        r = execute(e)
        rs.append(r)
        if m["operator_mode"] == "off":
            ordinary = search(e[0], return_solver=True, measure_exact=True)
            assert r["operator"] is None and r["block_events"] == 0
            for k in (
                "evaluations",
                "solved",
                "solver",
                "curve",
                "training_indices",
                "initial_tokens_hash",
            ):
                assert r[k] == ordinary[k]
        else:
            assert r["operator"]["eligible_children"] == 254
            assert r["block_events"] > 0
    assert len({r["initial_tokens_hash"] for r in rs if r["table_owner"] == "D"}) == 1
    assert len({r["initial_tokens_hash"] for r in rs if r["table_owner"] == "T"}) == 1
    validate_rows(rs, score[:6], saved, 512)
    bad = copy.deepcopy(rs)
    bad[0]["table_build"] += 1
    with pytest.raises(ValueError):
        validate_rows(bad, score[:6], saved, 512)
    # Declared legacy empty-library fallback is preserved, not bare-table mode.
    e = envelope(score[0], saved, 512)
    empty = execute((e[0], e[1], [], e[3]))
    assert empty["empty_library_fallback"] and empty["block_events"] > 0


def fake_rows(variable=False):
    rows = []
    for f in ("DG", "TS"):
        for c in range(2):
            for b in range(24):
                for s in range(2):
                    for a in ARMS:
                        ev = {
                            "D/D": 1024,
                            "T/T": 4096,
                            "T/D": 1024,
                            "D/T": 1024,
                            "D/none": 8192,
                            "T/none": 8192,
                        }[a]
                        if variable and a == "T/T":
                            ev = 256 * 2 ** (b % 10)
                        rows.append(
                            dict(
                                family=f,
                                cell=f + str(c),
                                pair=b,
                                repeat=s,
                                arm=a,
                                seed=1000 * c + 2 * b + s,
                                solved=True,
                                evaluations=ev,
                                cap=524288,
                                seconds=1,
                            )
                        )
    return rows


def test_replacement_vs_activity_and_native_dependence():
    rows = fake_rows()
    s = summarize(rows, draws=64)
    assert s["decision"]["primary"] == "worthwhile portable replacement increment"
    assert s["decision"]["sufficiency"] == "within 1.5x replacement tolerance"
    # Both libraries helpful under T, but no replacement advantage and D/T==D/D.
    for r in rows:
        if r["arm"] == "T/T":
            r["evaluations"] = 1024
    s = summarize(rows, draws=64)
    assert s["decision"]["primary"] == "no worthwhile replacement increment"
    assert s["decision"]["portable_activity"]
    assert not s["decision"]["native_D_identity_advantage"]
    assert not s["decision"]["table_contribution"]


def test_pair_uncertainty_not_cell_pseudoreplication():
    rows = fake_rows(variable=True)
    s = summarize(rows, draws=1024)
    interval = s["families"]["DG"]["ratios"]["R_replacement"]["interval95"]
    assert interval[1] / interval[0] > 2
    # Replication of the exact same cell signal cannot shrink pair uncertainty.
    more = []
    for i in range(4):
        more.extend(r | dict(cell=r["cell"] + str(i)) for r in rows)
    s2 = summarize(more, draws=1024)
    interval2 = s2["families"]["DG"]["ratios"]["R_replacement"]["interval95"]
    assert (
        abs(np.log(interval2[1] / interval2[0]) - np.log(interval[1] / interval[0]))
        < 0.2
    )
    with pytest.raises(ValueError):
        summarize(rows[:-1], draws=4)
    bad = copy.deepcopy(rows)
    bad[0]["seed"] += 1
    with pytest.raises(ValueError):
        summarize(bad, draws=4)


def test_runtime_admission_stops_unknown_slow_arms(frozen):
    saved, targets = frozen
    _, cal, score = schedules(saved["banks.json"], targets)
    rows = [
        r | dict(seconds=10, solved=True, exact_check_max_seconds=0.01) for r in cal
    ]
    batches = {f: dict(wall_seconds=48) for f in ("DG", "TS")}
    assert all(v["admitted"] for v in project(rows, batches, score, 10).values())
    for r in rows:
        if r["arm"] == "T/D":
            r["seconds"] = 200
    batches = {f: dict(wall_seconds=600) for f in ("DG", "TS")}
    assert not all(v["admitted"] for v in project(rows, batches, score, 10).values())


def test_hybrid_charged_two_acquisitions_and_bare_one(frozen):
    saved, targets = frozen
    _, _, schedule = schedules(saved["banks.json"], targets, smoke=True)
    rows = [r | dict(seconds=1, evaluations=256) for r in schedule]
    e = economics(rows, saved)["costs"]["DG"]
    native = e["D/D"]["per_pair"]["0"]["acquisition"]["evaluations"]
    t = e["T/T"]["per_pair"]["0"]["acquisition"]["evaluations"]
    assert e["T/D"]["per_pair"]["0"]["acquisition"]["evaluations"] == native + t
    assert e["D/none"]["per_pair"]["0"]["acquisition"]["evaluations"] == native
