---
node: questions/01-map-bias/08-evolve-bias
title: Sum vs max families on constant thresholds — does a fitted op-frequency bias transfer to a held-out member? (sampling only, re-run of 1510 with a feasible task set)
---

**Why this now.** Run [2026-10-05-1510](../2026-10-05-1510/decision.md) built and reviewed the
experiment, but it was blocked before running. Its thresholds were unreachable by uniform
sampling: sum>10, sum>15 and max>7 had 0 hits in 95M tapes
([code_review.md](../2026-10-05-1510/code_review.md)). Thresholds equal to an alphabet
constant (1, 2, 5) are hit about once per 1M tapes. [08](../../questions/01-map-bias/08-evolve-bias/question.md)
is still untested, with budget 3 and 0 used. This proposal keeps 1510's approved design and
changes only the task set and pool sizes.

**Build on** commit `3803bca` (branch `research/2026-10-05-1510`, not merged), i.e.
`experiments/chem_tape/family_bias.py` and the Rust TAG sampler. Keep the design unchanged:
TAG alphabet, ops 0..21, L 64, exact = correct on all 10,000 lists, 64 label-balanced
training cases, per-task knockout pruning with a joint check, exact equal-weight elites,
3 starts, P(exact) validation (≥ 3× with lower bound > 1 on every fitting task),
G/N/U classification with bounds adjusted over four looks, and the verdict table where
inconclusive comes first. Only these change:

| | 1510 | now |
|---|---|---|
| Σ family (SUM, REDUCE_ADD) | fit sum>5/10/15, hold out sum>7/12 | fit **sum>1, sum>5**, hold out **sum>2** |
| M family (REDUCE_MAX) | fit max>2/5/7, hold out max>3/6 | fit **max>1, max>5**, hold out **max>2** |
| Substitute holdouts | sum>8, sum>11 / max>4, max>1 | none. An ineligible task ends the run as *infeasible task set* |
| Descriptive holdouts | — | sum>6, sum>7, max>3, max>6: scored free on every pool, reported with counts, never used in gates or verdicts |
| Calibration | 30M, may extend to 60M | **200M** uniform, one look (≈ 6 min). This gives the pruning control ~200 solvers per task |
| Fit pool per iteration | ≈ 0.83M (15M per fit) | **10M** (≈ 180M per fit), so iterations after the first have ≥ 10 elites per task |
| Decisive transfer caps | 280M total | up to **500M per arm** (uniform, Σ-fit, M-fit, prune) over the four looks. The scaler can only cut; anything cut stays U |
| Timeout | 6 h | **3 h**; expected 1–1.5 h at ~550k tapes/s |

Before the queue, the researcher runs a **5M-tape uniform probe** of sum>1 and sum>2 and
reports it in plan.md. These two were never measured. sum>1 has only 5 distinct negatives, and
the existing replacement sampling covers that. The probe confirms eligibility; it is not data.

**Interpretation** (as in 1510, but with one holdout per family and labelled that way):
- **A** (specificity G and gain G in both families): a fitted frequency bias carries
  family-specific information to an unseen member, here a threshold whose constant (2) was
  not in the fit. Next cycle would test evolution on the held-out task (A vs B).
- **C** (specificity N in both, gain G in at least one): the gain is generic supply
  (aggregators, GT, constants). Park the frequency-only version of part 2 (stop rule).
- **D** (gain N in both, validated fits): no worthwhile matched transfer. Park.
- **Mixed or inconclusive:** report as such. Inconclusive does not count as C/D. One more
  run only if the bounds were close to 3×.
- **Infeasible task set:** park 08's sampling version and hand it to the strategist. Its
  reopen condition is a richer alphabet (more constants), or an owner-approved multi-G
  design for one-ADD thresholds.

**Prior.** C. In the reviewer's emulation, mismatched fits also raised P(exact) by ≈ 3–5×.
There is also a D-flavoured risk: the fits may push CONST_1 and CONST_5 up and leave CONST_2
behind, which would lower transfer to the >2 holdout. That outcome is informative too: the fit
overfits its members' constants.

**Scope.** Two families, three members each, and one holdout, differing only in which built-in
constant is the threshold. Sampling only; evolution is untested.

**Alternatives considered.**
- *Keep 1510's thresholds and raise calibration to 3–5G.* This reaches only one-ADD
  thresholds (~1e-8). Decisive transfer pools at that rate need several G tapes per arm,
  which is more than the 8 h queue limit.
- *Make one-ADD holdouts decisive.* Same cost problem. They stay descriptive.
- *Park 08 and go to strategy now.* Premature: nothing has run, and the code is reviewed.
