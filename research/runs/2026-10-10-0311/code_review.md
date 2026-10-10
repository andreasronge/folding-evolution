---
verdict: pass
---
Re-review after the fix commit. Reviewed `git diff 999fc9c..09c850d` (executor/alphabet/Rust `v2_x4`, frozen bank and O payloads, bank module, runner, report, tests), with the incremental fix `a81a449..09c850d` read line by line, plus proposal.md, critique.md, plan.md, queue.yaml, smoke.md and review_response.md.

## Blocking issues

None. The single blocking issue from the first review is resolved:

1. **Discovery gate removed from admission (was blocking).** `independent_input_run.py` `prepare()` now sets `admitted = score_projection <= 1770 and prepare_seconds <= 1470`; `score()` recomputes admission from the recorded `score_projected_seconds` and `prepare_seconds` only. A median first-batch yield below 4/16 is kept as a reason string in preparation.json and as `median_first_yield` / `discovery_obstacle` in source_summary.json, so the reading the proposal asked for survives while the main stage runs. Empty intermediate/final corpora and libraries flow through the unchanged `empty_fallback=True` operator path. The parametrised test `test_full_admission_reports_sparse_yield_and_stops_only_for_runtime` covers yields 0 and 3 admitted through the full 192-job development dispatch and stops only just beyond either runtime limit; the review-score smoke actually ran 48 reduced-cap searches with empty libraries. plan.md's "Code-review response" paragraph matches the code. `tests/test_independent_input.py`: 40 passed in this worktree.

## Remaining gates (checked, not blocking)

- **Preparation limit (1470 s).** `self.started` is taken in `__init__`, so bank load, O-payload hashing, validation and both source batches count. `run_jobs` uses the same `deadline_seconds - 30 = 1470` deadline, so the admission limit and the batch deadline agree. I ran the real all-executor bank validation in this worktree (492 canonicals and witnesses, depth-3 typed-state enumeration, 2000 random tapes): passed in 1.5 s, so the 10 000-tape queue setting costs a few seconds. With smoke timings (about 26 worker-s per G4 search, about 9 effective workers) the two 128-job batches project to roughly 750–800 s, leaving about 11 min of margin. A stop here can only come from the machine being genuinely slower than measured, which is the limit the plan states.
- **Scoring projection (1770 s).** `1.3 * 64 * (mean_g4 + mean_a8 + max(mean_g4, mean_a8, fullcap_g4)) / effective + 90` projects to roughly 800–900 s at smoke timings; it would need effective workers below about 4 to fire. Reasonable.
- **Freeze comparison across entries.** `method_freeze` contains source-file hashes, the Rust extension hash, worker count, schedules and bank/O SHAs; nothing RUN_DIR- or time-specific, so the score entry's `p["freeze"] != self.freeze` check passes as long as the worktree and `.venv` are not touched between the two entries. The extension `.so` (15:08) is newer than `rust/src/chem_tape.rs` (14:36) and the Python/Rust indexed-token tests pass against it, so the all-executor validation will not fail on a stale build.

## Minor notes

- `bank.validate()` now saves and restores `vm._SAFE_POP_CONSUME` in a `finally`; `test_bank_validation_preserves_safe_pop_mode` covers success and exception paths.
- `prepare_seconds` is captured once and used for both admission and the frozen record, removing the millisecond race noted earlier.
- The admission test mocks `jobs`/`report`, so it verifies dispatch of the full 192-row development schedule but not the search itself; the sparse-library search path is covered by the review-score smoke rather than by a unit test. Adequate for a probe.
- Carried over from the first review, unchanged and still fine: disjoint seed blocks (310k/320k/330k; smoke 390k/420k) matching plan.md; adaptive attempts use each build's own intermediate C4+F4 and development A8 the final refit; O maps ordinal//2 onto BE1..4/PA1..4 with original tables and libraries under `v2_x4`; shared development seeds across arms with an unpaired bootstrap; nine-token screen over `EXECUTABLE` with slots 12/13 as NOP and separators excluded, now stated in plan.md.
- Critique disposition unchanged: notes 1–4 and 6 implemented, 5 acknowledged, 7 outside the researcher's write scope and said so in plan.md.
- queue.yaml: two entries, 1500 + 1800 = 3300 s (55 min, within the 60 min probe cap), no `--smoke`, workers 10, `RAYON_NUM_THREADS=1`, `${RUN_DIR%/*}` resolves to the sibling prepare folder. `expect_outputs` for the score entry match the files `score()` writes in both the admitted and feasibility-stop branches (`result.json` is only written on a stop, `report.md` in both; the admitted branch's `result.json` is written by `report()`, which the smoke confirms).
