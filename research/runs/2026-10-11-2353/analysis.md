---
outcome: unresolved
---
# Analysis: 2026-10-11-2353 — consistent input rebinding (R-bind) vs the literal saved libraries (R-all)

Reviewer: Claude Fable 5.1, independent of the researcher. All numbers below were recomputed from
`score.jsonl` with [reanalysis.py](reanalysis.py) (output [reanalysis.json](reanalysis.json)) using my own
bootstrap seed; they agree with the run's `report.json` to the third decimal. Code: commit `465f2fa`.
Raw data: `experiments/output/2026-10-12/2026-10-11-2353-{prepare,score}/`.

## 1. Data completeness

| check | result |
|---|---|
| queue entries | 2/2 done, exit 0 (prepare 113 s, score 8,166 s wall; summed timeouts 13,800 s) |
| rows in `score.jsonl` | 8,064 = 3,456 R-all + 3,456 R-bind + 576 R-tree + 576 R-gate |
| grid | 24 builds × 24 cells × 6 repeats for both library arms; 24 × 24 × repeat 0 for both references; 0 missing, 0 extra, 0 duplicate (build, cell, repeat, arm) keys |
| seeds | 27,648 distinct attempt seeds, range 20481000–20508647, exactly one seed tuple per (build, cell, repeat) unit and shared across arms only within the unit; 0 overlap with the 32 smoke seeds |
| accounting | 0 rows where attempts do not sum to `evaluations`, where an unsolved row is not at the 524,288 cap, or where `solved` disagrees with `solver` |
| failures / errors | 0 |
| smoke rows | excluded (separate folder, timing only) |

Preparation replayed the frozen `83c7c5b` engine and 24 archived libraries, verified all 21,528 rebound
slots (1,708 unique forms) against the production VM and against column permutation of D625, and confirmed
roster-averaged needed-helper draw mass equal between R-all and R-bind per build (both 0.0283 averaged over
the 576 units). The identity replay and seed audit passed. Nothing is missing; the grid is exactly the
approved one.

Validity flags (pre-registered, checked before the primary):

| flag | value | threshold | pass |
|---|---|---|---|
| R-tree first-attempt rate | 158/576 = 27.4% | ≤ 85% | yes |
| R-tree capped share | 42/576 = 7.3% | ≤ 25% | yes |
| R-gate solves | 576/576 = 100% | ≥ 95% | yes |
| R-all/R-tree (repeat-0 paired) | 0.791 [0.650, 0.968] | within [0.6, 1.0] | yes (2150 gave 0.778) |

The tier is hard, caps do not dominate, the supplied reference is reliable, and R-all behaves as it did
in 2150. Interpretation is supported.

## 2. Primary result

**R-bind/R-all, pooled capped mean evaluations over 24 × 24 units (repeats averaged within units), paired
crossed build × cell bootstrap:**

| | point | 95% interval | log half-width |
|---|---|---|---|
| R-bind/R-all (r = 6, 3,456 vs 3,456 jobs) | **0.853** | **[0.785, 0.927]** | 0.084 |

Decision rule (pre-registered precedence): material gain needs upper < 0.90 (0.927, no); harm needs lower
> 1.00 (no); small/none needs lower > 0.85 (0.785, no). **Outcome: unresolved.** A saving above 10% is not
established and a saving above 15% is not excluded. The log half-width (0.084) is exactly in the proposal's
forecast band (0.08–0.09), so the run delivered its planned precision; the point estimate simply landed
inside the 0.85–0.90 gap where the rule cannot decide.

The point estimate is robust to how the cost is summarised, so this is not a tail artefact:

| summary | R-bind/R-all |
|---|---|
| ratio of pooled arithmetic means (primary) | 0.853 |
| geometric mean of the 576 unit ratios | 0.856 |
| ratio of medians (75,648 / 85,760) | 0.882 |
| repeat-0 rows only (576 vs 576) | 0.840 [0.701, 1.008] |
| units where R-bind's mean is lower | 354/576 (61%) |

Arm summaries (denominators are jobs):

| arm | jobs | solves | capped | first-attempt solves | mean evals | median | p95 | worker s/job |
|---|---|---|---|---|---|---|---|---|
| R-tree | 576 | 534 (92.7%) | 42 (7.3%) | 158 (27.4%) | 175,477 | 134,656 | 524,288 | 11.34 |
| R-all | 3,456 | 3,316 (95.9%) | 140 (4.1%) | 1,225 (35.4%) | 139,725 | 85,760 | 476,224 | 8.84 |
| R-bind | 3,456 | 3,375 (97.7%) | 81 (2.3%) | 1,403 (40.6%) | 119,222 | 75,648 | 402,944 | 7.59 |
| R-gate | 576 | 576 (100%) | 0 | 375 (65.1%) | 46,996 | 16,640 | 198,400 | 3.16 |

R-bind solves more (59 more solves, 59 fewer caps out of 3,456) and shifts the whole attempt distribution
left (1,403 vs 1,225 first-attempt solves; 127 vs 210 eight-attempt jobs). Worker seconds track
evaluations (ratio 0.858 [0.790, 0.934]); the rebound list of about 900 donor slots costs nothing extra
per evaluation.

