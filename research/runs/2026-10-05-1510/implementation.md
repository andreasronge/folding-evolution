# Implementation and verification

Implemented `experiments/chem_tape/family_bias.py` and sampling-only PyO3 helpers
in `rust/src/tag_sampling.rs`. Existing evolution and TAG execution paths are
unchanged. The new helpers preserve Python TAG semantics and share predictions
across tasks, with exact early rejection and exhaustive checks of survivors.

All proposal gates are automatic and checkpointed before subsequent stages:
uniform eligibility and holdout substitution; per-task observed-use pruning
with joint deletion and low-support reporting; exact, equally weighted elite
updates; independent start validation; reciprocal transfer with adjusted
scheduled-look intervals and separate beyond-pruning diagnostics. One-member
families, reversals, failed validation, under-supported pruning, budget cuts and
mixed/unresolved patterns are explicit. `plan.md` documents critique repairs and
implementation details. Output reports include calibration and transfer tables,
and `result.json` contains all task rates, fitting/validation details, vectors,
seed streams, actual sample counts, timing and gates.

Validation:

- Rust rebuilt in the worktree venv using
  `cd rust && VIRTUAL_ENV=../.venv uvx maturin develop --release --uv`.
- Focused fidelity/regression suite: 52 passed (family-bias tests, existing TAG,
  op-weight and exact-any tests). The family-bias suite alone has 10 tests.
- Rust/Python parity covers 500 tapes with enriched cycles and duplicate tags;
  every candidate threshold has a planted solver checked on all 10,000 inputs.
- Synthetic plumbing covers validated reciprocal transfer and unresolved
  zero-count transfer at all four looks. These counts are test fixtures only.
- Real smoke: 2,000 tapes for each benchmark distribution and 20,000 uniform
  calibration tapes; zero exact hits, eligibility gate fired, all expected
  artifacts generated. No full-run result is claimed.
- Final eight-thread smoke measured approximately 469k uniform / 519k crude
  enriched tapes/s at tiny batch size; successful planted exhaustive checks
  cost approximately 0.000125 s each. Full execution remeasures throughput,
  including actual exhaustive candidates under fitted enrichment.
- Ruff and queue validation passed; diagnostic plot visually inspected.

Smoke artifacts (ignored by git):
`experiments/output/smoke-family-bias-final/` in this worktree. Full output is
always under `$RUN_DIR`. The single full queue entry has a 21,600-second timeout
and a 21,000-second internal deadline; full sampling caps remain within the
approved 340M-tape maximum, excluding the small throughput benchmarks.

Task-owned plan/queue/proposal/approval/critique and these verification notes are
mirrored into this branch's `research/runs/2026-10-05-1510/` for a reproducible
commit snapshot. The live task folder in the owner's research tree contains the
same plan and queue; driver logs are left to the autonomous loop.

## Code-review repair — 2026-10-05

Addressed the fitting-capacity issue within the approved 15M-per-fit cap: start 0
uses retained fitting tasks' exact uniform calibration solvers for iteration 0.
This replaces one fresh fitting pool rather than adding a seventh update. Starts
1–2 retain their independent Dirichlet initializations. Calibration never seeds
their updates, and no holdout elites enter any fit. Validation and transfer remain
fresh. Bootstrap support, predicted uniform elite counts, per-start fresh updates,
and a distinct no-task-updated status/gate are recorded. An unadapted fit is no
longer described as an adapted fit that failed validation.

Completed decisive transfer results now survive deadlines in either the prune
extension or the both/swap diagnostics. Fitting-task rechecks are saved before
optional diagnostics. Diagnostic interruptions remain explicit, and deadlines
during decisive sampling remain inconclusive. Descriptive fixed-look confidence
intervals are named accurately, the prune floor is logged as a raw-weight ratio,
and swaps report probabilities falling below the fitting floor without changing
their literal mass exchange.

The calibration design blocker in code_review.md is **not resolved**. Its 35M
uniform probe results strongly predict ineligibility at the approved 60M cap.
No proposal amendment or steward agreement permits expanding calibration to 1B
or changing thresholds. Those changes were requested as a clarification; absent
authorization, this repair preserves the approved task set and caps. The queue
is syntactically runnable but should not be treated as scientifically cleared by
this repair. An infeasible outcome cannot support C/D or parking frequency bias.

Repair validation:

- 57 focused tests passed: 15 family-bias tests plus the existing TAG, op-weight
  and exact-any regressions. Added tests cover rare-task bootstrap with equal
  task weight, untouched holdouts/other starts, six-update/sample caps, no-update
  status, and primary versus descriptive deadlines (both prune and both-fit).
- Real smoke: 2,000 tapes per benchmark arm, 20,000 uniform calibration tapes,
  zero exact hits, correct eligibility stop and all five queued output artifacts.
  Synthetic all-stage tests are fixtures only, not experimental observations.
- Ruff, whitespace checks and queue schema/cap/output validation passed. The
  diagnostic PNG was visually inspected. Rust was not changed in this repair.
- Smoke artifacts: `experiments/output/smoke-family-bias-review-repair/` in this
  worktree (ignored). No full experiment was executed.
