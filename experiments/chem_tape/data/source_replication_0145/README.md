# Historical references for source replication 0145

`references.json.gz` is a deterministic compressed snapshot, with decompressed
SHA-256 pinned in `source_replication_run.py`. It contains the 256 G4 and 1,024
historical A8 two-sum confirmation rows, the 32 source rows needed to reconstruct
one historical 2033 A8 build exactly, and the historical source seed set used to
check new collection disjointness. Origins and raw input hashes are recorded in
`provenance.json`.

Historical source tapes are used only for the legacy replay gate, never for
complementary-source acquisition. Historical target A8 is a contextual roster
comparison, not a new acquisition replicate. For each new build j, ordinal s
maps to historical corpus j's block s artifact on identical target keys.

The runner validates the frozen source and target banks and preserves the
original training-only loader. New collection, intermediates, acquisition costs,
admission, scoring and all report artifacts are written only under RUN_DIR.
