---
node: questions/10-compositional-map-transfer/22-feedback-context-increment
title: Token-only T1 and T2 on the 1924 seeds to test whether feedback increased context's advantage
---

**Why this now.** This follows [strategy 2129](strategy.md) and its
[concept plan](../../plans/feedback-context-increment.md). Run 1707 found C1/T1 = 1.37×. Run
1924 found C2/C1 = 1.40×. Nobody has evaluated T2, the token-only fit to the same feedback
corpus, so "feedback helped" could mean that context became more useful or that the corpus
became better for any fit. The four tables already exist for all 32 lineages. No collection or
fitting is needed. New sub-question
[22](../../questions/10-compositional-map-transfer/22-feedback-context-increment/question.md)
has 1 slot. Root 10 was raised from 14 to 15 by the strategist.

**Change from the concept plan, to save about 15 minutes.** The plan asks for all four arms on
fresh shared seeds. However, C1 and C2 were already evaluated on 32 shared seeds per cell in 1924
(phase 11 training, phase 12 holdout, with identical `training_indices` across arms), and the
engine replays deterministically (1924 replayed all 40 GG rows from 1707 bit-identically). So
this run evaluates **only T1 and T2, on exactly those 1924 seeds and training indices**, and
reuses the saved C1/C2 rows. The result is a full four-arm crossing on shared seeds. No table was
chosen using these seeds. The interaction I has never been computed on them, though C2/C1 has
been reported on them. Before any T row counts, replay one C1 and one C2 row per lineage and
family (64 rows, about 1 min). Every scientific field must be identical, or row 0 applies.

**What runs.** The code is from commit `5565d54` (`solver_corpus_run.py` /
`solver_feedback_run.py`), with the bank, split, exact verifier, cap 524 288, population 256,
length 32 and 64 training cases all unchanged.
- T1 = `tables.T` from 1707 `corpora.json`. T2 = `C2.tables.T` from 1924 `corpora.json`. Before
  any search, validate both with `validate_table` and check their SHA256 against the saved hashes.
- Stage 1 (primary) is training. For T1 and T2, 32 lineages × 5 own training cells × 32 seeds =
  5 120 searches per arm.
- Stage 2 is holdout. For T1 and T2, 32 lineages × 3 withheld cells × 32 seeds = 3 072
  searches per arm. It is admitted in code only if work time remains after stage 1 (1924-style
  timing gate, full roster or none).
- Use 10 workers with RAYON_NUM_THREADS=1. Log all seeds, hashes, evaluations, solved flags and
  timings under RUN_DIR.

**Feasibility (measured from saved rows, read-only).** Worker-seconds per search:

| | training | holdout |
|---|---|---|
| T1 (1707) | 1.042 | 0.946 |
| C1 | 0.71–0.78 | 0.76 |
| C2 | 0.453 | 0.643 |

Solve rates were ≥ 98.8% for every arm. In 1924, phase B ran 99 worker-min in 10.2 min of wall
time, about 9.7 effective workers.
- Stage 1 needs about 89 worker-min for T1, and 60–89 for T2 (T2 is unmeasured; the bounds
  assume T2 is as slow as T1 or gains like C2). That gives 15.5–18.5 min of wall time.
- Stage 2 needs about 48 + 35–48 worker-min, or 8.5–10 min.
- The total, with replay, validation and report, is about **26–30 min**. Use a queue timeout of
  45 min.

This is a little above the strategy's 20–25 minutes. I keep all 32 seeds so that every saved
C1/C2 row is used, rather than shrinking the contrast to one that may not resolve. The holdout
gate lets the run fall back to training only.

Precision is estimated from the published intervals, treating the two rounds' noise as
independent (conservative; shared seeds should help):
- Training: 1707 C/T was ±0.083 log2 and 1924 C2/C was ±0.060. That gives an interaction
  half-width of about ±0.10 log2, or **×/÷ 1.075**.
- Holdout: ±0.092 and ±0.099 give about ±0.135, or **×/÷ 1.10**.

For scale, the two extremes are I = 1.40 (all of the feedback gain is contextual, T2 = T1) and
I = 1 (both fits gain equally). The interval can separate these comfortably.

**Deadline note.** It is 21:55. The autonomous deadline is 22:25. The critic, researcher and
reviewer will probably take longer than the remaining 30 min, so this queue will likely run after
the deadline, or the owner will need to approve it. I would rather propose the decision-sized
version than a probe that cannot resolve I.

**Estimator.** This is the same as 1707/1924. Per lineage and arm, take the mean log2
evaluations per cell (unsolved = 2 × cap), then average over cells. The per-lineage interaction
is D = (C2 − T2) − (C1 − T1) in log2 cost, and I = 2^(−D), where I > 1 means feedback increased
context's advantage. Training uses equal family weights, SE = 0.5·√(SE_BE² + SE_PA²), and t on
15 df. Holdout averages the 3 cells per lineage, with t on 31 df. Also report, with 95%
intervals and as descriptive results: T2/T1, C2/T2, C1/T1 (on these seeds), and per-family I.

**Outcome rules.** The training interaction I is primary. Apply the rules in order. Here
"lower" and "upper" are the 95% bounds of I, and the worthwhile effect is 1.10×.

| row | condition | meaning |
|---|---|---|
| 0 | validation, hash or replay failure, or stage 1 incomplete | No claim. Report measured cost. |
| 1 | lower > 1 | Feedback increased the contextual fit's advantage over the token fit. If T2/T1 also has lower > 1, both fits improved but context improved more. If not, the increment is resolved as mostly contextual. |
| 2 | upper < 1 | The token fit gained relatively more from feedback. C2/T2 says whether context still helps in round 2. |
| 3 | 1/1.10 < lower ≤ 1 ≤ upper < 1.10 | The interaction is bounded within ±10%. Feedback's increment is shared by both fits at this scope (check that T2/T1 > 1). There is no demonstrated increase in context's value, and no equality claim. |
| 4 | otherwise | Unresolved. Report the observed SD and the number of independent lineages needed. |

Holdout gets the same four rules applied to its own I. A training row 1 with an unresolved or
null holdout I means the increase is not shown to transfer. If stage 2 is not admitted, transfer
is unresolved. All outcomes return to strategy. This run does not authorize C3.

**Alternatives considered.**
- *Fresh seeds for all four arms* (the plan as written). This costs about 15 more minutes for C1
  and C2 and gives no information that the replay check doesn't already secure.
- *T2 versus C2 only.* This shows whether context still helps in round 2, but not whether
  feedback changed its value, which the strategy explicitly rejects.
- *Collect under C2 and fit C3, or a broader family bank.* The strategy defers both, and both
  need collection or screening that does not fit.
- *A smaller probe (8 lineages).* That gives roughly ×/÷ 1.15 on training, which cannot separate
  a bounded interaction from an unresolved one. I prefer the full roster with a holdout gate.