## 3. Secondary contrasts (labelled, repeat-0 pairing for references)

| contrast | pairing | point | 95% interval |
|---|---|---|---|
| R-bind/R-tree | repeat 0 (576 vs 576) | 0.664 | [0.545, 0.801] |
| R-bind (all 6 repeats)/R-tree (repeat 0) | mixed, descriptive | 0.679 | [0.586, 0.797] |
| R-all/R-tree | repeat 0 | 0.791 | [0.650, 0.968] |
| R-gate/R-bind | repeat 0 | 0.403 | [0.317, 0.510] |
| R-gate/R-all | repeat 0 | 0.339 | [0.271, 0.422] |

The rebound library is clearly cheaper than tree search (upper bound 0.80, versus R-all's upper bound 0.97
on the same seeds). The supplied repertoire is still about 2.5× cheaper than R-bind; R-bind does not
approach R-gate.

Economics (`A + N·S`, A = 215,520 historical acquisition evaluations charged once to both library arms):

| N | R-bind/R-all | R-bind/R-tree | R-all/R-tree |
|---|---|---|---|
| 10 | 0.873 [0.813, 0.939] | 0.787 [0.661, 0.932] | 0.914 [0.763, 1.099] |
| 100 | 0.855 [0.789, 0.930] | 0.676 [0.558, 0.813] | 0.803 [0.661, 0.979] |

At ten searches R-bind already repays its acquisition against R-tree (upper 0.93); R-all does not.

## 4. Where the saving comes from: R-all coverage strata (descriptive, pre-registered as a label)

Units are stratified by how many of the cell's three needed helper types the literal R-all library holds
with the right inputs. R-bind holds all three in 552/576 units and two in the 24 units of build 5 (no
negative gates). Intervals are a plain unit bootstrap and the strata are confounded with cell and build
difficulty, so this is a pattern, not a test.

| needed helpers in R-all | units | jobs/arm | R-all mean | R-bind mean | R-bind/R-all | unit-boot 95% | R-all solves | R-bind solves |
|---|---|---|---|---|---|---|---|---|
| 0 | 144 | 864 | 180,634 | 125,523 | **0.695** | [0.637, 0.758] | 792 (91.7%) | 841 (97.3%) |
| 1 | 275 | 1,650 | 139,998 | 121,952 | 0.871 | [0.815, 0.930] | 1,592 (96.5%) | 1,606 (97.3%) |
| 2 | 138 | 828 | 104,770 | 110,032 | 1.050 | [0.937, 1.171] | 819 (98.9%) | 814 (98.3%) |
| 3 | 19 | 114 | 79,612 | 98,697 | 1.240 | [0.981, 1.609] | 113 (99.1%) | 114 (100%) |

Mean needed-helper draw probability per library draw by stratum: R-all 0 / 0.027 / 0.053 / 0.081; R-bind
0.027 / 0.028 / 0.030 / 0.035; R-gate 0.125 throughout.

Two things stand out ([ratios.png](ratios.png), panel a):

- **R-bind's cost is nearly flat across strata** (126k → 122k → 110k → 99k) while R-all's falls steeply
  (181k → 80k). The strata are defined by R-all's content, and R-bind's content does not change with them,
  so this is the expected shape if literal helper coverage drives R-all's cost and rebinding equalises it.
- **The gradient survives build and cell fixed effects.** Regressing the unit log ratio on the stratum
  count with 23 build and 23 cell dummies gives a slope of +0.26 per needed helper (se 0.04; raw slope
  +0.22). So the pattern is not just "stratum 3 units are easy cells". Where R-all already held two or
  three needed helpers, spreading their mass over 24 bindings (dose per needed helper falls from 1/slots
  to roughly 1/(3·slots)) costs R-bind something; where R-all held none, reach wins by about 30%.

This is exactly the "gain concentrated at stratum 0, small loss possible at 2–3" shape the proposal
expected. It is consistent with a dose–reach trade-off, but it is also consistent with any other
difference between rebound and literal lists that correlates with coverage (the non-helper entries are
rebound too), so I would not promote the mechanism, only the pattern.

## 5. Per build and per cell

Per-build ratios (24 cells × 6 repeats each) range 0.73–1.03; 20/24 builds are below 0.90 and 3 (builds
4, 14, 20) are at or just above 1.0. Per-cell ratios (24 builds × 6 repeats each) range 0.65–1.25; 20/24
cells are below 1.0 and one cell, `p23+n31+p10`, is at 1.25 ([ratios.png](ratios.png), panels b and c).
The correlation between a build's helper share of slots and its log ratio is weak (−0.24, n = 24). Nothing
singles out a build or cell as driving the pooled result.

## 6. What would it take to resolve?

