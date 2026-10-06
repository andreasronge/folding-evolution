---
node: questions/10-compositional-map-transfer/13-post-addition-map-learning
title: Outer-loop decoder learning on six post-addition tasks, tested on two withheld compositions
---
# Proposal: learn a decoder on the post-addition family, test on the withheld pair

## Why this now

I am following [strategy 0132](strategy.md) and its
[plan](../../plans/post-addition-map-adaptation.md) as written. Root 10 has 3 of 5 slots left. No
decoder has been evolved in root 10 yet, and that is the part of the core question still
missing. Run 0001 left one usable split: eight post-addition (PA) cells on D1331 survived the
alias screen. Six are for training and two are holdouts, `(S?M:S)+M` and `(S?M:S)+m`. The
holdouts use the then/else pair M/S, which never occurs in training. The frozen G leaves room on
them: medians 13.7k and 21.2k evaluations, against U's 85.8k and 150k. I opened sub-question
[13](../../questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md) for
this. Its budget is 2: this run, plus one replication or resolution slot if the strategist
wants it.

## Steward probes (unreviewed; `a65ded0`, 10 workers, [results](steward_probes/results.md))

These are the measured numbers the design rests on. Setup: six training cells, cap 65 536,
20 fresh seeds per cell. Score: log2 of evaluations to an exact solve, with unsolved runs
scored 17.

- **G is a strong, repeatable start.** On two independent seed sets G scored 13.75 and 13.94
  (SE 0.14 each) and solved 93% of runs by 65k; U scored 16.57. Spread per run: sd 1.56 log2.
  So a candidate scored on 24 runs has SE ≈ 0.32.
- **The landscape around G is noisy, and most moves hurt.** I added N(0, 0.5) to all 552
  log-weights of G, four times. That cost 0.4–1.1 log2. Perturbing a single row by N(0, 0.7)
  moved the score by −0.26 to +0.54 (paired SE ≈ 0.17). The IF_GT row was the most sensitive
  (+0.54, worse). The SUM, REDUCE_MIN and CONST_1 rows gave −0.18 to −0.26 (better, but not
  resolved). Paired correlation between maps on the same seed was only 0.16–0.49, so common
  seeds cut the noise only modestly.
- **A hand-set family grammar does not beat G on training.** The PA rows from run 0001's
  diagnostic (IF_GT→INPUT/ADD, ADD→DUP) scored 14.10 against G's 13.75.
- **Cost.** At the 65k cap, one inner run took 0.65 s for G, 0.75–1.2 s for perturbed G and
  1.75 s for U, per worker with 10 workers busy. Throughput was 9.4–12.5 runs/s. Run 0001
  measured runs at the 524k cap at 1.1 s (G) to 4.3 s (U), and sampling 10⁸ genotypes at about
  680 CPU-s. G samples 20 and 27 exact holdout solvers per 10⁸ genotypes.

What follows from this: a training signal exists, but single steps are about the size of the
noise. Learning has to come from selection accumulating over many generations. The probes give
no evidence that improving directions near G are common, so a "no learning" result is a live
outcome, and the design must be able to report it cleanly.

## What would be run

The harness stays as it is: `composition_search.search` on D1331 (`v2_rmin`, P 256, 32
alleles, R 23 000, lexicase on 64 cases, crossover v2 0.7, allele mutation 0.03, exact check
on all 1 331 inputs). Bank, labels and split come from run 0001's `bank.json`. The frozen
U/F/G/G-marg tables come from `assembly_maps.frozen_controls()`. All seeds are new and disjoint
from run 0001 and from the probes. Canonical programs are used only as evaluator checks. No
holdout score may select maps, step sizes, checkpoints or stopping times.

**Learners.** All three start from a fixed table. All share one outer algorithm and one
training budget.

| learner | parameters (log-weights) | start | what it isolates |
|---|---|---|---|
| **C** contextual | all 24 × 23 table entries | G | learned context-dependent preferences |
| **M** G × token multipliers (restricted control) | 23 global multipliers applied to every row of G | G (all 1) | retuning token weights on G's fixed contextual template; not context-free |
| **T** token-only | 23 weights of a tied (context-free) table | frozen G-marg | frequency-only adaptation |

