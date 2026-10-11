# Can recurrent modifier variation make inherited choice useful?

Concept plan for [root 55](../questions/55-inherited-library-choice/question.md),
funded by [strategy 1736](../runs/2026-10-11-1736/strategy.md). One substantive
experiment, followed by strategy review. The steward supplies the proposal,
fixed size and decision rule. This is not an experiment registration.

The question is whether program selection can improve a reusable variation law
when loss of its inherited selector is reversible. The [1427 probe](../runs/2026-10-11-1427/analysis.md)
observed a small carrier advantage, rapid absorption, and an unresolved frozen
gain. The corrected first-episode absorption count is 290/336. Those observations
motivate this changed procedure; they do not establish that drift alone caused
the failure or that modifier mutation will cure it.

Three changes address distinct limitations: replenish selector variation, start
below the old donor probability of 0.125, and deploy each acquisition's own law
instead of averaging several independently evolved populations before deployment.
This tests a new procedure. It does not isolate the contribution of each change.

**Bounded implementation.** Reuse `inherited_library_run.py` and
`tree_gp_search.py` on `research/main`, introduced at `f8f4246`, plus the immutable
1228 R-all libraries and their reconstruction checks. Strategy inspected the
current engine: recipient inheritance, modifier shuffling, first-hit recording
with continued exposure, separate modifier seeds and lineage traces already
exist. Mutation and per-population readout are the new paths; no evaluator,
library learner or primitive changes are needed.

Use all 24 saved libraries and the six original order development cells. The
whole order bank is now development data, including its previously protected
roster. Keep this experiment on the original six cells. Leave rectifier
protected cells untouched. Preserve P256, lexicase, crossover, expanded-tree
accounting, ordinary initialization, and the fixed R-all content and donor law.

The single candidate starts with 16 randomly assigned carriers in 256 programs,
independent of their trees: f0 = 1/16. A carrier uses the existing half-library
donor law; a noncarrier uses ordinary donors. For each nonelite child, inherit
the recipient bit, then with probability 1/32 redraw it from Bernoulli(1/16).
Use the resulting child bit for its variation law and retain it with the child,
including rejected edits. Copy elite trees and their bits together. Keep
modifier randomness separate from program search randomness.

Thus off-to-on probability is 1/512 and on-to-off is 15/512 per nonelite birth.
Ignoring selection, the expected update is
`E[f_child | f_parent] = (31/32)*f_parent + (1/32)*(1/16)`.
The mutation law is centered on the initial frequency, rather than pushing it
toward half carriers. This identity is a bookkeeping check, not a prediction
of selected populations, their diversity, or their search costs. Recurrent
mutation removes permanently absorbing states; it does not guarantee sustained
polymorphism or useful selection under lexicase. Measure those properties.

Retain one balanced, fixed exposure schedule, initially the existing twelve
64-generation episodes as the costing reference. Discard trees between episodes
but retain the modifier population; reinitialization must be independent of
bits. Preserve equal scheduled evaluations across arms, including after a solve.
Do not pick a checkpoint, reset on success, or rank modifier populations by
readout performance. Any schedule change needed for cost must be fixed before
new efficacy results; no mutation-rate or exposure sweep is allocated.

**First experiment and controls.** Compare linked inheritance (L) with the same
mutation and exposure under pre-selection bit shuffling (S), and a neutral-bit
arm (N) where both bit states use ordinary donors. N checks movement caused by
mutation, finite-population ancestry and incidental hitchhiking without the
bit changing variation. S tests persistent program–modifier association. Neither
is an exact match for every consequence of changed donor content or rejection.
Keep pre- and post-mutation frequencies separate from selected-parent frequency;
record realized transitions, monomorphic intervals, pre-solve polymorphic
generations, first solves and insertion/rejection. Extra generations count as
exposure, not independent observations.

For every independently exposed population, discard its programs and freeze
`q = 0.5 * final_f` as a global donor probability for fresh searches with its
own saved library. Score that individual law before averaging search costs
over acquisitions. Apply the same extraction and R-all deployment to L, S and
N, including N even though it never used R-all during exposure. Do not average
frequencies across trajectories first: that deploys a different method and can
hide a costly lottery of endpoints. Never select the best trajectory.

