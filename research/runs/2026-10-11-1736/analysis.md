---
outcome: unresolved
---

# Analysis — 1736 recurrent-mutation selector (inherited R-all bit, separate endpoint readout)

Reviewer re-analysis from the raw rows, independent of `report.json`; every
number below was recomputed from `exposure.jsonl` and `score.jsonl` and agrees
with the report where they overlap. Printout: `figs/reanalysis.out`. Code:
commit `3a18ef5`. Raw data: `experiments/output/2026-10-11/2026-10-11-1736-exposure/`
and `…-readout/`. Design: [proposal](proposal.md), [queue](queue.yaml),
[code review](code_review.md).

## 1. Data completeness

Both stages finished inside their deadlines with exit 0 and no `failure.json`.
Exposure took 615 s wall of 1,800; readout 3,676 s of 7,200. The runner's own
checks (library hashes, method freeze, seed audit, endpoint-extraction hash,
per-job probability and budget) all passed.

| Check | Result |
|---|---|
| Exposure trajectories | 432 / 432 (L 144, S 144, N 144); no duplicate (build, arm, repeat) |
| Episodes per trajectory | 12 / 12 in all 432; 64 evaluated generations and 16,384 evaluations in all 5,184 episodes |
| Lead-cell balance | each of 6 cells leads 24 trajectories per arm |
| Start frequency | 1/16 in all 432 trajectories |
| Readout jobs | 8,640 / 8,640; 1,728 per law; 288 per (cell, law); 1,728 seed blocks each with all five laws; no duplicate keys |
| Readout probabilities | 0 mismatches against the exposure manifest (validator) |
| Unsolved readout jobs | 18 / 8,640, all forced to the 524,288 cap: initial 4, R-all 1, L-final 2, S-final 6, N-final 5 |
| Zero-carrier endpoints (deployed at q = 0, no library) | L 11, S 32, N 35 of 144 each |
| Protected cells scored | 0 |

Worker time: exposure 5,995 s, readout 36,582 s (proposal estimate 34,000 s).

## 2. Primary comparison

Capped mean evaluations over 12 fresh jobs per endpoint, averaged within
population, then library, then across 24 libraries. Interval: the
pre-registered nested paired bootstrap (libraries, populations within
libraries, one index set for all laws, 8,192 draws). My own bootstrap with a
different seed reproduces the report's intervals to the second decimal.

| Law | q | jobs | solved | capped mean evals | mean worker s |
|---|---|---|---|---|---|
| initial (q₀) | 1/32 | 1,728 | 1,724 | 61,571 | 4.70 |
| R-all | 0.5 | 1,728 | 1,727 | 29,030 | 2.21 |
| L-final | 0.5·f, mean 0.145 | 1,728 | 1,726 | 49,579 | 3.78 |
| S-final | 0.5·f, mean 0.026 | 1,728 | 1,722 | 70,890 | 5.41 |
| N-final | 0.5·f, mean 0.031 | 1,728 | 1,723 | 66,443 | 5.07 |

| Ratio (evaluations) | Point | 95% nested bootstrap | Worker-seconds point |
|---|---|---|---|
| **L-final / initial** | **0.805** | **[0.704, 0.913]** | 0.804 |
| L-final / N-final | 0.746 | [0.642, 0.860] | 0.746 |
| L-final / S-final | 0.699 | [0.609, 0.797] | 0.699 |
| L-final / R-all | 1.708 | [1.453, 2.014] | 1.711 |
| initial / R-all (headroom) | 2.121 | [1.825, 2.503] | 2.127 |

Against the proposal's decision rule: the upper bound of L-final/initial is
0.913, not below 0.90, and the lower bound is 0.704, not above 0.80. Neither
the "useful" nor the "no worthwhile saving" branch fires. **Unresolved**, as
the runner's `classify()` also returned. The miss is narrow: a library-only
bootstrap (no nested population resampling, not the pre-registered unit)
gives [0.737, 0.876]. Both inheritance controls are resolved on their own:
L-final beats N-final and S-final with upper bounds 0.86 and 0.80.

