# Does the frozen semantic extractor acquire a different useful computation?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
selected by [strategy 1315](../runs/2026-10-11-1315/strategy.md). The steward
supplies the proposal, fixed sizes and decision rule. Only a development probe
is allocated; this is not an experiment registration.

The [order result](../runs/2026-10-11-1228/analysis.md) establishes useful
acquisition after removing the semantic library cap, on the bank that motivated
that change. Freeze that procedure now. The next question is whether it acquires
useful bias from different source computations and transfers to excluded
combinations, without another extractor change. This tests portability of the
acquisition recipe; it does not expect old order libraries to contain new helpers.

**One candidate.** Keep `v2_x4`, D625, the tree engine and 32-token capacity.
For each unordered pair of distinct input indices define expanded expressions:

- `pos(a,b) = (Xa+Xb)>0 ? (Xa+Xb) : 0`;
- `neg(a,b) = (Xa+Xb)>0 ? 0 : (Xa+Xb)`.

IF_GT already tests positivity, so no explicit GT node is needed. Each helper
has eight tree nodes and twelve compiled tokens, inside the existing 3–9-node
emission range. Sources are `pos/neg(a,b)+Xc`, with c outside the pair:
24 candidates, fifteen compiled tokens each. Destinations are
`pos(a,b)+neg(c,d)` for different pairs: 30 candidates, twenty-five compiled
tokens each. Equal pairs are excluded because positive plus negative part is
the original sum. Both overlapping and disjoint pairs remain. These helpers
clip a computed sum; the earlier order helpers select between input values.
The primitive inventory and outer addition are familiar, so this is a bounded
content change, not a new language or a general synthesis benchmark.

The [label-only planning audit](../runs/2026-10-11-1315/rectified-sum-planning-audit.json)
found all 24 source and 30 destination behaviours distinct, no ≥80% matches
against 906 distinct behaviours in saved independent-input banks, maximum
source/destination agreement 24.8%, and maximum distinct-destination agreement
52%. No evolutionary search ran. This is not compiler validation, a short-program
screen, measured headroom or proof of minimality.

**Bank admission and freeze.** Reuse the bounded through-nine-token semantic
screen, independent label checks, recursive interpreter and production VM.
Exclude exact short aliases and ≥80% old-bank matches; report short-program
near-aliases explicitly without silently changing that admission rule. This
follows the executed order-bank distinction between exact short aliases and
reported near-aliases, rather than the original plan's stricter wording.
Retain all eligible sources by a performance-blind rule. Confirm multiple source
opportunities for each intended helper after screening; canonical occurrence
is an opportunity, not a bound on incidental recurrence in evolved solvers.

Freeze a deterministic development/protected split with at least eight distinct
protected destinations, retaining overlapping and disjoint compositions in both
rosters where available. Freeze the bank, source effort, extractor, priors and
operator settings together before any search on this candidate. Use only source
and development cells for runtime and value assessment. No replacement shape,
domain, size-limit increase or screened-roster cherry-picking belongs to this
allocation. If admission fails, return the specific obstacle to strategy.

**Build only the bank adapter and orchestration.** Reuse the reviewed tree,
restart, bank and semantic-extraction code at `60ab766` on the research history:
`tree_gp_search.py`, `order_bank.py`, `order_library.py`, `order_cap_run.py` and
their provenance/seed checks. These runners are absent from this `main`
checkout. Inspection confirms ADD and IF_GT support and the `cap=None` path;
there is no new executor or primitive to implement.

Keep R-all unchanged: exact D625 behaviour keys, minimum observed representative,
proper subtrees containing an indexed input, recurrence across at least two
source cells, the existing minimum-representative/emission filtering order,
3–9 nodes, every eligible class, uniform donor draws. Keep the half-library
mutation mix, fallback, initializer, crossover, primitive accounting and
eight-attempt restart schedule. Generalizing the reporting-only helper census
must not change extraction. Do not simplify trees, weight helpers, relabel input
bindings, select sources by yield or train on destination outputs.

