---
verdict: fail
---
# Code review: 2026-10-06-0811 contextual continuation

Reviewed commit range `f413e47..850c76e` (`contextual_learning.py`,
`contextual_learning_run.py`, `contextual_report.py`, vendored sources, tests),
plus proposal.md, critique.md, plan.md, queue.yaml and the feasibility /
smoke artifacts. The implementation is faithful to the approved design and
the arm wiring is correct. The single blocking issue is the stage-0
contextual gate, which decides whether the main stage runs and is a coin
flip on the pilot data.

## Blocking issues

1. **The stage-0 contextual gate (row-move true-effect sd ≥ 0.15) is
   unstable on the researcher's own pilot.** The gate skips stages 2–4
   (the whole learning study) when it fails. On the feasibility calibration
   (`feasibility/stage0.json`, 96 R children and 96 M+ children, 24 paired
   searches each) I reproduced the code's point estimates (R 0.164, M+ 0.170)
   and then recomputed the gate under resampling:

   | resampling scheme | P(R sd < 0.15) | P(M+ sd < 0.15) |
   |---|---:|---:|
   | start clusters, then children within start (the code's own bootstrap) | 0.55 | 0.51 |
   | children only | 0.48 | 0.44 |
   | threshold lowered to 0.09 (C's level) | 0.43 | 0.40 |
   | threshold lowered to 0 (estimate clamps to zero) | 0.35 | 0.35 |

   So the full queue's stage 0, which uses fresh seeds, has roughly a 50%
   chance of cancelling the main stage on noise. The M token step, the
   positive reference the proposal cites at 0.25–0.32, measures 0.17 here
   and would fail just as often. Split halves of the pilot (children 0–7 vs
   8–15) give R 0.21 vs 0.09. Per-start estimates range from 0.00 to 0.37.
   The reason is structural: the subtracted paired noise variance (R 0.089,
   M+ 0.146) is 3–5 times the signal variance (0.027), and the gate
   threshold (0.0225 in variance) sits within one standard error of the
   estimate. No threshold near the observed value is stable at this size,
   and lowering it does not help because the estimator clamps to zero in a
   third of resamples.

   The gate is also truncated below what the queue allows: stage 0 takes
   about 4 minutes while the uncut projection is 6.32 h against a 7.0 h
   cap, so about 40 minutes of calibration were available. But even that
   would not rescue a threshold sitting on the point estimate; getting the
   standard error of the variance difference down to the needed ~0.002
   would take thousands of children.

   **Required change (either is acceptable):**
   - Remove the spread gate. Keep the harness-mismatch gate (stable: 120
     searches, SE ≈ 0.18 against a 0.6 tolerance). Still run and save the
     calibration as the descriptive diagnostic the plan already specifies
     (signed effects, beneficial fraction, interval), and reduce outcome
     row 0 to harness mismatch only. This matches the critic's note 3 ("no
     additional elaborate gate is needed") and the README's rule that gates
     longer than the question are too heavy. The proposal's own probe plus
     this pilot already answer the feasibility question the gate was meant
     to ask: row moves give variation of the same order as M's token step.
   - Or keep a gate only if plan.md states one that the pilot data shows
     to be stable under resampling (I could not find such a threshold on
     the sd estimator). A relative gate, R variance > ½ M+ variance,
     also passes only 62% of resamples, so it does not qualify.

   Since the gate was part of the approved proposal, the change should be
   recorded in plan.md as a reviewer-required amendment, with the pilot
   numbers above as the reason, so the steward sees why row 0 narrowed.
   The code change is small: `gate_passed = True` unless harness mismatch,
   or drop `contextual_gate_passed` from the routing in `run()`; the
   `projection()` gate-failed branch and the gate-routing test then become
   dead paths and should be removed or kept as harness-only.

## Verified, no issue

- **Arm wiring.** Zero-residual R vectors reproduce every saved M table
  exactly (asserted in `Runner.__init__`, covered by tests, checked by me
  against the 0132 `final_maps.json`: vectors, tables and hashes equal).
  `R_abl` is exactly `R[:23]` through `table_for('M', …)`. M+ uses 0132's
  `mutate` unchanged, bounded ±log 16 around G as in 0132.
- **Seeds.** Learning and selection seeds are shared between M+ and R of a
  pair and differ across pairs; mutation streams are separate per arm
  (smoke `search.jsonl` and `generations.jsonl` confirm). Test seeds are
  identical across every map per cell. Namespaces 811M–818M are disjoint
  from 0001 (2606xxxx), 0132 (1322xxxx/1324xxxx), composition (2247xxxx)
  and the steward probe (8111xxxxx). Smoke (+10M) and calibration-only
  (+20M) offsets keep verification seeds out of the real run.
- **Vendored sources.** `contextual_0811_sources.json` paths and SHA-256
  hashes match the live 0132 and 0001 outputs; the eight off-family cells
  are exactly the retained non-PA cells of the 0001 bank with matching
  labels and canonical programs.
- **Metrics.** `contrast` computes 2^(mean cost_B − cost_A) with starts as
  clusters and seeds resampled jointly across maps and cells, as the plan
  says. Classification thresholds (lower > 1; upper < 1.25) match. The
  outcome rows match the plan's table. Completeness requires every
  expected map/cell to have exactly the expected unique seeds.
- **Scheduling.** `projection()` work counts (384 + 480 per generation
  block, 700 PA tests, 400 off-family) are right, headroom is applied once,
  and the cut order is sampling → stage 4 → 28 generations. Pairs are
  admitted only with a reservation for their tests, so a deadline leaves
  whole pairs. `run_jobs` honors the deadline and the `finally` block
  writes a partial report with no outcome.
- **Critique.** Notes 1–5 are addressed in plan.md and code (actual
  operator calibrated, signed effects saved, R/R_abl timings in the
  projection, six-cluster sensitivity, narrowed row language). Notes 6–11
  are digest edits outside the researcher's scope and correctly deferred.
- Queue loads via `queue_lib`, one entry, 28,800 s at the 8 h cap, internal
  deadline 27,600 s. 7 new tests pass.

## Minor notes

- Per-child noise variance is estimated from 4 seeds (3 df); only the
  pooled mean is meaningful. Report the calibration spread as descriptive,
  never as a per-start number.
- Stages 4 and 5 have no time reservation and can be cut by the deadline;
  this is the approved priority order and the report handles partial
  off-family contrasts, so it is fine, but `analysis.md` should state
  which were cut.
- The representative R timing table is one child plus one token step.
  With 1.3 h of slack in the projection this is adequate.
- `training65` contrasts reuse the 524k test rows re-capped at 65k; fine
  as a derived descriptive, but it is not a separate 65k run.
