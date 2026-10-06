"""Population preservation, historical stream identity and crossed uncertainty."""

import numpy as np
import pytest

from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.initialization_report import classify, estimate, resampling
from experiments.chem_tape.initialization_run import Runner


def test_conditional_encoding_full_tapes_and_endpoints():
    table = np.array([[1, 10], [8, 10], [5, 10]])
    d = Decoder.__new__(Decoder)
    d.n_tokens, d.allele_range, d.table = 2, 10, table
    d.lookup = np.array(
        [np.searchsorted(row, np.arange(10), side="right") for row in table],
        dtype=np.uint8,
    )
    d.tied = False
    tapes = np.tile([[0, 1, 0, 1], [1, 0, 1, 0]], (1000, 1))
    alleles = d.encode(tapes, np.random.default_rng(3))
    assert np.array_equal(d.decode(alleles), tapes)
    # Every tiny interval reaches both endpoints. This detects midpoint encoding.
    assert set(alleles[1::2, 0]) == set(range(5, 10))
    assert set(alleles[1::2, 1]) == set(range(8))
    assert set(alleles[::2, 2]) == set(range(8))
    with pytest.raises(ValueError):
        d.encode(np.array([[2]]), np.random.default_rng(0))


def test_identity_path_preserves_every_substantive_search_field():
    # Test the established 23-token engine as well as this experiment's 24-token bank.
    from experiments.chem_tape.composition_search import base_tables
    from experiments.chem_tape.composition_bank import INPUTS

    table = base_tables()["G"]
    cell = dict(id="identity", labels=[int(sum(x)) for x in INPUTS])
    original = (cell, "G", table, 9000024, 1024, 32, INPUTS, "v2_rmin")
    a = search(original)
    b = search((*original, dict(source_table=table, reencode=False)))
    timing = {"seconds", "budget_seconds", "decode_seconds"}
    assert {k: v for k, v in a.items() if k not in timing} == {
        k: v for k, v in b.items() if k not in timing
    }


def test_shared_seed_noise_does_not_shrink_by_replicating_maps():
    seed_effect = np.array([-0.8, 0.4, 1.2, -0.1, 0.9, -1.1])
    values = np.tile(seed_effect, (20, 1))
    w20 = resampling(6, 20, 10000)
    w10 = resampling(6, 10, 10000)
    a = estimate(values, w20)
    b = estimate(values[:10], w10)
    assert np.allclose(a["interval_log2"], b["interval_log2"])
    assert a["width_log2"] > 0.8  # Map-only uncertainty would spuriously be zero.


@pytest.mark.parametrize(
    "p1,p2,row",
    [
        ("P", "N", "1"),
        ("N", "P", "2"),
        ("P", "P", "3"),
        ("N", "N", "4"),
        ("X", "P", "5"),
        ("P", "X", "5"),
        ("X", "N", "5"),
        ("N", "X", "5"),
        ("X", "X", "5"),
    ],
)
def test_complete_outcome_cross_product(p1, p2, row):
    primary = {
        k: dict(label=label, resolved_negative=False)
        for k, label in (("P1", p1), ("P2", p2))
    }
    assert classify(primary, True)["row"] == row
    assert classify(primary, False)["row"] == "U"
    primary["P1"]["resolved_negative"] = p1 == "N"
    assert bool(classify(primary, True)["antagonism"]) == (p1 == "N")


def test_seed_major_grid_counts_and_payload_separation():
    r = Runner.__new__(Runner)
    r.maps = {
        k: np.tile(np.arange(1, 25) * 1000, (25, 1))
        for k in ["G4", *[f"{f}{i}" for f in ("BE", "PA") for i in range(1, 11)]]
    }
    r.map_ids = list(r.maps)[1:]
    r.cells = {cid: dict(id=cid, labels=[0] * 1331) for cid in ("a", "b", "c")}
    r.cap, r.inputs = 524288, [[0, 0, 0]] * 1331
    from types import SimpleNamespace

    r.args = SimpleNamespace(smoke=False)
    early, late = r.block_jobs(2331000), r.block_jobs(2331100)
    assert len(early) == 243 and len(late) == 183
    assert sum(len(r.block_jobs(s)) for s in range(2331000, 2331400)) == 79200
    for payload, _, _ in early:
        assert set(payload[0]) == {"id", "labels"}
        assert payload[3] == 2331000


def test_report_serializes_and_keeps_single_shared_gg():
    import json
    from experiments.chem_tape.initialization_report import make_report

    maps = [f"{f}{i}" for f in ("BE", "PA") for i in range(1, 11)]
    cells, seeds = ["a", "b", "c"], [1, 2]
    rows = [
        dict(map=tid, arm=arm, cell=cid, seed=seed, evaluations=cost, solved=True)
        for tid in ["G4", *maps]
        for arm, cost in (
            [("GG", 4096)]
            if tid == "G4"
            else [("MM", 1024), ("MG", 2048), ("GM", 1024)]
        )
        for cid in cells
        for seed in seeds
    ]
    report = make_report(rows, maps, cells, seeds, dict(passed=True), replicates=100)
    json.dumps(report, allow_nan=False)
    assert report["contrasts"]["P1"]["log2_mean"] == 1
    assert report["contrasts"]["P2"]["log2_mean"] == 0
    assert report["contrasts"]["D"]["log2_mean"] == 2
    assert report["contrasts"]["interaction"]["log2_mean"] == -1
    assert report["solve_fractions"]["G4"]["GG"]["a"]["n"] == 2
    assert report["outcome"]["row"] == "U"  # n=2 cannot receive a mechanism label.


