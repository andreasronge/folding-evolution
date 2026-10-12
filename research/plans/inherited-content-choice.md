# Can inheritance choose useful content for a task family?

Concept plan for [root 55](../questions/55-inherited-library-choice/question.md),
funded by [strategy 0250](../runs/2026-10-12-0250/strategy.md). One substantive
experiment, then strategy review. The steward supplies the proposal, fixed size
and decision rule. This is not an experiment registration.

The question is whether program selection can acquire a useful **family-dependent
choice between two externally acquired libraries**, at a fixed library-use rate.
The previous selector changed only the dose of one supplied library. Here both
states use library donors equally often, but draw from different repertoires.
This separates selection of an available content source from inventing content.
It is a prerequisite test for richer inherited maps, not a complete inherited
library learner or a fresh-bank transfer study.

Reuse all 24 order acquisitions from 1228 and all 24 signed-gate acquisitions
from 1938. Use the six original development destinations of each bank, on the
same `v2_x4`/D625 semantics. Fix a performance-blind bijection of library builds;
the cohorts are independent, not paired ancestors. No selection of helper-rich
builds. Use `semantic_all` in the 1228 artifact and `semantic` in 1938: these
are their respective uncapped R-all entries. Freeze contents and pairings.

The [static inventory](../runs/2026-10-12-0250/content-choice-audit.json),
reproduced by its [script](../runs/2026-10-12-0250/content-choice-audit.py), verifies
every retained semantic hash with an independent array interpreter. Order
libraries average 28.7 entries, including 7.4 order helpers and no signed-gate
helpers; gate libraries average 37.4 entries, including 8.6 gate helpers and no
order helpers. This supports a content contrast, **not reciprocal efficacy or
headroom over a mixed library**. Gate libraries on order tasks remain unmeasured.

**Bounded build.** Extend `recurrent_library_run.py` and `tree_gp_search.py` on
`research/main` (1736 introduced the recurrent path at `3a18ef5`; current research
head includes `465f2fa`). The current main checkout lacks these runners. Source
inspection confirms separate modifier randomness, recipient inheritance,
recurrent redraw, continued fixed exposure, and per-population frozen readout.
The new work is a two-library donor interface and explicit two-bank orchestration.
Do not repurpose the old off state without changing its validators: it currently
means ordinary donors, and its checks require zero library draws in that state.

A bounded candidate starts with half the individuals in each state. State 0
selects the order library, state 1 the gate library; **both use it on half the
mutation events**, with ordinary donors otherwise. Retain recipient inheritance,
aligned elites and rejected-child bits. Reuse recurrent redraw at rate 1/32,
now toward Bernoulli(1/2), so mutation has no family preference. These are one
fixed candidate's settings, not a rate sweep. The bit changes future variation,
never the meaning or execution of an existing tree.

Expose independent populations separately to balanced order or gate task
sequences. The existing twelve 64-generation episodes are a costing reference.
Keep exposure fixed across arms, continue after solves, and reset programs
independently of bits between episodes. Only program fitness selects recipients;
no library score, helper reward, target identity lookup or external endpoint
selection. Record pre-solve and maintenance dynamics separately.

Keep linked (L), pre-selection shuffled (S), and neutral-bit (N) exposure.
For N, both states use the **same fixed half-order/half-gate donor mixture** at
the same total library rate. Thus its bit carries no donor information, while
search still receives library content. This differs from 1736's no-library N.
Inherited states, frozen global mixtures, and a bit-independent mixture need
not produce identical population dynamics; state that limit.

Validate legacy replay, identical-library limits, pure-library limits,
within-library normalization, bit/tree alignment, neutral redraw expectations,
per-state attempted donor rates, rejection, first-hit recording, equal exposure,
exact execution and seed separation. A fixed attempted library rate does not
fix successful insertion rates, donor sizes or useful-helper mass. Those remain
outcomes of choosing the repertoire; do not call this a pure semantic-content
intervention or tune rejection away.

**First experiment and answer.** Discard resident programs and freeze each
population's final gate fraction f. In a fresh search, draw ordinary donors with
probability 1/2, order donors with (1-f)/2, and gate donors with f/2. Normalize
within each library before mixing; concatenating unequal lists is not this law.
Deploy each population's law separately before averaging costs. The initial
reference has f=1/2, not 1736's q=1/32.