Collect new independent corpora under ordinary R-tree, with the same two jobs
per admitted source cell as 1228. Charge every failed attempt and empty build.
New sources can be substantially harder than the order sources; the old cost is
an anchor, not a forecast. Preserve every build rather than collecting until a
desired helper appears.

Price four procedures: plain R-tree; newly acquired R-all; the frozen order
R-all libraries from 1228 transported unchanged; and a supplied R-rect prior
containing all twelve expanded pos/neg helpers uniformly. The supplied prior
knows the family and is the strong practical reference. It receives no complete
destination program or free macro size. The transported library tests whether
new acquisition buys anything beyond an already available bias. It is a
procedure comparison, not an isolated content intervention or a symmetric
family-preference test. Keep its historical acquisition cost visible separately
from the deployment case where that library is already owned.

Capped R-S need not be rescored: cap removal was answered on the order bank;
the decision here is portability, not another cap comparison. A positive against
R-tree alone may still reflect generic donor supply. A useful increment over
transported R-all would make a stronger case for collecting the new sources.
Neither contrast by itself identifies the causal contribution of rectifier helpers.

**First stage and eventual answer.** One fixed-seed development probe, with
descriptive output and no outcome table. Validate the bank, acquire a modest
fixed cohort, measure all four procedures on the frozen development subset,
inspect repertoire coverage and rejection, and price a decision-sized protected
comparison. Save source failures, per-cell costs and independent-build spread.
Timing alone or a helper census alone would not answer this stage's question.
Protected cells remain unsearched, including during smoke tests.

A later confirmation should use independently rebuilt libraries and fresh
populations, one primary capped arithmetic-cost contrast with a 95% interval,
solve counts, cell/overlap strata and acquisition-plus-search costs in evaluations
and comparable worker time. The steward must choose the primary decision and
worthwhile magnitude before protected scoring. Useful improvement over R-tree
would extend automatic acquisition; improvement over transported R-all would
support the value of new acquisition; repayment against R-rect is a separate
practical claim. A large remaining supplied-prior gap must count against further
investment even if acquisition is scientifically demonstrated. Censored costs
do not estimate unlimited time to solution; D625 equivalence does not imply
equality on arbitrary inputs.

**Cost and exit.** First stage: **4–6 h total**, including preparation/validation,
proposal, reviews, analysis and contingency; one prepare of at most 120 minutes
and at most **60 minutes summed queue timeouts**. The measured order anchor is
1,152 source jobs in 40 s preparation wall time and 2,304 scoring jobs in 836 s;
neither prices the new, larger computations. Measure sustained concurrency,
full-cap tails and extraction before proposing a full queue. Return earlier if
the complete stage cannot fit, rather than dropping hard cells or failed builds.

Conditional confirmation: **6–8 further hours**, currently unallocated; the
complete candidate is **10–14 h** against about 25 h remaining. Return to
strategy after the probe with scientific value and the measured full price,
not an automatic continuation. Useful development evidence need not pass a
significance gate in a small probe, but the remaining question must be resolvable
at worthwhile cost. Widespread capping, unavailable reusable content, strong
transported/supplied alternatives, or excessive acquisition may end this candidate.
If first-attempt R-tree solves exceed roughly 90%, surface question 50's reopening
condition before considering a deployment claim; do not silently add a library gate.
Complete analysis before **2026-10-12 14:19:15 Europe/Stockholm**.

The nearest precedent found for reuse is [Keijzer, Ryan and Cattolico,
*Run Transferable Libraries—Learning Functional Bias in Problem Domains*
(2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
Our mechanism is frozen external extraction of expanded donors. A different
candidate is [Bowers et al., *Top-Down Synthesis for Library Learning*
(POPL 2023)](https://arxiv.org/abs/2211.16605): Stitch synthesizes parameterized
abstractions guided by corpus compression. This plan tests the portability of
the existing extraction procedure before paying for that representation change.
