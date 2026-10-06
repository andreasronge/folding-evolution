"""Scientific invariants for FIRST, unordered roles and paired inference."""

from types import SimpleNamespace

import numpy as np
import pytest
from _folding_rust import rust_chem_execute
from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.four_reducer_bank import (
    ALPHABET,
    roster,
    role_set,
    split,
    validate,
)
from experiments.chem_tape.four_reducer_maps import tables, marginal
from experiments.chem_tape.four_reducer_report import contrast, summaries, witness
from experiments.chem_tape.four_reducer_run import Runner, projection
from experiments.chem_tape.map_learning import initial, table_for
from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program, resolve_op
from folding_evolution.chem_tape.evolve import _token_max


@pytest.mark.parametrize("inp", [[], [-3, 5, 8], [4, -1, 2]])
def test_first_dispatch_masks_and_wrong_type(inp):
    p = [a.INPUT, a.FIRST]
    expected = inp[0] if inp else 0
    assert execute_program(p, TA, inp, "intlist", ALPHABET) == expected
    assert rust_chem_execute(p, "NOP", "NOP", inp, "intlist", ALPHABET, 0) == expected
    stack = [("int", 7)]
    resolve_op(a.FIRST, TA, ALPHABET)(stack, inp, "intlist", TA)
    assert stack == [("int", 7), ("int", 0)]
    assert rust_chem_execute([3, 23, 7], "NOP", "NOP", inp, "intlist", ALPHABET, 0) == 1
    assert execute_program([1, 23], TA, inp, "intlist", "v2_rmin") == 0
    assert rust_chem_execute([1, 23], "NOP", "NOP", inp, "intlist", "v2_rmin", 0) == 0
    assert a.is_active(23, ALPHABET) and a.is_separator(20, ALPHABET)
    assert a.masks_for(ALPHABET)["active"][23]
    assert _token_max(SimpleNamespace(alphabet=ALPHABET)) == 23


def test_roster_and_unordered_sum_roles():
    cells = roster("D1331")
    assert len(cells) == 36
    assert sum(c["shape"] == "BE" for c in cells) == 12
    assert len({c["id"] for c in cells}) == 36
    for c in cells:
        assert len(c["canonical"]) == 10
        assert len(c["labels"]) == 1331
        assert set(c["roles"].values()) == set("SMmF")
    be = next(c for c in cells if c["shape"] == "BE")
    swapped = dict(
        be,
        roles=dict(
            be["roles"],
            sum_left=be["roles"]["sum_right"],
            sum_right=be["roles"]["sum_left"],
        ),
    )
    assert role_set([be]) == role_set([swapped])
    assert role_set([be]) <= role_set(cells)
    assert split(cells[:3]) is None
    # Pair feasibility really requires coverage of both holdouts jointly.
    toy = [
        dict(id=str(i), roles=dict(cond="S", then=r), label_hash=str(i))
        for i, r in enumerate("SMFS")
    ]
    assert split(toy) is None


def test_tables_and_exact_length_marginal():
    ts = tables()
    g = ts["G4"]
    counts = np.diff(g, prepend=0, axis=1)
    assert counts[24, 1] == 12500
    assert list(counts[1, [5, 11, 18, 22, 23]]) == [1813, 1812, 3625, 3625, 3625]
    assert np.all(counts[23, [1, 7, 9, 17]] == 3500)
    assert np.diff(ts["G4-PA"][17], prepend=0)[1] == 6500
    assert np.diff(ts["G4-BE"][7], prepend=0)[1] == 12500
    controls = {"G": g, "G-marg": ts["G4-marg"]}
    assert initial("M", controls).shape == (24,)
    assert np.array_equal(table_for("M", initial("M", controls), controls), g)
    rng = np.random.default_rng(7)
    alleles = rng.integers(24000, size=(20000, 32))
    for name in ("G4", "G4-BE", "G4-PA"):
        observed = (
            np.bincount(Decoder(ts[name]).decode(alleles).ravel(), minlength=24)
            / alleles.size
        )
        expected = np.diff(marginal(ts[name])[0], prepend=0) / 24000
        assert np.max(np.abs(observed - expected)) < 0.002


def rows_for_pair(n=50):
    return [
        dict(
            cell=c,
            arm=arm,
            seed=s,
            evaluations=base * (s + 1),
            cap=524288,
            solved=True,
            seconds=0.1,
            budget_seconds={"65536": 0.1},
        )
        for c in ("c1", "c2")
        for s in range(n)
        for arm, base in (
            ("match", 256),
            ("swap", 512),
            ("match-m", 128),
            ("swap-m", 256),
        )
    ]


