# Frozen 1717 artifacts for the 2001 crossing

All 24 D and 24 T final and intermediate builds are retained verbatim, along
with complete source rows, acquisition schedule, banks and admitted preparation.
`provenance.json` records original path, producing commit and SHA256 of each
uncompressed file. Compressed files have deterministic gzip timestamps.

The replay set contains 16 historical native target rows: DG/TS x D/T x builds
0/12 x first two sorted target cells, each build's first ordinal. This selection
uses identities only, never success or cost. It validates deterministic output
with elapsed-time fields excluded; these historical rows are never pooled into
new confirmation data. The original 1717 production freeze is checked alongside
original DG provenance and source membership, without fitting any artifacts.
