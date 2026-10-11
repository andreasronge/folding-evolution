---
outcome: observations
---

# Analysis — 1427 standing-variation probe (inherited R-all bit)

Reviewer re-analysis from the raw rows, independent of `report.json`
(numbers agree with the report where they overlap). Script:
`analysis_support.py` in this folder; its full printout is
`figs/analysis_support.out`. Code: commit `f8f4246`. Raw data:
`experiments/output/2026-10-11/2026-10-11-1427-exposure/` and
`…-readout/`. This is a probe: everything below is an observation, not a
finding.

## 1. Data completeness

Both stages completed inside their deadlines (exposure 480 s wall of 1,500;
readout 533 s of 1,800), exit 0, no `failure.json` in either folder, all
hash and seed-audit checks passed inside the runner.

| Check | Result |
|---|---|
| Exposure trajectories | 336 / 336 (L 96, S 96, Z 96, N 48); no duplicate (build, arm, repeat) keys |
| Episodes per trajectory | 12 / 12 in all 336; 64 evaluated generations in all 4,032 episodes |
| Lead-cell balance | each of 6 cells leads 16 trajectories per arm in L/S/Z, 8 in N |
| Readout jobs | 1,440 / 1,440; 288 per law; 48 per (cell, law); no duplicate keys |
| Readout probabilities | 0 mismatches against the exposure manifest |
| Unsolved readout jobs | 4 / 1,440, all at the 524,288 cap (R-tree 1, L-final 1, S-final 2) |
| `force_cap` episodes | 0; shortcuts (training-perfect but not exact) are rejected, never counted as solves |
| Protected cells scored | 0 |

Three of the four unsolved readout jobs are the same job in disguise:
build 3, cell `O:lo02+hi12`, where L-final and S-final both extracted
probability 0 and therefore reran R-tree's seeds. Paired seeds plus equal
probability means identical runs; this is intended and shows up again
below (7 builds have L-final = initial = 0.125 exactly).

## 2. Exposure: what happened to the bit

### 2.1 Every trajectory absorbed, almost all in the first episode

The design budgeted 12 episodes (768 generations). The bit's fate was
decided in the first one.

| Arm | n | fixed (f=1) | lost (f=0) | absorbed in episode 0 | absorbed in episode 1 | later | median absorbing generation (IQR) |
|---|---|---|---|---|---|---|---|
| L | 96 | 46 | 50 | 88 | 8 | 0 | 12 (8–22) |
| S | 96 | 27 | 69 | 80 | 16 | 0 | 18 (11–40) |
| Z | 96 | 29 | 67 | 82 | 14 | 0 | 17 (8–34) |
| N | 48 | 16 | 32 | 40 | 7 | 1 | 15.5 (9–50) |

No trajectory was polymorphic at the end. The latest absorption anywhere was
generation 136 (N). After generation ~140 the plots are flat lines
(`figs/frequency_trajectories.png`). Distinct recipients per generation
averaged 88 in the first 20 generations (99 overall), so 64 carriers in a
population of 256 live for about 15 generations of lexicase drift. Episodes
2–12 are dead weight in this design: 11/12 of the queue time measured
nothing about the bit.

### 2.2 Final frequency and the pre-stated contrasts

Final f per trajectory is 0 or 1, so each per-build mean is k/4 (k/2 for N)
and the contrasts are coarse. Bootstrap unit: whole libraries (24), 8,192
draws, same seed as the report.

| Quantity | Point | 95% bootstrap (libraries) | Trajectory-level Wilson 95% |
|---|---|---|---|
| L mean final f (= fixation rate) | 46/96 = 0.479 | [0.375, 0.583] | [0.382, 0.578] |
| S | 27/96 = 0.281 | [0.177, 0.385] | [0.201, 0.378] |
| Z | 29/96 = 0.302 | [0.208, 0.406] | [0.219, 0.400] |
| N | 16/48 = 0.333 | [0.208, 0.458] | [0.217, 0.475] |
| **L − S** | **0.198** | **[0.042, 0.354]** | |
| **L − Z** | **0.177** | **[0.052, 0.302]** | |
| L − N | 0.146 | [0.000, 0.302] | |
| S − Z | −0.021 | [−0.167, 0.115] | |
| S − N | −0.052 | [−0.240, 0.135] | |

Per build: L > S in 14 / 24 builds, tie in 4, L < S in 6. L > Z in 14,
tie 5, L < Z in 5 (`figs/final_f_by_build.png`). Neutral expectation for
fixation from f₀ = 0.25 is 0.25; S, Z and N are all compatible with it.

Advisory thresholds (as pre-stated; they decide nothing here):