The main question is useful frozen improvement over that initial mixture, with
the exposure-family dependence retained. Score L endpoints from **both exposure
families on both destination families**. Score S and N on their corresponding
family as interpretation controls. Keep both pure-library laws as references:
one library winning on both families would favor a shared law, not reciprocal
specialization. Ordinary R-tree is a useful absolute reference if affordable;
the existing supplied R-order/R-gate results remain stronger practical benchmarks.

Use one primary cost effect with a 95% interval, separate directional results,
solve counts, and controls sufficient to distinguish useful inherited selection
from drift and a universally preferred library. A pooled interaction alone may
hide a loss in one family. A selector shift alone, or beating degraded controls
without improving the start, is insufficient. Reciprocal usefulness requires
both directions; one direction is a narrower answer. All tasks are development
data. New populations test frozen reuse, not unseen-task transfer.

The steward prices a material effect, such as a 20% saving, before confirmation;
do not inherit an obligation to resolve the old 10% label. Preserve uncertainty
over library pairs and populations nested within them, with shared references
counted once. Price precision using 1736's bimodal endpoint variation, not just
search-row CV. Neither 1736's dose curve nor the pure-library contrast forecasts
the new mixture's performance. If adequate headroom or precision is absent,
report that limitation without choosing new libraries, starts or task subsets.

**Complete cost.** Expected **8–9.5 h**, ceiling **10 h**, including proposal,
preparation/validation (at most 120 min), reviews, queue, analysis and contingency.
Summed queue timeouts at most **4 h**, subordinate to the complete ceiling and
the actual remaining deadline. Reserve at least one hour for analysis/decision
before **2026-10-12 14:19:15 Europe/Stockholm**.

Measured anchors: [1736](../runs/2026-10-11-1736/execution.md) ran 432 exposure
trajectories in 615 s and 8,640 readouts in 3,676 s, approximately ten effective
workers. Its readout means ranged from 2.21 to 5.41 worker-seconds. The 1938
development readouts used 0.28 s for gate-acquired donors and 0.56 s for transported
order donors. None measures gate donors on order tasks or the new exposure law.

An illustrative complete grid with 24 library pairs, six populations per pair
and family, three exposure arms, six cells per destination family and two scoring
seeds gives 864 exposures and 24,192 readouts: seven laws per destination family
(two L endpoints, own-family S/N, initial mixture, and two pure laws). At 1736's
aggregate rate this is about 3.2 queue hours including doubled exposure, before
new-path overhead. The easy gate family may reduce that; slower crossed donors
may increase it. This is a pricing scenario, **not a justified sample size or
runtime guarantee**. Measure sustained development timing, validate manifests,
and price all references and reporting before admitting the complete queue.

There is no unused standalone probe allowance at this review (18 full experiments,
five probes). Correctness and bounded timing are preparation for a substantive
comparison, not an efficacy pilot for choosing a winner. Return to strategy if
the decision-sized full comparison cannot fit; do not silently drop a family,
controls or frozen readout, or run merely to establish feasibility.

Charge both historical acquisitions plus one exposure trajectory to a newly
deployed selector, then report arithmetic acquisition-plus-search costs. Also
show the already-owned-library case. Fixed mixtures need both libraries but no
exposure; pure laws need only their own library. A mechanism result need not
beat an informed hand choice, but that limitation must remain explicit.

Exit to strategy after the answer or an earlier build, validity, precision or
cost obstacle. Useful family-dependent selection would justify considering an
inherited repertoire whose content can change. Failure despite usable fixed-law
headroom bounds this selector/exposure rule. Saturation of the initial mixture
would remove the need for this selector on these tasks. Broad uncertainty remains
unresolved, with no automatic top-up, rate sweep, fresh bank or new root.

The mechanisms found in this review's literature search are indirect selection
of encoded variation parameters in [Stephens et al., *Self-Adaptation in Evolving
Systems* (1997 preprint)](https://arxiv.org/abs/adap-org/9708002), and inherited
operator choice in [Serpell and Smith (2010)](https://uwe-repository.worktribe.com/output/975827).
They motivate testing inheritance; neither predicts this result or makes the
externally acquired libraries endogenous.
