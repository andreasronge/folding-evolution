# Implementation verification

Implementation commit: `3f60bd9` on `research/2026-10-10-2254`.

No full calibration or fresh target scoring was run by the researcher. The full queue still requires Stage 0 admission.

- `pytest tests/test_tree_gp.py tests/test_tree_gp_report.py tests/test_component_transfer.py -q`: 17 passed (10.75 s).
- Ruff and `git diff --check`: passed.
- Queue parser/validator: three sequential entries, 14,400 s summed timeouts; all ids have the required prefix.
- Driver import checks: Python package and Rust extension both load from this worktree.
- The scoring gate refuses smoke preparation before creating a target-search file; see `smoke-blocked-scoring.log` and `smoke-blocked-scoring/failure.json`.

## Committed smoke measurements

- Full schedule audit: 256 calibration rows, 1,792 scoring rows; zero unintended overlaps against calibration, smoke, reserved tail diagnostics and 1,544 saved acquisition/replay seeds.
- Development preparation smoke: 32.00 s; all 16 native replay records match every historical non-timing field. Smoke mix selection is never admitted for production.
- Six initializer bins and 1,998 independent-interpreter/Python/Rust checks pass; all 16 canonical validation fixtures agree on D625. Fixtures never enter search.

|Family|Development seed|Solved|Evaluations|Worker-search seconds|Deterministic replay|
|---|---:|---|---:|---:|---|
|DG|22160000|True|6144|0.263|True|
|TS|22161000|False|524288|31.077|True|

See `smoke-committed/` for raw schedules, provenance, replay, development calibration and validation files. The earlier debugging smoke is preserved separately; its four truncated calibration-labelled rows cannot authorize scoring.

## Final ten-worker full-cap diagnostic

Ten development searches per family, frozen smoke mix 0.9, Rayon one thread; every job forced to spend 524,288 evaluations. These are timing diagnostics, not calibration or performance estimates.

|Family|Batch wall seconds|Mean worker-search seconds|Maximum search seconds|Effective concurrency|Planning projection seconds|80% scoring limit seconds|
|---|---:|---:|---:|---:|---:|---:|
|DG|55.90|51.54|55.42|9.22|4068|5760|
|TS|52.79|48.65|52.78|9.22|3203|4320|

Planning projections use conservative native replay/historical rates and historical G4 rates, 30% reserve plus 120 seconds overhead. Production admission still requires the complete sustained 256-search Stage 0, selected-mix full-cap tails, precision diagnostics and DG solve fraction at least 25%.

All requested code is committed and the branch is clean. No research/ files were included in the three implementation commits. Queue is ready for the loop code review, not yet executed.


## Code-review repair verification

Repair commit: `c32ff04`; original implementation remains `3f60bd9`.
Blocking code-review issue 1 is fixed by canonically sorting reloaded tails
once before both hashing and projection. All design parameters and gates
remain unchanged. Smoke preparation now receives the intended `ValueError`
instead of `KeyError` when scoring is attempted.

- Final targeted suite: 19 passed in 14.10 s (tree search, report, and component transfer).
- Both new admitted-preparation regressions (DG/TS) reach the scoring execution
  boundary with synthetic evidence and shuffled tails. Changed timings are
  rejected. Search-semantic validation is replaced only for this synthetic
  fixture; existing real development-search tests cover that boundary.
- Replaying the old reload function in memory makes both regressions fail at
  `timing/solve gate changed`: [regression-original-code.log](regression-original-code.log).
  No worktree code was changed for this negative control.
- Ruff lint, Ruff formatting and `git diff --check` pass.
- Queue validator passes for the unchanged three sequential entries; timeouts
  total 14,400 s, all ids start with the required task prefix.
- Corrected full schedule audit passes against all 1,544 saved seeds; pairing
  is intact, with zero unintended overlaps: [audit-review-repair/](audit-review-repair/).
- Committed development preparation smoke completed in 32.21 s;
  all 16 native replay records match, semantic/initializer validation passes,
  and no fresh target was searched: [smoke-review-repair/](smoke-review-repair/).
- Attempting DG scoring against that smoke produces the intended gate failure
  with `targets_scored: false`: [smoke-review-repair-blocked/failure.json](smoke-review-repair-blocked/failure.json).

No production mix has been selected and full preparation/scoring remain queued.
Minor reviewer observations are handled as recorded in plan.md: strict approved
deadlines and low-solve stop retained, same-invocation sibling dependency
retained, historical TS timing floor retained. No design infeasibility was
observed in repair verification. Production admission remains mandatory.
No research/ files are committed on the task branch.
