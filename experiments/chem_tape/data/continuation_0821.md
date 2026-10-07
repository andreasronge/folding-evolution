# Pinned 0821 fresh-scoring reference for 1137

`continuation_0821.json.gz` is a compact, deterministic extraction from the
completed `2026-10-07-0821-rank-one-continuation` output, produced by commit
`f61aec48c08a9b083ab9e2e6da7ee2acda85fee0`. Its SHA-256 is pinned in
`continuation96_report.py`. The artifact embeds the original config and
SHA-256 values of config.json, fresh_scores.json and trajectories.json.

Only BE1–8 and PA1–8 own-cell S and T observations are retained: 4,000 S
fingerprints and 4,000 T24 evaluation/solve records. For each S row, include
every field in the original search schema except `arm`, `phase`, and fields
whose names contain `seconds`. Serialize that scientific payload as sorted
JSON with separators `(',', ':')`, `allow_nan=False`, and hash its UTF-8 bytes.
This includes training cases, the entire cost curve, decoder and initialization
hashes, and shortcut counts, as well as success and evaluations.

The artifact is sorted-key compact JSON followed by a newline, compressed
with `gzip.compress(..., mtime=0)`. No timing fields, witness programs,
holdout observations, or context scores are retained. Historical score rows
are used for baseline validation and the descriptive T96/T24 comparison;
they never enter continuation selection or the F1/F2 primary contrasts.
