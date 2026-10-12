---
outcome: 20_percent_pooled_saving_excluded
---

# Analysis: 2026-10-12-0250 inherited content choice (order vs gate library bit)

Reviewer re-analysis from the raw rows, independent of `report.json`. Every number below was recomputed from
`exposure.jsonl` and `score.jsonl` with a different bootstrap seed and agrees with the report where they overlap
(primary 0.991 [0.926, 1.060] here against 0.991 [0.928, 1.059] in the report). Scripts: [reanalysis.py](reanalysis.py),
[reanalysis_decomp.py](reanalysis_decomp.py); printouts in [figs/reanalysis.out](figs/reanalysis.out) and
[figs/reanalysis_decomp.out](figs/reanalysis_decomp.out). Code: commit `4ed0469`. Raw data:
`experiments/output/2026-10-12/2026-10-12-0250-exposure/` and `…-readout/`. Design: [proposal](proposal.md),
[queue](queue.yaml), [code review](code_review.md), [execution](execution.md).

## 1. Data completeness

Both stages finished with exit 0 inside their deadlines and without `failure.json`. Exposure 1,704 s wall of 3,000;
readout 4,649 s of 9,600. The runner's own fail-closed checks (library and archive hashes, method freeze, schedule and
seed audit, per-episode continuity and donor accounting, exact witnesses, readout fraction and budget) all passed and the
readout admitted the exposure manifest.

| Check | Result |
|---|---|
| Exposure trajectories | 1,152 / 1,152: 192 per (family, arm), no duplicate (family, build, arm, slot) |
| Episodes | 12 × 64 generations and 16,384 evaluations in every trajectory; 13,824 episodes, 10,854 solved |
| Start frequency | exactly 128/256 in all 1,152 trajectories |
| Readout jobs | 36,288 / 36,288; order 2,304 per population law and 288 per pure law; gate 4,608 and 576; no duplicate keys |
| Grid | 24 builds × 8 populations × 6 cells × 2 (order) or 4 (gate) seed blocks per population law; pure laws 24 × 6 × 2 or 4 |
| Seeds | the five population laws share seeds within (family, build, slot, cell, block): 6,912 / 6,912 slots identical for L-matched, M, S, N; pure laws in their own namespace |
| Fraction wiring | L-matched fractions on gate equal L-swapped fractions on order and vice versa (same 128 and 112 distinct values); M = 0.5, O = 0, G = 1 in every row |
| Unsolved readout jobs (charged 524,288) | order 19 / 12,096: L-matched 6, L-swapped 1, S 1, N 2, M 1, G 8; gate 0 / 24,192 |
| Restarts used | 32,074 jobs solved on the first 65,536-evaluation attempt; 34 needed all eight |
| Protected cells scored | 0 |

Worker time: exposure 18,340 s, readout 54,700 s (proposal estimate 16k + 48k).

## 2. Primary comparison

Capped mean evaluations, averaged over 12 (order) or 24 (gate) jobs per population, then over 8 populations per
build, then over 24 builds. Interval: the pre-registered nested paired bootstrap (builds with one index set for both
families and all laws, populations within builds, pure references constant across populations), 8,192 draws.

| Family | L-matched | L-swapped | S | N | M | O (f = 0) | G (f = 1) |
|---|---|---|---|---|---|---|---|
| order (6 dev cells) | 41,524 | 43,556 | 44,312 | 42,861 | 42,268 | 30,648 | 94,003 |
| gate (6 dev cells) | 4,955 | 5,336 | 5,135 | 5,068 | 4,961 | 9,575 | 3,860 |

| Ratio (evaluations) | order | gate |
|---|---|---|
| **L-matched / M** | **0.982 [0.882, 1.093]** | **0.999 [0.928, 1.075]** |
| L-matched / L-swapped | 0.953 [0.846, 1.081] | 0.929 [0.856, 1.005] |
| L-swapped / M | 1.030 [0.940, 1.129] | 1.076 [0.992, 1.166] |
| S / M | 1.048 [0.942, 1.168] | 1.035 [0.960, 1.110] |
| N / M | 1.014 [0.898, 1.145] | 1.022 [0.942, 1.109] |
| L-matched / S | 0.937 [0.830, 1.060] | 0.965 [0.892, 1.044] |
| L-matched / N | 0.969 [0.855, 1.103] | 0.978 [0.899, 1.060] |
| own pure / M (headroom) | O/M 0.725 [0.594, 0.876] | G/M 0.778 [0.679, 0.887] |
| other pure / M | G/M 2.22 [1.86, 2.65] | O/M 1.93 [1.69, 2.20] |

