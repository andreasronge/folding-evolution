---
estimated_minutes: 75
---

# Implementation plan, fixed before execution

Implement the approved frozen K replacement test, without acquisition, fitting,
new targets, new G4 searches, or sample-size changes. Full scoring is exactly
2,048 K searches: BE1–BE8 and PA1–PA8, all 16 then-addition-v1 selected cells,
eight paired seeds per corpus/cell. Reuse all row F C/T/G4 observations from
1548, produced by `45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a`. Population 256,
tape length 32, cap 524,288, 64 sampled training cases and exact D1331
verification remain unchanged. Search payloads contain labels, never canonical
programs. Outputs go under RUN_DIR; task notes stay in this task folder.

## Conditions and seeds

Use `then_addition_run.fresh_schedule` verbatim, replacing each C row's arm
with K. Seed = 202610081548 + 6,000,000 + (family == PA)*100,000 +
corpus_index*10,000 + cell_index*200 + seed_index (zero-based indices).
Case draws use NumPy default_rng([seed, 0]), 64 of 1,331 without replacement.
Match every K row to both saved C and T rows by corpus/cell/seed and check
their training indices. No top-up, efficacy-dependent prefix or early decision.
The full primary estimate requires all 16 corpora and 2,048 K observations.

Before any K search: verify pinned source provenance and all C/T/K table
hashes against 1246 freeze.json, then-addition bank SHA, original row F
schedule/config/freeze/search hashes, and the finite 32-position pooled C/K
marginals. Require max absolute marginal error <= 0.001 (original fit gate);
record all 16 errors and confirm the strategy's approximately 2.9e-5 maximum.
Pin historical implementation files to git object 45b2bdb and log the actual
Rust extension and Python source hashes. Run 32 C/T replay jobs in the current
worktree/build: BE1 and PA1, first seed in each of the first eight cells, both
arms. Compare every deterministic output field, excluding wall-clock timings;
any mismatch blocks admission and produces infeasible.md with correction cost.

Then time 16 full-cap K searches at the intended ten spawned workers: first
seed and first selected cell for each of the 16 corpora. This fixed feasibility
sample is not used to route the scientific decision; the full queue reruns
these seeds and checks deterministic equality. Measure worker times, wall time,
effective concurrency, solved/capped counts and evaluations. Retain both a
sample-rate projection and an all-capped projection (using measured throughput
plus the earlier approximately 1.7 h bound); a material runtime obstruction
stops preparation rather than redesigning the approved comparison.

## Measurements and interpretation

Primary C/K = exp(mean_corpus(mean_cell_seed(log(cost_K)-log(cost_C)))).
Unsolved cost is 2*cap. Produce a 95% t interval with 15 df over the 16 corpus
means; the only routing threshold is 1.20. This is an effect-size/interval
decision, with no p-value or additional confirmatory tests. Report C/T beside
C/K, K/T = exp(mean(log(cost_T)-log(cost_K))), descriptive log(K/T)/log(C/T),
K/G4 with its unpaired-baseline uncertainty limitation, solve counts, per-cell
C/K, and BE- versus PA-fitted C/K. Produce 1*cap and both-solved sensitivities;
both-solved subsets are selection-conditioned and report occupancy per corpus.
Save deterministic per-search trajectories and a diagnostic plot of exact
solve fraction, training accuracy and behavioural diversity. No bond metric
applies to this token decoder experiment. All metrics and grouping will be
emitted by the new runner/report wrapper using the existing search and t
interval routines; smoke checks will validate these before queue admission.

| Outcome | Meaning and next action |
|---|---|
| C/K lower bound >= 1.20 | This G4-based pooled-frequency replacement is insufficient within 20% on these cells. Return to strategy with the structural-learner price; useful structure remains unidentified and fragments are not established. |
| C/K upper bound <= 1.20 | This G4-based frequency map is adequate within the stated 20% bound at this capped endpoint. Prioritize acquisition of these frequencies while acknowledging supplied G4 context. |
| Interval crosses 1.20 | Representation choice unresolved. Return to strategy with the interval and approximate price of resolving it; no equality claim or top-up. |
| Validation/replay fails, or design cannot fit approved runtime | Stop before the full queue; write measured infeasible.md and a priced correction, commit code and end. |

A very weak K answers replacement sufficiency, not active-order causation.
An unusually strong K or all-solved sample triggers identity/pairing checks,
not changed thresholds. The comparison does not match positional frequencies,
solver supply or mutation neighbourhoods. This is a development-bank mechanism
follow-up, not new fresh-transfer evidence. The C/T SD 0.243 and expected
approximately x1.14 half-width are planning assumptions, not measured C/K
precision. Keep n=16 and the unresolved branch.

## Critic notes and cost

Notes 1–4 are incorporated above. Saved row F solves were C 1,771/2,048
(86.5%), T 1,547/2,048 (75.5%), G4 162/256 (63.3%). K solve rate and runtime
are unknown; T/G4 rates are projections only. K full-run estimate is 40–60 min,
about 1.7 h if all searches cap. Preparation/replay/timing allowance is 30 min;
full K queue timeout is 150 min, so their combined allowance is <=180 min
(strategy's three-hour ceiling). Log actual preparation wall time; stop if
preparation exhausts its allowance or all-capped projection exceeds admission.
Internal scoring deadline leaves reporting reserve within the queue timeout.
Total cycle remains the approved 4–4.5 h including review and analysis.

Notes 5–8 request edits to questions/logs outside the researcher's permitted
task-folder scope. Those edits are deferred explicitly to the steward: use
“no improvement resolved; gains above about 10% excluded at this scope,”
“BE gain resolved; PA unresolved,” qualify yield diagnostics as descriptive,
and mark gap closure as point-estimate arithmetic with F/R unresolved. This
implementation makes no edits to questions/, digest.md or briefs/.

## Measured preparation update (no scientific design changes)

Preparation completed in 96.62 s. All 32 C/T replay rows matched every
deterministic field; all 18 historical Python source hashes also match git
objects at 45b2bdb. Frozen maximum marginal mismatch is 2.8970847247511422e-5.
The 16 K searches solved 9/16; this small first-cell timing sample is not a
whole-bank solve-rate estimate. Mean worker time was 14.89 s, wall time 33.57 s,
effective concurrency 7.10 including the final idle tail. Direct small-block
projection is 71.61 min; conservative all-capped projection is 110.49 min,
127.06 min with the admission margin. Both fit the 150-minute queue timeout.
The frontmatter estimate is updated to 75 min from these measurements.
Full scoring uses the committed preparation artifact; its implementation and
actual extension hashes must match, and all 16 timed K rows are replayed as
part of the full 2,048-row roster. No additional replay/timing queue entries
are needed. Actual preparation plus full timeout is 151.61 min; even the
original 30-minute preparation allowance plus timeout is exactly 180 min.