Headroom holds (2.12 ≥ 1.25), so the test was informative in the plan's
sense. Robustness: removing the 18 capped jobs changes L/initial from 0.805
to 0.811 and L/N from 0.746 to 0.754. Per library, L-final is cheaper than
initial in 20 / 24 (ratios 0.53 to 1.10); per population, in 94 / 144, and
L-final is cheaper than both N-final and S-final in 94 / 144. Per cell, the
L/initial ratio is 0.66 to 0.97 (below 1 in all six); N/initial is 1.00 to
1.18 and S/initial 1.03 to 1.34.

## 3. What the exposure did to the bit

`figs/frequency_trajectories.png`, `figs/final_f_hist.png`.

| Arm | n | mean final f [95%] | median | f = 0 | f ≤ 1/16 | f > 0.25 | f > 0.5 | max | episodes solved / 1,728 |
|---|---|---|---|---|---|---|---|---|---|
| L | 144 | 0.290 [0.230, 0.351] | 0.150 | 11 | 55 | 61 | 46 | 0.887 | 839 |
| S | 144 | 0.052 [0.035, 0.073] | 0.016 | 32 | 115 | 8 | 1 | 0.527 | 699 |
| N | 144 | 0.062 [0.038, 0.091] | 0.008 | 35 | 114 | 10 | 4 | 0.777 | 590 |

L − N in mean final f: 0.228 [0.158, 0.297]; L − S: 0.237 [0.172, 0.304].
L's per-library mean exceeds N's and S's in 24 / 24 libraries; per paired
trajectory L > N in 103, L < N in 32, tie in 9 of 144. No trajectory fixed
(one L generation out of 110,592 reached f = 1). Nothing absorbed: with
recurrent mutation the bit stayed polymorphic in 94,661 of 110,592 L
generations, so unlike probe 1427 all twelve episodes carried information.

The L distribution is bimodal, not a shifted copy of N: 55 / 144 populations
ended at or below the starting 1/16, and 46 / 144 above 0.5. Mean f at the
end of episodes 1 to 12 in L was 0.21, 0.23, 0.25, 0.25, 0.32, 0.31, 0.28,
0.29, 0.32, 0.29, 0.28, 0.29: most of the rise happens in the first episode
and the level then holds with mutation pulling back. In N and S the
episode-end mean never leaves 0.04 to 0.08.

Per-episode change by starting frequency (L): +0.12 from f = 0 (n 156),
+0.14 from (0, 1/16] (627), +0.12 from (1/16, 1/8] (164), +0.10 from
(1/8, 1/4] (148), −0.02 from (1/4, 1/2] (178), −0.22 from (1/2, 1] (455).
In N and S the change is +0.03 to +0.06 from f ≤ 1/16 (mutation refilling
toward 1/16) and negative above it. So in L selection is pushing up to
roughly f ≈ 0.3 to 0.5, where the 1/32 redraw toward Bernoulli(1/16)
balances it.

Per-generation selection differential (recipient f − census f), pre-solve,
0 < f ≤ 0.25: L +0.0013 over 41,245 generations (report's
population-then-library estimate +0.0017 [+0.0011, +0.0022]); S −0.00004 over
59,081; N −0.0008 [−0.0010, −0.0006] over 60,673. Relative advantage
Δf / f(1−f) in that band: L +0.017, N −0.043. Pre-solve above f = 0.25, L's
differential is +0.016 per generation (22,111 generations), about ten times
the low-f value. Mean distinct recipients per generation: 97 to 99 in all
arms, as the forecast assumed.

Mutation bookkeeping (N): off→on 50,596 / 25,878,574 = 0.00196 (expected
1/512 = 0.00195); on→off 52,030 / 1,772,882 = 0.0293 (expected 15/512 =
0.0293). L and S match to three decimals.

Operators: L carriers' library draws are rejected 40% pre-solve and 55%
post-solve, against 30 to 37% for ordinary donors in every arm and state.
N carriers never draw from the library (0 draws in both states), as wired.

## 4. The saving is a dose effect

`figs/endpoint_dose_response.png`. Since content and donor law are frozen,
an endpoint law differs from q₀ only in its probability q = f/2. Pooling all
8,640 jobs by the q they ran at:

| q | jobs | solved | capped mean | median |
|---|---|---|---|---|
| 0 | 936 | 934 | 74,067 | 27,136 |
| (0, 1/32) | 2,400 | 2,390 | 70,143 | 34,816 |
| 1/32 | 1,800 | 1,796 | 61,248 | 21,760 |
| (1/32, 1/16] | 444 | 444 | 60,221 | 22,656 |
| (1/16, 1/8] | 384 | 383 | 53,465 | 14,336 |
| (1/8, 1/4] | 336 | 336 | 44,214 | 7,424 |
| (1/4, 1/2) | 612 | 612 | 31,600 | 5,376 |
| 1/2 | 1,728 | 1,727 | 29,030 | 4,096 |

