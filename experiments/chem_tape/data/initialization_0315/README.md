# 0315 exact historical reference

`reference_2331.jsonl.gz` contains the four-arm rows (MMr excluded) for all
20 frozen maps and three cells, seeds 2331000–2331001: 366 rows. Every
substantive search field, including full-token initialization hashes and
curves, is retained; wall/decode timing metadata is excluded. Compression
uses mtime=0. `provenance.json` records the source file SHA256, producing
commit, selected fields and uncompressed subset SHA256. The runner pins the
subset hash and verifies its full roster before dispatch.

1723's 420 reference rows are read from the separately pinned complete
`../crossed_1723/fresh_scores.json.gz` artifact. No historical cost enters
0315 inference. Probe/smoke seeds 3150900–3150901 are excluded as well.

`descriptive_2331.json` freezes the three prior per-cell P1/P2/S point values
from the validated 400-seed 2331 result (source result SHA256 included).
The report's 13-cell roster adds those three points to the ten current cells
with explicit seed-cohort labels. This is descriptive only; no cross-cohort
pooled inference or outcome routing uses the reference.
