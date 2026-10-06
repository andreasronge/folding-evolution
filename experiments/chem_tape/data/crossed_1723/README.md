# Frozen stage-1 artifacts for holdout evaluation 2229

Source run: `2026-10-06-1723-crossed-family-training`, source code commit
`db96645f54b72e890f55d9236dbeec85c41df256`. See `provenance.json` for the
original output directory and SHA256 of each original uncompressed file.

`config.json` and `trajectories.json` are byte-identical copies. To avoid
committing 17 MB of repeated JSON, `fresh_scores.json.gz` uses deterministic
gzip compression (`gzip.compress(raw, mtime=0)`); decompression restores the
original bytes. The evaluator pins all three SHA256s in source, checks the
20 saved tables and their vector reconstructions, validates all 10,500 fresh
training rows, and uses those rows only for descriptive transfer loss.
No training search is repeated. Canonical/witness programs are never search
payloads. The full evaluation outputs only under `RUN_DIR`.
