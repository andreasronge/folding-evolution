---
node: questions/10-compositional-map-transfer/60-signed-chain-protected-reuse
title: Protected confirmation of frozen signed-gate library reuse on the hard signed-chain cells
bank: x4-signed-chain-v1 (18 protected cells, frozen with the method in 2044 and never searched; saved 1938 R-all libraries unchanged)
---
**Question.** Restarted tree GP needs a restart on 70% of jobs on this hard tier. Do the 24 unchanged
signed-gate libraries cut capped search cost on never-searched compositions here? And how many searches would
repay their acquisition? This follows [strategy 2150](strategy.md) and its
[addendum](../../plans/signed-chain-protected-reuse.md).

The development probe ([2044](../2026-10-11-2044/analysis.md)) saw R-all/R-tree **0.79 [0.60, 1.03]** on six
cells, four of them chosen in stage 0. R-gate/R-tree was 0.30. The point estimate repays acquisition in about
7 searches; the interval runs from about 3 searches to never.

**Closest known technique.** Run-transferable libraries
([Keijzer, Ryan & Cattolico 2004](https://link.springer.com/chapter/10.1007/978-3-540-24855-2_63)) carry
functions learned in one GP run into later runs and harder problem sizes. Here the map adapts by external
fitting, frozen before use, and the libraries act as mutation donors in restarted subtree GP. The mechanism is
known. This is a **boundary/replication test**: does frozen reuse survive harder linked assembly on held-out
cells? It is judged against a strong restarted baseline and a supplied repertoire.

**Design.**
- Reuse the reviewed `8a621df` engine, the frozen bank and method, and the 24 hash-verified 1938 libraries with
  their charged acquisition costs. The only new code is a `confirm` phase that releases the 18 protected cells.
- Arms and settings are as in 2044: R-tree, R-all, R-gate; P 256, mix 0.5, half-library donors, at most
  8 × 65,536 evaluations, exact D625 check.
- The unit is build × cell: 18 × 24 × **r = 4** = 1,728 paired units per arm, 5,184 jobs in all.
- Each unit's 8-seed tuple is shared across arms. Seeds come from namespace 20460000 onward, audited as
  disjoint from stage 0, 2044 and 1938.
- No pooling with the development cells. Smoke tests use development cells only.

**Feasibility, measured in 2044.**
- 1.14 jobs/s on 8 workers, 6.9 worker-seconds per job, slowest job 35 s.
- R-tree capped 5.6% of jobs; R-gate solved 288/288.
- 5,184 jobs take about **76 min central and 152 min with doubled tails**. Summed timeouts are about **207 min**,
  under the 4 h ceiling; r = 5 would exceed it.

**Full cost.** About 1–1.5 h preparation (subcommand, seed audit, smoke test), 1.5–2.5 h queue and about 1 h
review and analysis: **4–5 h** in all, within the 6 h ceiling.

**Primary comparison, fixed before any protected scoring.** The statistic is pooled capped mean evaluations,
R-all/R-tree, on the 18 protected cells. The 95% interval comes from a two-way build × cell bootstrap, with
repeats kept and arms paired.
- **Saving** if the upper bound is < 1.00.
- **Harm** if the lower bound is > 1.00.
- **Unresolved** otherwise. That means uncertain, not a limit of reuse.

**Secondary results, labels only:**
- the 20% bar: upper bound < 0.80 is a ">20% saving"; lower bound > 0.80 is "20% saving excluded";
- R-gate/R-tree and R-gate/R-all;
- solves, caps, first-attempt rate, attempt tails and worker seconds;
- needed-helper coverage strata, descriptive only;
- economics A + N·S with A ≈ 216 k evaluations per build, at N = 10 and N = 100. The repayment interval is
  unbounded if S's interval includes 0. The already-owned case is shown separately.

**Validity checks, reported first.** Expected values: R-tree first-attempt rate ≤ 85%, R-tree capped ≤ 25%,
R-gate solves ≥ 95%.
- If R-tree caps more than 25%, the primary is labelled cap-dominated.
- If R-tree mostly solves on the first attempt, the protected roster is not the hard tier.

**Forecast.** At r = 4 the expected interval width ratio is 1.53 under doubled variance (the planning anchor,
since the model under-predicted the probe's own width) and 1.35 under the central model. The probability that
the "saving" rule resolves:

| True ratio | Doubled variance | Central |
|---|---|---|
| 0.79 | about 0.6 | about 0.85 |
| 0.72 | about 0.85 | about 0.99 |

The 0.80 bar should stay unresolved near 0.79.

**Expectations.** I expect R-all/R-tree around 0.75–0.90, barely resolved or unresolved, and R-gate/R-tree
around 0.25–0.35. These would surprise me:
- resolved harm;
- protected R-tree mostly solving on the first attempt (the stage-0 cells would then have been atypically hard);
- R-all within 1.5× of R-gate;
- R-gate capping often.

**What each outcome changes.**
- **Saving:** the digest gains that frozen acquired libraries pay on harder linked assembly on unseen cells.
  That is one shape and one recipe, still about 2.6× behind supplied helpers, with repayment stated in searches.
- **Harm or a tight small effect:** stop expanding this recipe on the hard tier.
- **Unresolved:** close 60 as unresolved. No larger run is allocated.

**Next action.** Return to strategy after the analysis. The candidate it would weigh next is why acquisition
keeps only about a third of the helpers. That needs new acquisition work and is not proposed here.
