# Implementation and admission

Implementation commit: `8e628310bba8f4cca6c473fb5c2102de3854df3a` on
`research/2026-10-09-0125`. Worktree status is clean. Preparation precedes this
commit and records the exact source/binary hashes rather than relying on its
then-current HEAD; the full runner enforces those hashes after commit.

Implemented `experiments.chem_tape.frequency_matched_run` and its report wrapper.
The existing spawned-worker, checkpointed search path, seed streams, decoder,
cap, population, fitness and exact-D1331 checks are reused unchanged. Rust code
was not changed; no rebuild was necessary. Immutable 1548 row F inputs are
vendored with independently pinned provenance, original clean-commit metadata
and decompressed search hashes. The existing pinned 1246 C/T/K tables are reused.

Preparation passed in 96.62 s on the actual worktree build. Evidence:

- Raw preparation: `/Users/andreas/developer/folding-evolution-research/2026-10-09-0125/experiments/output/2026-10-09/2026-10-09-0125-preparation/`.
- Committed admission artifact: `experiments/chem_tape/data/frequency_matched_0125/preparation.json`.
- All 32 fixed C/T replay jobs exactly matched all non-clock fields, including
  complete trajectories, sampled indices, initial token hashes, evaluations,
  solved flags, shortcut counts and metadata. All 18 original Python source
  hashes were independently checked against git objects at 45b2bdb.
- All 48 table hashes and the bank SHA passed; maximum pooled marginal error
  was 2.8970847247511422e-5, reproducing strategy's stated approximately 2.9e-5.
- The fixed 16 K timing jobs used ten workers, solved 9/16, took 33.57 s wall
  and 14.89 s mean worker time. Effective concurrency including the small-block
  idle tail was 7.10. This is timing on one fixed cell, not a whole-bank solve
  estimate. The direct projection is 71.61 min; all-capped projection 110.49 min
  (127.06 min including 15% admission margin), inside the 150-minute timeout.
- Full-run constructor/payload smoke passed: all 2,048 scheduled jobs, exact
  prepared implementation/binary identity, labels-only search payloads and
  unchanged P256/cap524288. Its artifacts are in the sibling
  `2026-10-09-0125-full-admission-smoke/` output directory.

Verification: 26 tests passed across the new six checks and existing
then-addition, comparison-gate and solver-corpus suites. Tests cover exact
rosters, deterministic replay fields, corpus aggregation/ratio direction,
incomplete/error refusal, cap sensitivity and empty both-solved occupancy.
The C/T endpoint and both 95% sensitivity intervals reproduce the original
1548 report to 1e-12. Partial-result report/plot generation passed and the
diagnostic image was visually inspected (sibling
`2026-10-09-0125-report-smoke/`). Ruff and git whitespace checks passed.
`scripts/run_queue.py --validate` accepts the one-entry full queue.

No scientific design changes or top-up. The full queue has not been executed.
Every timed K row is rerun and checked within the full fixed roster. Only all
16 complete corpora permit the primary sufficiency decision; errors/timeouts
exit nonzero with an incomplete report. The report retains the C/T result,
per-cell/family comparisons, solve counts, 1*cap and selection-conditioned
both-solved sensitivities, descriptive log share and unpaired K/G4 caveat.

Critic notes 1–4 are incorporated. Notes 5–8 are explicitly deferred to the
steward in plan.md because this role cannot edit questions/logs or belief files.
Task files are in the main checkout task folder; no research/ files are committed
on the implementation branch.