| Rule | Threshold | Observed | Holds |
|---|---|---|---|
| (a) L − S | ≥ 0.15, lower bound > 0 | 0.198 [0.042, 0.354] | yes |
| (b) L − Z | ≥ 0.10 | 0.177 | yes |
| (c) initial / R-all cost | ≥ 1.25 | 1.33 [1.03, 1.72] | yes (interval reaches 1.03) |
| Neutral alarm | N interval excludes 0.25 | 0.333 [0.208, 0.458] | no alarm |

### 2.3 Direct selection signal per generation

The trace records, for every generation, the carrier fraction in the
population (`census_f`) and among the parents actually selected to
produce children (`recipient_f`). Their difference is the selection
differential on the bit in that generation, before drift of the children
and before elites. Over polymorphic generations only:

| Arm | pre-solve polymorphic generations | mean recipient_f − census_f (±1.96 SE, generations) | library-level bootstrap 95% | approx. s per generation* |
|---|---|---|---|---|
| L | 1,901 | +0.0104 ± 0.0031 | +0.0156 [0.0088, 0.0233] | +0.036 ± 0.024 |
| S | 2,704 | +0.0022 ± 0.0028 | +0.0013 [−0.0026, 0.0053] | +0.009 ± 0.023 |
| Z | 2,527 | +0.0020 ± 0.0023 | −0.0004 [−0.0048, 0.0041] | −0.018 ± 0.019 |
| N | 1,388 | +0.0020 ± 0.0030 | −0.0030 [−0.0117, 0.0053] | 0.000 ± 0.026 |

\* (recipient_f − census_f) / (f(1−f)), i.e. the relative advantage of
carriers among selected parents.

Only L departs from zero. The magnitude is about one percentage point of
carrier frequency per generation, or a relative advantage of about 4%,
for the ~15 generations the bit survives. Post-solve polymorphic
generations are too few to say anything (L 29, S 99, Z 12, N 5): the bit
is nearly always absorbed before, or within a few generations of, the
first exact solve.

Same thing from the episode-level deltas, restricted to episodes that
started polymorphic:

| Arm | solved episodes | pre-solve Δf per generation | post-solve Δf per generation | unsolved episodes | Δf per generation |
|---|---|---|---|---|---|
| L | 58 | +0.035 | +0.001 | 46 | +0.001 |
| S | 65 | +0.007 | −0.000 | 47 | +0.001 |
| Z | 37 | +0.008 | +0.000 | 73 | −0.000 |
| N | 16 | +0.005 | +0.002 | 41 | +0.001 |

L's rise is concentrated in the pre-solve phase of episodes that go on to
solve. In unsolved episodes L moves like the controls.

### 2.4 The revert-rate confound was matched

The proposal worried that carriers produce more clones (oversize
insertions revert to the parent) and could be favoured for robustness.
The counters show the confound exists and is matched across the three
library arms:

| Arm, pre-solve | library-draw rejection (state 1) | ordinary-donor rejection (state 1) | ordinary-donor rejection (state 0) |
|---|---|---|---|
| L | 369,807 / 947,110 = 0.390 | 0.297 | 0.308 |
| S | 234,407 / 592,562 = 0.396 | 0.297 | 0.307 |
| Z | 442,095 / 1,060,043 = 0.417 | 0.315 | 0.309 |

Post-solve all three library arms sit at 0.55–0.56 library rejection and
0.37–0.38 ordinary rejection. Carriers therefore revert about 4–5 points
more often than non-carriers in L, S and Z alike. Z, with the same extra
reverts and linked bits but random size-matched content, fixed at the
neutral rate (29/96). So the extra clones alone did not raise the bit in
this regime; whatever favoured L's carriers was associated with the R-all
content.

### 2.5 Exposure-phase solving (descriptive, confounded by absorption state)

| Arm | episodes | solved within 64 generations | share |
|---|---|---|---|
| L | 1,152 | 625 | 0.543 |
| S | 1,152 | 544 | 0.472 |
| Z | 1,152 | 420 | 0.365 |
| N | 576 | 183 | 0.318 |

This difference is mostly a consequence of fixation, not an independent
observation: stratified by carrier frequency at episode start, L and S
are indistinguishable (f₀=1: L 374/503 = 0.74, S 214/291 = 0.74; f₀=0: L
193/545 = 0.35, S 265/749 = 0.35). Z at f₀=1 solved 135/312 = 0.43 against
N at f₀=1 49/170 = 0.29, a hint that size-matched random donors are not
pure noise either; it is unresolved at this size.

## 3. Frozen readout: does the extracted law make fresh search cheaper?

