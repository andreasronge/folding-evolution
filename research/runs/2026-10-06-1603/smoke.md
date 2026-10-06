# Implementation verification

Full queue has **not** been executed. These are infrastructure and cost smokes,
not the fifty-seed outcome analysis. No infeasibility obstacle was found.

- Rust rebuilt successfully in this worktree with the prescribed release command.
- Full validation: 137,561 raw executable-token programs through depth four,
  complete Python typed stacks versus semantic machine on five representative
  sign/tie inputs; exact dedup state/output sets versus raw enumeration.
  100,000 random 32-token programs checked against Python/Rust on those inputs
  plus empty input (600,000 program/input comparisons). All 36 NOP-padded
  canonicals checked against Rust on each of D625/D1331/D2401. Passed in 3.75 s.
  Evidence: [full_validation.json](smoke/full_validation.json).
- Full D1331 depth-nine screen: 108.66 s, peak 5,188.875 MiB (5.07 GiB),
  13 retained cells (BE five, PA eight), matching the proposal probe. Every
  best alias witness and canonical checked in Rust. BE has no covered pair;
  PA's first covered pair is `PA:(F?S:M)+m`, `PA:(S?M:m)+F`.
  This is the expected split-gate outcome; the approved B calibration remains
  feasible and is still queued. Evidence: [full_screen.json](smoke/full_screen.json).
- Full-cap cost smoke: 64 searches, four retained cells × eight arms × two fresh
  seeds 1603900–1603901, P256, length32, cap524288, ten workers. Cells include
  two BE and two PA targets, with new F-conditioned targets. 42.30 s wall;
  mean 5.532 worker seconds/search including capped searches. Measured wall
  extrapolation for 5,200 B searches: 57.29 minutes before full screening and
  reporting. Within the approved 3.5 h internal deadline / 4 h timeout.
  Two seeds/cell/arm cannot establish the full-run solve forecast.
  Evidence: [full_cap_benchmark.json](smoke/full_cap_benchmark.json).

| Arm | Exact solves / 8 | Mean worker seconds/search |
|---|---:|---:|
| U | 3 | 12.919 |
| F4 | 6 | 5.596 |
| G4 | 6 | 6.006 |
| G4-marg | 7 | 5.100 |
| G4-BE | 8 | 0.678 |
| G4-PA | 6 | 6.558 |
| G4-BE-marg | 8 | 2.172 |
| G4-PA-marg | 6 | 5.226 |

- Reduced end-to-end run (`--smoke --workers 2 --screen-depth 3 --seeds 2
  --cap 4096 --deadline-seconds 600`): all three shallow screens, 32 calibration
  searches, tables/hashes, checkpoint, censored summaries, paired contrasts and
  plots completed in 2.64 s. Explicit `smoke_only` outcome. A shallow-screen
  split initially referenced cells omitted from the reduced smoke bank; fixed
  by excluding smoke from full split/headroom routing. Final smoke passes.
- Tiny actual learner runs: one generation plus initialization and fresh final
  parent selection on each of BE and PA, inner cap256, two workers. BE 2.87 s,
  PA 2.59 s. Raw generations/candidate tables, fresh seeds, final maps and
  within-generation ranking diagnostics emitted. These exercise the conditional
  code path and do not test learning or the approved full pilot gates.
- Deadline smoke with a one-second work slot: writes interruption.json and
  summary/plots, B marked incomplete, retaining completed outputs. Smoke remains
  labelled `smoke_only`; regression tests separately verify U precedence for
  missing calibration seeds and unfinished C scoring.
- 203 tests passed in 15.52 s: FIRST and legacy dispatch, 24-token decoders,
  exact tied marginals, unordered BE roles, sparse learner compatibility,
  seed-paired interval cancellation/direct context contrast, censor bounds,
  C cost search counts, all feasibility outcome routes, original composition,
  assembly, family-bias, map learner, and v2 Python/Rust differential tests.
- Ruff check passed on all new modules and modified experiment helpers.
  `scripts.queue_lib.load_queue` accepts the one-entry queue; ID prefix correct,
  timeout sum 14,400 s < eight-hour cap. All output paths derive from RUN_DIR.

Raw supplementary reduced-run/pilot/deadline files remain in this task's
`smoke/runner-final`, `smoke/actual_pilot` and `smoke/deadline` directories.
The committed task snapshot retains the full validation, reviewed D1331 screen,
full-cap benchmark observations and the benchmark script.
