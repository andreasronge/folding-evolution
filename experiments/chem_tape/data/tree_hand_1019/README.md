# 1019 immutable TS acquisition archive

Gzipped, byte-hashed artifacts from the completed 0833 preparation, identified in
`provenance.json`. All 768 source rows, including failures, reconstruct the 24 TS
libraries with the original source-only extractor and control seeds; measured
acquisition costs and source cohorts are checked against the saved libraries.
The 1019 hand prior is constructed independently from the alphabet; this archive
is used only by its TS comparator, historical-seed audit and provenance checks.

`original_tree_gp_search.py.gz` preserves the exact 0833 engine. Its uncompressed
hash must equal the archived method freeze. The current engine may differ only by
the optional `donor_observer` signature and callback after a library insertion
decision; the runner checks that exact source transformation, enforces all other
original core hashes, records current hashes, and requires historical off-path
replays. The callback only counts insertion outcomes; it consumes no randomness.