**Primary R (geometric mean of L-matched/M over families): 0.991 [0.926, 1.060].** Worker seconds give the same
ratios (order 0.983, gate 1.002). Against the proposal's rule: upper bound 1.06 is not below 0.90 (not useful),
lower bound 0.93 is above 0.80, so the "no worthwhile saving / 20% pooled saving excluded" branch fires. Neither
family meets the directional conjunction (L-matched/M upper < 1 and L-matched/L-swapped upper < 1): on gate the
swapped contrast just misses (upper 1.005) and the M contrast is centred on 1.

Validity guard: pooled own-pure/M is 0.751 [0.652, 0.856], per family 0.725 and 0.778 with upper bounds 0.88 and
0.89, so the pre-set 10% headroom bar is met in both directions. The test had room to show a saving and did not.

Paired counts (same seeds): L-matched cheaper than M in 13/24 builds and 102/192 populations on order, 13/24 and
109/192 on gate. Per-build L-matched/M ratios span 0.68 to 1.42 (order) and 0.71 to 1.22 (gate), median 0.99 in
both ([figs/paired_builds.png](figs/paired_builds.png)). Per cell, L-matched/M is 0.88 to 1.05 on the six order
cells and 0.90 to 1.14 on the six gate cells, with no cell resolving a direction on its own.

Robustness: dropping the 19 capped order rows moves order L-matched/M from 0.982 to 0.957 (L-matched holds 6 of
the 11 capped population-law rows); gate is unchanged. Nothing in the primary depends on the cap.

## 3. What exposure did to the bit

[figs/final_f_hist.png](figs/final_f_hist.png), [figs/episode_sawtooth.png](figs/episode_sawtooth.png).

| Family / arm | mean final f [95%] | sd | f < 0.25 | f > 0.5 | f > 0.75 | episodes solved / 2,304 | median pre-solve generations |
|---|---|---|---|---|---|---|---|
| order / L | **0.377 [0.341, 0.413]** | 0.19 | 65 / 192 | 55 / 192 | 10 | 1,471 | 14 |
| order / S | 0.485 [0.441, 0.525] | 0.21 | 24 | 82 | 25 | 1,361 | 16 |
| order / N | 0.486 [0.444, 0.529] | 0.23 | 36 | 96 | 28 | 1,409 | 16 |
| gate / L | **0.516 [0.472, 0.560]** | 0.21 | 25 | 97 | 32 | 2,202 | 11 |
| gate / S | 0.484 [0.445, 0.522] | 0.19 | 18 | 88 | 18 | 2,190 | 11 |
| gate / N | 0.475 [0.433, 0.519] | 0.22 | 39 | 86 | 29 | 2,221 | 11 |

Frequency contrasts (build-paired bootstrap): order L − S **−0.108 [−0.163, −0.056]**, L − N −0.109 [−0.164, −0.054],
L below S in 22/24 builds. Gate L − S +0.032 [−0.029, +0.095], L − N +0.040 [−0.020, +0.100], L above N in 17/24
builds. So selection moved the bit toward the matched library in both families, resolved on order and unresolved
on gate, and in both cases by far less than the proposal expected (0.15–0.3 endpoint on order). The S and N
endpoints are compatible with the 0.5 start but spread widely (sd about 0.2) because 1/32 redraw plus drift in a
population of 256 is a random walk over 768 generations.

**The endpoint is a maintenance-phase equilibrium, not the selected frequency.** Within every episode on order, the
linked arm's f falls during the pre-solve phase and climbs back once the population has a solver
([figs/episode_sawtooth.png](figs/episode_sawtooth.png); episode means start → at first solve → end: 0.50 → 0.28 → 0.43,
then 0.43 → 0.23 → 0.41, …, 0.43 → 0.24 → 0.38). Per-generation decomposition of Δf from the trace
(selection = recipient f − census f; redraw = post-redraw f − recipient f; elites = the rest):

| Family / arm | phase | generations | mean f | selection | redraw | elites | net per generation |
|---|---|---|---|---|---|---|---|
| order / L | pre-solve | 77,873 | 0.398 | **−0.0064** | +0.0034 | −0.0004 | −0.0033 |
| order / L | maintenance | 67,279 | 0.311 | −0.0012 | **+0.0060** | −0.0013 | +0.0035 |
| gate / L | pre-solve | 36,254 | 0.500 | **+0.0037** | −0.0002 | 0.0000 | +0.0036 |
| gate / L | maintenance | 108,898 | 0.557 | +0.0002 | **−0.0018** | +0.0005 | −0.0012 |
| order / S, N; gate / S, N | both | | ≈ 0.5 | within ±0.0004 | ≈ (0.5 − f)/32 | ≈ 0 | within ±0.001 |