All programs discarded; five global laws per build scored on the six
development cells × 2 repeats × 8 restarts of 65,536, seeds paired across
laws. The L-final and S-final laws are 0.5 × (mean final f over the
build's 4 trajectories), so per build they take values in {0, 0.125, 0.25,
0.375, 0.5}.

| Law | mean probability over builds | jobs | solved | capped mean evaluations | median | mean worker s |
|---|---|---|---|---|---|---|
| R-tree | 0 | 288 | 287 | 69,990 | 30,080 | 5.21 |
| initial | 0.125 | 288 | 288 | 43,544 | 8,448 | 3.25 |
| L-final | 0.240 | 288 | 287 | 39,561 | 6,784 | 2.98 |
| S-final | 0.141 | 288 | 286 | 56,772 | 13,184 | 4.25 |
| R-all | 0.5 | 288 | 288 | 32,704 | 4,608 | 2.46 |

Ratios of capped mean evaluations, library-level bootstrap:

| Ratio | Point | 95% |
|---|---|---|
| initial / R-all | 1.33 | [1.03, 1.72] |
| **L-final / initial** | **0.91** | **[0.71, 1.20]** |
| L-final / S-final | 0.70 | [0.57, 0.82] |
| L-final / R-all | 1.21 | [0.98, 1.46] |
| S-final / initial | 1.30 | [1.09, 1.61] |
| R-all / R-tree | 0.47 | [0.38, 0.55] |

