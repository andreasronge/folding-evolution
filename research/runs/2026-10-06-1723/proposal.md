---
node: questions/10-compositional-map-transfer/16-crossed-family-adaptation
title: Crossed BE/PA token-multiplier learning on the four-reducer bank, stage 1 (training only)
---
# Proposal 1723: independent BE and PA learning trajectories from G4

## Why this now

[Strategy 1723](strategy.md) puts root 10 first and asks one question. Does adapting the
same decoder to branch-else (BE) or to post-addition (PA) make that family's own withheld
compositions easier than the other family's training does? It also authorizes the narrower
split of one BE holdout and two PA holdouts, and it raises root 10 to 9 slots, three of them
for this. I follow it. I opened sub-question
[16](../../questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md).
This proposal is slot 7. It covers independent learning and fresh training scores only.
Holdouts are not scored until the final size has been fixed from training data (slot 8).

One change from the strategy: **the measured cost is about a third of the cost it assumed**.
That changes the stage sizes, not the design (see Feasibility). The strategy assumed 35–70
min per trajectory, taken from 1603's projection, which used the worst cell's mean, a 2×
slowdown allowance and full-cap final scoring. 1603's own G4 rows and 0132's real M
trajectories give about 12–14 min. So stage 1 can run 10 trajectories per family in one
queue, instead of the 2 + 2 batch sketched in the plan. A 2 + 2 batch would have measured
training variance on two maps per family. That is too few to size the crossed test.

## What would be run

Bank and split are frozen from run 1603 (`experiments/output/2026-10-06/2026-10-06-1603-four-reducer-family/bank.json`):
D1331, alphabet `v2_rmin_first`, G4 (hash `8a7b3091…`), and the reviewed four-reducer search
code on `research/main` (`four_reducer_run.py`, `map_learning.py`).

- **BE training (4):** `F?S:(M+m)`, `F?m:(S+M)`, `S?F:(M+m)`, `S?M:(m+F)`. Holdout `S?m:(M+F)`
  is not used.
- **PA training (6):** `(F?S:m)+M`, `(F?m:M)+S`, `(F?m:S)+M`, `(S?M:F)+m`, `(S?m:F)+M`,
  `(S?m:M)+F`. Holdouts `(F?S:M)+m` and `(S?M:m)+F` are not used.
- The run asserts that no training label vector equals a holdout's (1603 found no shared
  labels) and that no holdout cell ID appears in any job.

**Learner.** This is 0132's M learner as already implemented in 1603's unrun stage C, with
no procedural change:
- 24 log-multipliers on G4's rows, starting at G4, clipped to [1/16, 16].
- (4 + 12) with rescored parents and three-coordinate N(0, 0.5) mutations, for 25
  generations.
- Each candidate is scored by the mean log2 evaluations over 24 fresh 65 536-cap training
  searches. Unsolved runs count as 2 × cap.
- The 24 searches cycle over the family's training cells: 6 per cell for BE, 4 per cell
  for PA. Both families get the same search count and the same cap per candidate. Actual
  evaluations are reported.

Both families use identical starts, support, parameters and procedure. No family grammar,
canonical program or old solver enters.

**Trajectories.**
- Target 10 per family, each with its own outer seed (new block 1723200+). These are
  independent starts from G4, not continuations.
- They run as BE/PA pairs. Running each pair concurrently on the 10 workers is a
  load-balancing choice for the researcher.
- Before starting a new pair, the code checks that it fits: (slowest finished pair × 1.3)
  plus the remaining scoring must fit before the internal deadline. So any cut leaves equal
  n per family. Achieved n is a runtime outcome, not a data-dependent one.

**Final map rule** (training data only):
- Rescore the 4 final parents and G4 on 120 fresh 65k-cap training seeds (BE 30 per cell,
  PA 20 per cell).
- Keep the parent with the lowest mean log-cost.
- G4 is rescored on the same seeds for the gate and for the repeatability check.

**Early signal gate** (in code, after the first two pairs):
- Stop learning if all four selected maps beat G4 by less than log2(1.1) on their selection
  seeds.
- Selection is best of 4, so this gate is biased toward continuing. A stop is strong
  evidence of no learning.
