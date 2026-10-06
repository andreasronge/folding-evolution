---
node: questions/10-compositional-map-transfer/13-post-addition-map-learning
title: Contextual moves versus continued token learning from the six saved M maps, with an off-family check of M
---
# Proposal: does learning contextual changes on top of M beat continuing to learn token weights?

## Why this now

I am following [strategy 0811](strategy.md). It asks for the comparison that run
[0132](../2026-10-06-0132/analysis.md) could not reach. In 0132 the token-multiplier learner M
improved fresh search over G by 2.2× on training and by 2.0× / 1.7× on the two withheld
compositions. The contextual learner C never left G. The reason was its operator: three
of 552 cells per child. The question for root 10 is still open: do learned *contextual*
preferences add anything beyond retuning token weights on G's template?

This uses sub-question 13's last slot (13: 1 left; root 10: 2 left). Following the strategy,
I start from the six saved M maps. I compare adding contextual moves against continuing
M's own token-only learning, with the same extra budget. Frozen G and frozen M are the
references. In the same queue, a cheap supporting check scores the frozen M maps on the
eight retained non-PA cells.

## Feasibility (steward probes, unreviewed; [results](steward_probes/results.md))

- **Why C failed, measured.** I re-read 0132's `generations.jsonl`. For each operator I took
  the spread of true child effects that selection could act on: the variance of
  child-minus-parent means, minus the paired sampling variance. C's three-cell steps had a
  true-effect sd of 0.00–0.09 log2 in every generation band. M's token steps had 0.25–0.28,
  still 0.25 at generations 18–25. T's had 0.12–0.25. Per-candidate noise sd was 0.37–0.42
  for all three (24 runs). So M had no shortage of variation when it stopped.
- **Row-level contextual steps at the M maps are visible to selection.** I took 10 children
  per operator per M map (6 maps, 24 paired training searches each, cap 65 536; 4 464
  searches, 192 s). True-effect sd:
  - M token step (3 multipliers, N(0, 0.5)): 0.32.
  - Whole-row step (one row, all 23 log-weights), N(0, 0.5): 0.18.
  - Whole-row step, N(0, 1.0): 0.34. At σ 1.0 children were worse on average (+0.09) and
    only 3% looked better by > 0.5. At σ 0.5, 15% did.

  Each estimate rests on 60 children, so 0.18 could be anywhere from about 0.10 to 0.24.
  Even so, row steps give 2–4× C's spread, about the size of M's own steps.
- **Runtime.**
  - Training searches at the M maps: 23.3 per second with 10 workers, 0.39–0.46 s per
    search per worker for every operator.
  - 0132 test searches for M maps at the 524k cap: about 13 per second (231 s for 3 000).
  - 0001 per-run cost on the 16-cell bank under G: 1.14 s. Capped runs cost 13–24 s.
  - Sampling 10⁸ genotypes: about 68 s per map at 10 workers.
- **Starting points.** The six M maps scored 12.4–13.5 on probe seeds, against G's 13.8 on
  0132's seeds. Linear non-PA cells are near the floor under G (medians 2–4k evaluations);
  the two branch-else (BE) cells are not (8.2k and 41.7k; BE:S?M:(S+m) G 42/50).

## What would be run

The harness is unchanged from 0132: `composition_search.search` on D1331, P 256, `v2_rmin`,
lexicase on 64 cases, crossover 0.7, allele mutation 0.03, and an exact check on all 1 331
inputs. The six-training / two-holdout PA split comes from 0132's bank. The starts are 0132's
`final_maps.json` M1–M6. All seeds are new, disjoint from 0001, 0132 and these probes. No
holdout or off-family score selects maps, step sizes, checkpoints or stopping times.

**Two arms per continuation, from the same start M_k.** Both arms use 0132's outer loop:
(4 + 12), with parents re-scored on fresh shared seeds (4 per training cell) each generation,
fitness = mean log2 capped cost at 65k with unsolved = 17. At the end, the best of the 4
final parents is picked on 6 cells × 20 separate seeds.

| arm | parameters | each child |
|---|---|---|
| **M+** (continue token learning) | M's 23 log multipliers on G's rows | 3 multipliers + N(0, 0.5), exactly 0132's M operator |
| **R** (contextual moves allowed) | M's 23 multipliers + 24 × 23 row residual log-weights (start 0) | with probability ½ the M+ step; otherwise one row chosen uniformly, all 23 of its residuals + N(0, σ), with σ drawn from {0.5, 1.0} with equal probability |

