---
verdict: pass
---

# Code review: 2026-10-11-1530 frozen R-all libraries on the 24 protected order cells

Reviewed `git diff 8fccf5e..53f0e06` (new `experiments/chem_tape/order_protected_run.py` and
`tests/test_order_protected.py`, 610 lines), proposal.md, critique.md, plan.md and queue.yaml.
Independently re-ran the 11 tests (pass, 3.4 s), the `prepare` phase into a scratch RUN_DIR
(28 s, all provenance checks admitted, 36/36 development smoke jobs solved) and `score --smoke`
against that preparation (replay 6.7 s, 21 s batch, costs identical to the prepare smoke).

## Blocking issues

None.

## What was checked

1. **Arm wiring.** R-tree passes no donors; R-order passes the twelve supplied helpers taken from
   the 1228 method freeze (length asserted); R-all passes `semantic_all` of the unit's own build,
   the same path 1228 used (`dict(semantic=lib['semantic_all'])`). Workers receive only cell id and
   labels; helper labels, disjoint flags and canonical trees never reach search (test confirms a
   mutated bank yields identical envelopes). Libraries are the saved 1228 `libraries.json`, verified
   against a rebuild from `acquisition.jsonl` through `archive.load_saved`. No collection, fitting
   or ranking happens anywhere in the new code.
2. **Seeds.** Namespace is `2026-10-11-1530`; each (cell, build, repeat, attempt) seed is shared
   by exactly the three arms and nothing else (audit raises otherwise); 9,216 score + 96 smoke seeds
   checked against 302,283 historical seeds including 1129, 1228, 1427 and the raw data artifacts
   (hash-verified). Every unit has its own R-tree run (build is in the seed), as the proposal says.
3. **Method pinning.** `freeze` compares every `src/`, `rust/src/` and engine-relevant chem_tape
   module hash to the 1228 freeze. The two files allowed to differ (`tree_gp_search.py`,
   `order_library.py`) are pinned to their current hashes; I diffed both against `60ab766`: the new
   keyword arguments default to the old behaviour and the RNG draw order for the half-library donor
   mix is unchanged (same short-circuit before `variation.random()`). `tree_hand_run.py` also changed
   since 1228 but is not used here (the R-order prior comes from the saved freeze, not `hand_prior`).
4. **Roster.** Bank hash `2fc0d88c…d74a` reloaded and checked; `split.protected` has 24 cells,
   4 disjoint; smoke uses only development cells and build 0; non-smoke envelopes reject any
   development cell or build ≥ 24. Protected searches in prepare: 0 (asserted and recorded).
5. **Metric and decision rule.** Pooled capped arithmetic mean, failures charged 524,288
   (`validate_rows` rejects an unsolved row with any other cost, and a solved row outside
   [256, 524,288] or not a multiple of 256). Whole-build percentile bootstrap, 8,192 draws, seed
   202610111530, pairs kept. `classify` implements the plan's precedence: lower > 0.67 ends first;
   useful needs upper < 0.80 and R-tree solves − R-all solves ≤ units/96 (12 at 1,152, 6 at 576);
   otherwise unresolved. Strict inequalities. Parametrised tests cover [0.70, 0.78] → end,
   13 extra failures → unresolved, and the fallback allowance.
6. **Timeout fallback (critique note 3).** Rows are written, flushed and fsynced one by one;
   repeat 1 is not submitted until every repeat-0 row has passed exact-grid/seed/cap/solver
   validation and a completion marker is written. `balanced_rows` accepts only the full 3,456-row
   grid or the complete 1,728-row first block, rejects duplicates, unknown keys, altered seeds or
   caps, and raises if a repeat-1 row exists without a complete repeat 0. Partial repeat-1 rows are
   counted as `ignored_partial_jobs`, never analysed. Internal deadline is `--seconds − 30`
   measured from process start, so `report.json` is written before the queue's SIGTERM;
   `dynamics.png` comes after the report and is not in `expect_outputs`.
7. **Queue.** Timeouts 1,500 + 5,400 = 6,900 s (1.9 h) under `max_queue_hours = 8` and the plan's
   115 min. `--seconds` values match the module's hard limits. `run_queue.py` computes the date
   directory once per queue start, so `$RUN_DIR/../2026-10-11-1530-prepare` resolves correctly.
   Commands run from the worktree, which has its own `.venv`; the `--saved` path is absolute and
   exists. Measured development rates (2.6 s/job R-tree and R-all, 0.27 R-order on 10 workers)
   project roughly 11–15 min for 3,456 jobs; the 90-min allowance admits about a 3.5× cost
   increase on protected cells for the full two repeats, and the balanced repeat-0 fallback covers
   worse. No gate depends on efficacy: prepare fails only on provenance, method drift or a smoke
   that does not finish within the deadline, so the main stage cannot be stopped for the wrong
   reason and there is no pilot whose resampling could change whether it runs.
8. **Critique.** Notes 1–5 are reflected in plan.md and in the code (feasibility anchor,
   precedence and exact-count reliability rule, balanced fallback, scope, unresolved
   interpretation). Notes 6–9 concern earlier question/log wording; plan.md defers them to the
   steward because the researcher may write only its task folder, and instructs that the
   overstated claims not be reproduced. That is an adequate answer.

## Minor notes (not blocking)

- The scratch development smoke (1 build × 6 cells × 2 repeats, new seeds) gave R-all/R-tree
  = 0.96 on 12 units (52.2 k vs 49.9 k evaluations). It is a single build with new seeds and is
  not evidence about anything, but the analyst should not read `smoke_report.json` as a
  replication of 1228's 0.40.
- `smaller_saving_supported` is `upper < 1`, whereas plan.md's "acknowledge a smaller saving
  separately" in the end-expansion branch refers to upper < 0.80. The analyst should read the
  interval directly rather than this flag.
- `main()` refuses a RUN_DIR that already holds artifacts. A retry of a failed entry into the
  same directory would therefore fail immediately; a retry needs a fresh RUN_DIR.
- Coverage of needed helpers on the protected roster (0/1/2 present: 84/278/214 of 576
  build×cell pairs) closely matches the development roster's distribution (18/73/53 of 144), so the
  symmetric-coverage expectation in the proposal holds; this is descriptive and was computed before
  any protected search.
- The `rust_extension` binary hash is not pinned (1228 excluded it too); `rust/src` is unchanged
  since 1228 and the worktree builds the extension from source, so this is fine.
