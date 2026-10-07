"""0315 weighting, Welch routing, validation and balanced deadline coverage."""

import numpy as np
import pytest

from experiments.chem_tape import initialization_bank_run as runner
from experiments.chem_tape.initialization_bank_report import (
    cell_weights,
    classify,
    family_interval,
    make_report,
    masked_summary,
)
from experiments.chem_tape.initialization_report import resampling

MAPS = [f"{f}{i}" for f in ("BE", "PA") for i in range(1, 11)]
CELLS = [f"BE:{i}" for i in range(4)] + [f"PA:{i}" for i in range(6)]


def test_cell_families_receive_equal_weight():
    cw = cell_weights(CELLS)
    assert np.allclose(cw[:4], 0.125) and np.allclose(cw[4:], 1 / 12)
    seeds = [1, 2]
    rows = [
        dict(
            map=tid,
            arm=arm,
            cell=cid,
            seed=seed,
            evaluations=cost,
            cap=524288,
            solved=True,
        )
        for tid in ["G4", *MAPS]
        for arm in (["GG"] if tid == "G4" else ["MM", "MG", "GM"])
        for cid in CELLS
        for seed in seeds
        for cost in [
            8192
            if arm == "GG"
            else 1024
            if arm in ("MM", "GM") or cid.startswith("PA")
            else 4096
        ]
    ]
    r = make_report(rows, MAPS, CELLS, seeds, dict(passed=True), replicates=100)
    assert r["contrasts"]["P1"]["log2_mean"] == pytest.approx(
        1
    )  # naive 10-cell mean=.8
    assert r["family_balance"]["log2_mean"] == pytest.approx(2)
    assert r["map_family_by_cell_family"]["BE"]["BE"]["P1"] == 2
    assert r["map_family_by_cell_family"]["PA"]["PA"]["P1"] == 0
    assert r["solve_fractions"]["G4"]["GG"]["BE:0"]["n"] == 2
    assert r["sensitivities"]["winsorized_65536"]["contrasts"]["P1"][
        "log2_mean"
    ] == pytest.approx(1)
    assert r["sensitivities"]["uncapped_triplets"]["contrasts"]["P1"][
        "log2_mean"
    ] == pytest.approx(1)
    assert r["outcome"]["row"] == "U"


@pytest.mark.parametrize(
    "be,pa,label,inside",
    [
        (-0.1, 0, "B", True),
        (0.1, 0, "E", True),
        (0.4, 0, "R", False),
        (0, 0, "E", True),
    ],
)
def test_family_label_precedence(be, pa, label, inside):
    b = family_interval({c: be if c.startswith("BE:") else pa for c in CELLS})
    assert b["label"] == label and b["inside_margin"] == inside
    assert b["family_means"] == {"BE": pytest.approx(be), "PA": pytest.approx(pa)}


def test_welch_cells_are_units_and_negative_c_need_not_flip_sign():
    from scipy.stats import t

    be, pa = np.array([0.1, 0.2, 0.3, 0.4]), np.array([0.6, 0.65, 0.7, 0.75, 0.8, 0.9])
    b = family_interval(dict(zip(CELLS, np.r_[be, pa])))
    a, v = be.var(ddof=1) / 4, pa.var(ddof=1) / 6
    df = (a + v) ** 2 / (a * a / 3 + v * v / 5)
    half = t.ppf(0.975, df) * np.sqrt(a + v)
    assert b["interval_log2"] == pytest.approx(
        [be.mean() - pa.mean() - half, be.mean() - pa.mean() + half]
    )
    assert b["label"] == "B" and min(b["family_means"].values()) > 0


@pytest.mark.parametrize(
    "p1,p2,expected",
    [
        ("P", "N", "5"),
        ("N", "P", "5"),
        ("N", "N", "6"),
        ("X", "P", "6"),
        ("P", "X", "6"),
        ("X", "N", "6"),
        ("N", "X", "6"),
        ("X", "X", "6"),
    ],
)
def test_component_routing(p1, p2, expected):
    primary = {
        k: dict(label=label, resolved_negative=False)
        for k, label in [("P1", p1), ("P2", p2)]
    }
    assert classify(primary, dict(label="B"), True)["row"] == expected
    assert classify(primary, {}, False)["row"] == "U"
    for label, row in [("B", "1"), ("E", "2"), ("R", "3"), ("X", "4")]:
        primary["P1"]["label"] = primary["P2"]["label"] = "P"
        assert classify(primary, dict(label=label), True)["row"] == row


