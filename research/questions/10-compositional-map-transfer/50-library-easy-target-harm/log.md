# Log: 50 library harm on easy targets

- 2026-10-11 (steward, 0833): opened as parked from [49](../49-tree-library-source-portability/log.md)'s
  native-TS reading ([run 0833](../../../runs/2026-10-11-0833/analysis.md), commit `28db964`). Native TS, 8
  cells × 24 builds × 4 repeats, mix 0.5: mean evaluations R-tree 5,414, R-TS 9,622, R-DG 7,198; all 768/768
  solved; first-attempt solves 98.7% / 95.3% / 96.5%. R-TS ÷ R-tree 1.777 [1.578, 2.000], R-DG ÷ R-tree 1.329
  [1.122, 1.574], R-TS ÷ R-DG 1.337 [1.116, 1.604]. Per build R-TS ÷ R-tree > 1 in 23/24, unrelated to library
  size. Library draws are 50% of mutations, and 48% of draws are rejected as oversize.

  Decision: park because no experiment is funded (root 10 is spent) and strategy 0833 asked to stop rate
  sweeps; a gate test is cheap with the saved libraries if deployment becomes the question.