**Outer algorithm.** This is fixed for all learners and frozen before any run.
- (μ + λ) with μ = 4 and λ = 12. Each generation draws one fresh set of inner seeds: 4 per
  training cell, so 24 runs, shared by every map that generation.
- Parents are re-scored each generation on the new seeds. Old scores are never carried over,
  so a lucky elite cannot persist. The 4 best of the 16 by mean score become the next parents.
- Each child changes 3 log-weights of one parent, chosen uniformly from that learner's vector,
  by N(0, 0.5) each. C draws from 552 parameters, M and T from 23. So C searches a larger space
  with the same budget; see "Risks" below.
- Fitness is mean log2 capped evaluations at cap 65 536, with unsolved runs scored 17.
- Constraints: every entry stays ≥ 250/23 000 (the 2247 support rule), and every log-weight
  stays within ±log 16 of its start.
- 25 generations. At the end, the 4 parents are scored on a separate selection set (6 cells ×
  20 seeds, 65k cap). The best one becomes the trajectory's map.
- Saved per generation: parents, children and scores, plus each map's L1 distance from its
  start, cumulative inner evaluations and wall time.

**Replication.** 6 independent trajectories per learner, 18 in all. Each has its own mutation
stream. Trajectory k of C, M and T shares its generation seed sets. Trajectories are the unit
of evidence about learning. More inner seeds under one map do not replicate learning.

**Evaluation (stage 2).** Every final map is scored on the same fresh test seeds, cap 524 288:
- Fresh training: 6 cells × 50 seeds. This separates "did not learn" from "did not transfer".
- Holdouts: 2 cells × 100 seeds.
- Learned marginals: for each C map, its token marginals are measured under the genotype prior
  (`token_counts`, 312 500 genotypes) and turned into a tied table, called C-marg. The table is
  checked with the 0001 marginal-agreement rule and evaluated like the others. That gives 6
  C-marg maps.
- References on the same seeds: G and G-marg on both sets; U and F on holdouts only.
- Sampling (stage 3, lowest priority): 10⁸ genotypes for each C and M map, counting exact
  solvers on all 8 PA cells. G and G-marg rates are reused from run 0001, since the tables are
  identical.

**Stage 0 gate (same queue, about 10 min).** Smoke the full pipeline. Then time the first two
generations of trajectory 1 for C, M and T, and score G on two fresh 120-run training sets as a
repeatability check.
- If the two G sets differ by more than 0.6 log2 (about 3 SE): stop as a harness mismatch.
- If projected stages 1–3 exceed 7.0 h: cut T to 4 trajectories, then cut generations to 20
  for all learners. If still over 7.0 h, stop and write `infeasible.md` with the timings.

**Ordering under the deadline.** Trajectories run round-robin: C1, M1, T1, C2, and so on. Each
finished map is evaluated in stage 2 right away (holdout scores never feed back), so a deadline
cut leaves balanced arms. Sampling runs last and is dropped first.

**Runtime projection.**
- One trajectory is 25 × 16 × 24 + 480 = 10 080 inner runs at the 65k cap. At a conservative
  10 runs/s that is about 17 min, so 18 trajectories take about 5.0 h.
- Stage 2 covers 13 fast maps (C, M, G) and 12 slow maps (T, C-marg, G-marg, plus U/F on
  holdouts only). Using 0001's per-run costs, that is about 50 min.
- Stage 3 is 12 × 10⁸ genotypes, about 15 min. Stage 0 is about 10 min.
- **Total ≈ 6.3 h.** Queue timeout 8 h, with internal deadline checks.

## Statistics

Per map and test set, the cost is mean log2 evaluations to an exact solve over the seeds, with
unsolved runs scored log2(2 × 524 288) = 20. A contrast A vs B is a speed ratio
r = 2^(cost_B − cost_A), averaged over A's trajectories (and B's, when B is learned). Its 95%
interval comes from a two-level bootstrap, resampling trajectories and then paired seeds, with
10 000 resamples. Each interval is classified with the practical effect set at **1.5×**:

- **faster**: the lower bound is > 1;
- **no practical gain**: not faster, and the upper bound is < 1.5;
- **unresolved**: everything else.

