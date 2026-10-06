---
verdict: pass
---

# Code review: 2026-10-06-0132 PA decoder refinement

Reviewed `git diff ddf07df..02cf76f` (new `map_learning.py`, `map_learning_run.py`,
`map_learning_report.py`, `tests/test_map_learning.py`, two data files; no change to the
search harness or frozen controls), plus proposal.md, critique.md, plan.md, queue.yaml and
the researcher's smoke output under
`experiments/output/2026-10-06/2026-10-06-0132-researcher-smoke-final/`.

## Blocking issues

None.

## What was checked

**Arm wiring.** C/M/T start tables reproduce G, G and G-marg exactly (test passes; smoke
generation records show the four initial parents hashing to one table and twelve distinct
children). M multiplies G's rows by one exp-vector per token before normalisation; T is a
tied table; C is the full 24×23 log-weight table. Mutation changes exactly three
coordinates, clips to ±log 16 of the start, and normalisation enforces the 250-count floor
(water filling, stable largest remainder). Selection is on training cells only; `evaluate`
rows go to `self.tests` and nothing reads them until `make_report`. The schedule gate and
the per-trajectory reservation use timings and the G repeatability pair only.

**Seeds.** Learning seeds `132100000 + k·10000 + gen·100 + i` are shared by C/M/T for the
same k and disjoint across k and generations; selection, test, marginal, sampling and
mutation streams use separate namespaces; calibration uses `132001000+`, repeatability
`132005000/132005100+`, timing `132006000+`. All are disjoint from 0001 (`2606xxxxx`),
2247 (`2247xxxx`) and the steward probes (`9132xxxx`, `9133xxxx`). Smoke `search.jsonl`
confirms the per-phase ranges (with the +1e6 smoke offset).

**Metric and contrasts.** `log_cost` censors at the cap (17 at 65k, 20 at 524k). The
derived 65k training contrast is exact because the search is deterministic per seed and
has no cap-dependent behaviour before the cap. `contrast` returns `2^(mean cost_B − mean
cost_A)` (ratio > 1 means A faster), resamples matched trajectory blocks once per replicate
for both learned arms (so C and its C-marg, and C vs M, share draws), uses a frozen control
once with no block dimension, and resamples seeds jointly across cells and contrasts.
Classification and the five outcome rows match plan.md, with "unresolved training" routed
to row 5 and "no practical gain" to row 1 as the critic asked.

**Bank.** `post_addition_0132_bank.json` records the 0001 `bank.json` source and its
SHA-256; I verified the hash against the file in the main checkout. `load_bank` re-checks
label hashes, canonical outputs on all 1 331 inputs, and that the split equals
`split_shape` of the eight cells (holdouts `(S?M:S)+M`, `(S?M:S)+m`, as in 0001's
analysis).

**Stage-0 gate stability.** Resampling the smoke's per-run timings (96 runs per arm for
learning, 16–32 per arm for the 524k benchmarks) 2 000 times and recomputing
`schedule_projection` selected the full design (C6/M6/T6, 25 generations, sampling) in
1 999 of 2 000 resamples; the other fell to the next option (no sampling). The projected
full-design total was 351–403 min (95% range) against the 420 min gate. A uniform rate
inflation of 5% over the smoke drops sampling; 15% cuts T to four trajectories; the full
stage 0 (384 jobs per generation instead of 96) should measure lower per-run rates than the
smoke because the idle-tail term in `train_seconds_per_run` shrinks. The grid's largest
option is the full approved design, so the gate is not truncated. The repeatability gate
(two 120-run G sets differing by > 0.6 log2) has a false-stop probability near 0.3% at the
probes' per-run sd of 1.56 (difference SE ≈ 0.20).

**Critique coverage.** Notes 1–5 are implemented (per-arm projection with 26 full stage-2
maps plus U/F, representative 524k PA timings including G-marg, sampling dropped first,
three-coordinate operator timed in stage 0 with table-change rate and paired-score sd
recorded, 65k and 524k training contrasts, joint bootstrap, reservation before each
trajectory, explicit incomplete-study marker with missing IDs). Notes 6–9 concern belief
files outside the researcher's write scope; plan.md says so and leaves them to the steward.

**Queue.** One entry, timeout 28 800 s (= `max_queue_hours`), internal deadline 27 600 s
with a 180 s reporting reserve; `expect_outputs` are all written on the complete,
incomplete and infeasible paths. Commands run from the worktree, whose `.venv` exists.
Tests: 9 passed.

## Minor notes (not blocking)

1. **Headroom stacking.** The 15% factor inside the projection and the 7 h gate on a
   7.67 h deadline leave roughly 65–90 min of real queue time unusable by the gate. At the
   smoke rates the full design still clears it, but a stage-0 timing 15% slower than the
   smoke would cut T to four trajectories although the raw work would fit in the deadline.
   The fallback order is the approved one, so this only costs T power if it triggers;
   stage 0 records all four projections, so the analysis can say whether it did.
2. **Repeatability gate semantics.** The gate compares two fresh G sets with each other,
   not with the probes' 13.75/13.94. It cannot catch a systematic shift of both sets. This
   is what the proposal specified; the analysis should still report the stage-0 G cost
   next to the probe values.
3. **Whole-schedule reservation.** The loop refuses to start a trajectory unless the
   entire remaining schedule fits (×1.15), which is stricter than "finish this trajectory
   and its evaluation". A late slowdown would therefore stop before round 5 rather than
   complete it. Either way the study is incomplete and gets no outcome, so this is a
   data-loss risk, not a bias.
4. **Generation 1 scores four identical copies of the start** (72 duplicate searches per
   trajectory, under 1% of the budget). Harmless.
5. **Fresh RUN_DIR required.** `Runner` refuses a directory that already holds
   `search.jsonl`. A driver retry into the same run directory would fail immediately
   rather than append; that is the intended behaviour, but worth knowing if the entry is
   re-queued.
6. **Marginal agreement check** is a `RuntimeError` outside the `TimeoutError` handler:
   a failure would still write result.json/summary.md (incomplete) via `finally` but exit
   non-zero. At a tolerance of about ten standard errors this should never trigger.
