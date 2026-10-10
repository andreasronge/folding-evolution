# Does acquired bias still pay against restarted tree search?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 0024](../runs/2026-10-11-0024/strategy.md). The steward
supplies the proposal, fixed size and primary decision rule. This is not an
experiment registration.

The next question is whether a fixed, acquisition-free restart procedure removes
enough of tree GP's DG failure cost to change the decision to acquire A8. The
previous comparison answered geometric cost but left A8 with better reliability
and positive arithmetic savings. That remaining value deserves a direct test
before either expanding A8 to another bank or building learning into tree GP.

The mechanistic alternative is repeated independent discovery, with no learned
program distribution. [Luby, Sinclair and Zuckerman, *Optimal Speedup of Las Vegas
Algorithms* (1993)](https://www.cs.utexas.edu/~diz/pubs/speedup.pdf) analyzes
restart schedules for randomized algorithms. This motivates the candidate; its
theory does not establish our empirical cost or a universal optimum at a finite
GP budget. A fixed cutoff here is not an implementation of their universal
sequence.

**Evidence and scope.** In [2254](../runs/2026-10-10-2254/analysis.md), tree GP
solved 179/384 DG searches by 65,536 evaluations and only another 23 before the
524,288 cap. A8 kept making later discoveries. The strategist's
[saved-data audit](../runs/2026-10-11-0024/planning-audit.json) projects eight
independent attempts of at most 65,536 evaluations each, stopping at an exact
solve. It estimates each cell separately, then weights the eight cells equally.
The DG projection is about 87,314 evaluations and 98.97% solving, versus observed
single-run means of 263,353 for tree GP and 177,639 for A8. These are post hoc
empirical projections without uncertainty or restart overhead, not observed
restarted performance. They justify pricing a comparison, not updating beliefs.

**Bounded build.** Reuse `tree_gp_search.py`, `tree_gp_run.py`, the reporting
and validation machinery at `c32ff04` on the research branch. These files are
absent from the current `main` checkout. Source inspection confirms that the
search accepts a population-aligned evaluation cap and returns exact first-hit
costs. Add a narrow scheduling wrapper; preserve the grammar, 32-token size
limit, initialization, frozen crossover mix, selection and subtree operators.
Do not add size control, a larger representation, learned objects or a cutoff
grid to this experiment.

The concrete candidate is the 65,536-evaluation cutoff already suggested by
2254, with total budget 524,288. Reset the entire population, verifier cache and
randomness at each restart. Draw fresh training cases as the existing search
does from each independent seed; retain exhaustive D625 verification. Thus this
tests the complete restart procedure, including renewed training samples, not
population reset alone or a causal diagnosis of bloat. Stop the aggregate job
on its first exact solve. Count all unsuccessful attempts, initialization,
verification and scheduling overhead; never give eight full-cap attempts.

Validate first-attempt solves, later solves, complete failures, cumulative
evaluation accounting and deterministic replay. The first attempt must reproduce
the corresponding ordinary capped search. A restart seed namespace must be
disjoint from calibration, acquisitions, old scoring and every other aggregate
job; publish the actual sets and check intersections, not just distant-looking
base constants. Common cases or seeds between methods do not imply identical
random choices across representations.

**First and only allocated experiment.** Compare restarted tree GP with the
unchanged full-cap native A8 procedure on all eight DG target cells from 2254.
Keep all 24 native acquisition builds, with fresh evaluation seeds. Retain the
eight TS cells as a separately reported boundary: a pooled result must not hide
loss on either family. Both banks are development data. No fresh-bank or
new-family claim is available, even though these evaluation seeds are new.

Use ordinary full-cap tree GP as a reference for the restart effect. Its saved
rows can inform or supply a labelled historical reference after provenance and
replay checks; price contemporaneous rows if a paired causal comparison needs
them. Do not manufacture independent replications by recycling the same baseline
rows under multiple build labels. The unit of restarted-search evidence is the
complete scheduled job, not each sub-attempt. Preserve A8 acquisition uncertainty,
cell differences and independent scoring uncertainty.

Prioritize **arithmetic cost and reliability at the same total cap**, because
those are the remaining reasons to buy A8. The steward should set one primary
cost contrast with a 95% interval and a decision-relevant reliability condition
before new scoring. About a 1.5-fold cost change is a useful sizing scenario,
not a promised effect. Show per-cell solve probabilities, full solve-cost curves
and the earlier geometric/penalty sensitivity as supporting results. Lower cost
caused by more failures is not an efficiency success. Capped expenditure is not
unlimited expected time to solution. This compares the frozen A8 recipe with one
new restart policy; it does not find the optimal policy for either representation.

Charge each deployed A8 build its complete historical acquisition once, including
failed sources and intermediate/final fits. Report arithmetic `A + N*S` curves
and uncertainty in evaluations; show measured worker time separately under
comparable sustained load. There is no assumed owner reuse horizon. Historical
acquisition timing remains historical, and no positive mean saving means no
demonstrated repayment. Benchmark-development effort is distinct from per-build
acquisition for both procedures.

**Full price and exit.** One substantive experiment through the next strategy
review, **4–6 hours total** for proposal, implementation, validation, calibration,
queue, review, analysis and contingency. Aim for **1–2 queue hours**, with at
most **3 hours summed queue timeouts** and **120 minutes preparation**. The
measured anchor is 2254: 1,792 scoring searches plus preparation completed in
48 minutes; full-cap tree searches cost about 50 worker-seconds. Restarted jobs
are unmeasured, particularly repeated initialization and verification. Time
representative sustained batches, and use the saved per-cell variation to price
a decision-sized comparison before admitting the queue. Leave analysis time
before the run deadline, 2026-10-12T14:19:15 Europe/Stockholm.

Return to strategy after the result, or a measured validity, precision, build or
complete-cost obstacle. A useful restart advantage would replace plain tree GP
as the practical comparator for future learning. Failure to remove A8's useful
reliability/economic advantage preserves that narrow reason to acquire it.
Broad uncertainty needs a resolution price; a cutoff sweep is not an automatic
continuation. Neither outcome erases learned family dependence within tape
search or proves that learning cannot improve structural search. The separate
[tree-native learning plan](tree-native-fragment-learning.md) remains unallocated.