The redraw column equals (0.5 − f)/32 to four decimals, as the design specifies: a child's bit is redrawn from
Bernoulli(1/2) with probability 1/32, which is a restoring force toward 0.5 with a 32-generation time constant.
Selection on the bit is only present before the first solve (order −0.0064 per generation, about a 1.6% relative
disadvantage for gate carriers; gate +0.0037) and is an order of magnitude weaker afterwards. Solved episodes spend
23% (gate) to 29% (order) of their 64 generations pre-solve, so for most of the exposure the redraw pull wins and the
bit relaxes back toward 0.5. On order the bit reached a mean of 0.24 at the moment of first solve (n = 1,471
episodes; 0.242 in the final episode) but was handed to the readout at 0.38. On gate the pre-solve rise to 0.58 was
handed over at 0.52. The design therefore measured the mutation–selection balance of an intermittently selected
bit, and the balance sits close to the start.

The S arm shows a small sawtooth too (pre −0.024, maintenance +0.039 per episode), with a selection differential of
−0.0004 per generation: not a linkage effect, and it cancels. N is flat.

Rejection by state (from the report's per-state counters): pre-solve library-draw rejection is 0.41 for both states
on order and 0.33 (order donors) vs 0.29 (gate donors) on gate; maintenance rejection is 0.55–0.59 everywhere. Both
states attempted library donors on exactly half of mutations in every arm and phase, so the intervention was the
repertoire, as designed.

## 4. The readout as a dose curve

[figs/dose_curve.png](figs/dose_curve.png). The four population laws on each family give 768 (f, cost) points on
the same cells and seeds, and the pure laws anchor f = 0 and f = 1. Cost rises monotonically with f on order
(Spearman +0.42) and falls on gate (−0.36). Bins built from S, N and L-swapped populations only (cost / M):

| f bin | [0, .15) | [.15, .25) | [.25, .35) | [.35, .45) | [.45, .55) | [.55, .65) | [.65, .75) | [.75, .85) | [.85, 1] |
|---|---|---|---|---|---|---|---|---|---|
| order | 0.78 | 0.73 | 0.83 | 0.89 | 1.00 | 1.06 | 1.16 | 1.43 | 1.82 |
| gate | 1.35 | 1.21 | 1.11 | 1.03 | 0.99 | 0.92 | 0.86 | 1.00 | 0.84 |

Reading L-matched off this curve: its order endpoints (mean f 0.377, sd 0.19) predict 0.90 of M; it actually cost
0.98 (0.96 without its capped rows). Its gate endpoints (mean f 0.516) predict 1.01 and cost 1.00. So the linked
law carries nothing visible beyond its frequency, and the frequency it reached buys at most a few percent. The curve
is convex on order between 0.2 and 1, so a population spread of f costs more than its mean f would (predicted 0.90
for the distribution against 0.89 for a single f of 0.377); the same spread explains why S and N, centred on 0.5,
cost 1.01–1.05 of M rather than 1.00.

Projection, not measured: had the readout frozen f at the first solve of the last episode instead of at the
episode's end (order mean 0.24, sd 0.29), the same bins predict about 0.91 of M, because those endpoints are more
dispersed. The pure order library (0.725) remains the cheapest law on order, and the pure gate library (0.778) on
gate; no evolved endpoint distribution approaches either.

## 5. Economics (reported only)

Per population on order: acquisition of both libraries 429,707 evaluations, exposure 196,608, fresh search 41,524
against 42,268 for M. The exposure saves about 740 evaluations per fresh search on order and about 6 on gate, so it
would repay after roughly 260 searches on order and never in practice on gate. Hand-set pure libraries need no
exposure and cost 0.73 and 0.78 of M.

## 6. What the data shows and does not show

Shows (six development cells per family, 24 build-paired libraries, P 256, lexicase, crossover 0.5, library
probability 1/2, redraw 1/32 toward 1/2, twelve 64-generation episodes with continuation after solves):

- A per-individual inherited bit choosing between two supplied repertoires moves toward the repertoire that suits
  the exposure family: resolved on order (−0.11, 22/24 builds), directionally consistent but unresolved on gate
  (+0.03 to +0.04). Both shifts are small.
- The frozen endpoint mixtures do not make fresh search cheaper than the 50/50 start: pooled 0.99 [0.93, 1.06], with
  a 20% pooled saving excluded and no family resolving even a 1% saving. Headroom was present (own pure library
  0.73–0.78 of M).
- The endpoint's cost is what the dose curve predicts for its frequency; nothing beyond the dose was found (same
  conclusion as 1736 for a one-library dose).
- Mechanism of the small shift: selection on the bit acts only before the first solve (about a quarter of
  generations in solved episodes), while the 1/32 redraw toward Bernoulli(1/2) pulls the bit back toward 0.5 for the
  rest of each episode. The readout froze the relaxed frequency.