def test_missing_cap_triplets_do_not_turn_into_zero_costs():
    values = np.ones((20, 10, 2))
    mask = np.ones_like(values, dtype=bool)
    values[:10, 0, 0] = 100  # exclude these extreme capped triplets
    mask[:10, 0, 0] = False
    r = masked_summary(values, mask, resampling(2, 20, 20), cell_weights(CELLS))
    # With just two seeds, some draws miss all available pairs: explicitly unresolved.
    assert r["label"] == "X" and "Empty bootstrap" in r["reason"]
    r = masked_summary(
        values,
        mask,
        (np.full((1, 20), 0.05), np.full((1, 2), 0.5)),
        cell_weights(CELLS),
    )
    assert r["log2_mean"] == pytest.approx(1)


def test_grid_count_no_mmr_and_two_block_partial_prefix(tmp_path, monkeypatch):
    r = runner.Runner.__new__(runner.Runner)
    r.map_ids, r.cells = MAPS, {c: {} for c in CELLS}
    r.job = lambda tid, arm, cid, seed: (seed, tid, arm, cid)
    assert len(r.block_jobs(1)) == 610
    assert sum(len(r.block_jobs(s)) for s in runner.MAIN_SEEDS) == 122000
    assert all(job[2] != "MMr" for job in r.block_jobs(1))
    r.seeds, r.out, r.rows = [1, 2, 3, 4], tmp_path, []
    r.complete_seeds, r.validation, r.work_deadline = (
        [],
        {"pairing_blocks": 0},
        float("inf"),
    )
    r.started, r.stop_reason = 0, None
    r.block_jobs = lambda seed: [(seed, 0), (seed, 1)]
    r.check_block = lambda rows, seed: None
    r.persist_validation = lambda: None
    seen = []

    def run(pool, fn, jobs, deadline, callback):
        seen.extend(jobs)
        # First seed completes, second remains partial. Never schedule seeds 3/4.
        for seed, pos in jobs:
            if (seed, pos) != (2, 1):
                callback(dict(seed=seed))
        return False

    monkeypatch.setattr(runner, "run_jobs", run)
    r.grid(None)
    assert seen == [(1, 0), (2, 0), (1, 1), (2, 1)]
    assert r.complete_seeds == [1] and r.validation["pairing_blocks"] == 1
    assert r.stop_reason.startswith("internal deadline")


def test_bad_pairing_stops_before_next_batch(tmp_path, monkeypatch):
    r = runner.Runner.__new__(runner.Runner)
    r.seeds, r.out, r.rows, r.complete_seeds = [1, 2, 3, 4], tmp_path, [], []
    r.validation, r.work_deadline = {"pairing_blocks": 0}, float("inf")
    r.block_jobs = lambda seed: [seed]
    r.check_block = lambda rows, seed: (_ for _ in ()).throw(
        ValueError("token mismatch")
    )
    seen = []

    def run(pool, fn, jobs, deadline, callback):
        seen.extend(jobs)
        callback(dict(seed=1))
        return True

    monkeypatch.setattr(runner, "run_jobs", run)
    with pytest.raises(ValueError, match="token mismatch"):
        r.grid(None)
    assert seen == [1, 2] and r.complete_seeds == []


def test_historical_reference_exact_rosters_and_corruption_gate(tmp_path, monkeypatch):
    from types import SimpleNamespace

    r = runner.Runner.__new__(runner.Runner)
    r.maps = dict.fromkeys(["G4", *MAPS])
    r.map_ids = MAPS
    r.cells = dict.fromkeys(sum(runner.TRAINING.values(), []))
    r.args = SimpleNamespace(source=str(runner.SOURCE), smoke=False)
    refs = r.reference_rows()
    assert len(refs) == 786
    assert sum(origin == "1723" for origin, *_ in refs) == 420
    assert sum(origin == "2331" for origin, *_ in refs) == 366
    assert not any(ref["arm"] == "MMr" for _, ref, *_ in refs)
    import gzip

    bad = tmp_path / "bad.gz"
    bad.write_bytes(gzip.compress(b"{}\n"))
    monkeypatch.setattr(runner, "REFERENCE", bad)
    with pytest.raises(ValueError, match="reference SHA256"):
        r.reference_rows()
