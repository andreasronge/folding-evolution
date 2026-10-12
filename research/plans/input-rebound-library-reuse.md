# Can acquired computations be reused across input roles?

Concept plan under [root 10](../questions/10-compositional-map-transfer/question.md),
funded by [strategy 2353](../runs/2026-10-11-2353/strategy.md). One substantive
development experiment, then strategy review. The steward supplies the proposal,
sample size, seeds and primary decision rule. This is not an experiment registration.

The question is whether literal input bindings limit the usefulness of acquired
computations on the hard signed-chain bank. The unchanged libraries already save
search cost, but remain about three times costlier than a supplied repertoire.
This comparison chooses whether to pursue reusable expressions with variable
arguments before acquiring more literal examples or integrating an abstraction
learner. It is a bounded procedure comparison, not a fresh transfer claim.

The [saved-corpus audit](../runs/2026-10-11-2353/library-planning-audit.json)
reconstructed the semantic membership of all 24 saved 1938 libraries. Simply
allowing classes observed in one source cell raises helper coverage from 8.6 to
14.9, but raises entries from 37.4 to 113.9 and lowers the mean helper fraction
of uniform library draws from 0.230 to 0.130. The 121 inadmissible helper/build
cases have minimum observed representatives of 10–20 nodes; they are not lost
through a too-short representative. More permissive extraction is therefore
not an obviously better use of the existing source evidence.

**What to build.** Retain the original R-all extractor and all 24 saved 1938
libraries. For every entry, construct its 24 variants under all permutations
of X0, X1, X2, X3. Within a variant use the same bijection at every occurrence
of an indexed input. Keep constants, ANY, operators and tree positions unchanged.
Retain all slots, including identical variants and duplicates across entries.
Uniform drawing from this expanded list is exactly uniform original-entry
choice followed by uniform input permutation. Call this R-bind. Do not
deduplicate by syntax or behaviour: that would change the learned entry weights.

This can use the existing frozen donor-list interface without modifying the
search engine. Inspection of `tree_gp_search.py` and `order_library.py` on
`research/main` confirms uniform entry draws and ordinary expanded-tree insertion;
these modules are absent from this `main` checkout. Start from the completed
`83c7c5b` search/provenance path, not a new executor. The new work is a small donor
constructor, checks and scoring/report orchestration. Preserve old paths and
identity-permutation replay. Do not silently repair unrelated legacy test failures.

R-bind preserves each entry's function/constant labels, equality pattern among
input occurrences, shape, node count and compiled length. It changes indexed-input
frequencies and their roles. It preserves total signed-helper draw probability
on this domain, while redistributing that probability across bindings. This is
**a supplied input-symmetry prior applied to externally acquired content**.
It neither learns that symmetry nor synthesizes a missing computation type.

The planning audit found support for all 24 signed helpers in 23/24 rebound
libraries; build 5 has positive gates only and supports twelve. Keep that build.
Average helper support rises from 8.6 to 23.5 without increasing total helper
draw mass. This is support, not a prediction of useful arrival or search speed:
probability per formerly frequent binding can fall. Every non-helper entry is
rebound too, so their effects and changed input supply remain part of the procedure.

Validate provenance against saved sources/libraries and exact construction
multiplicities. Independently verify interpreter/production-VM agreement on D625
and the identity relating input renaming to permuting input columns. Check all
24 mappings, repeated input occurrences, negative values, zero, ANY and the VM's
IF_GT operand order. The planning script uses an independent array interpreter;
it is not this production validation. Check primitive-size accounting, identity
replay and seed disjointness. Retain helper counts only as diagnostics; no
destination labels, required-helper list or recipient tree may select a mapping.

**First experiment.** Compare R-bind with unchanged R-all on the complete
24-cell `x4-signed-chain-v1` roster, with contemporaneous R-tree and R-gate
references. All cells are development data now. Use all saved builds, fresh
paired search seeds and the frozen initializer, selection, crossover, half-library
mutation probability, 32-token cap and eight 65,536-evaluation attempts.
Fresh populations and seeds do not make the bank fresh. No new source searches,
recurrence/size changes, helper completion, donor weighting or recipient-aware
binding belong to this block.

The primary question is a worthwhile incremental reduction in capped arithmetic
search cost relative to R-all; merely reproducing its win over R-tree adds little.
The steward should fix one effect and 95% interval with adequate acquisition-build
and cell uncertainty before scoring. A 20% reduction is a sizing scenario, not
a registered outcome rule. Retain solve fractions, restart/cap tails, worker
seconds and the remaining R-gate gap. More helper support without lower search
cost is not success. Additional searches within a build are not new acquisitions.

Report realized donor insertion/rejection and the distributions of required-helper
draw probabilities. Use those to describe the intervention, not to select builds
or fit the conclusion after observing performance. Equal donor sizes do not
guarantee equal rejection once evolving populations diverge. A useful result
would establish this generic rebinding procedure's value, not helper-only
causality, optimal bindings, new abstraction discovery or inherited learning.

Charge the historical acquisition, including failures, once per deployed
library plus construction and verification. Saved source files avoid new
experimental collection but do not erase deployment acquisition cost. Report
`A + N*S`, with uncertainty, against R-tree and R-all at the existing 10- and
100-search horizons and retain the supplied-prior comparator. Separate evaluation
and worker-time accounting; old acquisition seconds ran under different load.

**Complete cost and exit.** Allocate one full experiment, expected **5–7 h
complete, ceiling 8 h**, including preparation, proposal, reviews, scoring,
analysis and contingency. Preparation at most 120 minutes; summed queue timeouts
at most four hours, subordinate to the complete ceiling. The measured 2150
reference means were 11.56 / 8.80 / 3.18 worker-seconds for R-tree/R-all/R-gate,
at roughly eight effective workers. An illustrative 24 builds × 24 cells ×
four repeats × four arms would need about 155 queue minutes if R-bind costs
R-all's time. The new arm's tails and expanded-list overhead are unmeasured;
price them conservatively and justify precision from saved rows before admission.
This example is neither a fixed sample size nor a promised runtime.

The run has used its current probe allowance (17 full experiments, five probes).
Bounded correctness and timing are preparation; an efficacy pilot followed by
choosing a binding variant is not funded. Return to strategy if a decision-sized
comparison cannot fit. Finish analysis before **2026-10-12 14:19:15
Europe/Stockholm**, reserving at least an hour for the final analysis/decision.

Return after the answer or an earlier validity/build/cost obstacle. A material
increment earns consideration of a frozen fresh-bank test or a richer argument
representation; neither is allocated. A bounded small effect or harm ends this
uniform-rebinding candidate, even if its helper support is complete. Broad
uncertainty remains unresolved and needs a new value-and-cost case. Do not
automatically add recurrence relaxation, learned binding weights or more depth.

The closest reuse precedent found in this review is [Keijzer, Ryan and Cattolico,
*Run Transferable Libraries—Learning Functional Bias in Problem Domains*
(2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
Parameterized reuse has a much earlier precedent in [Koza, *Hierarchical Automatic
Function Definition in Genetic Programming* (1993)](https://doi.org/10.1016/B978-0-08-094832-4.50024-6).
Our restricted input permutation keeps expanded expressions and adds no evolved
function definitions or arbitrary argument substitution. [Bowers et al.,
*Top-Down Synthesis for Library Learning* (POPL 2023)](https://arxiv.org/abs/2211.16605)
instead learns corpus abstractions for compression. R-bind tests whether a small
part of that representational direction earns its cost here; those papers do
not predict the result.