Bounds and normalization are 0132's: ±log 16 per coordinate, 250/23 000 support, and the
same water-filling. The R table is G's counts × exp(multiplier per column) × exp(residual per
cell), then normalized. I use mixed σ instead of tuning it: σ 0.5 was nearly neutral, σ 1.0
had more spread but more harm, and selection can keep whichever helps. R spends half its
children on token steps, so the comparison holds total budget fixed. It does not hold the
number of token steps fixed. That is the question as the strategy put it: does allowing
contextual change help, given the same extra resources?

**Replication.** 2 continuations per start per arm: 12 matched pairs and 24 trajectories,
35 generations each. Within a pair, M+ and R share the start and every generation's seed set.
Each has its own mutation stream. Run order is 1a, 2a … 6a, 1b … 6b, M+ before R within a pair.
A deadline cut therefore leaves whole pairs with one per start first.

**Ablation (no extra learning).** R_abl is each final R map with its residuals removed. It is
the same multipliers on G, a `table_for('M', …)` map. R versus R_abl shows whether R's learned
residuals carry its performance. The multipliers co-adapted with the residuals, so removing
them can hurt more than they "help". This is an attribution check, not a clean causal split.

**Stage 0 (gate, about 8 min).**
- Smoke the pipeline.
- Score G on one fresh 120-run training set. Stop as a harness mismatch if it differs from
  0132's 13.84 by more than 0.6.
- Calibrate at M1–M6 on training only: 16 R-operator row-move children and 16 M-step children
  per start, each paired with its start on 24 searches. Estimate true-effect sd as in the
  probe.
- **Gate:** if R's row-move true-effect sd is below 0.15, skip stages 2–4. That is above C's
  ≤ 0.09 and below M's 0.25–0.32. Run stage 1 and stage 5 and report outcome row 0.
- Time representative searches and project the rest.
- If the projection (10% headroom, applied once) exceeds 7.0 h, cut in this order: sampling,
  then stage 4, then generations 35 → 28. Stop with `infeasible.md` if still over. Save this
  decision before learning; it uses timings only.

**Stage 1: frozen references and the off-family check (about 10 + 15 min).**
- Score G and M1–M6 on fresh training (6 cells × 50 seeds) and holdouts (2 cells × 200 seeds)
  at the 524k cap.
- Score G and M1–M6 on the 8 retained non-PA D1331 cells from 0001 (2 BE, 6 linear),
  50 seeds each, 524k cap.

**Stage 2: learning, then immediate test.** Each finished pair's M+, R and R_abl are scored on
the same fresh training and holdout seeds as stage 1: 300 + 400 searches per map, 36 maps in
all.

**Stage 4: off-family for learned maps (lower priority).** The "a" continuation of M+ and of
R per start, 12 maps, on the 8 non-PA cells × 50 seeds.

**Stage 5: sampling (lowest priority).** 10⁸ genotypes for M1–M6 and the 12 stage-4 maps,
counting exact solvers on all 16 retained cells. G rates are reused from 0001.

**Runtime projection.**

| stage | work | estimated time |
|---|---|---:|
| 0 | smoke, gate, calibration, timing | 8 min |
| 1 | 7 maps × 700 PA searches, plus 7 maps × 400 non-PA searches | 25 min |
| 2 | learning: 24 × (35 × 384 + 480) = 334 080 searches at 23/s | 4.0 h |
| 2 | test: 36 × 700 = 25 200 searches at about 12/s | 35 min |
| 4 | 4 800 searches | 15 min |
| 5 | 18 maps × 68 s | 20 min |
| **total** | | **≈ 5.7 h** |

Queue timeout 8 h, with an internal deadline at 7 h 40 min.

## Statistics

**Cost per map and test set.** Mean log2 evaluations to an exact solve, with unsolved =
log2(2 × 524 288) = 20. The derived 65k training cost is reported too.

**Contrasts.** A/B = 2^(mean paired log-cost difference); > 1 means A is faster. The 95%
interval comes from a two-level bootstrap with 10 000 resamples. It resamples the six starts
with all their continuations, then the shared seeds jointly across maps.

**Classification for the primary contrasts (R/M+ and R/R_abl):**
- **faster**: lower bound > 1;
- **no practical gain**: not faster, and upper bound < **1.25**;
- **unresolved**: everything else.

I use 1.25×, not 0132's 1.5×. This is an increment on top of a map that is already 2× faster
than G. A contextual learner adding less than a quarter would not justify a 24× larger
parameterization in the next map design; one adding more would.

