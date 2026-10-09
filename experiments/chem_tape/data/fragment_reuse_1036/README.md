# Frozen reuse references (1036)

`whole_libraries.json.gz` preserves the exact uncompressed 0843 whole-library
artifact (all 16 corpora, 32 fragments each, including source provenance and
stack/default diagnostics). Its decompressed SHA is pinned in
`fragment_reuse_run.py`; preparation rebuilds each record from the SHA-pinned
1246 collection and requires exact equality. Compression uses gzip mtime=0.

`history.json` is SHA-pinned separately. It records the original artifact
paths, original byte hashes and code commits, 16 C replay rows from 1548,
per-cell arithmetic capped-cost means for deterministic timing-cell selection,
and all observed historical seeds from 1548 and 0843 for exclusion checks.
For replay, zero-based even corpus indices use then-addition, odd indices use
holdouts, and each uses the first C row for that corpus in the original log.
Each source family contributes eight replay rows, four per bank.

Difficulty is computed from **all C rows** in each bank's saved 1548 log:
mean(evaluations if solved else 2*cap), sorted ascending then by cell ID.
The eight fixed smoke cells use primary ranks 0/5/10/15 and reference ranks
0/2/5/7. F/W outcomes never enter selection. Historical rows and difficulty
metadata are validation/selection artifacts; they never enter the scored
endpoint. Search receives only cell IDs/labels and the original C table.

Source paths are descriptive provenance. Reruns use only these vendored files,
the vendored 1246 source, and the existing two pinned bank artifacts; the
original output directories are not required at execution time.