Per cell, L-final/initial ranges 0.71–1.18 (0.71, 0.79, 0.84, 1.00, 1.18,
0.88 in the report's cell order); L-final/S-final 0.64–0.78 in all six.

**The informative view is the dose-response curve.** Pooling every readout
job by the probability it actually ran at (`figs/readout_dose_response.png`):

| probability | jobs | builds | solved | capped mean evaluations |
|---|---|---|---|---|
| 0 | 396 | 24 | 393 | 74,285 |
| 0.125 | 492 | 24 | 492 | 44,707 |
| 0.25 | 144 | 11 | 143 | 36,789 |
| 0.375 | 96 | 7 | 96 | 31,653 |
| 0.5 | 312 | 24 | 312 | 32,408 |

Cost falls steeply from 0 to 0.125 and flattens by 0.375. Two
consequences:

1. **S-final is worse than initial for a Jensen reason, not a selection
   reason.** S-final has 9 / 24 builds at probability 0 (each paying the
   74k R-tree cost) and 15 above 0.125; the convex curve makes that mixture
   cost 57k versus 44k for a uniform 0.125. The dose curve alone predicts
   51k for S-final's mixture and 39.9k for L-final's (actual 39.6k). The
   L-final/S-final ratio of 0.70 is therefore mostly "S-final lost the bit
   in more builds", which is section 2 restated, not new evidence of
   usefulness.
2. **L-final vs initial, the question the readout was built to ask, is
   unresolved**: 0.91 [0.71, 1.20]. In 7 builds L-final = initial exactly
   (same probability, same seeds); in 1 build L-final = R-tree; the other
   16 sit at 0.25–0.5. The L-final law is also not better than simply
   using R-all everywhere: 1.21 [0.98, 1.46] against R-all.

## 4. What the data show

- Under program selection alone, with no bit mutation and 64 carriers of
  256, an inherited bit that switches a program's mutation donors to the
  saved R-all library fixed in 46 / 96 trajectories, against 27 / 96 when
  the same bits were shuffled before every selection, 29 / 96 with linked
  bits and size-matched random donors, and 16 / 48 with no library at all.
  The library-level bootstrap intervals for L − S and L − Z exclude zero;
  the differences are about 0.18–0.20 on a 0–1 scale with lower bounds
  near 0.05.
- The signal is a per-generation selection differential of about one
  carrier-frequency point (relative advantage ~4%) during the pre-solve
  phase, visible only in L. It acts for a median of ~12 generations before
  the bit is fixed or lost.
- The clone/revert confound is real (carriers revert 4–5 points more often)
  and matched between L and Z; Z fixed at the neutral rate. In this probe
  the bit's advantage travelled with the R-all content, not with the extra
  reverts.
- The fresh-search dose-response of the global law is steep and convex:
  R-all at 0.5 costs 0.47× R-tree, and most of that is already bought at
  probability 0.125.

## 5. What the data do not show

- **Usefulness of the evolved frequency.** L-final / initial = 0.91 [0.71,
  1.20]. The readout cannot say whether deploying the selected frequency
  beats the starting frequency. The extracted law is a 4-coin-flip mean per
  build, so this comparison was always going to be dominated by sampling
  noise in k/4, and its headroom was small because the dose curve is flat
  above 0.125.
- **Any effect of continued exposure.** The 12-episode, cell-rotated design
  contributed nothing after episode 1 in 328 / 336 trajectories. "Does
  selection keep raising f across tasks" and "does crossover erode the
  association over time" were not observed because polymorphism never
  lasted long enough.
- **Post-solve dynamics.** 29 polymorphic post-solve generations in L and 12
  in Z; the predicted "Z rises after the solve" is untestable here.
- **Content versus robustness, fully.** Z matches the revert rate but
  carries different, possibly harmful, content (Z's own s is −0.018 ±
  0.019). L > Z says the R-all content matters; it does not say how much of
  L's advantage is the helpers themselves versus their neutrality.
- **Anything about the protected cells or transfer.** Development bank only,
  fixed saved content, no protected searches.
- **Single-population deployment.** The readout scores an aggregate law
  (mean over four trajectories), not the law one evolved population would
  carry (which is 0 or 0.5).

Plots in this folder: `figs/frequency_trajectories.png` (mean f and fixed
fraction over all 768 generations by arm), `figs/final_f_by_build.png`,
`figs/readout_dose_response.png`. The runner's own `dynamics.png` is in the
readout output folder and agrees.

## Against the predictions

The plan carries no outcome table (probe); it fixes advisory thresholds,
an interpretation rule for each, and inherits the proposal's expectations.
Outcome label: `observations`.

| Plan / proposal statement | Observed | Verdict |
|---|---|---|
| Advisory (a): L − S ≥ 0.15 with lower interval > 0 | 0.198 [0.042, 0.354] | holds |
| Advisory (b): L − Z ≥ 0.10 | 0.177 [0.052, 0.302] | holds |
| Advisory (c): initial / R-all ≥ 1.25 | 1.33 [1.03, 1.72] | holds on the point; interval reaches 1.03 |
| "Passing them motivates strategist review, not confirmation; a useful frozen L-final saving must also be inspected" | L-final / initial = 0.91 [0.71, 1.20]; L-final / R-all = 1.21 [0.98, 1.46] | the saving the plan says must be inspected is **unresolved**; the all-pass is not a usefulness result |
| Neutral alarm if N's interval excludes 0.25 | 16/48 = 0.333 [0.208, 0.458] | no alarm; bookkeeping consistent |
| Expectation: L − S about 0.05–0.10 | 0.198, interval [0.04, 0.35] covers the expected range | larger than expected on the point; not distinguishable from it |
| Expectation: benefit mostly pre-solve | per-generation differential +0.010 ± 0.003 pre-solve in L only; post-solve polymorphic generations too few (29) | consistent, as far as it is testable |
| Expectation: Z rising after the solve (robustness) | Z 29/96 fixed, neutral rate; 12 polymorphic post-solve generations in Z | not observed; untestable at this exposure length |
| Surprise: L fixing in ≥ 60% of trajectories | 46/96 = 48% | not met |
| Surprise: L below S | L above S | not met |
| Surprise: Z matching L | 0.30 vs 0.48, L − Z lower bound 0.05 | not met |
| Plan: "Matching donor sizes does not equate realized rejection … compare measured rejection by bit and solve phase" | library-draw rejection pre-solve L 0.390, S 0.396, Z 0.417; post-solve all 0.55–0.56 | realized rejection was matched to within 3 points; the confound Z was built for was present and equalised |
| Plan: 12 episodes with rotation so "each cell leads equally often"; continued exposure across tasks | 328/336 trajectories absorbed in episode 0, all by generation 136 | the exposure design was 11/12 unused; the probe measured a ~15-generation fixation race, not multi-task standing variation |
| Plan: "Failing linkage contrast leaves weak selection, drift, early allele loss or insufficient exposure unresolved" | linkage contrast did not fail, but early allele loss was universal: median absorbing generation 12 (L) to 18 (S) | drift dominates; the observed effect is the net of a ~4% relative selective advantage over ~15 generations |
| Plan: aggregate deployment rule tested, "not deploying a randomly selected evolved population" | per-build laws are k/4 × 0.5 with k ∈ {0..4}; 7 builds L-final = initial exactly | the readout's resolution on L-final vs initial was limited by this construction |

Net: the exposure observation the probe was built for (program selection
alone raises an inherited R-all bit above its shuffled and size-matched
controls) is present at a size the pre-stated advisory rule accepts, on
24 libraries. The usefulness observation the plan says must accompany it
(the evolved frequency cheapens fresh search over the starting frequency)
is unresolved, and the dose-response curve suggests little headroom
existed for it. If anything follows, it should address the absorption
time first: at f₀ = 0.25 with ~90 distinct parents per generation, the
bit is decided in about 15 generations, so 12-episode exposure and a
per-build 4-trajectory mean are the wrong instruments for both questions.
