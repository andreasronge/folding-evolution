---
node: questions/01-map-bias/08-evolve-bias
title: Does a fitted op-frequency bias help evolution on held-out sum>2 / max>2? (uniform vs matched vs mismatched vs hand-set aggregator)
---

**Why this now.** Run [2026-10-05-1558](../2026-10-05-1558/analysis.md) returned sampling
verdict A. A vector fitted on sum>1 and sum>5 (max>1 and max>5) raised held-out sum>2 (max>2)
P(exact) 4.9× (8.9×) over uniform and 4.8× (6.7×) over the other family's fit. Its plan
pre-registered the next step for A: test evolution on the holdouts. That separates A (the bias
helps search) from B (it changes supply, not success; item 12 predicts B). 08 has 2
experiments left, and this uses 1.

**What runs.** Use the TAG-alphabet chem-tape evolution (`evolve.py`, which draws initial
genomes and mutations from `op_probs`). Two tasks: sum>2 and max>2 on length-4 lists over
[0,9], with 64 label-balanced training cases. A run is *solved* when an individual is exact on
all 10,000 lists, checked whenever a candidate is perfect on the training cases. Four arms per
task, with vectors frozen from 1558's `result.json` (`vectors`):

| Arm | Vector |
|---|---|
| uniform | 1/22 each |
| matched | the selected fit for the task's family (Σ start 1, M start 0) |
| mismatched | the other family's selected fit |
| hand-set | uniform, except INPUT, GT and the family's aggregator ops (SUM + REDUCE_ADD, or REDUCE_MAX) set to the matched fit's folds; renormalised. Constants stay uniform |

- **Sampling check first** (pre-registered prediction). 125M tapes for each hand-set vector
  with the 1558 sampler (~4 min each). The post-hoc four-fold product model predicts about 13×
  (sum>2) and 25× (max>2) over uniform. Report the observed fold against that prediction. This
  is descriptive and does not gate the evolution.
- **Evolution.** 50 seeds per cell (8 cells, 400 runs), with the same seed list across arms.
  Use the standard tagged setup (lexicase, crossover v2, mutation 0.015, L 64) unless the
  researcher finds a reason not to. Before the queue, a small uniform-only pilot picks the
  population and generation cap so that uniform solves roughly 30–60% of runs on each task. If
  uniform solves ≥ 90% even at tiny budgets, the primary metric becomes generations-to-solve.
  Expected well under 2 h of queue; cap 4 h.
- **Primary measures:** solve rate at the cap (matched vs uniform, matched vs mismatched,
  hand-set vs matched), and generations to first exact solve (censored at the cap). The plan
  fixes the tests and the margins for "no difference".
- **Free baseline:** random search with the same evaluation budget, computed as
  1 − (1 − p)^N from each arm's sampling P(exact). This shows whether evolution beats sampling
  under each bias, which links to §28 ("evolution is mostly a worse sampler").

**What each outcome means.**
- **A** (matched beats uniform and mismatched in both families): the fitted bias helps search,
  not just supply. If hand-set ≥ matched, record this as **A'**: "yes, through one op weight".
  Then close 08 as answered and hand any heritable-bias follow-up to the strategist.
- **B** (matched ≈ uniform on both measures, despite 5–9× supply): frequency bias matters to
  sampling, not to search on these tasks. Park the frequency-only version of 08, as item 12
  would predict.
- **Partial** (one family only), or matched beats uniform but not mismatched: report it as
  such. It would most likely mean generic speed-up, not family transfer.
- **Ceiling or inconclusive** (both arms near 100%, or wide intervals): this says nothing about
  A vs B. Do not spend the last budget slot re-running; go to strategy.

**Prior.** Mildly A on speed, B on solve rate if the cap is generous. These tasks are easy, so
a 5–9× supply lift most plausibly shows up as earlier arrival. I expect hand-set ≥ matched (A'),
because the fitted vectors suppress CONST_2.

**Scope.** Two holdouts that differ from their fit members only in a constant. There is one
fitted vector per family (M has a single trajectory), and the alphabet is TAG. Nothing about
heritable or co-evolving bias.

**Alternatives considered.**
- *A second M fit trajectory, or a harder fit to see whether CONST_2 suppression reaches D.*
  Either would refine the sampling result but decide nothing for 08.
- *Evolution without the hand-set arm.* This is cheaper by a quarter, but a fitted-vector win
  could not be told apart from "knowing the aggregator helps".
- *`next: strategy` now.* Premature: this is the pre-registered next step and it is cheap.
