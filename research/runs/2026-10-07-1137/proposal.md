---
node: questions/10-compositional-map-transfer/19-selection-calibrated-continuation
title: Token continuation at 96 searches per candidate from the saved maps, then context at the same loop if it learns
---

## Why this now

I follow [strategy 1137](strategy.md) and its [plan](../../plans/selection-calibrated-continuation.md).
In 0821 neither arm moved: T/S was 1.03× [0.90, 1.16]. So its C/T null could not tell whether
context does nothing or the loop simply does not climb. The cheapest thing that could change
this is the one the probe below points to. Each candidate-versus-parent comparison is mostly
noise at 24 searches. At 96 searches it is about half signal. If the token arm still does not
learn from these starts, the result says these token-tuned starts cannot test context with this
operator, and root 10 goes back to strategy. If it does learn, the same queue tests context in a
loop known to climb, before the 22:25 deadline. A second queue would not fit before then.

This is new sub-question [19](../../questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)
(slots 12 and 13 of root 10; this run uses one). Question 18 stays parked. This run tests its
reopen condition.

## What would be run

Code: 0821's reviewed runner (`experiments/chem_tape/rank_one_run.py`, `rank_one_learning.py`,
commit `f61aec4`, already on `research/main`). The task split, inner search, operators and
representation are unchanged: D1331, `v2_rmin_first`, P 256, length 32, 64 lexicase cases,
crossover 0.7, mutation 0.03, and an exact check on all 1 331 inputs. The token step is three
coordinates with N(0, 0.5), using 0821's bounds and normalization. Rank-one context steps work
exactly as in 0821. Only one thing changes: how much evidence scores each candidate.