def test_population_pairing_gate_rejects_changed_inactive_token_hash():
    from types import SimpleNamespace
    from experiments.chem_tape.initialization_run import SOURCE, frozen_source
    from experiments.chem_tape.composition_search import Decoder
    import hashlib

    r = Runner.__new__(Runner)
    trajectories, g4, _, _ = frozen_source(SOURCE)
    r.maps = {
        "G4": g4,
        **{tid: np.asarray(tr["table"]) for tid, tr in trajectories.items()},
    }
    r.map_ids = list(trajectories)
    r.cells = {cid: dict(id=cid, labels=[0] * 1331) for cid in ("a", "b", "c")}
    r.cap, r.inputs = 8192, [[0, 0, 0]] * 1331
    r.args = SimpleNamespace(smoke=True)
    r.config = dict(
        map_hashes={tid: Decoder(table).hash() for tid, table in r.maps.items()}
    )
    seed = 9000024
    initial = np.random.default_rng([seed, 1]).integers(
        24000, size=(256, 32), dtype=np.int32
    )
    hashes = {
        tid: hashlib.sha256(Decoder(table).decode(initial).tobytes()).hexdigest()
        for tid, table in r.maps.items()
    }
    cases = np.random.default_rng([seed, 0]).choice(1331, 64, replace=False).tolist()
    rows = []
    for payload, tid, family in r.block_jobs(seed):
        src = "G4" if payload[1] in ("GG", "GM") else tid
        dst = "G4" if payload[1] in ("GG", "MG") else tid
        rows.append(
            dict(
                map=tid,
                arm=payload[1],
                cell=payload[0]["id"],
                seed=seed,
                table_hash=r.config["map_hashes"][dst],
                initial_source_hash=r.config["map_hashes"][src],
                initial_tokens_hash=hashes[src],
                initial_reencoded=payload[8]["reencode"],
                training_indices=cases,
                cap=8192,
                pop_size=256,
                family=family,
                solved=False,
                evaluations=8192,
            )
        )
    r.check_block(rows, seed)
    rows[5]["initial_tokens_hash"] = "changed"
    with pytest.raises(ValueError, match="invalid paired search row"):
        r.check_block(rows, seed)
    rows[5]["initial_tokens_hash"] = hashes["BE1"]
    with pytest.raises(ValueError, match="incomplete/duplicate/unexpected"):
        r.check_block(rows[:-1], seed)


@pytest.mark.parametrize("stop", ["law", "deadline"])
def test_runner_stops_expansion_and_excludes_partial_seed(tmp_path, monkeypatch, stop):
    from types import SimpleNamespace
    from experiments.chem_tape import initialization_run as module

    r = Runner.__new__(Runner)
    r.args = SimpleNamespace(workers=1, probe=False, smoke=False, validate_only=False)
    r.out, r.started, r.work_deadline = tmp_path, 0, float("inf")
    r.maps, r.map_ids, r.cells = {}, ["BE1"], {"a": {}}
    r.seeds = list(range(2331000, 2331400))
    r.rows, r.complete_seeds, r.stop_reason = [], [], None
    r.validation = dict(passed=False, pairing_blocks=0, search_law=None)
    r.persist_validation = lambda: None
    r.reproduction = lambda pool: r.validation.update(reproduction=dict(passed=True))
    r.block_jobs = lambda seed: [seed]
    r.check_block = lambda rows, seed: None
    pool = SimpleNamespace(terminate=lambda: None, join=lambda: None)
    monkeypatch.setattr(
        module.mp,
        "get_context",
        lambda method: SimpleNamespace(Pool=lambda workers: pool),
    )
    monkeypatch.setattr(module, "encoding_checks", lambda maps: dict(passed=True))
    monkeypatch.setattr(
        module, "law_report", lambda *a: dict(passed=False, interval_log2=[0.1, 0.2])
    )
    seen = []

    def jobs(pool, fn, block, deadline, callback):
        seen.extend(block)
        callback(dict(seed=block[0], seconds=1))
        return stop != "deadline" or len(seen) == 1

    monkeypatch.setattr(module, "run_jobs", jobs)
    captured = {}

    def report(rows, maps, cells, seeds, validation, diagnostic, replicates):
        captured.update(rows=rows, seeds=seeds[:])
        return dict(outcome=dict(row="U"))

    monkeypatch.setattr(module, "make_report", report)
    monkeypatch.setattr(module, "save_report", lambda *a: None)
    result = r.run()
    if stop == "law":
        assert result == 1 and seen[-1] == 2331099 and len(seen) == 100
        assert "99% search-law" in r.stop_reason
    else:
        assert result == 0 and seen == [2331000, 2331001]
        assert captured["seeds"] == [2331000]
        assert [row["seed"] for row in captured["rows"]] == [2331000]
