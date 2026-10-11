# 0150 validation fixtures

`replay.jsonl.gz` contains eight complete 0024 R-tree jobs (build 0, repeat 0,
one per frozen DG target cell), used only to validate the disabled donor hook.
No saved tree participates in acquisition, extraction or scoring. Its uncompressed
SHA-256 and the original implementation commit are in `provenance.json`.

`historical_seeds.json.gz` is an immutable union of numeric seed fields in earlier
main-checkout output/task JSON and JSONL artifacts at implementation time. The
provenance records its uncompressed SHA-256, artifact count and path-list hash.
The audit also reconstructs known historic schedules, including unexecuted and
refused formulas, so the snapshot is not restricted to completed searches.

Changing tree_gp_search.py makes the old 0024 harness's pristine-file gate refuse
new runs. This is intentional: do not rewrite its historical hashes. The 0150
harness uses complete deterministic replays to establish off-path compatibility
and freezes current methods independently for new preparation/scoring.