**Loop (both arms).** Each generation has 2 parents and 6 children. All 8 candidates, including
the rescored parents, are scored on the same 96 new in-loop searches at the 65 536 cap. The
searches are spread evenly over the family's own cells: BE gets 4 cells × 24 seeds, PA gets
6 × 16. The two cheapest candidates are kept. There are 12 generations. At the end, each final
parent is scored on 192 new searches and the cheaper one is kept. Each trajectory costs
9 216 + 384 = **9 600 searches** (2.4× 0821's 4 040 per arm). Each candidate gets 4× the
evidence, and the number of generations is 0.6× 0821's. The trajectory is shorter, so this is
not "0821, but longer". Report the inner evaluations actually spent, as well as the search
counts.

**Starts.** The saved 1723 maps BE1–8 and PA1–8, all 16, are the same starts 0821's stage B
used. None are dropped or picked by success. BE9/BE10/PA9/PA10 are left out: they were 0821's
calibration units, and adding them would push the context stage past the deadline.

**Stage 1: token arm T (always runs).** 16 trajectories. Fresh block **F1** uses 0821's fresh
seeds (1 824 000 000–049, 50 per own cell, cap 524 288). Nothing was ever selected on them.
Score three maps per start on F1: S (the saved start), T_mid (the parent with the lower in-loop
score after generation 6) and T (the final map). Re-score S in full and require its rows to be
bit-identical to 0821's. That checks that the harness has not changed. It also makes 0821's
T24 maps directly comparable on the same seeds at no cost.

**Gate (in code, pre-stated).** On F1, compute T/S as a family-balanced paired estimate: the mean
over own cells and seeds of log2(S) − log2(T), with equal weight per family, t on 14 df, as in
0821. **Run stage 2 if and only if the T/S point estimate is ≥ 1.10×** (0.1375 log2). I set the
gate at the point estimate, not the lower bound. With a half-width of about 0.18 log2, a lower
bound above 1 would block a true 1.15× gain about half the time. The token control is then
confirmed on independent seeds (F2 below). Nothing on F1 is reused for any stage-2 contrast.

**Stage 2: context arm C (gated).** Same 16 starts and same loop. Every generation uses T's
in-loop seed blocks (the pairing is deterministic, so C can run after T). C has its own
mutation stream. Each step is a token step, or with probability ½ a rank-one context step, as
in 0821. C trajectories are admitted in the order BE1, PA1, …, BE8, PA8. Admission stops at the
first trajectory that does not fit, using 0821's reserve rule: 1.3 × the slowest completed T
trajectory, plus F2 scoring for everything admitted plus the prospective pair. The internal
deadline is min(queue start + 5.5 h, 22:00 local). Fresh block **F2** uses new shared seeds
(50 per own cell, cap 524 288). Score S, T, C and C0 (C with its residual removed) for each
start, plus G4 on all ten cells (500).

**Runtime (from 0821's measured rows).** Learn searches take 0.471 s per worker, about 20 per
second on 10 workers after overhead. Fresh searches at 524k take 0.867 s, about 11.5 per second.
- Stage 1: 153 600 learn searches (2.13 h) plus 12 000 F1 searches (0.29 h), about **2.4 h**.
- Stage 2: 153 600 learn searches (2.13 h) plus 16 500 F2 searches (0.40 h), about **2.5 h**.
- Total about **4.95 h** if the gate passes, and 2.5 h if it does not.
- Queue timeout: 5.75 h.

If the queue starts by about 15:00, it ends by about 20:00 and leaves time for analysis before
the deadline. A later start shortens stage 2 through admission. That stage is then row 3
(below), not a smaller comparison.

Seeds: new namespaces, disjoint from every earlier run. The only exception is F1, which reuses
0821's fresh block on purpose. T and C share in-loop and final-selection seeds within a start.
No canonical programs, no hand-set family directions and no holdout cells are used.

## Feasibility (measured)

| Quantity | Value | Source |
|---|---|---|
| Per-search variance of a shared-seed child − parent difference | 3.95 log2² (single candidate 2.54; seed correlation ≈ 0.22) | steward probe, 0821 `search.jsonl`, 1 920 T/C learn comparisons |
| Noise sd of that difference | 0.41 log2 at 24 searches → **0.20 at 96** | same |
| True token-step effect sd from saved maps | ≈ 0.17 (σ²_T 0.028 [0.005, 0.051]); mean step +0.03 (harmful) | 0821 stage A |
| Reliability of one comparison | 0.15 at 24 → **0.41 at 96** | the two rows above |
| True between-start sd of fresh S cost | BE ≈ 0.04 log2 (8 starts, close to noise); PA ≈ 0.25 | steward probe, 0821 F1 S rows |
| T/S pair sd | 0.33 log2 → half-width ≈ 0.18 log2 (1.13×) at 8 + 8 | 0821 |
| C/T pair sd | 0.38 log2 → half-width ≈ 0.20 log2 (1.15×) at 8 + 8 | 0821 |
| Solve fraction | 0.95 at 65k, 0.988 at 524k | 0821 |

What this does **not** establish is that the loop will climb. 0821's effort model predicted
gains that never appeared, and I do not reuse it. The PA spread shows that better token maps
exist for the weaker PA starts, at least up to the best saved PA map. The tight BE spread fits a
common plateau, and fits a noise-limited equilibrium just as well. I put the gate pass at about
45%.

## Outcome rules

Apply in order. "T/S(F1)" is the stage-1 primary estimate. "T/S(F2)" is its independent
confirmation. C/T, C/S and C/C0 are on F2. All are family-balanced, with 95% t intervals on
14 df (fewer if trajectories are missing).

| Row | Condition | Meaning / next |
|---|---|---|
| U | Hash mismatch, leakage, F1 S rows not bit-identical to 0821, missing or duplicate rows, or < 6 complete T trajectories in either family | Infrastructure result; no claim. (~5%) |
| 1 | Gate fails and T/S(F1) upper < 1.10 | **Bounded no-progress.** At 96 searches per candidate and 9 600 searches, token continuation does not improve these saved maps by ≥ 1.10×. These starts cannot supply a token positive control with this operator. Stop this procedure, keep 18 parked, return to strategy (D, joint learning from G4, stays untested). (~25%) |
| 2 | Gate fails and T/S(F1) upper ≥ 1.10 | **Unresolved.** Report the bound. Return to strategy. Do not automatically spend slot 13 on precision. (~25%) |
| 3 | Gate passes but < 6 complete C trajectories in either family | Report T/S(F1) and T/S(F2). C/T is U (runtime). Return to strategy. (~3%) |
| 4 | Gate passes and C/T lower > 1 | **Context adds to token tuning on training cells** at this loop. Resolved C/C0 > 1 supports the residual carrying it, though removal also changes the token marginals. Next, if any time remains, frozen transfer on the three withheld cells with a frequency-matched control. Otherwise hand to strategy. (~10%) |
| 5 | Gate passes, C/T lower ≤ 1 and T/S(F2) lower ≤ 1 | **Token progress not independently confirmed.** The gate passed on F1 but F2 does not resolve it, so the C/T interval is reported but says nothing about context. Return to strategy. (~7%) |
| 6 | Gate passes, T/S(F2) lower > 1 and C/T upper < 1.15 | **The informative null 0821 lacked.** In a loop where token continuation demonstrably learns, rank-one context adds < 1.15× on training cells. Close 18 for this representation and loop. D stays untested. (~12%) |
| 7 | Otherwise | Unresolved C/T with a working token control. Size any follow-up with the observed pair sd, only if it fits and would change a decision. (~13%) |

Descriptive readouts, none of which change a row:
- T_mid/S and T/T_mid on F1, to show whether progress flattened by generation 6.
- T96 versus 0821's T24 maps on F1. Same starts and seeds, but 9 600 versus 4 040 searches, so
  this compares procedures, not effort.
- In-loop slope of the mean parent score.
- Accepted child minus its retained parent, rescored on the next generation's independent block
  (counts too). This is the "selected change against its parent" check.
- Winner's curse: score at acceptance minus the next-generation rescore.
- Per-family T/S, and the gain against the start's S level (PA heterogeneity).
- C's operator survival, clipping and the residual's cosine with the hand-set BE − PA direction.
- A learning-curve figure.

## Alternatives considered

- **Run 0821's loop 3× longer (n 24, about 60 generations).** The strategy says to stop
  repeating it unchanged. Its in-loop slope was flat with 1.4 replacements per generation,
  which looks like drift, not slow climbing. If this run lands in rows 1–2 and the T_mid/T
  curve is still falling, depth becomes the next candidate.
- **n = 192 with 6 generations.** Reliability is about 0.58, but there are too few steps for a
  0.17-sd step distribution to add up to a gain I could detect.
- **All 20 starts, T only.** The T/S half-width would be about 0.155 rather than 0.18. But then
  no context answer fits before the deadline, and context is what the strategy wants made
  informative.
- **A calibration stage that picks n.** 0821's calibration could not predict accumulation. The
  plan says to fix the procedure in advance, and the gate plus the F2 confirmation do that job.
- **Joint context and token learning from G4 (explanation D).** Deferred by the strategy. A
  null here would not reject it.