The 1427 fit cost(q) ≈ 32k + 42k·e^(−q/0.104) applied to each endpoint's
actual q and averaged predicts 52.2k for L-final (observed 49.6k, ratio
0.95), 67.1k for S-final (70.9k, 1.06) and 66.8k for N-final (66.4k, 0.99).
At matched q, L endpoints cost 2.8k less than the pooled bin mean, N 1.0k
less, S 3.5k more: no sign that an L endpoint is anything other than the
R-all library at its own q.

Within L, the saving comes entirely from the populations where the carrier
rose. The 62 L endpoints with f ≥ 0.25 cost 34.1k against 64.2k for q₀ on
the same seeds (ratio 0.53, close to R-all's 27.7k on those seeds). The 68
with f < 1/8 cost 62.6k against 60.2k; the 11 at f = 0 cost 64.9k against
59.0k. L/initial is therefore a mixture of a large saving in 43% of
populations and a slight loss in the rest.

Why N-final and S-final cost more than q₀ although their mean q is about
1/32: the curve is convex and 35 N and 32 S endpoints sit at q = 0 (74k each),
the Jensen effect already seen in 1427. L/N and L/S are thus "L kept or
raised the bit, N and S drifted", which is section 3 restated.

## 5. Economics (reported, deciding nothing)

Acquisition of one library 214k evaluations, modifier exposure 197k per
population, fresh search 49.6k (L). Total L / total q₀-with-library 1.67
[1.61, 1.74]; total L / total R-all 1.89 [1.82, 1.98]. The exposure saves
12.0k evaluations per fresh search against q₀, so it pays back after about
16 fresh searches per population. Setting q = 0.5 by hand (R-all) costs 1.71
[1.45, 2.01] times less than the evolved law and needs no exposure.

## 6. What the data show and do not show

Shown:

- Under lexicase program selection alone, a recurrently mutated inherited bit
  that switches a program's mutation donors to the saved R-all library rose
  from 1/16 to a mean of 0.29 after 12 episodes, against 0.06 with the same
  bit and no library and 0.05 with the same bit shuffled every generation.
  The difference is resolved: 24 / 24 libraries, interval well clear of 0.
- The rise is bimodal: 46 / 144 L populations above 0.5, 55 / 144 at or
  below the start. Selection is weak per generation at low f (+0.0013) and
  about ten times stronger above f = 0.25, and the 1/32 redraw holds the
  high state near 0.3 to 0.5.
- Deployed alone, the law L ended with is cheaper than its starting law:
  0.805 [0.704, 0.913] in capped mean evaluations, cheaper in 20 / 24
  libraries, and cheaper than both controls with upper bounds below 1.
- The cost of every endpoint is predicted within 6% by the 1427 dose curve
  from its q alone. The saving is the dose the selected frequency buys, in the
  populations where it rose.
- Headroom is present: q₀ costs 2.12 [1.83, 2.50] times R-all, more than the
  1.9× the forecast expected.

Not shown:

- A saving of at least 20% against q₀ is neither confirmed nor excluded by
  the pre-registered interval. The point is 0.805; the interval runs 0.70 to
  0.91.
- Nothing here is about content learning or transfer: the library and its
  donor law were fixed, the bit chooses only how often it is used, and the
  deployment is on the six development cells.
- The low-f per-generation differential is tiny (+0.0013); the forecast's
  s ≈ 0.036 was not observed at low f. What the forecast missed is the
  positive frequency dependence: selection on the carrier strengthens as
  carriers become common, so populations that escape the low-f band run
  away to f > 0.5 while the others stay near the mutation floor. The
  forecast's single-s model predicted mean f ≈ 0.13 and no bimodality.
- L endpoints are not cheaper than N or S endpoints at the same q, so the
  "law" carries nothing beyond q. This is by design, not a finding against
  inheritance.
- Precision: the half-width is about ±13% of the point, wider than the
  ±10% the proposal budgeted, because endpoint q varies between 0 and 0.44
  and the cost curve is steep over that range.

## Against the predictions

Read after the analysis above was written. The plan's frozen outcome table
has four rows; the data match the fourth.

| Plan row | Condition | Observed | Matches |
|---|---|---|---|
| 1 Useful with controls | L/q₀ upper < 0.90 and L/N, L/S upper < 1 | upper 0.913; L/N 0.86, L/S 0.80 | no (primary bound alone fails) |
| 2 Saving, inheritance unresolved | upper < 0.90, a control unresolved | upper 0.913 | no |
| 3 20% saving excluded | lower > 0.80 and upper ≥ 0.90 | lower 0.704 | no |
| **4 Unresolved** | any other interval | [0.704, 0.913] | **yes** |

So `outcome: unresolved`, the plan's own label, with the plan's instruction to
report a resolving price to strategy (section below). The plan's caveats were
met: headroom q₀/R-all is 2.12, above 1.25; the result is not "beating only a
degraded S" since L also beats N and q₀ itself; and the saving is for this
fixed mutation/exposure/deployment procedure with supplied content only.

**Proposal expectation versus outcome.** The proposal expected the "no
worthwhile saving" row with L/q₀ ≈ 0.95, mean final f of L ≈ 0.13 and N ≈
0.065, and 17 to 23% of populations at zero carriers. Observed: L/q₀ 0.805,
L mean f 0.29, N 0.062, zero-carrier endpoints L 8%, N 24%, S 22%. The
forecast was right about N and about the zero-carrier share in N and S, and
wrong about L by a factor of two in f and by 0.15 in the cost ratio. Its
model used one constant selection coefficient; the data show selection that
is nearly flat at low f (+0.0013 per generation) and about ten times stronger
above f = 0.25, giving a bimodal split instead of the forecast's unimodal
mean. The forecast's claim that "low-frequency selection would need s ≈ 0.1"
was not what happened: low-f selection stayed weak, and escape from the
low-f band, not strength within it, decided each population.

**The proposal's listed surprises.**

| Surprise | Observed | Triggered |
|---|---|---|
| L-final/q₀ ≤ 0.85 | point 0.805, interval [0.70, 0.91] | point yes, interval does not settle it |
| low-f differential ≥ 0.08 | +0.0017 per generation (report), +0.0013 generation-weighted | no, by a factor of 50 |
| L's mean final f no higher than N's | 0.29 vs 0.06, L − N 0.228 [0.158, 0.297] | no |
| q₀ ≤ 1.25 × R-all | 2.12 [1.83, 2.50] | no |

**Feasibility anchors.** Exposure 615 s against a forecast of about 11 min;
readout 3,676 s against about 57 min; both inside the 30 + 120 min reserve.
Solve rates: readout 8,622 / 8,640; exposure episode solves L 839, S 699,
N 590 of 1,728, so L's exposure solve share (49%) is close to the forecast's
50%, and N's (34%) matches 1427's 32%.

**Precision.** The plan's pre-check warned that ±10% was not established and
that high endpoint variance could leave 0.80 unresolved. The realised
half-width is about ±0.105 on a point of 0.805 (±13%), between the
pre-check's "half spread, CV 0.5" case ([0.81, 1.10] width 0.29) and its
"full spread" case; the actual width is 0.21, narrower than either, but the
point landed where a 0.90 bound matters. Per-population ratio SD is 0.65,
of which the between-library SD of means is 0.20 and the within-library SD
0.55, so most of the noise is between populations (the bimodal fate of the
bit), not between libraries.

**Resolving price, for strategy.** Reusing the observed rows and resampling
more populations per library from the same 24 libraries (an approximation,
since new populations would also add new endpoint fates): 12 populations per
library gives about [0.72, 0.90], 18 gives [0.73, 0.89], 24 gives
[0.73, 0.89]. Doubling populations would just about bring the upper bound
under 0.90 if the point held at 0.805; it would cost another 432 exposure
trajectories plus 8,640 readout jobs, about 70 min of queue. That resolves
only rows 1 versus 4; it does not change what the mechanism is, which the
dose analysis already identifies: the evolved law is R-all at the frequency
selection reached, and its saving over q₀ is the dose curve applied to a
bimodal frequency distribution. A cheaper way to the same quantity is to
read the saving off the 1427 and 1736 dose curve for whatever f distribution
one is willing to assume, since the endpoints' costs sit on that curve
within 6%.