Decomposing the unit-level log ratio (shared seeds, 6 repeats): within-unit seed variance 3.45 per
repeat pair, variance of unit means 0.61, of which seed noise contributes 3.45/6 = 0.58. The persistent
build × cell heterogeneity is therefore small (about 0.04); roughly 94% of the interval width is seed
noise and more repeats would shrink it close to 1/√r. Doubling to r = 12 would give a log half-width of
about 0.06; at the observed 0.853 the upper bound would be about 0.905, still a coin flip for "material".
Resolving a true 0.85 against the 0.90 threshold needs a half-width below about 0.055, roughly r ≥ 14
(about 3.5× this queue's library jobs, 6–7 h). That is the steward's call; the data say the saving is
most likely 12–18%, centred on the gap between the two pre-registered labels.

## 7. What the data show and do not show

Shown:

- Uniform input rebinding of the saved libraries, without dedup and with original weights, costs
  0.85 [0.79, 0.93] of the literal library on the 24 development cells, with more solves and fewer caps.
  Harm is excluded (upper bound 0.93); a saving above 10% is not established.
- R-bind is clearly cheaper than R-tree (0.66 [0.55, 0.80]) and repays acquisition within ten searches;
  R-all alone did not resolve that against R-tree on these seeds (0.79 [0.65, 0.97]).
- R-gate stays about 2.5× cheaper than R-bind (0.40 [0.32, 0.51]); rebinding does not close the gap to
  the supplied repertoire.
- The saving is concentrated where the literal library had no needed helper (0.69) and vanishes or
  reverses where it had two or three (1.05, 1.24); the gradient survives build and cell fixed effects.

Not shown:

- Whether the pooled saving is above or below 10–15%; the primary is unresolved by the pre-registered
  rule and unresolved is not equality.
- Why the stratum gradient exists: strata are R-all-defined and confounded; no per-entry causal test was
  run, and the non-helper entries were rebound too.
- Anything about transfer: all 24 cells are development cells and the libraries were built on them.
- Anything about the never-built helper types (the R-gate gap): R-bind supplies all 24 bindings in 23/24
  builds, so missing bindings do not explain the remaining 2.5× gap; something else (weights, non-helper
  dilution, half-library draw rule) does, and this experiment cannot say what.

## Against the predictions

Read after the analysis above was written. The plan's labels are material gain (upper < 0.90),
small/none/harm (lower > 0.85, harm if lower > 1.00) and unresolved; the plan says every outcome returns to
strategy with no automatic top-up.

| plan item | predicted / required | observed | verdict |
|---|---|---|---|
| Grid | 24 × 24 × 6 × 2 library arms + 24 × 24 references = 8,064 jobs, seeds 20481000–20508647, r = 6 by the timing rule | exactly that; r = 6 | met |
| Validity flags | R-tree first-attempt ≤ 85%, caps ≤ 25%, R-gate solves ≥ 95%, R-all/R-tree in [0.6, 1.0] | 27.4%, 7.3%, 100%, 0.791 | all pass; interpretation supported |
| Queue time | ~145 min search + preparation, 230 min timeouts | 136 min search + 2 min preparation | met |
| Precision | log half-width 0.08–0.09 forecast (reviewer expected 0.09–0.11) | 0.084 | met; the forecast held |
| Primary label | proposal expected material gain, ratio 0.70–0.90 | 0.853 [0.785, 0.927] | **unresolved**: inside the expected range, but the interval straddles 0.90 |
| Threshold facts | report both | saving > 10% established: no; saving > 15% excluded: no; harm: no | reported |
| Stratum shape | gain concentrated at stratum 0, small loss possible at 2–3 | 0.69 / 0.87 / 1.05 / 1.24 across strata 0–3; gradient survives build and cell fixed effects | matches the expectation; descriptive only, as the plan requires |
| R-gate reference | still ≥ 1.5× cheaper than R-bind | 2.5× (R-gate/R-bind 0.40 [0.32, 0.51]) | met; R-bind does not reach R-gate |
| Listed surprises | R-bind reaching R-gate; resolved harm; stratum-0 loss | none occurred | no surprise |
| Economics | A + N·S at N = 10, 100, per-build historical charges | R-bind/R-all 0.87 [0.81, 0.94] and 0.86 [0.79, 0.93] | reported; R-bind repays against R-tree at N = 10 (0.79 [0.66, 0.93]) |

The plan's meaning for this outcome: "a broad interval spanning useful saving and little benefit remains
unresolved, without equality/bottleneck claims or automatic top-up"; return to strategy. The result is not
broad in the sense of a failed design (precision was as forecast); the true ratio simply appears to sit
near 0.85, where the registered rule has no label. Two points for the steward:

1. The direction is consistent across summaries (61% of units, more solves, fewer caps, every stratum
   except 2–3) and harm is excluded, so "uniform rebinding does nothing" is not a reading the data
   support. Equally, a saving above 10% is not established, and the proposal's "material gain points to a
   fresh-bank test or an argument representation" routing is not earned by this run.
2. Because about 94% of the interval width is seed noise, a top-up could resolve the label, but at the
   observed ratio it needs roughly r ≥ 14 (about 6–7 h more queue) to reach an upper bound under 0.90,
   and would still fail if the true ratio is above about 0.86. The stratum gradient suggests the more
   informative next step may be a design that separates dose from reach (for example rebinding only the
   non-helper entries, or rebinding with helper mass preserved) rather than more seeds on the same
   contrast. That is a proposal question, not something this analysis decides.
