# Frozen 1036 reference for the 1743 sparse-acquisition boundary

Copied from the completed 1036 fragment-reuse score run (commit
`348f9e236045eac6c31a6c6b50e1b869483bb7a2`). `provenance.json` records the
original file hashes and source path. The runner pins the provenance SHA,
verifies every decompressed JSON, verifies the primary JSONL SHA, and checks
its complete 16-corpus × 16-cell × 16-seed × C/F/W roster against the original
1036 schedule generator. Primary searches are retained without modifying any
fields; holdout, replay and timing phases were omitted. Other artifacts are
byte-preserving gzip copies of the originals. All gzip files use mtime=0.

To reconstruct: read the named original files in provenance, preserve each
JSON byte-for-byte, and for search.jsonl select lines whose `phase` is
`then_addition`, retaining original arrival order and terminating each with
one newline. gzip-compress each artifact with mtime=0; write the search subset
as primary.jsonl.gz. The complete original search hash and the subset hash are
both recorded, so this is an audited subset, not a new historical run.

The 1548 G4 reference and 1246 acquisition attempts remain in their existing
SHA-pinned repository fixtures. No additional source searches were executed.
