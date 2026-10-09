---
verdict: pass
reviewed_commit: e9a04f8b74bb101849ef78d17eb2897dde2b5088
base: de159a1ec2613c1b84c2cf0b0847a79cd6339382
---

# Code review: 1350 pre-solve fragment source assay

Reviewed the diff `de159a1..e9a04f8` (9 files, 825 insertions), proposal.md, critique.md,
plan.md, queue.yaml, and the final smoke outputs in `smoke-final-prepare/` and
`smoke-final-handoff/`. I also re-ran the new test file and checked the worktree state.

## Blocking issues

None.

## What I verified

1. **Arm wiring.** `pre_solve_run.execute` maps E to the reviewed `F` executor with the
   pre-solve library and W_E to the reviewed `W` executor with the same library, then restores
   the public arm label. `BlockOperator('W', …)` takes only its length law from the library it is
   handed (`self.lengths`) and draws content from the C chain, so W_E is C-chain content under
   E's per-corpus length and uniform start law, as the proposal specifies. Historical C/F/W
   replay rows go through the unchanged executor with the pinned 1036 whole libraries.
2. **Seeds and pairing.** `schedule()` takes the 1036 then-addition C rows and duplicates them
   for E and W_E, so E/W_E share initial populations and case draws with each other and with
   the historical C/F/W rows. `jobs()` enforces equal `initial_tokens_hash` and
   `training_indices` within each (corpus, cell, seed) group, and the report re-checks pairing
   metadata against the historical C row before admitting E/F, E/C and W_E/W. Smoke seeds live
   in a separate namespace and are checked for collision against the 1036, 1831 and 1548
   rosters. The 12-seed fallback is a prefix of the 16-seed roster (tested).
3. **Metric direction and rules.** `comparison(rows, 'E', 'W_E')` computes
   log cost(W_E) − log cost(E), so E/W_E > 1 favours E, matching plan and queue notes.
   Unsolved cost is 2 × cap, 95% t interval over 16 corpus means (df 15). `route()` applies the
   four rules in the plan's order (harm, useful, no worthwhile increment, unresolved); no power
   gate or sequential look exists. Boundary cases are tested.
4. **Source selection and extraction.** `select_sources` validates every archive row's
   checkpoint, evaluations, cell, seed, non-exactness and tape before use, raises on any
   checkpoint at or after the first-solve generation, and picks the minimum-slot `S` row per
   checkpoint without reading accuracy or eventual success (tested by flipping `solved`). `S`
   rows are the archived lexicase-selected parents, as the proposal says. Selected tapes are
   re-evaluated on the full domain and must reproduce the saved accuracy and remain non-exact.
   The extractor is the shared 0843 `library()` with the probe's ranking (−cells, −raw
   occurrences, −length, tokens), the family training-cell NOP-pad exclusion, 96 `rng(0)`
   activity inputs and top 32. The legacy exact-source path still reconstructs the pinned 1036
   whole library bit-exactly (tested).
5. **Gates that decide whether the main stage runs.** Admission in `admit()` uses only
   measured worker-seconds and smoke concurrency efficiency; solve counts are recorded but
   unused (tested both ways). Final smoke: E 6.03 s, W_E 3.98 s per search, efficiency 7.39,
   projected 106 min at 16 seeds against the 135 min bound, 80 min at 12. The score deadline
   leaves 146 min of job time against that projection, and the smoke efficiency (7.39) is
   lower than 1036's full-run efficiency (9.94), so the projection is conservative. All other
   preparation checks are fail-closed consistency checks that the end-to-end smoke already
   passed on the same code, data and Rust build. I see no gate that could stop the main stage
   for a reason unrelated to its feasibility.
6. **Historical replay demotion.** A mismatch in any of the 48 replays sets
   `historical_paired=False`, which drops all three of E/F, E/C and W_E/W and keeps E/W_E as
   the only inferential contrast (tested). The smoke replay matched 48/48 on the full field
   list including `solver` and `operator`.
7. **Handoff and freeze.** The score refuses a preparation whose freeze (implementation and
   Rust hashes, bank/table/provenance SHAs, library and law hashes, candidate/smoke/replay
   schedule hashes) differs from what the running code computes, then replays all 64 smoke
   rows bit-exactly before any efficacy search. The committed handoff passed this path.
8. **Environment.** Worktree is clean at e9a04f8. The worktree `.venv` Rust extension hash
   equals the hash recorded in the smoke's config, and the smoke's `git_commit` is e9a04f8.
   `tests/test_pre_solve_fragments.py`: 12 passed. `run_queue.py --validate` passes; the two
   entries are solo sequential groups, the date directory is computed once per queue run, and
   the `${RUN_DIR%/*}` path to the prepare output is the same construction 1036 used.
   Timeouts 1800 + 9000 s = 3 h, under the 8 h cap.
9. **Critique coverage.** Notes 1–5 are implemented in code and plan (solve-count scenarios,
   staged decision, pinned extractor with the occurrence-ranking choice stated explicitly,
   procedure-comparison scope string, ordered rules and precision caveat). Note 6 is
   acknowledged in the plan. Notes 7–8 concern question 32 wording outside the researcher's
   write scope; the plan says so and defers them to the steward. No substantive point is
   unanswered.

## Minor notes (not blocking)

- **Test count.** plan.md says 32 focused tests passed; the new test file holds 12 (8 functions,
  one parametrised ×5). The rest presumably come from other files. Not a correctness issue.
- **Common random numbers.** E and W_E share the search seed and the operator seed `[seed, 4]`,
  so their first block draws (fragment index, length, start) coincide before content diverges.
  This is the 1036 F/W design and tightens the paired contrast; the analysis should remember the
  interval reflects this pairing, not independent runs.
- **Admission under load.** The queued prepare re-measures timing. If the machine is busy, the
  design drops to 12 seeds or stops as infeasible. That is the approved rule; just note that a
  12-seed result widens the interval as the plan warns.
- **W_E faster than E in smoke.** W_E averaged 3.98 s against E's 6.03 s on 32 searches each.
  That is descriptive only, but if it persists the arithmetic worker-second "savings" in
  result.json will be negative; the report handles that (`break_even` becomes null).
- **Hash of the entry module.** `pre_solve_run.py` is hashed explicitly because it runs as
  `__main__`; prepare and score compute it the same way, so the freeze check is consistent.
