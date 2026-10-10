# 0024 historical reference

Frozen full 2254 DG/TS search rows, gzip compressed with deterministic headers.
`provenance.json` records original SHA-256 hashes, source paths and the producing
commit c32ff04. These rows supply descriptive historical full-cap tree references,
empirical restart sensitivities and the historical F-A8 timing anchor. They are
never re-labelled as fresh jobs or used to initialize populations.

`observed_seeds.json` captures seeds in JSON/JSONL artifacts from 2214, 2239,
2254 (including smoke/replay/preparation), complementing complete historical
schedule formulas and the existing audited source/acquisition/replay records.
The audit publishes their union and all new seed sets before searches.

The loader checks hashes, frozen search sources, complete historical grids,
training indices, table/library identity and every exact solver using the
unchanged 2254 validator. The saved 1717 A8 builds and all sixteen native replay
records remain in `../component_transfer_2001/` and are loaded with its existing
provenance validator. No acquired map is fitted anew.
