---
verdict: pass
---

Reviewed `eb0bba0..4a60cc7` (rectified_bank.py, rectified_run.py, order_library.py diagnostic hook, data/rectified_1315, tests), proposal.md, critique.md, plan.md, queue.yaml, smoke.md and the smoke-final artifacts. Ran `tests/test_rectified_probe.py` in the worktree (6 passed).

## Blocking issues

None.

## What I checked

1. **Arm wiring.** `envelopes()` gives R-tree no donors, R-rect the twelve `helper(kind,a,b)` prefixes (IF_GT with children [else=0, then=a+b, cond=a+b]; token 5 is the constant `0`), R-all the build's own uncapped `semantic` pool, R-order-all `transport()['libraries.json'][b]['semantic_all']` for builds 0–7. Workers receive only `{id, labels}`; the test mutates helper/canonical annotations and checks envelopes are unchanged. Protected cells are refused for every arm.
2. **Seeds.** `seed()` keys on (task, domain, cell, build, repeat, attempt) and not on arm, so the four arms of a unit share attempt seeds and nothing else does; `seed_audit()` enforces exactly one record per arm per seed, checks full and smoke namespaces against 1129, 1228 (saved audit, transported audit) and the stage-0 ranges, and the smoke audit passed against 318 k historical seeds.
3. **Metrics match the proposal.** Ratios are ratios of pooled capped arithmetic means with a paired whole-build bootstrap (the test reproduces the exact point and interval from a hand-built grid). Coverage is 48 cell × build pairs with ≥ 1 needed helper `included` in the R-all pool. Own-helper fraction is over solved sources. The `investment()` labels implement all four cases the critique asked for (low acquisition / coverage shortfall unresolved / supplied prior below threshold / helpers available but insufficient saving). Failures are charged the full cap and checked.
4. **Extraction unchanged.** `diagnostic_vectors` only swaps the reporting vectors; the test shows identical `semantic` and `literal` pools with default, rectifier and empty diagnostics. `freeze()` verifies every 1228 method hash except `order_library.py` and the extension, which is instead pinned by path and SHA-256 inside the worktree `.venv`.
5. **Provenance.** Bank manifest pinned by digest, admission and split re-derived on load; transport archive pinned by SHA-256 with inner preparation/library/freeze/schedule/audit hash checks; score replays libraries from the acquisition rows and compares deterministically; tampering tests fail closed.
6. **Gates that decide whether score runs.** Only prepare success and the score deadline. Prepare has no yield-dependent gate (bank already admitted, 24 protected ≥ 8, source jobs ~0.07 worker-s each). Score worst case: all 384 jobs capped at the observed 39.6 worker-s max with the smoke's 8.5 effective concurrency gives ~1790 s against a 2370 s internal deadline, and the smoke concurrency is underestimated by its 16-job tail. Replay validation is ~0.14 s per build. No risk of stopping for the wrong reason; no pilot resampling involved.
7. **Critique.** Notes 1–4 are implemented (import-path plus interpreter/Python/VM agreement before acquisition in `load_bank()`, fixed 384 + 384 grids, hashes and throughput recorded, descriptive labels). Notes 5–7 concern question/digest wording outside the researcher's write scope; plan.md says they are deferred to the steward, which is adequate for this review.
8. **Queue.** Two entries, 900 + 2400 = 3300 s ≤ the 60-minute probe cap; `--seconds` values sit 30 s inside each timeout; `$RUN_DIR/../<id>-prepare` is the layout 1228 used successfully; expected outputs match what `prepare()`/`score()` write.

## Minor notes (not blocking)

- `mechanism_lead` is set only when **no** helper of any kind entered any R-all build, whereas plan.md frames the lead as "saving ≤ 0.67 without helper coverage". With, say, 1/48 coverage and a ratio ≤ 0.67 the flag would be False. The analyst should read `coverage_pairs` and the ratio directly rather than rely on the flag.
- `prepare()` writes `preparation.json` before `main()`'s post-deadline check; if that check fires, `failure.json` is also written and `load_prepared()` refuses, so the outcome is correct, but the folder will contain both files.
- `transport()` decompresses and re-parses the 1228 archive on every call (freeze, envelopes, seed audit, summarize). Harmless at this size.
- The smoke's 1/4, 3/4, 0/4, 1/4 solves and 0/48 coverage are consistent with stage 0 and with the proposal's stated expectation; they are observations only and were not used to size or trim anything.
