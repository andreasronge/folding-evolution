---
verdict: pass
---

Reviewed `2b4b8d0..7244fa1` (runner `--protected` mode, new `independent_input_protected_report.py`, tests), proposal.md, plan.md, queue.yaml and critique.md. Tests: 49 passed in the two experiment test files, 5 passed in `tests/test_queue_runner.py`; `run_queue.py --validate` accepts the queue (2 entries, 7200 s).

## Blocking issues

None.

## What was verified

1. **Arm wiring and roster.** `schedules(bank, smoke=False, protected=True)` yields 768 source searches (24 builds × 4 cells × 4 attempts × 2 phases) and 896 scoring searches (384 G4 + 384 A8 + 128 O, phase `protected`). A8 builds 0..23, O builds 0..7, build = ordinal // 2 for every arm. G4, A8 and O share one seed per (cell, ordinal), as the proposal specifies. No protected cell appears in any source row; the smoke path still targets development cells only.
2. **Seeds.** Sources 500000–523033 and 600000–623033, scoring 700000–707047. Zero overlap with 0311's 310000–333015 or the smoke blocks. Seed overlap and duplicate-key checks run before any search.
3. **Unseen-pairing subgroup.** Three protected cells use pairing {02|13}, which no source cell has, matching the proposal; the report derives this from the frozen bank rather than a hard-coded list.
4. **Primary statistic.** Equal-weight log-cost mean over fixed cells, failures at `penalty * cap`, decision at margin 1.5 with the critique-corrected label ("useful protected-cell replication on x4-double-gate-v1, relative to G4 at this cap"). Bootstrap resamples A8 builds (24, with replacement), then two seeds within build and cell, with one cell-stratified G4 draw shared across contrasts; O is resampled within BE/PA strata, and the frozen O artifact order (BE1–4 then PA1–4) matches the stratum indices the code assumes. 1 × cap sensitivity, penalty-sensitivity flag, mostly-capped and unresolved readings, descriptive Wilson intervals and once-per-build repayment are all implemented as plan.md states.
5. **Admission gates.** Preparation admits on runtime only: prepare ≤ 2970 s and projected scoring (1.3 × measured per-arm worker time, O priced at a full-cap G4 proxy, + 90 s) ≤ 4170 s. The median-first-yield < 4 condition is recorded as a reason but does not affect `admitted`, so sparse acquisition cannot stop the main stage (plan.md and critique note 1). Scoring recomputes the admission from the frozen record and refuses to run on a mismatch, so the gate cannot be edited after the fact.
6. **Provenance.** Scoring re-verifies method/backend hashes, schedule hashes, bank and O SHA-256, source rows and build digests before the first protected search; `protected_performance_scored` flips to true only after the protected batch completes. The scoring command derives the preparation path from `${RUN_DIR%/*}`; `run_queue.py` sets `RUN_DIR` via `resolve()` (no trailing slash), fixes the date folder once per launch, and runs commands with `shell=True`, so the path is correct even if the queue crosses midnight. 0311 used the same pattern successfully.
7. **Critique disposition.** Notes 1–5 are addressed in plan.md and in code (label, fallback retention, runtime-only admission, descriptive O and Wilson scoping, penalty/subgroup readings). Notes 6–7 concern question metadata outside the researcher's write scope and are explicitly flagged for the steward. Note 8 needs nothing.

## Minor notes

- **Gate headroom.** With the smoke's measured per-search times the scoring projection exceeds 4170 s only if effective workers fall below about 6.8 (pilot 9.2–9.5, smoke 8.4 on a short tail-limited batch). A false feasibility stop is therefore unlikely, but if it fires the 24 builds cannot be rescored without a code change, because the admission record is hash-frozen. Acceptable for a runtime guard; worth knowing when reading a stop.
- **Report after search in the same timeout.** The bootstrap (five `summarize` calls × 8192 draws) and plot run after the 896 searches inside the 4200 s entry; the projection reserves 90 s for this. Expected raw scoring time is about 2550 s, so this only matters if the search ends near the deadline, in which case `search.jsonl` would be complete but `result.json` missing. The analysis should confirm 896 rows in `search.jsonl` regardless.
- **Conditional outputs.** `expect_outputs` for the scoring entry deliberately omits `search.jsonl`, `timing.json` and `diagnostics.png` so a feasibility stop still satisfies the runner. Analysis must check for them explicitly.
- **Test count.** plan.md cites 55 tests; the two experiment test files contain 49. The difference is presumably other engine tests the researcher ran; no concern.
- The discovery-obstacle reason, if present, is printed in a feasibility-stop report alongside the runtime reason; readers should not take it as the cause of the stop.