**Power.** Between-trajectory sd was 0.13–0.30 in 0132. Take 0.3 for the R−M+ difference
and a seed term of about 0.13 per map on 200 holdout seeds. The SE is then about 0.10–0.12
log2 with 12 pairs, a half-width of ×1.15–1.18. A true null should then come out "no practical
gain", and a true 1.4× gain "faster". True differences of 1.15–1.3× may land unresolved. Six
pairs would only resolve 1.25 if the spread is well below 0.4.

## Outcome rules (first match decides)

| row | condition | meaning / next |
|---|---|---|
| 0 | Stage-0 gate fails (row-move true-effect sd < 0.15) or harness mismatch | Row-level contextual steps give no usable training signal at the M maps (or the harness changed). No contextual-learning claim. Return to strategy with the calibration numbers and the off-family result. |
| 1 | R/M+ **faster** on both holdouts | Learned contextual changes add transferable speed beyond continued token learning, within this screened family (A1 supported here). Report R/R_abl. If it is not also faster, the gain is not attributable to the residuals alone. Return to strategy; root 10's last slot could replicate this. |
| 2 | R/M+ **faster** on fresh training, and **no practical gain** on both holdouts | Contextual changes improve training but not the withheld compositions at this budget (C1 for the contextual part). Next: investigate generalization, not longer training. |
| 3 | R/M+ **no practical gain** on fresh training and on both holdouts | Allowing contextual moves adds < 1.25× over continued token learning at this budget and operator (a bound on B1, not equality). R/R_abl on training separates two readings. **faster** means context was learned but was worth no more than the token steps it displaced. Otherwise row moves found no useful context. |
| 4 | anything else | **Unresolved.** Report every interval and the between-pair spread. Give the number of pairs that would resolve R/M+ at that spread; root 10's last slot is the candidate. |

**Reported in every row, never deciding one:**
- M+/M and R/M on training and holdouts: did continuing help at all?
- The training-to-holdout shrinkage per arm. M lost about a third of its gain in 0132.
- Learning curves.
- L1 drift from M_k, with R's residual and multiplier parts separately.
- Which rows R changed, and whether the change is consistent across its 12 continuations.
- Adaptation cost (evaluations, wall time), kept separate from test cost.
- Sampled solver rates (descriptive; sparse counts are bounds).

**Off-family check (descriptive; selects and gates nothing).** M/G is reported with
intervals, with BE and linear kept separate.
- M/G on BE comparable to the PA holdout gains: M's change looks generic among IF_GT shapes.
- BE upper bound below 1.25: M's gain does not extend to BE.
- Linear cells: G sits near the population floor, so small ratios there mean little. Linear
  tasks also lack IF_GT.

Neither reading establishes family specificity. The two BE cells are not an independently
trained family, and baseline difficulty differs.

**Not answerable here in any row:** mechanism (supply and mutation still move together),
family specificity, and other optimizers. Tests on fresh seeds remain evaluation on a
screened bank.

**My expectation.** Row 3 or row 4 is most likely, perhaps 60%. Row steps are mostly
harmful at σ 1.0, and R gives up half its token steps while M is still improving. Row 1
is perhaps 25%. In the probe, about 15% of σ-0.5 row children looked better by more than
0.5 log2.

## Alternatives considered

- **Six pairs × 50 generations (≈ 4.4 h).** This is cheaper and allows longer learning. But
  with a between-pair spread of 0.4 the 1.25× line would not resolve, and the unresolved row
  would eat root 10's last slot. I traded 15 generations for twice the pairs.
- **A pure contextual arm (row moves only, no token steps).** It would show whether context is
  learnable at all, independent of step dilution. The R/R_abl ablation answers the attribution
  part for free. A third arm costs about 2 h.
- **Re-running C from G with row steps, or CMA-ES / natural-ES.** The strategy asks for the
  M-start comparison. No probe supports a new optimizer, and row steps are now measured.
- **Empirical-marginal controls for R.** G already beats its marginals. Beating marginals
  would not show newly learned context. The ablation is the targeted control.
- **Tightening M's 1.5× holdout interval with more seeds on frozen M.** The strategy says not
  to spend a cycle on this. Stage 1's 200 holdout seeds on frozen M sharpen it in passing.
- **A second family with the same primitive support.** This is the strategic alternative if
  specificity becomes the binding question. It needs its own plan addendum and screen.
