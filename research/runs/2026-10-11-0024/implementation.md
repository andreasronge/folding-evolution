# Implementation and smoke evidence

Implementation commit: `1773d11e97ccbc710a1ead0d969c926102cb0860` on
`research/2026-10-11-0024`; final worktree status is clean. No `research/` files
were committed.

The approved three-arm, two-roster design is implemented without changes to the
2254 search engines. `restart_gp_run.py` supplies the fixed scheduling wrapper,
seed publication/audit, preparation gates and complete per-attempt evidence.
`restart_gp_report.py` supplies the paired 24-build bootstrap, reliability guard,
secondary contrasts, per-cell reports, historical sensitivity and acquisition
economics in both cost units. Historical rows and observed seed evidence are
hash-checked repository data; source hashes enforce the frozen c32ff04 search.

All task artifacts remain here in the main checkout; no `research/` changes are
included in the task-branch commit. Critique dispositions are in plan.md. There
were no code_review.md or driver_feedback.md files at task entry.

Validation:

- `tests-final-corrected.log`: **26 tests pass in 52.47 s** across restart,
  original tree and original report suites. Tests cover later solve and complete
  failure accounting, real-engine first-attempt equivalence/replay, altered
  training indices, seed overlaps, grid counts/pairing, failure penalties,
  ratio/reliability boundaries, bounded/unbounded repayment, report artifacts,
  preparation reloading in completion order, modified evidence refusal and smoke
  admission refusal. Synthetic report/admission fixtures are test data only.
- Ruff lint and format checks pass. Plots from the synthetic complete-grid report
  were visually inspected: dynamics and acquisition-plus-search graphics render
  in both cost units. These plots are not experiment results.
- Direct preparation smoke: all eight development scheduled searches matched
  their ordinary first attempts on every non-timing field, and replayed as whole
  jobs. Examples include DG tree solving on attempt 3 (5,376 evaluations), TS
  tree solving on attempt 2 (4,096), and complete eight-attempt failures
  (16,384). All sixteen saved native A8 replays matched. Smoke cutoff is **2,048**,
  not the production cutoff; no target searches ran.
- `smoke-queue.log`: the actual queue runner completed its smoke entry with
  status **done**, exit 0, wall **73.834 s**, including seed/semantic checks,
  eight equivalence checks, eight deterministic job replays and all sixteen
  native A8 replays. Output is under `smoke-queue-output/2026-10-11/2026-10-11-0024-smoke-queue/`.
  Queue-owned metadata/stdout/stderr files are accepted; prior experiment files
  are refused. This integration check caught and fixed the fresh-directory
  interaction before the full queue was handed off.
- Published unique search seed counts: restarted 12,288 (intentionally shared
  between primary arms), full-cap 768, Stage 0 512, development validation 32,
  semantic validation 1. Against **3,692 historical seeds**, every prohibited
  intersection is empty. Original native replay reuse is an explicit exception.
- `queue.yaml` passes `scripts/run_queue.py --validate`: three entries with
  approved-prefix IDs, timeouts **1800/5400/1800 seconds**, **2.5 hours** summed.

An intermediate test edit placed a new test inside the preceding function.
Lint caught the placement error; it was corrected, and the full final suite
passes. The failed intermediate log is retained as debugging evidence.

The measured historical sensitivity costs **0.24 worker seconds**, with 256
simulated datasets and 512 paired build draws per dataset. Cell pooling recovers
the proposal's DG projections (tree 87,314 evaluations / 98.97% solving;
A8 110,563 / 98.68%). Build pooling gives tree 96,956 / 97.68% and A8 123,714 /
96.44%; its simulated joint evaluation-win/reliability-pass frequency is about
**58.6%**, versus **99.6%** for cell pooling. Cell×build empirical pooling gives
no joint resolutions: with two observations per cell/build, it freezes many
zero-hit buckets and is an unstable sensitivity, not a forecast. Paired historic
rows are sampled jointly across arms, with independent attempts within each
fixed build. These scenarios qualify the original power/reliability expectations;
they do not alter the approved scoring size or constitute a feasibility gate.

Full-scale Stage 0 remains **queued**: 64 sustained DG jobs per restarted arm
at the production cutoff, after validation and replay. Its projection includes
all 768/768/384 DG jobs, measured effective concurrency, historical full-cap A8
worker time, 30% reserve and 90 seconds overhead. Above **4,500 seconds (75 min)**
it refuses scoring. Tiny smoke projections are not production runtime evidence,
and smoke preparation is explicitly unadmitted. No measured obstacle was found
in the authorized small-scale checks; no full queue or fresh target scoring was
run during implementation. Expected full queue wall remains **80 minutes**,
conditional on that admission gate. Return to strategy after the result or any
measured gate failure; no tuning or enlargement.
