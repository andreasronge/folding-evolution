---
status: parked
tags: [compositional-transfer, tree-gp, restarts, library-learning, deployment-policy, easy-targets]
budget: {experiments: 0, used: 0}
---
# Can a library-use policy keep the B/C saving without raising cost on targets plain tree GP already solves?

Current summary: parked at opening (steward, run 2026-10-11-0833). In [49](../49-tree-library-source-portability/question.md),
frozen subtree libraries used as half the mutation donors raised mean evaluations on the eight native TS targets:
TS-built 1.78 [1.58, 2.00] and DG-built 1.33 [1.12, 1.57] of plain restarted tree GP. On the same run they cut
gate-sum B/C to 0.38. Plain R-tree solves 98.7% of the TS jobs on the first attempt in about 3 k evaluations.
All arms solved every job; the extra cost is in second-or-later attempts and the tail (p90 22 k vs 9 k).
So the complete procedure at mix 0.5 is a cost on near-solved targets, measured on one roster.

Competing explanations:
- (a) donor draws displace useful ordinary mutations on easy targets: a lower mix, or using the library only
  after a failed first attempt, would remove the harm and keep most of the B/C saving;
- (b) library content misdirects search toward sums the TS target does not need (TS is harmed more than DG,
  1.34 [1.12, 1.60], though TS libraries came from TS sources): content-dependent, not fixed by gating alone;
- (c) a cost of the restart schedule's interaction with the library, specific to this cutoff.

Scope: one native TS roster (development data), one mix (0.5), one restart schedule; observed in 49 only.

Opened 2026-10-11 (steward, run 2026-10-11-0833) as parked. Strategy 0833 asked to stop insertion-rate
sweeps, and this is a deployment-policy question, not the acquisition question root 10 is pursuing.

Related: [49](../49-tree-library-source-portability/question.md), [45](../45-tree-subtree-library/question.md)
(reopen item (ii): another insertion rate), [44](../44-restarted-tree-vs-a8/question.md),
[analysis 0833 §2.2](../../../runs/2026-10-11-0833/analysis.md), [log](log.md).

Reopen if: the strategist funds deployment of libraries by default across mixed-difficulty or mixed-family
destinations (e.g. a broader benchmark plan), where a library built for other targets would meet near-solved ones.
(The earlier trigger, any destination with R-tree first-attempt rate above about 90%, was met in run 1938 and showed
no harm from matched libraries; see the [log](log.md).) Then test a library-on-failure gate (library only from
attempt 2) against mix 0.5 and R-tree on native TS, B/C and the 1938 signed-gate cells with transported order
libraries, using saved libraries (no new acquisition).
