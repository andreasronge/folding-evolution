---
verdict: pass
---

# Code review: 2026-10-09-2303 (commit `74196a8`)

Reviewed `git diff abb473f..74196a8` (bank builder, run driver, report, tests, frozen
2033 artifacts), `proposal.md`, `critique.md`, `plan.md`, `queue.yaml`, the committed
smoke outputs, and ran `tests/test_two_sum.py` (10 passed, 5 s) in the worktree. The
worktree is clean at the pinned commit and `.venv/bin/python` imports `_folding_rust`
and `two_sum_run`.

## Blocking issues

None.

## What was verified

1. **Bank** (`two_sum_bank.py`, `data/two_sum_2303_bank.json`). Byte SHA matches
   `BANK_SHA`. Independently recomputed: 444 raw, 333 nonconstant, 289 distinct
   behaviours, 76 eligible after the ≤9-token screen and the <80% agreement check
   against all 306 old behaviours (220 comparison-gate + 86 then-addition, excluded
   cells included). Re-running the SHA-256 greedy pick reproduces exactly the 16
   confirmation and 4 timing ids; gate-pair quota is exactly 4 per unordered pair
   across all 20 (MS, Sm, FM, FS, Fm); max mutual agreement across the 20 is 0.778;
   max old-roster agreement 0.782; no confirmation/timing overlap. Canonical
   validation covered every assignment on all 1331 inputs in Python and Rust with
   zero mismatches, which answers critique note 2. The search envelope receives only
   `{id, labels}`; canonicals and witnesses never reach the search.
2. **Arm wiring** (`two_sum_run.py:329-366`). A8/S8 use the per-corpus-per-block 2033
   builds (table + fragment library); full F uses the per-corpus 1036 C table and
   pinned library, cross-checked against the 1036 freeze hashes and `pinned_history`;
   G4 uses the G4 table with no fragments and the operator off. All fitted arms run the
   same F `BlockOperator` (the job's arm string is only used to construct the operator
   and is restored to the arm label afterwards). The decoder hash of every search row
   is checked against its envelope, so a mis-wired build would fail loudly.
3. **Seeds and pairing.** Fitted arms share `(corpus, cell, ordinal)` seeds and hence
   training cases (checked in `jobs()`); timing seeds (+1 000 000), confirmation
   seeds, G4 timing (+2 000 000) and G4 confirmation (+3 000 000) are disjoint, and
   disjointness from the replay seeds is asserted at start-up. Blocks are balanced:
   8 seeds gives 2 per block, 4 seeds 1 per block; timing covers BE1 and PA1, all four
   blocks, one seed each, all three fitted arms (96) plus 16 G4 = 112.
4. **Estimator** (`two_sum_report.py`). Primary ρ reuses `small_source_report.contrast`:
   log capped cost, unsolved = 2·cap, mean over cell/seed pairs within (corpus, block),
   equal-block mean, 16 corpus contrasts, t interval with 15 df, and the report refuses
   to run with missing blocks or n ≠ 16. Usefulness G4/A8 resamples G4 seeds within
   each fixed cell, shares each baseline draw across all corpora and methods, and
   resamples corpora stratified by family (critique note 4). The 25% full-F solve
   guard, the ρ thresholds (1.20, 1) and the separate labelling of bounded retention,
   usefulness failure and relative loss match plan.md and the proposal.
5. **Gates and stop rules.** Stage 0 projects 8/all, 4/all, 4/no-S8 in order from the
   measured per-arm timing means, always adding the unchanged 256-search G4 roster,
   with the 1.15 margin, the 150-min search ceiling, the 3-h score budget (minus
   timing-replay and report reserves) and the actual 07:12:10 analysis cut-off (one
   hour before the strategist's 08:12:10 deadline; local tz is +02:00 as hard-coded).
   With the committed smoke full-cap means (A8 10, S8 21, full F 16, G4 20 worker-s)
   the 8-seed option projects to about 12 000 s and will almost certainly fall to the
   pre-registered 4-seed/all-arms option (about 6 400 s); that fallback was approved
   in the proposal. The "stop and report" branch requires the 2304-search option to
   exceed 150 min, i.e. a mean A8+full-F search cost above roughly 68 worker-s, while a
   capped search measures about 21 s, so a stop for the wrong reason is not a realistic
   risk. Smoke prepare ran in about 2 min, far inside the 2580-s prepare limit.
6. **Queue.** Two solo entries run sequentially; `${RUN_DIR%/*}/…-prepare/preparation.json`
   is the same handoff pattern that worked in 2033, and `run_queue.py` fixes the date
   directory once at launch, so crossing midnight does not break it. Timeouts
   2700 + 10800 s = 3.75 h, under `max_queue_hours = 8`; `--deadline-seconds` sits
   120 s inside each timeout. Every `expect_outputs` entry is written by the code path
   that succeeds. The score stage re-verifies the freeze, the admission hash, the worker
   count, the remaining wall time, and replays all 112 timing rows scientifically before
   any confirmation search.
7. **Critique disposition.** Notes 1–6 are implemented in plan.md and the code as
   described above. Notes 7–10 concern wording in the digest and question logs, which
   the researcher role may not edit; plan.md says so and defers them to the steward.
   That is an adequate answer, but the steward should act on them at `decide`.

## Minor notes (non-blocking)

- `admission()` estimates effective throughput as Σworker-s / wall over 112 jobs, which
  includes the end-of-roster tail, so projections are mildly conservative. The bias
  pushes toward a smaller schedule, never toward running an unaffordable one.
- The timing cells are four separate targets, so the projection assumes they are
  representative of the 16 confirmation cells; this is inherent to the approved design.
  The 4-seed option leaves about 2 h of slack in the 3-h score budget to absorb harder
  confirmation cells.
- On the smoke timing cell S8 capped out in 3 of 3 full-cap searches; if that holds on
  the roster, σ = S8/A8 will be driven by the 2·cap penalty. It is reported without a
  rule, so this is an interpretation caveat for analysis, not a design flaw.
- "Canonical sum order" is ASCII order (F < M < S < m); the plan states this
  explicitly, and dedup by label hash makes the choice immaterial to the bank.
- Both `comparison_gate_report.describe` (`verification_seconds`) and the local
  override (`external_verification_seconds`) are used; the override wins, so worker
  seconds in `summaries` include external verification as documented.
