# Do frozen tree libraries transfer to a new composition shape?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 0348](../runs/2026-10-11-0348/strategy.md). This supplies
the next direction and its complete cost envelope. The steward supplies the
proposal, sample size and decision rule; this is not an experiment registration.

**Question.** Does the unchanged DG-acquired subtree procedure reduce search
cost beyond restarted tree GP when the target requires a new combination of
predicate and output computation? The [0150 result](../runs/2026-10-11-0150/analysis.md)
establishes a large development-bank gain. It leaves transfer open. Its
homogeneous libraries and input-frequency imbalance also leave the ingredient
open, but that does not prevent testing the complete procedure as it stands.

**One bank candidate.** Keep `v2_x4`, the D625 independent inputs, primitive
semantics and 32-token capacity. Use
`(A+B)>(C+D) ? E+F : G`, where the predicate pairs partition X0–X3,
E and F are distinct readouts, and G is any readout. This combines DG's
compound predicate with a sum in one output branch: a new 19-primitive-token
canonical shape, rather than more DG seeds or another input permutation alone.
It deliberately tests recombination of familiar operations, not unfamiliar
primitives or general program synthesis.

A [read-only planning audit](../runs/2026-10-11-0348/semantic-planning-audit.json)
enumerated 144 distinct behaviours on the saved 625 inputs, none identical to
any of the 708 enumerated old DG/TS cells. All 144 meet pairwise agreement
strictly below 80%. This only establishes semantic room. It has not run the
short-program screen, verified compiled canonicals or measured search cost.

**What to build.** Reuse the reviewed `research/main` code at `d7ec100`:
`independent_input_bank.py`, `branch_sum_bank.py`, `tree_library.py`,
`tree_library_run.py` and the restart/search/reporting interfaces. These are
absent from the current `main` checkout. Generalize the bank plumbing and
reporting without changing the tree grammar or operators. No VM change,
callable abstraction engine or new acquisition algorithm is needed.

Apply the existing executable-token screen through nine tokens on D625;
retain active branches/gates, exact exclusion from the old DG/TS banks and
the below-80% separation rule. Nine-token screening does not certify
19-token minimality. Validate labels and canonicals in the reference and
Rust executors. By a performance-blind rule, select at least four development
and eight protected cells, covering all three predicate pair splits and
several output sums. Record the entire candidate roster and exclusion reasons.
The steward freezes the deterministic selection rule before search. Do not
filter targets according to learned-library matches or pilot success.

Freeze the complete method, bank and split together before any new-bank
search. Development cells may then price the unchanged method; protected cells
remain untouched by all arms, including timing runs, until confirmation.
If semantic admission fails, return the concrete obstruction to strategy;
do not silently weaken the screen or substitute TS/DG targets.

**Transfer these artifacts, unchanged.** Use every one of 0150's 24 independently
acquired libraries from the preparation output, not a subset of high-performing
builds. Reconstruct entries from source rows under the original extraction
rule, verify hashes and preserve source/failure accounting. The source roster
remains the four DG cells. No new-shape source solutions, target canonicals or
development outcomes enter a library. This tests cross-shape transfer of the
existing acquisition cohort; it does not show that the recipe learns from a
different source family. The cohort already replicates acquisition; collecting
another cohort on the same sources is unnecessary for this immediate question.

Keep the 0150 initializer, crossover, selection, donor rule and primitive cap;
keep the common eight-attempt, 65,536-evaluation restart policy and exact D625
verification. The frozen rule draws library donors for half the mutation
events; approximately 11% of all children received one on DG. Freeze the rule,
not that realized percentage, which may change on the new bank. Record insertion,
oversize rejection and fallback counts. Preserve ordinary mutation support.

**First experiment and answer.** Compare R-lib with contemporaneous R-tree on
fresh populations across the protected roster. Retain the saved size- and
compiled-length-matched donor procedure as a secondary content reference if
it fits the complete price. It is not a token-frequency control. Do not add a
hand-library matrix or optimize the extractor first. Pair evaluation seeds,
audit historical seed disjointness, retain acquisition-level uncertainty, and
report each target as well as the equal-cell aggregate.

Use arithmetic capped evaluations as the primary scientific unit, with a
reliability guard and a fixed decision-sized comparison. Measure worker time
under comparable sustained load. Useful improvement over R-tree supports
transfer of this complete externally acquired bias; improvement over only the
size control is insufficient. Tight small effects or harm limit this transfer
route. Broad intervals stay unresolved and need a priced resolution. Neither
success nor failure identifies subtree dependencies versus token supply,
establishes family specificity or demonstrates inheritance.

Report acquisition-plus-search curves in both units, including failed source
attempts and extraction. Although acquisition is sunk for this experiment,
charge it for a newly deployed library. Do not transport DG's approximately
54-search repayment to this bank, or call it the minimum possible acquisition
cost. A positive capped-cost effect with poor solving is not an unrestricted
time-to-solution result. Keep failure sensitivity and solve counts visible.

**Price and exit.** Allocate one substantive experiment, expected **5–8 h total**:
up to two hours implementation/validation, about one to three hours preparation
queue and scoring, and two to three hours proposal, reviews, analysis and
contingency. Preparation remains limited to 120 minutes; summed queue timeouts
at most four hours. These are planning allowances, not measured new-bank rates.
For scale, 0150's scoring took 52 minutes for 4,608 jobs at effective concurrency
about ten; its ordinary tree jobs averaged 8.83 worker-seconds. The extra output
computation could change the tails substantially. Measure sustained rates on
the designated development cells and price informative confirmation before
admission. A small cheap queue without decision value is not the purchase.

Return to strategy after the comparison or a measured semantic, build,
precision or full-cost obstruction. A separate probe is a fallback only if it
prices a consequential complete answer; it uses the one allocated slot,
at most 60 minutes of queue timeouts, and returns before any confirmation.
No second slot, shape sweep, source-size sweep or extractor change is allocated.
The approximately 34 hours remaining can accommodate this complete comparison,
with analysis finished before 2026-10-12T14:19:15 Europe/Stockholm.

The nearest precedent, found in this review's literature search, is
[Keijzer, Ryan and Cattolico, *Run Transferable Libraries—Learning Functional
Bias in Problem Domains* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
It transfers acquired functions between GP runs and problem sizes. Our literal
subtrees are fully expanded mutation donors; there are no dynamic function
calls or inherited decoder parameters. The paper motivates the transfer
question, not an expected effect on this bank.
