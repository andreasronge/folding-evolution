# Preparation verification

The approved design is feasible at the measured scale. No full-run scientific
results were generated during preparation. Outcome rules and critique responses
are in [plan.md](plan.md); machine-readable diagnostic counts, timings and file
SHA256s are in [verification.json](verification.json).

## Implementation

Dedicated frozen holdout mode:
`experiments.chem_tape.crossed_holdout_run`. It uses the unchanged production
`composition_search.search` and stage-1 t/Welch helpers. All 20 final maps and
G4 are preserved. The source config and trajectories are copied byte-for-byte;
the 17 MB training-row source is losslessly compressed to 2.4 MB. Pinned original
SHA256s, table hashes, vector reconstruction, all 10,500 stage-1 fresh rows,
and bank labels are checked before any job is admitted. Training cells and
unfrozen maps/seeds are rejected. No outer learning path is called.

The reporter validates the full row product and seed-derived case indices;
partial/deadline jobs produce U with no subset inference. It retains signed
crossed contrasts, separate improvement/bound flags, individual PA contrasts,
PA aggregate G4 gains, matched usefulness/mismatched damage classifications,
and the secondary interaction in every scientific outcome. Future-study sizing
separates expected interval width from approximate 80% detection and gives
BE/PA/interaction-specific costs. No Rust changes were needed.

## Checks

45 focused tests passed in 13.13 seconds:

```
.venv/bin/python -m pytest tests/test_crossed_holdout.py tests/test_crossed_learning.py tests/test_four_reducer.py tests/test_composition_bank.py -q
```

Coverage includes corrupt provenance/table rejection, exact 25,200-job
accounting, no training or learning, trajectory Welch inference, interaction
identity, unsolved cost=cap, missing/duplicate/extra rows, altered maps/cases/
phases/caps, G4 solve gating, reversed/small/unresolved label precedence,
map exclusion, diagnostic seed separation, and partial-row persistence at the
deadline. Ruff lint and formatting checks passed. Both figures were visually
inspected; all 11 queue `expect_outputs` are present and nonempty in the smoke
and probe outputs. Queue schema loads through `scripts.queue_lib.load_queue`;
one entry, task-prefixed ID, timeout sum 7,200 seconds, below the eight-hour cap.

## Diagnostic searches

Final reduced smoke: 21 maps × 3 cells × 2 shared seeds 2229400–2229401,
cap 8,192, ten workers. Complete 126/126 rows; 3.91 seconds wall. Scientific
inference suppressed (diagnostic U). Output:
`experiments/output/2026-10-06-2229-smoke-final/` in this worktree.

Full-cap feasibility probe: same maps/cells, five shared seeds
2229500–2229504, cap 524,288, ten workers. Complete 315/315 rows;
34.21 seconds wall, 236.46 summed worker-search seconds,
mean .75065 seconds/search. G4 solves 5/5 on each cell. Learned-map/cell
counts range 3/5–5/5; BE total 150/150, PA 147/150. Cell totals:

| Holdout | G4 | BE maps | PA maps |
|---|---:|---:|---:|
| BE:S?m:(M+F) | 5/5 | 50/50 | 48/50 |
| PA:(F?S:M)+m | 5/5 | 50/50 | 49/50 |
| PA:(S?M:m)+F | 5/5 | 50/50 | 50/50 |

Output: `experiments/output/2026-10-06-2229-probe/` in this worktree.
These are feasibility measurements, not trajectory-arm effect estimates or
assurances that the final 400-seed G4 gate will pass. The reporter suppresses
scientific inference for this mode, and no map is selected or excluded.

Full-run projection: 25,200 × .75065 / 10 / 60 + 3 = 34.53 minutes;
prior loaded rates project 46–55 minutes. Expected queue time is conservatively
45 minutes, internal deadline 105 minutes (including three-minute reporting
reserve), external timeout 120 minutes. No infeasibility condition was found.
The full approved 400-seed evaluation is left to the driver.

## Initial smoke seed exposure

The first low-cap infrastructure smoke used 2229000–2229001, inadvertently
overlapping two planned full-run seeds. All 126 rows remain only in
`experiments/output/2026-10-06-2229-smoke/`; their counts/hashes are retained
in verification.json. They never entered scientific inference, learning,
selection or design changes, and are excluded from full-run outputs. The
final smoke uses a disjoint block. The required 2229000–2229399 full block is
unchanged and every job is independently repeated at the approved cap.
This exposure is recorded in the plan and emitted full-run config; it limits
a literal claim that every seed was wholly unseen during preparation.