Fresh-search references are the starting law q0 = 1/32 and fixed R-all q = 0.5.
The primary question is a worthwhile capped arithmetic-cost improvement of
L-final over the starting law. S-final and N-final are essential interpretation
controls: beating a degraded control alone is insufficient, and a gain shared
by N could be mutation/endpoint-distribution effects. A useful linked increment
over those controls supports an inheritance account. Fixed R-all tests the
practical alternative of simply using the known useful law. Keep the much
cheaper supplied R-order prior visible from the existing record; do not imply
that this selector has invented its content or beaten supplied domain knowledge.

The low-probability starting law has not been measured. Do not extrapolate the
old pooled dose curve as a monotonic law: its probability groups used different
build compositions. The contemporaneous initial/R-all comparison measures the
available headroom at this fixed starting point. Insufficient headroom is an
answer about this candidate, not permission to choose a new starting point.

Choose one fixed, decision-sized primary comparison with a 95% interval and
solve counts; a 20% saving is a sizing scenario. Use saved rows to price
precision and fresh independent exposure/scoring seeds for the experiment.
Preserve library-level uncertainty and trajectories nested within each library;
more searches under one endpoint are not independent acquisitions. Shared
reference searches must not be counted repeatedly as independent data. Report
cell heterogeneity, failure charges and worker seconds alongside evaluations.

Validate inherited/mutated state alignment, elite and rejected-edit handling,
neutral transition expectations, identical-law limits, zero-mutation replay,
separate streams, equal exposure and first-hit recording. Bounded correctness
and sustained timing checks are preparation. New efficacy pilots or selecting
among rates are not: the run has exhausted its current probe allowance.

**Full cost and exit.** Allocate one full experiment, **8–10 hours total, with
a ten-hour ceiling**, including proposal, preparation/validation, reviews,
queue, analysis and contingency. One prepare remains at most 120 minutes;
summed queue timeouts at most three hours, subordinate to the complete ceiling.
Finish analysis before **2026-10-12 14:19:15 Europe/Stockholm**.

The measured 1427 anchor is 336 complete exposure trajectories in 480 seconds
and 1,440 readout searches in 533 seconds at ten workers. An illustrative
24-library × four-trajectory × three-arm exposure needs 288 trajectories;
per-population readout on six cells with two seeds and five laws gives 5,760
rows before sharing identical reference jobs. Linear scaling suggests roughly
43 minutes combined, but replenished variation and the lower starting dose may
change costs substantially. Reserve 1–3 queue hours; the rest buys the new
instrument, validation, decision-sized inference and agent work. These are
costing examples, not a sample-size justification or measured new-path rates.
Price the complete comparison before queue admission; do not run an inadequate
sample simply to fit a nominal slot.

Charge each deployed law one historical library acquisition and one modifier
trajectory, plus extraction and fresh search. Show acquisition-plus-search
costs against the starting law and fixed R-all in evaluations and worker time.
An inheritance mechanism can be informative without repaying against R-all;
that distinction must remain explicit in the continuation decision.

Return to strategy after this result, or earlier if validity, preparation,
precision or full cost cannot fit. Useful L-final improvement with the control
contrasts would justify considering transfer or a content-learning step; neither
is funded. A tight small-effect bound ends this mutation rule. Mutation-only
movement, inadequate headroom, or continued ineffective exposure ends expansion
of this candidate. Broad uncertainty needs a priced resolving comparison, not
an automatic negative or top-up. No result licenses a rate sweep, table
reassignment, new content family or second selector variant in this block.

The relevant mechanism is indirect selection of inherited strategy parameters,
as studied by [Stephens et al., *Self-adaptation in evolving systems*
(1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/), and inherited operator choice,
as studied by [Serpell and Smith (2010)](https://uwe-repository.worktribe.com/output/975827).
These papers were found in the strategy's literature search. They motivate the
mechanism, not these mutation rates or expected GP results. The library itself
remains externally acquired throughout.
