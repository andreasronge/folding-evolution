# Frozen inputs for the 0348 gate-sum transfer experiment

These gzip snapshots retain the **complete 0150 acquisition cohort**, its 24
libraries and matched random donors, source schedules, admission evidence and
historical seed audit. The source location and SHA-256 of each decompressed
artifact are in `provenance.json`; original method hashes are retained there.
Gzip timestamps are zero for reproducible snapshots.

`planning.json.gz` is the read-only 0348 semantic planning audit, and
`probe_rows.json.gz` retains the disclosed two-cell probe and discarded seed
namespaces. Neither artifact supplies new donors. The candidate bank is built
from labels, short-program screening and the deterministic split alone.

Preparation rebuilds every library from source solver trees under the exact
0150 extractor, including failed source-job costs, and regenerates R-size from
each recorded control seed. Entries, controls and source hashes must match.
All 24 acquisitions are retained. Development stage pricing uses actual eight
attempt restart jobs on all four development cells in all three arms.
Protected scoring fails closed unless preparation, methods, bank, split,
schedule, donor artifacts and stage evidence still match.

Run with `RAYON_NUM_THREADS=1` and the worktree's release Rust extension:

```sh
RUN_DIR=/path/to/fresh/prepare RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.gate_sum_run --prepare --deadline-seconds 2400
RUN_DIR=/path/to/fresh/score RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.gate_sum_run --preparation /path/to/fresh/prepare --deadline-seconds 5400
```

`--prepare --smoke` uses 2,048-evaluation attempts on development cells and
always writes `admitted=false`; it cannot authorize scoring. The production
queue and plan live in the main checkout's `research/runs/2026-10-11-0348/`;
research files are not committed on the task branch.

In gate-sum reports, the shared reporter's legacy per-cell
`source_pair_split_covered` key identifies the common learned-predicate split
`((0, 1), (2, 3))`. The `pair_split` section names all three splits explicitly
and supplies `learned_predicate_split`; these flags describe the frozen cohort,
not causal attribution or a predicate present in every build.
