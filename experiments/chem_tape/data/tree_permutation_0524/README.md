# Frozen reference evidence for the 0524 replacement study

These deterministic gzip snapshots retain the already admitted **development**
GS bank from 0348, its preparation and seed audit, all-cell R-tree/R-lib worker
rates, and six fixed R-lib replay rows (first sorted job for build 0 and build 23
on each predicate split). `provenance.json` records decompressed SHA256 hashes,
the complete reference-search hash, source paths and reviewed commit `1f02bb7`.
They supply validation and baseline pricing, never new donors. Source libraries
are rebuilt from the full cohort in `../gate_sum_0348/`; all 24 builds and four
failed source jobs survive. No new bank screening or acquisition is performed.

```sh
RUN_DIR=/path/to/fresh/prepare RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_permutation_run --prepare --deadline-seconds 2400
RUN_DIR=/path/to/fresh/score RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_permutation_run --preparation /path/to/fresh/prepare --deadline-seconds 7200
```

`--prepare --smoke` validates all constructions and saved replays but calibrates
only fixed builds 0, 11 and 23 on the four development cells (36 full-budget jobs),
in a disjoint smoke namespace. It always writes `admitted=false` and cannot
admit scoring. Production calibration covers all 288 development jobs. The
original six-repeat schedule is frozen before calibration; admission records
its six- or four-repeat selection, with the first three or two constructions
and repeat modulo the active count. Seeds use the versioned rule in
`tree_permutation.seed`, separate domains for construction, stage, score, smoke
and bootstrap; case sampling and ordinary search RNG are unchanged.

Scoring independently reconstructs donor contents and checks hashes, admission,
method implementations, all saved replay fields, stage rows/timings and the
selected schedule. `result.json` records the hierarchical paired bootstrap,
registered guards, cells/subgroups, construction-specific costs and motif supply,
operator totals, acquisition-inclusive curves and conditional resolution prices.
Both repeats of a construction and precisely corresponding baseline rows are
resampled together. The 72 constructions remain nested in 24 acquisitions.
Retention concerns this particular matched replacement; the bank is development
data and no causal decomposition or cheaper acquisition is inferred.

The queue and implementation plan are in the main checkout's
`research/runs/2026-10-11-0524/`; research files are not committed on this branch.
