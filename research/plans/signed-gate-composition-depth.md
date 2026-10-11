# Can acquired conditional computations help when assembly gets harder?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
selected by [strategy 2044](../runs/2026-10-11-2044/strategy.md). The steward
supplies the proposal, seeds, sizes and decision rule. Only a development probe
is allocated. This is not an experiment registration.

The [1938 result](../runs/2026-10-11-1938/analysis.md) established useful new
acquisition on signed gates, but ordinary R-tree solved 97.7% of destinations
on its first attempt. Ask whether the acquired content helps assemble a more
demanding composition. This separates having useful parts from being able to
use them beyond the easy regime, without changing both acquisition and targets.
It can justify broader transfer work or expose an assembly/coverage limit.

Use one candidate, `x4-signed-chain-v1`, on the unchanged D625 domain and
`v2_x4` alphabet. Retain the definitions `p(a,b) = Xa>0 ? Xb : 0` and
`n(a,b) = Xa>0 ? 0 : Xb`. Destinations are
`(p(a,b) + n(b,c)) + p(c,d)` for all permutations of four distinct indices.
This requires three conditional pieces with linked input roles, versus two
disjoint pieces in 1938. It does not introduce new primitives or acquire new
content. The canonical expansion has 14 tree nodes and 20 compiled tokens,
leaving room below the existing 32-token limit. Greater length is a hypothesis
about difficulty, not a measured property of search.

The [static audit](../runs/2026-10-11-2044/gate-composition-planning-audit.json)
found 24 distinct behaviours, maximum agreement 48.8% with 1,032 distinct
saved independent-input behaviours, and 53.6% between destinations. Two
comparison-of-gates sketches were rejected by the existing 80% old-behaviour
criterion; their label checks are retained in the audit. No evolutionary
search, short-program enumeration, compiler validation or timing ran.

Build a bank adapter and scoring wrapper using the reviewed tree, signed-gate
and semantic-library code at `9da9c2c` on the research history. Inspection of
`tree_gp_search.py` and `signed_gate_bank.py` confirms the required interfaces;
no new executor is needed. Use the correctly built research extension, not an
assumed compatible extension in the main checkout.

Independently verify labels, canonical trees and random-tree execution against
the recursive interpreter and production VM, including zero conditions. Repeat
the existing through-nine-token exact-alias screen and old/pairwise 80%
agreement exclusions against all saved banks. Report short near-aliases and
the limits of that screen. Record exclusions without replacing rejected cells
with another shape. Freeze a deterministic semantic/hash split, aiming for six
development and eighteen protected cells and requiring at least eight protected
behaviours. Freeze the bank and method before any new-bank search. Protected
cells are unavailable for timing, smoke tests or selecting effort.

Reuse **all 24 saved 1938 libraries**, unchanged, with their acquisition
identities and reconstruction/hash checks. Compare R-all with ordinary R-tree
and the unchanged supplied R-gate repertoire of all 24 p/n helpers. Preserve
half-library mutation, fallback, initializer, crossover, lexicase, primitive
accounting and eight 65,536-evaluation attempts. R-gate supplies family
knowledge but no complete destination program; donors remain expanded trees.
No new sources, helper-aware extraction, input rebinding, cap increase, rate
tuning or destination-derived donors. Existing order libraries need not be
rescored: the question is deeper use of this family's acquired content.

The first experiment is a fixed-seed, descriptive development probe, with no
outcome table and at most 60 minutes of summed queue timeouts. Measure search
costs, exact solves, first-attempt rates, restart tails and worker time for all
three procedures. Record donor rejection, library coverage of the three needed
helpers and variability across builds. Coverage is descriptive; never select
helper-rich builds or cells for continuation. Price a complete protected
comparison, including uncertainty, from sustained throughput and conservative
failure scenarios. A working compiler or a helper census alone is insufficient.

At review the purchase is a consequential difficulty boundary. If R-tree still
solves almost everything on its first attempt, another modest saving does not
answer the intended question; do not rename the bank a hard tier or extend its
depth automatically. Conversely, a bank where all three procedures cap with
essentially no exact solves does not justify a large confirmation just to
reproduce the ceiling. A useful range of failures or substantial restart costs,
and an affordable comparison capable of distinguishing worthwhile savings from
small effects, can justify continuation. The probe need not show a significant
R-all win. R-gate helps distinguish a limit of acquired supply from a limit
that persists even with all helpers supplied; it does not isolate either cause.

A separately allocated confirmation would score the frozen protected roster
with fresh paired searches and one fixed primary usefulness comparison, keeping
build uncertainty, solve counts and failure charges visible. A capped-cost
saving with poor reliability is not unrestricted time-to-solution improvement.
Keep the strong prior visible and charge historical acquisition for a newly
deployed library: report `A + N*S`, arithmetic evaluations and comparable worker
time, alongside the already-owned-library case. The old 66-search repayment is
not portable to this bank. A useful protected effect would establish deeper
reuse on one new shape, not new-content acquisition, inherited learning or
transfer across families generally.

**Full price and exit.** The allocated probe is expected to take **3–4 h
complete, ceiling 5 h**, including preparation (at most 120 minutes), proposal,
reviews, queue and analysis. A conditional confirmation costs **5–7 h more**;
the complete candidate is **8–11 h expected, ceiling 12 h**, including review
between stages. Confirmation is unallocated and should have at most four hours
of summed queue timeouts, subordinate to the complete ceiling and actual
deadline. Reprice it before spending the probe allowance.

1938's full queue took six minutes, but its easy targets do not price this
study. A more conservative anchor is 1315's 384 largely capped scoring jobs in
1,151 s, with 10.8 effective workers and a maximum observed 45.6 worker-seconds
per job. A costing example of 24 builds × 6 development cells × one repeat ×
three arms is 432 jobs: roughly 33 minutes at 46 worker-seconds each and ten
effective workers, before overhead. The analogous 18-cell confirmation with
two repeats is 2,592 jobs, roughly 3.3 queue hours under that scenario. These
are arithmetic scenarios, not measured rates, worst-case bounds or adequate
sample-size claims. Do not trade away informative precision merely to fit them.

Return to strategy after the probe or an earlier semantic, build or cost
obstacle. Continue only if a useful complete answer fits the remaining time,
with analysis before **2026-10-12 14:19:15 Europe/Stockholm**. No second shape,
extractor rescue, confirmation or additional probe is automatically authorized.

The nearest precedent found in this review is [Keijzer, Ryan and Cattolico,
*Run Transferable Libraries—Learning Functional Bias in Problem Domains*
(2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
The alternative [Bowers et al., *Top-Down Synthesis for Library Learning*
(POPL 2023)](https://arxiv.org/abs/2211.16605) synthesizes parameterized corpus
abstractions. Here external extraction stays frozen: first test whether known
acquired parts buy useful harder search before building a different learner.
