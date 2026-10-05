"""Frozen 2247 controls and pre-screen diagnostic grammars."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from experiments.chem_tape.assembly_bank import SHAPES, deadline_check
from experiments.chem_tape.composition_bank import REDUCERS
from experiments.chem_tape.composition_calibrate import token_counts
from experiments.chem_tape.composition_search import Decoder, base_tables, cumulative
from folding_evolution.chem_tape import alphabet as a

SOURCE = Path(__file__).with_name("data") / "composition_2247_maps.json"
SOURCE_HASH = "3ad0ce8a7ad290af4235b66d61cbf25331e490f27a0c6778695c61eded16390b"


def frozen_controls():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH, (
        "2247 source drift"
    )
    record = json.loads(SOURCE.read_text())
    tables = {k: np.asarray(v, dtype=np.int64) for k, v in record["tables"].items()}
    for arm, table in tables.items():
        assert Decoder(table).hash() == record["hashes"][arm]
    for arm, table in base_tables().items():
        assert np.array_equal(table, tables[arm]), "2247 control drift"
    return tables


def grammar(shape):
    table = frozen_controls()["G"].copy()

    def row(previous, destinations):
        counts = np.full(23, 500, dtype=np.int64)
        assert 11500 % len(destinations) == 0
        for destination in destinations:
            counts[destination] += 11500 // len(destinations)
        table[previous] = np.cumsum(counts)

    if shape in ("GA", "BT", "BE"):
        row(a.ADD, [a.INPUT])
        row(a.IF_GT, [a.DUP])
    elif shape == "PA":
        row(a.IF_GT, [a.INPUT, a.ADD])
        row(a.ADD, [a.DUP])
    elif shape in ("D1", "D2"):
        for reducer in REDUCERS.values():
            row(reducer, [a.DUP if shape == "D1" else a.INPUT])
        row(a.ADD, [a.INPUT if shape == "D1" else a.DUP])
    else:
        raise ValueError(shape)
    assert np.all(np.diff(table, prepend=0, axis=1) >= 500)
    return table


def freeze_diagnostics(deadline=None, count=312500):
    tables, records = {}, {}
    for i, shape in enumerate(SHAPES):
        deadline_check(deadline)
        table = grammar(shape)
        counts, seconds = token_counts(
            Decoder(table), 260600100 + 2 * i, count, deadline
        )
        marginal = np.tile(cumulative(counts), (24, 1))
        check, check_seconds = token_counts(
            Decoder(marginal), 260600101 + 2 * i, count, deadline
        )
        p, q = counts / counts.sum(), check / check.sum()
        assert np.all(np.abs(p - q) <= np.maximum(0.02 * p, 0.0005)), (
            "marginal mismatch"
        )
        tables[shape] = table
        tables[shape + "-marg"] = marginal
        records[shape] = dict(
            counts=counts.tolist(),
            check_counts=check.tolist(),
            genotypes=count,
            seconds=seconds,
            check_seconds=check_seconds,
            seed=260600100 + 2 * i,
            check_seed=260600101 + 2 * i,
        )
    return tables, records
