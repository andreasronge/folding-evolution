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
