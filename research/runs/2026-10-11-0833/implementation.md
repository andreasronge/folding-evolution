Implemented `experiments/chem_tape/tree_source_run.py` and `tree_source_report.py`
using the unchanged 0150 extractor, control generator, tree search and restart
executor. Original method files remain unchanged and are checked against archived
0150 hashes. The wrapper exposes actual TS provenance throughout acquisition and
scoring; it does not relabel TS jobs as DG. Full queue remains fixed at 768 source
jobs and 9,216 scoring jobs, plus bounded validation/calibration.

Feasibility evidence: [smoke/stage_gate.json](smoke/stage_gate.json),
[smoke/verification.json](smoke/verification.json),
[smoke/reconstruction.json](smoke/reconstruction.json),
[smoke/replay.json](smoke/replay.json), [smoke.log](smoke.log).
The smoke's `preparation.json` is explicitly unadmitted and cannot authorize
scoring. Calibration runs are excluded from confirmation; the production prepare
entry repeats the same calibration before collecting any confirmation source jobs.

- Rebuilt the worktree Rust extension with the required release maturin command.
- Canonical checks passed on all 12 TS source/native cells and all 144 GS screen
  cells, with independent interpreter, Python and Rust outputs on D625.
- Reconstructed all 24 archived DG libraries and verified all eight saved
  off-path deterministic replay jobs. Seed/source-target audits passed.
- Actual TS-source calibration: 64/64 solves; 16 jobs per source cell; mean
  evaluations 4,288 / 2,768 / 12,048 / 6,048 (source IDs in the gate JSON).
  Across sources, mean 6,288 evaluations and 0.354 worker seconds/job. The two
  32-job builds cost 201,216 evaluations/build on average; yields seven/six entries.
  This tests the proposal's source-cost assumption directly; target-cell rates
  and pseudo-library yields were not substituted for source measurements.
- Scoring calibration: 96 B/C and 48 native jobs, all solved. B/C mean worker
  seconds: R-tree 4.998, R-TS 2.509, R-DG 1.532, R-sizeTS 2.880. Native:
  R-tree 0.297, R-TS 0.628, R-DG 0.764. Timing only; no usefulness decision
  or library selection based on these observations.
- Stage elapsed 60.47s. Conservative timing projection with registered floors,
  observed concurrency and reserve: preparation 268.69s; scoring 5,706.09s.
  Passed the 2,700/9,000s envelope. `estimated_minutes` is updated to 105 to
  cover this conservative projection and score-loading/reporting overhead.
- New tests: 11 passed, covering full schedule/seed separation, actual TS family
  identity, empty fallback, source-family rejection, outcome/guard precedence,
  complete-grid reporting, independent DG bootstrap, acquisition accounting,
  plots, smoke rejection and timing-only admission. Existing tree-library and
  tree-GP tests: 16 passed. A synthetic reporting fixture initially omitted
  attempt evaluation counts; corrected the fixture and reran all new tests.
  Ruff check and format pass on all three new files.
- Queue parsed with `scripts.queue_lib.load_queue`: two sequential entries,
  11,700s total timeouts (195 minutes), below the approved four-hour ceiling.

The full confirmation queue has not been run by the researcher. Production
preparation hashes all current method files and rejects incompatible or changed
preparation at score time. Reporting keeps B/C and native separate, jointly
resamples acquisition with its owner build, and resamples the independent DG
cohort separately for TS/DG contrasts. Shared baseline rows are retained once
per slot. Historical DG acquisition worker costs remain historical measurements;
this host/load limitation is explicit in report scope and the raw timing evidence.

Committed implementation and tests as
`28db9640e98cb86c8dd2ac44d372877fcfde933f` on `research/2026-10-11-0833`.
Task files/evidence remain in the main checkout task folder; no `research/` files
were committed on the task branch. Worktree `git status --short` is empty.
