# Round-one replay reference

`replay.json` is a compact scientific fingerprint of the completed 1831
partial-program run at commit `998a9fe` (full source commit and output location
are recorded in the manifest). It records all 16 lineages, 128 original G4
sources/lineage, accumulated S count hashes and C_S/T_S decoder hashes.

Every source hash covers all non-timing scientific search fields, including
the full S and P archives, training indices, initial genotype/token hashes,
solve stopping and fitness/diversity curves. Only runtime fields and run
metadata (`phase`, `family`, `corpus`, `round`) are omitted by
`partial_feedback_run.source_fingerprint`. The manifest also records SHA256
of the original config, freeze, corpora, schedule and search artifacts. During
extraction, the original complete/non-smoke flags and C/T table hashes were
checked against the original freeze.

The manifest's own SHA256 is pinned in the runner. Full execution regenerates
all original sources and compares scientific source hashes, pooled counts and
both first-fit table hashes before using each lineage. Smoke checks BE1/PA1
only. Any mismatch is fatal; there are no replacement seeds. No historical
scoring output is used by acquisition or fitting. The raw historical output
folder is not needed to run the experiment.
