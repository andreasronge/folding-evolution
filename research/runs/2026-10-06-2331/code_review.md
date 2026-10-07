---
verdict: pass
---

# Code review: 2026-10-06-2331 frozen starting-program × ongoing-decoder 2×2

Reviewed `912e91e..8f42f38` in the experiment worktree (`composition_search.py`
encode/initialization hook, `initialization_run.py`, `initialization_report.py`,
`tests/test_initialization_intervention.py`, the pinned 2229 reference, and the
task folder: proposal, critique, plan, queue, smoke, projection, verification).

## Blocking issues

None.

## What I checked

1. **Arm wiring.** `Runner.job` sets source/destination tables as the proposal
   specifies: GG and MM use original alleles with source = destination
   (`reencode=False`), MG re-encodes the M-decoded tapes under G, GM re-encodes
   the G-decoded tapes under M, MMr re-encodes M into M. GG is built once per
   cell and seed from `G4` and shared across maps in `cost_matrices`. The
   payload only carries the cell id and labels. `check_block` independently
   recomputes the generation-0 token hashes from `default_rng([seed, 1])`
   under every table and verifies every row's table hash, source hash,
   token hash, re-encode flag, cases, cap and evaluation bookkeeping, then
   asserts MG = MM and GM = GG token hashes per (map, cell, seed).
2. **Streams.** Re-encoding uses `default_rng([seed, 3])`; cases `[seed, 0]`,
   initial `[seed, 1]`, variation `[seed, 2]` and selection `seed + 1e8` are
   untouched. Nothing else consumes `[seed, 3]`. The identity path adds no
   draws, and the 630-row 2229 reproduction (evaluations, solved, curve,
   table hash) matched bit-exactly in preparation.
3. **Encoding law.** `Decoder.encode` draws `rng.integers(lo, hi)` within the
   conditional interval of the destination table's previous-token row, with
   the start row for position 0, matching `decode`'s conditional lookup.
   Minimum interval width ≥ 250 is asserted for all 21 tables in
   `encoding_checks`, so no interval is empty. Round trips (400 000 tapes, 40
   directed pairs) and the three chi-square diagnostics passed; source tapes
   are decoded from uniform alleles, as the critique asked.
4. **Analysis.** Contrasts are paired per (map, cell, seed) on log2
   evaluations with cap for unsolved. The crossed bootstrap resamples whole
   seed blocks once per replicate and reuses them across every arm, map,
   cell and contrast; maps are resampled within family (10 + 10) and families
   weighted equally; cells weighted equally. Map order from the frozen
   `trajectories.json` is BE1–BE10, PA1–PA10, so the family slices in
   `resampling` and `per_family` are correct. N/P/X labels and the row table
   match plan.md, including the resolved-negative (antagonism) flag and U for
   any failed gate, < 200 seeds or diagnostic mode.
5. **Gates that decide whether the main stage continues.**
   - *MMr/MM 99% interval must contain 0 (stops expansion past seed 100).*
     MMr's alleles are, by construction, an independent draw from the same
     uniform law as MM's, so the null is exact. I simulated the gate on 300
     structured null datasets (20 maps × 3 cells × 100 seeds, map, seed and
     shared-token components sized from the probe's log2 spread, 2 000
     replicates each): 0/300 false fails, mean 99% width 0.17 log2. The crossed
     bootstrap is conservative here, which is the safe direction for a
     validity gate. Stable.
   - *Validation checks before the grid* are deterministic and already passed
     in preparation on the same code.
   - *GG ≥ 85% per cell, D lower bound > log2 1.25, ≥ 200 complete seeds* are
     outcome (row U) gates, not run gates. 2229 had GG solves 377–398/400 and
     2–3× diagonal gains, and the probe's GG per-cell solves were 23–24/25, so
     these are far from their thresholds.
6. **Queue time.** The researcher's forecast (149 min, 222 min with 1.5×
   slack) does not model the seed-major barrier. I simulated list scheduling
   of the actual per-block job order on 10 workers, drawing durations from
   the 2229 per-map MM/GG timings and the probe's MG/GM timings (unsolved
   searches take ~25 s and almost every block has one): about 215 min wall,
   efficiency 0.58. That is inside the 270 min internal deadline and the
   300 min timeout, and 200 complete seeds would be reached in roughly
   110 min even at a 2× slowdown. The full 400-seed grid is reachable; no
   truncation.
7. **Critique.** Notes 1–5 are addressed in plan.md (crossed whole-seed
   bootstrap as primary with t as sensitivity, conditional row wording,
   antagonism flag, pre-stated chi-square threshold 0.05/3 with decoded
   source tapes, no equivalence claims from the law check, 200-seed fallback
   recomputes precision). Notes 6–8 are digest/question wording fixes outside
   the researcher's folder and plan.md says they are deferred to the steward;
   that is a reasonable answer since they do not affect this experiment.
8. **Smoke and tests.** The 17 intervention tests pass in the worktree. The
   fixed smoke produced every file in `expect_outputs`, returned row U with
   `minimum_seeds: false`, and deferred the law check as intended. Queue sum
   18 000 s is under the 8 h cap.

## Minor notes (non-blocking)

- Expect the run to take ~3.5 h, not 2.5 h: the seed-major barrier costs
  roughly 40% of worker time because each block waits for its slowest
  unsolved search. It still fits the deadline. If a later stage (slot 2, ten
  cells) reuses this runner, dispatch two seed blocks at once or
  check pairing after the fact rather than at the barrier.
- `projected_minutes_at_8_7_speedup` in projection.json should be read as a
  lower bound for the reason above.
- `make_report` filters `r["seed"] in seeds` against a list; with 400 seeds
  and 73 200 rows this is fine (benchmark 1.2 s) but a set would be cleaner.
- The t-sensitivity interval for `interaction` adds GG seed variance once,
  although the interaction cancels GG; it is labelled sensitivity-only so it
  cannot affect routing.
- The law check runs only when seed 2331099 completes; a deadline before that
  leaves `search_law` None and routes to U, which coincides with the
  < 200-seed rule, so no inconsistency.
