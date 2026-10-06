# Historical reproduction reference for 2331

`reference_2229.jsonl.gz` contains all 21 tables × three cells × ten seeds
(2229002–2229011) from 2229, with the substantive allowlist `arm`, `cell`,
`seed`, `evaluations`, `solved`, `curve`, `table_hash`. No runtime fields
participate in reproduction. `provenance.json` records the original search
file hash and code commit; the new harness pins the uncompressed subset
SHA256 independently. Compression is deterministic (`mtime=0`).

The reference is for exact reproduction only. Historical seeds and costs
do not enter the mechanism analysis. The 1723 tables remain in
`../crossed_1723/` with their existing independent artifact validation.

Run the new runtime probe with `python -m
experiments.chem_tape.initialization_run --probe --workers 10` and a fresh
`RUN_DIR`. This repeats the proposal's fixed three-map, 25-seed calibration
and records all 900 raw searches and counts/timings. It selects no maps,
cells or inference seeds. The original scratch probe's raw artifact was
not found; task smoke notes distinguish the repeat from the original.
