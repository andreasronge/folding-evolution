# 1707 frozen validation data

`replay.json` contains the first 20 GG seeds (3150000–3150019) from each of
`BE:F?S:(M+m)` and `PA:(F?S:m)+M` in the completed 0315 training run. The source
is commit `5dae3a63b59f71df612c7fa9424a946722a5e895`.

`provenance.json` records source paths and SHA256 of the full streamed source
files, SHA256 of the selected rows, and G4 mean seconds on each holdout from
400 GG seeds in 2331. These timing summaries serve only to inflate the
stage-2 admission projection; they never enter fitting or scientific contrasts.
Both vendored files have independent hash constants in `solver_corpus_run.py`.

To extract again, stream the 0315 `search.jsonl`, select arm GG, the two cells
above and the stated seeds, sort by (cell, seed), and serialize with
`json.dumps(rows, indent=2) + "\n"`. For 2331, stream GG rows and divide each
cell's summed `seconds` by its row count. Stream all source bytes through
SHA256 while doing so. Retain all original replay fields; only timing and
metadata fields are excluded at comparison time.