Rough power: within one trajectory, the paired SE per holdout is about 0.2 log2 (100 seeds,
low pairing). Between-trajectory sd is unknown; at 0.3, six trajectories give a half-width of
about 0.33 log2 (×1.26). So a true 1.5× gain should come out "faster", and a true null should
come out "no practical gain". If trajectories differ much more than that, row 5 says so, and
the measured spread sizes the next slot.

## Outcome rules (apply in order; the first match decides)

| row | condition (C = contextual learner, on the stage-2 test seeds) | meaning / next |
|---|---|---|
| 1 | C vs G on fresh training is **not faster** | The outer loop did not improve training search at this budget (E1). There is no transfer claim, and holdouts are reported descriptively. If M or T is faster than G on training or holdouts, that is reported as a secondary result. Return to strategy with the measured obstacle (score noise, step sizes, per-generation gain). |
| 2 | C faster on training; C vs G is **no practical gain** on both holdouts | Learning did not transfer to the withheld compositions at this budget (C1, overfitting). Return to strategy. |
| 3 | C faster on training; C **faster** than G on both holdouts; C **faster** than M on both holdouts | Learned contextual preferences transfer within this screened family, beyond retuning token weights on G (A1). Generic syntax learning is not excluded, and family specificity is untested. Return to strategy, which may use slot 2 for replication. |
| 4 | C faster on training; C **faster** than G on both holdouts; C vs M **no practical gain** on both holdouts | Transfer happens, but retuning token weights on G's template reproduces it within 1.5× (B1). New contextual preferences are not needed here. |
| 5 | anything else: one holdout only, an interval spanning 1–1.5, or C vs M unresolved or split | **Unresolved.** Report every interval and the number of trajectories that would resolve the leading contrast at the measured between-trajectory spread. |

Reported in every row, but never deciding one:
- C vs C-marg on holdouts. "Faster" would mean the learned map's final token frequencies alone
  do not reproduce it.
- T vs G-marg (whether frequency-only learning helps at all) and M vs G.
- The training-versus-holdout gap per learner.
- Learning curves and the L1 drift of each map from its start.
- Sampled holdout solver rates for C and M against G's 20–27 per 10⁸ (descriptive; sparse
  counts are bounds).
- Adaptation cost (inner evaluations and wall time) kept separate from transfer cost.

None of the rows can name a mechanism, since supply and mutation effects still move together.
None can establish family specificity.

**My expectation.** Rows 1 and 2 are the most likely. G is already close to a local optimum on
training in the probes, and a hand-set family grammar did not beat it. A clean row 1 or 2 is
still useful: it bounds what this kind of outer loop can add on top of a good supplied prior.

## Risks and what I did not choose

- **C's larger parameter space.** C has 24× more parameters than M or T with the same budget.
  A C ≈ M result (row 4) is therefore about this procedure as well as about context. I kept one
  shared operator so that "comparable budget" means the same thing for every learner. Giving C
  row-wise or targeted mutations would be a second, tuned procedure.
- **CMA-ES or gradient-style natural ES.** These are probably more sample-efficient, but they
  add a design surface with no probe behind it. A plain (μ + λ) loop with re-scored parents is
  the transparent first measurement. If row 1 comes back, a better optimizer is the obvious
  next diagnosis.
- **A calibration-only stage, then a separate main run.** The strategy and README both advise
  against a tiny experiment. The probes already measured cost and noise, so stage 0 only gates
  scale.
- **Fewer candidates with more seeds each (e.g. λ = 8, 36 runs).** The expected selection
  response is similar. I chose more children per generation.
- **More trajectories per learner (8) at fewer generations (15).** That would shorten learning,
  and the probes suggest learning needs the generations. If row 5 comes from trajectory spread,
  slot 2 can add trajectories.
- **Training the restricted control on linear tasks, or screening a second family.** The
  strategy rules both out (a linear fit is not token-matched; no more bank screens).
- **Starting C from U.** That would test learning from scratch, but it is out of reach at this
  budget: U solves 23% of training runs by 65k. Starting from G tests refinement of a supplied
  prior, and the results should be read that way.
