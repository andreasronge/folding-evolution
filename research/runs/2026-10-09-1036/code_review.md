---
verdict: pass
---
# Code review: 2026-10-09-1036 frozen fragment reuse on excluded compositions

Reviewed `git diff a8bfc3d..348f9e2` in the worktree (new `fragment_reuse_run.py`,
`fragment_reuse_report.py`, pinned fixtures, tests; small parametrisations of the 0843
operator/report/runner), plus proposal.md, plan.md, queue.yaml and critique.md. Ran the
focused tests (11 pass), recomputed fixture SHAs, rebuilt the rosters and checked seeds,
pairing and cell membership.

## Blocking issues

None.

## What was checked

- **Arm wiring.** C/F/W share one seed per (corpus, cell, seed index); the base runner's
  `jobs()` rejects any triple whose initial-token hash or case draw differs, and rejects any
  edited elite. F receives the whole-corpus library; W receives the same library so its length
  law is identical, but samples block content from the C chain conditioned on the preceding
  token. C's operator never edits. `search()` uses the arm only as a label.
- **Rosters and seeds.** 16-seed roster: 15 360 rows, exactly 3 arms per pair, 4 096 per
  then-addition arm and 1 024 per holdout arm. The 12-seed fallback roster is a strict subset.
  Seed offsets cannot collide across phase/family/corpus/cell/index, and `check_seeds` rejects
  overlap with 6 704 historical 1548/0843 seeds and the 1246 source schedule (the earlier base
  overlap mentioned in plan.md is fixed by the new base). All 16 scheduled then-addition IDs are
  in the retained cell map and the 8 holdouts are in the bank with no overlap with training.
- **Metric and rules.** `comparison(X, Y)` returns exp(mean over corpora of log cost_Y − log
  cost_X), so F/W > 1 favours F; unsolved = 2×cap; t interval on 15 df. `route()` applies the
  four proposal rules in the stated order on then-addition only; holdouts are reported
  separately with no rule. W-cheaper flag requires rule 3 and W/C lower bound > 1, as proposed.
- **Library fidelity.** Reconstruction must equal the pinned 0843 whole-library record and
  hash per corpus; scoring re-checks the libraries against the pinned fixture. The NOP-pad
  exclusion remains source-cell only; evaluation-cell padded hits are recorded, not filtered
  (12 288 tests, 0 hits in the smoke).
- **Gates and stop rules.** The only gate that can stop the main stage is timing: 16 → 12
  seeds → infeasible, with 1.15 margin against 195 min. The smoke roster is preselected from
  historical C difficulty (ranks 0/5/10/15 and 0/2/5/7); I checked that the mean historical
  cost of those ranks is within 2% of the full-cell mean for both banks, so the projection is
  not biased low. Even using 1548's higher C time (7.1 s) the projection is about 166 min
  against a 201 min scoring deadline. The gate cannot stop the main stage for an efficacy
  reason, and no efficacy-based sizing or pruning exists in the code.
- **Handoff.** Scoring verifies implementation hashes, bank/source/library/table/roster hashes,
  then replays all 96 smoke searches and compares solver tapes and operator counters before
  any efficacy search. Incomplete or duplicated rosters raise before `report()`.
- **Smoke artifacts.** `smoke/prepare-final` admitted 16 seeds (153 min projected). Its config
  records commit a8bfc3d (the then-uncommitted tree), but all 40 recorded implementation hashes
  equal the files at 348f9e2, and the queued prepare regenerates preparation.json anyway.
- **Queue.** Timeouts 1800 + 12300 s = 3.92 h < 8 h cap. `${RUN_DIR%/*}` resolves to the
  dated output directory, which run_queue computes once per invocation, so prepare and score
  share it; same pattern as 0843. `expect_outputs` match what the code writes.
- **Critique.** Notes 1–5 are addressed in plan.md and in code (explicit solve scenarios,
  preselected smoke roster, timing-only fallback, conditional precision labelling, W length-law
  saved in `operator_laws.json`, repayment versus both C and W with extraction separate from
  corpus collection). Notes 6–8 (digest/question wording) are outside the researcher's write
  scope; plan.md says so and defers them to the steward. That is an acceptable "why not".

## Minor notes

1. The subclass `admit()` does not add the smoke replay and reporting reserve to the fit test
   as 0843's did. With a 195 min ceiling, a ~48 s replay and a 201 min deadline the reserve is
   about 5 min; real projection is 153 min, so this is fine, but a projection near the ceiling
   would leave little room for the report.
2. `validation.update(libraries_match_0843=True, paired_initial_tokens=True,
   elite_exclusion=True)` records constants. The properties are enforced by raises upstream, so
   the flags are truthful, but they are asserted rather than computed.
3. If the queue were resumed on a later calendar date with prepare already marked done, the
   score entry would look for preparation.json under the new date and fail loudly. Not a
   correctness risk; same as 0843.
4. For the steward at decide time: the exact wording corrections in critique notes 6–8 live
   only in critique.md; the plan asked for them to be relayed in handoff notes but no separate
   handoff file exists in the task folder.
5. `self.cells.update(ta_cells)` loads every retained then-addition cell, not only the 16
   selected; only selected IDs are scheduled, so this is harmless.