- On a stop, the run goes straight to fresh scoring of those four maps.

**Fresh scoring** (cap 524 288, P 256, as 1603):
- Every saved map, plus G4, on all **ten** training cells (both families), 50 shared fresh
  seeds per cell (block 1723300–1723349).
- So each map is scored on its own family's training cells (in-sample) and on the other
  family's training cells (cells it never saw, but not holdouts).
- Holdout seeds are not generated in this run.

**Saved:**
- Every generation's candidates, scores and mutations.
- The within-generation Spearman between previous and rescored parent scores.
- Selection scores, final vectors, tables and hashes.
- Per-trajectory wall time and evaluations.
- The search rows.

**Runtime.**
- Learning: 20 trajectories × 12–14 min ≈ 4.0–4.7 h.
- Fresh scoring: 21 maps × 10 cells × 50 = 10 500 full-cap searches, about 1.5–1.9 s each
  (learned maps are faster) ≈ 30–40 min on 10 workers.
- Total expected ≈ 4.7–5.4 h. Internal deadline 7.5 h, timeout 8 h, so there is room for
  1.3× slower candidates.
- One queue entry. It is a heavy run, so it goes on the overnight queue unless the
  autonomous run's schedule says otherwise.

## Feasibility (measured)

| Quantity | Value | Source |
|---|---|---|
| G4 mean seconds per 65k-cap search, 10 workers loaded | BE training 0.93 s (0.71–1.11 by cell), PA training 0.76 s (0.40–1.21) | 1603 `search.jsonl`, 50 seeds per cell |
| G4 solved within 65 536 | BE 76–94 %, PA 80–100 % per training cell | same |
| G4 objective (mean log2 cost, 65k cap) | BE 13.95, PA 13.86; per-run sd 1.4–2.1 log2 → about 0.35 log2 SE per 24-search candidate | same |
| Can the objective see a family preference? | Hand-set G4-BE vs G4: 0.41 log2 lower cost on BE training cells, 0.55 higher on PA | same |
| Real learner cost at similar per-search cost | 0132 M trajectories (G, 0.78 s per inner search at generation 1): 530–644 s each; generation time fell from about 30 s to about 17 s as maps improved | 0132 `generations.jsonl` |
| Learner gain to expect | 0132 M over G on fresh training 2.23× [1.82, 2.75]; 6/6 trajectories faster | 0132 analysis |
| Inner searches per trajectory | (4 + 25 × 16) × 24 = 9 696, plus 600 selection | 1603 stage-C code |

Projected per trajectory: BE 9 696 × 0.93 s / 10 ≈ 15 min at G4's speed, PA ≈ 12 min, both
falling as the maps improve. No stage-0 probe is needed. The rates, tractability and
headroom on these cells are already measured. The code exists, was reviewed in 1603, and
never ran. I expect the researcher's work to be wiring, seed blocks, the pair scheduler and
fresh scoring on ten cells.

## Readouts

All speeds are paired capped-time speed ratios, as in 1603. Per map and cell, the ratio is
the geometric mean over the 50 shared seeds of T(G4) / T(map), where T is the evaluations
to solve, or the cap if unsolved. Cell values are then averaged in log2 over a cell set.
**The unit is the trajectory.** Intervals are 95% t intervals over trajectories: n − 1 df,
or Welch for between-family contrasts. There is no natural pairing between BE trajectory k
and PA trajectory k.

1. **Own-family training gain over G4**, per family (primary). Each family is classed:
   - **L**: lower bound > 1.0.
   - **N**: upper bound < 1.25.
   - **X**: otherwise.
2. **In-sample crossed contrast on training cells**, per family (secondary):
   - BE-trained over PA-trained maps on BE training cells.
   - PA-trained over BE-trained maps on PA training cells.
   - Classed **W** (lower > 1), **B** (upper < 1.25) or **X**.
   - For one arm these cells are in-sample, so this measures whether learning picked up any
     family information. It does not measure transfer.
3. **Off-family gain over G4** (descriptive), and its per-cell between-trajectory sd
   s_off: the median over the ten cells of the sd across trajectories of the per-map log2
   gain. This is the sizing proxy for a single unseen holdout cell.
