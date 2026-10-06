---
verdict: pass
---
# Code review: 2026-10-06-1425 saved-map shape shift

Reviewed `git diff dea27ae..b397f72` (three new modules under `experiments/chem_tape/saved_shape_*.py`, `tests/test_saved_shape.py`, plan, queue, validation), the proposal, the critique, and the smoke output under the worktree. I re-ran the new tests (3 passed) and recomputed the gate and the proposal's precision inputs from the 0811 raw `search.jsonl`.

## Blocking issues

None.

## What was checked

1. **Arm wiring matches the proposal.** 55 maps: G from `frozen_controls()` and checked against 0811's `config.json` hash; M1–M6 from 0132 `final_maps.json`; M+, R, R_abl (1a–6b) from 0811 `final_maps.json`; 12 R_fm fitted deterministically. Every loaded table is hash-checked and reconstructed from its vector with the production `table()`; R_abl's 23 multipliers are verified equal to R's. Source files are SHA-256 pinned. A hash failure aborts before any search and writes `gate.json`.
2. **R_fm is what the proposal says.** G row counts × per-token `exp(vector)` (same parametrisation as the M learner, `table_for("M")`), bound ±ln 16, exact pooled uniform-allele emitted frequencies over 32 positions (START row 23, matching `Decoder`), production `normalize()` at the end, evaluator-side TV < 0.005 recheck on every saved row. Smoke: 12/12 fits accepted, TV 3e-5 to 7e-5, no multiplier at the bound.
3. **Harness identical to 0811.** Same `search()` (P 256, L 32, crossover 0.7, mutation 0.03, lexicase, 64 cases, cap 524288), same `inputs_for('D1331')`, same 8 frozen off-family cells from the pinned sources file, label hashes and canonical programs re-verified at load. Cost is `log_cost` with unsolved = log2(2·cap). Seeds 1419000000–1419000199 are shared across maps and cells as in 0811; they do not overlap any 0811 seed range (811M–818M) or the smoke range. Smoke: 1760/1760 unique (map, cell, seed) keys, all at cap 524288 / P 256.
4. **Gate is stable.** Prior G off-family 8-cell mean recomputed independently = 12.5023 log2 (matches `gate.json`). Resampling the 50 prior seeds with replacement 5000 times gives SD 0.071 log2 and a maximum deviation of 0.29, well inside the 0.6 threshold; the 200-seed replication mean will be tighter still. Smoke difference +0.013. There is no power or size-grid gate, so nothing is truncated.
5. **Outcome rules and intervals.** `primary()` and `dependency()` implement rows 0–4 and D-a/D-b/D-c first-match exactly as approved (D-a precedence, linear-loss flag, residual-branch-help flag). Intervals require exactly six starts (t, df 5); pooled averages a/b within start; a missing start or fit yields `unresolved`, never fewer df. Duplicate rows and hash mismatches make a map incomplete. Smoke verdicts are forced to row 0 / D-c. Downstream action text matches the proposal's "what each outcome changes".
6. **Precision inputs verified.** Recomputed per-start "a" log2 R/M+ on BE = 0.52, 0.56, 0.60, −0.10, 0.47, 0.42 (sd 0.26) and shifts 0.65, 1.23, 1.24, 1.77, 0.81, 0.43 (sd 0.49), matching the proposal. IF_GT is token 17 (`alphabet.py`, `chem_tape.rs`).
7. **Time budget.** 88 000 searches at the smoke's 0.24 s or 0811's 0.36 s per search is 35–53 min on 10 workers; internal search deadline 8640 s, queue timeout 9000 s, leaving reporting headroom. Order (G, b pairs, a pairs, M refs) makes a deadline stop leave complete b starts. Partial data are saved per row.
8. **Critique.** The critic approved with notes only and requested no changes; plan.md records this and keeps every retained check.

## Minor notes (non-blocking)

- A "complete b start" in `report()` requires M+, R and R_abl but not R_fm, whereas the proposal's "b pair" also lists R_fm. Because each pair runs as one batch and all 12 fits were accepted, this cannot bite in practice; a dropped fit correctly leaves only the dependency layer unresolved, as the proposal specifies.
- SIGTERM is converted to `TimeoutError` so a runner timeout still produces a partial report; if the signal landed during final reporting the outputs could be truncated. The 6-minute margin between the internal deadline and the queue timeout makes this unlikely.
- `plots()` loops over every row's curve (up to 88 000 rows); this is seconds, not minutes, and runs after the search deadline.
- Family labelling (`R_fm`, `R_abl`, `M+`, `R`, else name) is prefix-ordered correctly; M1–M6 keep their own names.
