"""Reproduce the bounded D1331 feasibility probe (not the full queue).

From the worktree: PYTHONPATH="$PWD" RUN_DIR=<smoke-output> RAYON_NUM_THREADS=1
.venv/bin/python research/runs/2026-10-06-0001/smoke_benchmark.py
"""

import json
import os
from multiprocessing import get_context
from pathlib import Path
import time

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.assembly_run import sample
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import Decoder, search

if __name__ == "__main__":
    os.environ["RAYON_NUM_THREADS"] = "1"
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    tables = frozen_controls()
    write_json(out, "controls.json", {k: Decoder(v).hash() for k, v in tables.items()})
    screen = screen_domain("D1331", 9)
    write_json(out, "screen_D1331.json", screen)
    bank = [c for c in screen["cells"] if c["retained"]]
    inputs = inputs_for("D1331")
    jobs = [
        (c, arm, table, 260609100 + i, 524288, 256, inputs)
        for i in range(2)
        for c in bank
        for arm, table in tables.items()
    ]
    start = time.monotonic()
    with get_context("spawn").Pool(8) as pool:
        rows = pool.map(search, jobs, chunksize=1)
        elapsed = time.monotonic() - start
        chunks = pool.map(
            sample,
            [
                (arm, table, 260609200 + i, 100000, bank, inputs)
                for i, (arm, table) in enumerate(tables.items())
            ],
            chunksize=1,
        )
    record = dict(
        domain="D1331",
        cells=[c["id"] for c in bank],
        jobs=len(jobs),
        wall_seconds=elapsed,
        mean_run_seconds=sum(r["seconds"] for r in rows) / len(rows),
        searches=rows,
        sampling=chunks,
    )
    write_json(out, "benchmark.json", record)
    print(
        json.dumps(
            {
                k: v
                for k, v in record.items()
                if k not in ("searches", "sampling", "cells")
            }
        )
    )
