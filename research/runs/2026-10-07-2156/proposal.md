---
node: questions/10-compositional-map-transfer/22-feedback-context-increment
title: Token-only T1 and T2 on the 1924 seeds, rerun of 2129 in a fresh work window
---

**Why this now.** This is the same approved comparison as [run 2129](../2026-10-07-2129/proposal.md)
([critique](../2026-10-07-2129/critique.md), [plan](../2026-10-07-2129/plan.md)). 2129 stopped
before any primary search because the autonomous deadline left 26.5 min against a gated 36.9 min
([infeasible](../2026-10-07-2129/infeasible.md), [decision](../2026-10-07-2129/decision.md)).
Nothing scientific has changed. Run 1707 found C1/T1 = 1.37×, and run 1924 found C2/C1 = 1.40×.
Without T2 we cannot tell whether feedback made context more valuable, or improved this corpus
for the token-only fit as much. Question 22's slot is unused; root 10 has 1 of 15 slots left.
[Strategy 2129](../2026-10-07-2129/strategy.md) ranked this first. No other open question is
better prepared.

**What runs.** The code is reused from commit `ec742da` on branch `research/2026-10-07-2129`
(`context_increment_{freeze,run,report}.py`, `tests/test_context_increment.py`, and the pinned
inputs under `experiments/chem_tape/data/context_increment_2129/`). Bring that commit onto this
run's branch. The search/fitting engine is unchanged from `5565d54`. The only code change is
the time budget, described below.
- Arms are T1 (`tables.T` from 1707) and T2 (`C2.tables.T` from 1924). The saved C1 and C2 rows
  are reused. C1 and C2 were already scored on the 1924 phase-11/12 seeds and training indices.
- Before any T row counts: validate the table hashes and the full saved-row roster, and replay
  64 C1/C2 rows exactly. This is unchanged and already passed once.
- Stage 1 (primary) is training: 16 BE lineages × 4 cells + 16 PA × 6 cells, 32 seeds, for
  5 120 searches per arm. The 160 T2 timing rows (seed 0) stay in the roster and count once.
- Stage 2 is holdout: 32 lineages × 3 withheld cells × 32 seeds, for 3 072 searches per arm.
  It runs as a complete stage, or not at all.
- 10 workers, RAYON_NUM_THREADS=1. Cap 524 288, population 256, length 32, 64 cases, exact
  D1331 verification. Unsolved searches count as 2 × cap.

**Time budget (the one change from 2129).** Remove the absolute 22:20:38 cutoff. Stage 1 runs
unconditionally. Stage 2 is admitted only if 1.25 × its projected time fits within the queue
timeout, less a 5-min reporting reserve. The projection uses stage 1's *observed* worker cost
and effective workers on the full roster. It does not use the 160-row block. The gate uses
timing only, never solve rates or effects. Queue timeout is 75 min. Run it in the night window
(23:00–08:00) or whenever the owner approves; it needs owner approval because the autonomous
run ended at 22:25.

**Feasibility (measured).** From the 2129 preflight: T2 costs 0.665 worker-s per training search
on BE and 0.343 on PA (160/160 solved). T1 historically costs 1.042 per training search and
0.946 per holdout search, with 98.8% and 98.6% solved.
- Training: 5 120 × 1.042 + (2 048 × 0.665 + 3 072 × 0.343) ≈ 7 750 worker-s ≈ 129 worker-min.
- Holdout: 3 072 × 0.946 + 3 072 × (0.64–0.95, unmeasured for T2) ≈ 81–97 worker-min.
- Total ≈ 210–230 worker-min. At 1924's full-roster 9.7 effective workers, that is about 22–25
  min. At the preflight's small-block 4.33, it is 48–53 min. Both fit in 75 min.
- This is under the README's 30-min guideline at the likely throughput. It is still the right
  size. The sample is fixed by the 32 saved lineages and their 32 saved C seeds. More T seeds
  without matching C seeds would not tighten the per-lineage D much if between-lineage
  variation dominates, and adding C seeds would cost twice as much for an untested gain.

**Estimator.** As in 2129's plan. Per lineage, take the mean log2 cost per cell, averaged over
the lineage's own training cells (or its 3 holdouts). Then D = (C2 − T2) − (C1 − T1), and
I = 2^(−D); I > 1 means feedback increased context's advantage. Training weights the two
families equally: SE = 0.5·√(SE_BE² + SE_PA²), with t on 15 df. Holdout uses all 32 lineage
Ds, with t on 31 df. Descriptive results, with 95% intervals: T2/T1, C2/T2 and C1/T1 on these
seeds, and per-family I. Also split seed noise within cells from between-lineage variation.
2129's precision figures (×/÷ 1.075 training, 1.10 holdout) are heuristics only (critique
note 3). The final intervals come directly from the lineage Ds.

**Outcome rules** (applied in order, separately to training, which is primary, and to holdout).
"Lower" and "upper" are the 95% bounds of I.

| row | condition | meaning |
|---|---|---|
| 0 | hash, validation or replay failure, or stage 1 incomplete | No claim. Report the measured cost. |
| 1 | lower > 1 | Feedback increased the advantage of the additionally fitted context. If T2/T1 also has lower > 1, both fits improved. Otherwise report T2/T1's interval and leave the token increment unresolved. Do not say "mostly contextual". |
| 2 | upper < 1 | The token fit gained relatively more from feedback. C2/T2 says whether the additional context still helps after feedback. |
| 3 | 1/1.10 < lower ≤ 1 ≤ upper < 1.10 | The relative increment is bounded within ±10% for these two procedures on this bank. This is not an equality claim or a shared-mechanism claim. Call a fit improved only if its own interval supports it. |
| 4 | otherwise | Unresolved, for example an interval that spans 1 and a worthwhile I > 1.10. Report the lineage SDs, the seed-versus-lineage split and conditional sizing. |

A training-only result, a skipped holdout or an unresolved holdout leaves transfer unresolved.
T learns global token multipliers over G4's fixed context. The contrast is about *additional*
fitted context, not about removing all decoder context. Every outcome returns to strategy. None
authorizes C3.

**What each outcome would change.** Row 1 means feedback sharpens something a token map
cannot carry. That would justify a C3 probe or active-token analysis as the next allocation.
Row 2 or 3 means the 1924 gain is mostly a better corpus, not more contextual. Then the
feedback line is better spent on corpus yield and diversity, or on the family-transfer bank.
Row 4 sizes a decision-worthy rerun, or parks 22 with that size as its reopen condition.

**Alternatives considered.** A smaller roster (8 lineages) would fit any window, but at
roughly ×/÷ 1.15 it cannot separate a bounded interaction from an unresolved one. A
saturation-only probe first would spend a cycle measuring throughput that this run measures
anyway. Fresh seeds for all four arms add about 15 min and nothing that the replay check doesn't
secure. C3 and a broader family bank remain deferred by strategy 2129.
