---
verdict: pass
---

# Code review: uncapped semantic library (R-all), commit 60ab766

Reviewed `git diff 1fad6e1..60ab766` (new `order_cap_run.py`, `tests/test_order_cap.py`,
the `cap` keyword in `order_library.build`, frozen bank and pilot freeze under
`data/order_cap_1228/`), proposal.md, critique.md, plan.md, queue.yaml and the
smoke artifacts. Tests in `tests/test_order_cap.py` pass in this worktree (9/9).

## Blocking issues

None.

## What was checked

- **Intervention is exactly what the proposal says.** `build(cap=None)` replaces
  `ranked[:16]` with `ranked`; eligibility (≥2 cells, 3–9 nodes), ranking and
  representatives are unchanged. `libraries_from` asserts R-all's first 16 entries
  equal R-S and that R-all has every eligible class, and that each entry occurs as a
  proper subtree of a solver in its own build's corpus. Smoke build: 16 vs 25 classes.
- **Arm wiring.** R-all is dispatched through the base `R-S` path with
  `semantic_all` substituted per build (`envelopes`, lines 154–158); R-S uses the
  capped `semantic`; R-tree/R-order use the base paths. Worker envelopes carry only
  cell id and labels. Donors are drawn uniformly from the library with the unchanged
  50% mutation-draw rule, so library size only dilutes, as the proposal states.
- **Seeds.** Task namespace `2026-10-11-1228`; the four arms share attempt seeds per
  (cell, build, repeat); source/score/smoke sets are disjoint from each other and from
  1129's published seeds and the historical artifacts (audit: 283,130 historic seeds,
  no collision). Full grid is 1,152 source + 2,304 score jobs, 384 per development cell.
- **Frozen inputs.** `data/order_cap_1228/bank.json` digests identical to the 1129
  prepare output; `pilot_freeze.json` is byte-identical to 1129's `method_freeze.json`.
  All pilot method hashes except `order_library.py` and the Rust binary are required to
  match the current code. No re-screen; protected cells are rejected by the base
  envelope check (tested).
- **Metric and inference.** Capped arithmetic mean evaluations; failures asserted at
  524,288 (all 8 failed 1129 rows carry exactly that, each attempt exactly 65,536, so
  the assertion will not fire spuriously). Primary ratio is the ratio of pooled means,
  bootstrapped over 24 whole paired builds with equal cell/repeat weights, fixed seed,
  8,192 draws, as critique note 5 asked. The test confirms the point estimate is not a
  mean of build ratios.
- **Decision rule.** `classify` applies the plan's precedence: lower > 0.67 → end
  recipe; else upper < 0.80 → useful; else unresolved. [0.70, 0.78] → end;
  [0.67, 0.80] → unresolved (tested). This resolves critique note 2.
- **Critique disposition.** Notes 1–5 are addressed in plan.md and in code. Notes 6–9
  concern wording in existing digest/question files; plan.md defers them to the
  steward because the researcher may not edit outside the task folder, and commits to
  not copying the over-strong wording into new conclusions. Acceptable.
- **Gates and stop rules.** There is no pilot gate; the main stage runs unconditionally
  after prepare. The only stop is the fixed deadline, which preserves rows and refuses
  inference on a partial grid (no complete-case bias). Timing headroom: 1129 worst
  single job was 39.6 s; even with every R-S and R-all job at that cost plus measured
  R-tree/R-order rates, scoring is ≈78 min on 10 workers against a 90-min timeout;
  the realistic estimate is 25–51 min. Prepare at the smoke rate (21 worker-s per build,
  1.8× pilot) is ≈1 min of a 20-min timeout. Queue total 110 min is within
  `max_queue_hours = 8`. Machine has 12 cores for 10 workers.

## Minor notes (not blocking)

1. `score()` draws `dynamics.png` before writing `report.json` (the 1129 driver did the
   reverse). A plotting exception on full data would lose `report.json` while
   `score.jsonl` and `libraries.json` survive, so the report could be regenerated
   offline with `summarize`. Smoke exercised the plot code on the same row shape, and
   every attempt has ≥1 curve point, so the risk is low.
2. `methods()` does not hash the new `order_cap_run.py`, so the method freeze cannot
   prove which driver produced the smoke artifacts (their recorded commit is the
   parent). The committed `order_library.py` hash does match the smoke freeze, and the
   full run records the clean commit, so provenance for the real run is fine.
3. Worker-second acquisition cost in `economics` counts literal extraction twice (once
   inside each of the two `extraction_census_seconds`); about a millisecond per build,
   descriptive only.
4. Smoke R-all cost 0.26× R-tree on 12 jobs from one build. This is one acquisition and
   not evidence; the pre-stated decision rule and fixed n should be read without
   reference to it.
