# Log: 50 library harm on easy targets

- 2026-10-11 (steward, 0833): opened as parked from [49](../49-tree-library-source-portability/log.md)'s
  native-TS reading ([run 0833](../../../runs/2026-10-11-0833/analysis.md), commit `28db964`). Native TS, 8
  cells × 24 builds × 4 repeats, mix 0.5: mean evaluations R-tree 5,414, R-TS 9,622, R-DG 7,198; all 768/768
  solved; first-attempt solves 98.7% / 95.3% / 96.5%. R-TS ÷ R-tree 1.777 [1.578, 2.000], R-DG ÷ R-tree 1.329
  [1.122, 1.574], R-TS ÷ R-DG 1.337 [1.116, 1.604]. Per build R-TS ÷ R-tree > 1 in 23/24, unrelated to library
  size. Library draws are 50% of mutations, and 48% of draws are rejected as oversize.

  Decision: park because no experiment is funded (root 10 is spent) and strategy 0833 asked to stop rate
  sweeps; a gate test is cheap with the saved libraries if deployment becomes the question.

- 2026-10-11 (steward, 1129): related observation from probe [52](../52-order-helper-acquisition/log.md)
  ([analysis](../../../runs/2026-10-11-1129/analysis.md)): on order-helper destinations where R-tree solves only
  56% first time, donor libraries whose content the targets do not need still raised cost (1019 sum prior 2.12×
  [1.54, 2.91], literal library 1.55× [1.09, 2.17] of R-tree; geometric cost, 96 paired jobs each). So donor harm is
  not confined to near-solved targets; it tracks irrelevant content at mix 0.5. Reopen condition (≥ ~90% first-attempt
  rate, or funded default deployment) not met; status unchanged.
- 2026-10-11 (steward, 1228): wording correction from [critique 1228](../../../runs/2026-10-11-1228/critique.md)
  note 9: the 1129 entry's "it tracks irrelevant content at mix 0.5" claims more than the probe isolated. Better:
  donor libraries whose content these order targets do not need raised cost there; content mismatch is a plausible
  explanation, not an isolated mechanism (destination family, difficulty and donor size/acceptance were not
  separated). Related evidence from [53](../53-order-library-cap-release/question.md) (run 1228, full experiment,
  same six order development cells, R-tree first-attempt rate about 56% in 1129): the capped 16-entry semantic
  library cost 1.23× [1.07, 1.41] of R-tree in arithmetic mean evaluations, while the uncapped library cost 0.40×
  [0.32, 0.50]; the cell × build pairs whose uncapped pool held no needed helper were unresolved from R-tree (0.77×
  [0.50, 1.12], 18 pairs, descriptive). Uncapped libraries were not tested on easy targets. Reopen condition (≥ ~90%
  first-attempt targets, or funded default deployment) not met; status unchanged.
- 2026-10-11 (steward, 1938): reopen check. The condition "libraries applied to a destination where R-tree's
  first-attempt rate exceeds about 90%" is met by [58](../58-signed-gate-acquisition/question.md) (run 1938,
  signed-gate protected cells, R-tree 97.7% first attempt, 1,728 jobs per arm). There, at mix 0.5, the matched new
  R-all libraries cost 0.577× [0.47, 0.72] of R-tree (below 1 in 18/18 cells) and the supplied gate prior 0.246×;
  only the transported order libraries, whose content these targets do not need, sat above R-tree, 1.12× [0.94,
  1.34] (unresolved; 11/18 cells above 1). So near-solved targets do not by themselves bring harm; harm in 49 and
  here travels with libraries built for other targets (a pattern, not an isolated mechanism). A library-on-failure
  gate would buy little where the library helps on attempt one. Status stays parked; the next step is the
  strategist's (run 1938 returns to strategy). Reopen condition narrowed in question.md.