- L-swapped (the wrong family's endpoint) costs 1.03 (order) and 1.08 [0.99, 1.17] (gate) of M: a mildly wrong
  mixture is mildly costly, as the dose curve predicts.

Does not show:

- That the selector could not reach a useful mixture under a different exposure rule (stopping at first solve,
  weaker or asymmetric redraw, longer pre-solve phases). The within-episode minimum on order (0.24) is in the region
  where the dose curve gives 0.73–0.83 of M, but that is a projection from other populations' endpoints, not a
  measured readout, and the pre-solve frequencies are more dispersed than the endpoints.
- Anything about content learning, inherited token semantics, or transfer to protected or fresh cells. All
  scored cells are development data; the repertoires were supplied.
- Whether persistent program–bit linkage, as opposed to any other route, caused the frequency shift: L differs from
  S and N in frequency (resolved on order) but not in readout cost (L-matched/S 0.94 [0.83, 1.06]; L-matched/N 0.97
  [0.86, 1.10]), so the linkage contribution to cost is unresolved.
- A precise value of L-matched/L-swapped on gate (0.93 [0.86, 1.005]): the point favours the matched endpoint but the
  interval touches 1.

## Against the predictions

Read after the analysis above was written. [plan.md](plan.md) and the [proposal](proposal.md) set the rules and
expectations.

**Outcome precedence (plan).** Reciprocal usefulness, one-direction usefulness and pooled-improvement all require a
pooled upper bound below 0.90; the observed upper bound is 1.06, so none applies. "20% pooled saving excluded"
attaches independently when the lower bound exceeds 0.80; the observed lower bound is 0.93, so it attaches. The
usefulness classification is therefore the plan's residual class with the exclusion label attached, which is the
runner's `20_percent_pooled_saving_excluded` and the proposal's "no worthwhile saving: this ends the candidate".
No directional conjunction resolved (gate L-matched/L-swapped upper 1.005; both L-matched/M intervals contain 1).

**Validity guard.** The plan treats own-pure/M upper ≥ 0.90 as unresolved headroom. Observed uppers are 0.88 (order)
and 0.89 (gate), pooled 0.86, so headroom is established and the negative result bounds this selector and exposure
rule, as the plan says a negative with established headroom should.

**Control language.** The plan: if controls match L in dynamics and cost, linkage's contribution is unresolved. Here
L differs from S and N in dynamics on order (resolved frequency shift) but not in cost (L-matched/S and L-matched/N
intervals contain 1 in both families), and the endpoint laws are not useful. The plan's "selector shift alone is
insufficient" clause applies: the shift is real on order and is not a usefulness result.

**Steward's expectations (proposal).**

| Prediction | Observed |
|---|---|
| Order exposure drives f to about 0.15–0.3 | mean endpoint 0.377 [0.341, 0.413]; 65/192 populations below 0.25. The pre-solve minimum (0.24 at first solve) is in the predicted range, but the redraw relaxed it before the endpoint was taken |
| Gate exposure moves f less, episodes mostly maintenance | correct: +0.03 to +0.04, unresolved; 77% of generations in solved gate episodes are maintenance |
| R ≈ 0.85–0.9, most likely unresolved or one direction (order) | R 0.99 [0.93, 1.06]; worse than the predicted range, and the 20% exclusion fired instead of unresolved |
| L-matched < L-swapped clear on order | 0.953 [0.846, 1.081], not resolved on order; nearer on gate (0.929 [0.856, 1.005]) |
| Surprises listed: N or S matching L; L-matched worse than M anywhere | S and N match L in cost (both families). L-matched is not resolved worse than M anywhere (gate point 0.999) |
| Precision ±8–9% on R (plan's conservative ±12–15%) | achieved ±6.5%: the endpoints were unimodal and far from the steep part of the dose curve, so population variance was smaller than 1736's bimodal case |

**Why the prediction missed, as the data show it.** The proposal priced the endpoint as if selection acted throughout
exposure. The decomposition in §3 shows selection acting at −0.0064 per generation only before the first solve
(29% of generations in solved order episodes) against a redraw pull of +(0.5 − f)/32 that acts every generation.
With f₀ = 1/2 and redraw toward 1/2, the mutation pressure is maximal exactly in the direction selection has to
overcome, which 1736 (redraw toward 1/16, selection pushing up from 1/16) did not face. The endpoint is the
balance of the two, about 0.38, and the dose curve says 0.38 is worth about 10% at best on order.

**Next action per proposal.** "Return to strategy whatever the outcome; a negative bounds this selector and exposure
rule (no top-up or rate sweep)." The data support that: more seeds would narrow an interval already centred on 1.
The one observation that could inform a redesign (not a funded follow-up) is that the pre-solve frequency reaches
the useful region of the dose curve and the maintenance phase gives it back; a first-solve freeze or a redraw not
aimed at 0.5 would be a different exposure rule, outside this experiment's claim.