4. **Descriptive measures:**
   - Repeatability: within-generation Spearman; the correlation across maps of final in-loop
     score, selection score and fresh own-training gain.
   - Parameter divergence: distance between the two families' mean log-multiplier vectors
     against the within-family spread, with a permutation p and the tokens that differ.
   - Cost per trajectory.

**Stage-2 size rule, fixed now.**
- Take n per family as the smallest of {achieved n, 14, 18} with
  t(0.975, 2n − 2) · s_off · √(2/n) ≤ 0.50 log2. That half-width lets a true 1.5×
  matched-over-mismatched effect on one holdout cell show a lower bound above 1.
- s_off includes 50-seed noise, so it is conservative for 200-seed holdout scoring.
- If 18 does not reach 0.50, stage 2 runs at the achieved n, and the proposal states the
  effect it can resolve.
- Stage 2 runs any extra trajectories with the identical procedure, then the frozen holdout
  evaluation. That evaluation covers all maps plus G4, on the three holdouts, 200 fresh
  seeds each, plus fresh training.
- With s_off near 0811's 0.41–0.45 log2 spread, 10 per family already meets the rule.

## Outcome rules (non-overlapping, applied in order)

| Row | Condition | Meaning | Next |
|---|---|---|---|
| U | Validation or pairing fails, a holdout appears in any job, or fewer than 6 per family complete for reasons other than the gate | Unresolved. Saved maps are pilot data. | Re-plan the cost. The slot is used. |
| 1 | The early gate stops learning after 2 per family | The token learner does not improve G4 on either training set at this budget. This limits this learner and budget, not learnable family structure. | Strategy. Holdout slots are not spent on this design. |
| 2 | Both families N | Same as row 1, with full data. | Strategy. |
| 3 | Both families L, and the crossed contrast is B in both | Learning works and carries little family information even in-sample (bounded below 1.25× both ways). A useful crossed holdout preference is implausible but not excluded. | Stage 2 holdout evaluation at the achieved n, with no extension. It should be read mainly as a generic-transfer check. |
| 4 | Both families L, and the crossed contrast is W or X in at least one family | Learning works, and family information is possible or present. | Stage 2 at the size set by the rule above. |
| 5 | Exactly one family L | Learning on one training set only. Crossed transfer can be tested only in that family's direction. | Stage 2 holdout evaluation at the achieved n, labelled one-directional. Or strategy, if the non-learning family is N, since the plan's two-way comparison is then gone. |
| 6 | Neither family L, and not both N | The learning gain is unresolved against between-trajectory spread. | Strategy, with the measured spread and the n that would resolve 1.25×. |

**My prediction:** row 4.
- Both families L, about 1.5–2.2× over G4, as M was over G.
- In-sample crossed contrasts small, about 1.1–1.3×, so X.
- Positive off-family gains, as M was on BE (2.23×).
- s_off about 0.45–0.55 log2, so 10 per family meets the size rule or comes close.

## What it cannot show

- Nothing about the holdouts. They are not scored.
- Nothing about learned context. G4's context stays hand-supplied.
- Off-family training cells are screened bank cells, and so is the single BE holdout. Every
  claim is about these training sets, not shape alone.
  - The two training sets differ in size (4 against 6 cells) and in role distribution.

## Alternatives considered

- **The 2 + 2 batch from the plan.** I rejected it because, at the measured cost, it would
  be a 1–1.5 h queue. Its variance estimate would rest on two maps per family, and the plan
  itself says a noisy small pilot should not decide the size.
- **More generations** (0132's curves were still falling at 25; 0811 gave 1.45× more after
  35). Deferred. It changes the reviewed procedure, and replication matters more for the
  crossed contrast than a bigger per-map gain. If row 2 or 6 occurs, it is the first
  redesign to consider.
- **Scoring holdouts now under a sealed rule.** Rejected. The strategy asks for the size to be
  fixed before holdout results are examined, and sealing is not reliable in this loop.
- **A contextual (row-residual) arm.** Not added, per the strategy. The hand-set witness
  keeps it as a later option.
- **Another bank or root 01 work.** The strategy defers both. Nothing in the parked questions
  meets a reopen condition: 08, 09, 02, 04 and 07 are unchanged since 1603's check.