def test_pairing_cancels_seed_noise_and_direct_context_difference():
    rs = rows_for_pair()
    result = contrast(rs, ["c1", "c2"], {"swap": 1, "match": -1})
    assert result["ratio"] == pytest.approx(2)
    assert result["interval_95"] == pytest.approx([2, 2])
    direct = contrast(
        rs, ["c1", "c2"], {"swap": 1, "match": -1, "swap-m": -1, "match-m": 1}
    )
    assert direct["ratio"] == pytest.approx(1)
    assert direct["interval_95"] == pytest.approx([1, 1])
    assert witness(rs, ["c1", "c2"], "match", "swap")["reading"] == "W"
    assert contrast(rs, ["missing"], {"swap": 1, "match": -1})["ratio"] is None


def test_censor_bounds_and_cost_counts():
    rs = rows_for_pair()
    for r in rs:
        r.update(solved=False, evaluations=r["cap"])
    ss = summaries(rs)
    assert ss["c1|match"]["km_median"] is None
    assert ss["c1|match"]["km_median_interval_labels"] == ["> 524288", "> 524288"]
    assert witness(rs, ["c1", "c2"], "match", "swap")["reading"] == "C"
    bank = [dict(id="c1"), dict(id="c2")]
    ps = projection(
        [dict(r, arm="G4") for r in rs if r["arm"] == "match"],
        bank,
        {"BE": {"training": ["a"] * 3}, "PA": {"training": ["b"] * 6}},
        10,
    )
    assert ps["inner_searches"] == 38784
    assert ps["final_parent_selection_searches"] == 1440
    assert ps["final_scoring_searches"] == 4250


def test_validation_and_tiny_pilot(tmp_path, monkeypatch):
    assert validate(50, 2)["passed"]
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    args = SimpleNamespace(smoke=True, cap=256, deadline_seconds=600, workers=1)
    runner = Runner(args)
    runner.bank = [c for c in roster("D1331") if c["shape"] == "BE"][:3]
    runner.splits = {"BE": {"training": [c["id"] for c in runner.bank]}}

    # Deterministic substitute isolates outer scheduling/selection/rank handling.
    def fake_jobs(jobs, phase):
        return [
            dict(
                cell=c["id"],
                arm=arm,
                seed=seed,
                evaluations=256,
                cap=cap,
                solved=False,
                seconds=0.001,
            )
            for c, arm, t, seed, cap, *rest in jobs
        ]

    runner.jobs = fake_jobs
    learned = runner.evolve("BE", 0)
    assert learned.shape == (25, 24)
    assert runner.pilot["BE1"]["within_generation_spearman"] == [None]
    assert runner.pilot["BE1"]["median_spearman"] is None
    assert (tmp_path / "generations.jsonl").exists()


def test_outcome_precedence_and_missing_seed(tmp_path):
    from experiments.chem_tape.four_reducer_report import report

    bank = [dict(id=f"{f}{i}", shape=f) for f in ("BE", "PA") for i in range(3)]
    splits = {
        f: dict(training=[f + "2"], holdouts=[f + "0", f + "1"]) for f in ("BE", "PA")
    }
    screens = {
        d: dict(complete=True, obstacles={f: dict(split=splits[f]) for f in splits})
        for d in ("D625", "D1331", "D2401")
    }
    rs = [
        dict(
            cell=c["id"],
            arm=a,
            seed=s,
            evaluations=8192,
            cap=524288,
            solved=True,
            seconds=0.1,
        )
        for c in bank
        for a in tables()
        for s in range(1603100, 1603150)
    ]
    args = [screens, bank, rs, True, False, False, {}, dict(fits=False)]
    assert report(*args)["outcome"] == "3"
    screens["D1331"]["obstacles"]["BE"]["split"] = None
    assert report(*args)["outcome"] == "1"
    assert (
        report(screens, bank, rs[:-1], True, False, False, {}, dict(fits=False))[
            "outcome"
        ]
        == "U"
    )
    screens["D1331"]["obstacles"]["BE"]["split"] = splits["BE"]
    # A fast comparator fails only the frozen threshold, not capacity.
    for r in rs:
        r["evaluations"] = 2048
    assert report(*args)["outcome"] == "2"
    for r in rs:
        r["evaluations"] = 8192
    pilots = {f: dict(family=f, gain={"interval_95": [1.1, 2]}) for f in ("BE", "PA")}
    assert (
        report(screens, bank, rs, True, True, True, pilots, dict(fits=True))["outcome"]
        == "4"
    )
    pilots["BE"]["gain"]["interval_95"] = [0.9, 2]
    assert (
        report(screens, bank, rs, True, True, True, pilots, dict(fits=True))["outcome"]
        == "5"
    )
    assert (
        report(screens, bank, rs, True, True, False, pilots, dict(fits=True))["outcome"]
        == "U"
    )
