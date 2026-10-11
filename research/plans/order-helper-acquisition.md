**Can the same acquisition procedure learn useful order-based helpers?**

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
selected by [strategy 1129](../runs/2026-10-11-1129/strategy.md). The steward
supplies the proposal, fixed sizes and decision rule. This is a staged research
direction, not an experiment registration. Only the first stage is allocated.

The latest [sum-prior result](../runs/2026-10-11-1019/decision.md) removes the
average practical case for TS acquisition on gate-sum B/C. It does not tell us
whether the extractor can acquire a different kind of useful expression. Test
that boundary with the existing primitives, while giving the supplied-prior
alternative knowledge of the new family too. Beating an ADD-only prior on a
deliberately non-ADD helper family would be insufficient evidence for investing
in another learner.

**Candidate bank.** Retain `v2_x4`, D625 (all four-input vectors over −2..2),
the existing tree representation and exact evaluator. Define pairwise order
helpers using ordinary GT and IF_GT:

- `lo(a,b) = Xa > Xb ? Xb : Xa`;
- `hi(a,b) = Xa > Xb ? Xa : Xb`.

These are descriptions of expanded trees, **not new primitive instructions**.
Each helper has six tree nodes and ten compiled tokens; the existing extractor
admits proper subtrees of 3–9 nodes. Candidate sources are
`lo(a,b)+Xc` and `hi(a,b)+Xc`, for unordered distinct pairs and c outside the
pair: 24 expressions. Each helper occurs in two different source specifications.
Candidate destinations are `lo(a,b)+hi(c,d)` with different unordered pairs:
30 expressions, including overlapping and disjoint pairs. Equal pairs are
excluded because min plus max equals the ordinary pair sum. Source canonicals
have 13 compiled tokens; destination canonicals have 21, inside the common
32-token cap. Canonicals validate semantics; they never seed search or extraction.

A label-only planning check in strategy 1129 enumerated these formulas on
D625: 24 distinct source behaviours, 30 distinct destination behaviours, no
source/destination identity, maximum source/destination agreement 0.60, and
maximum agreement between distinct destinations 0.52. This ran no evolution,
compiler verification, old-bank exclusion or short-program screen. It establishes
a plausible semantic candidate, not an admitted bank or measured headroom.

Build the manifest using the existing bank interfaces. Verify independently
computed labels against the recursive interpreter and production VM, including
ties and negative inputs. Reuse the bounded through-nine-token alias screen
and its declared limits; do not claim minimality of the 21-token canonical.
Check semantic overlap with all saved independent-input banks. Apply the
established 80% agreement exclusion without quietly relaxing it to admit cells.
Retain the eligible source roster by a performance-blind rule; do not select
sources by ease, solver structure or favourable learned donors. Record how
screening affects recurrence and helper coverage.

Select disjoint development and protected destination rosters by a deterministic
semantic/hash rule, with at least eight protected behaviours and both overlapping
and disjoint pair compositions represented. Freeze the rule, domain, rosters,
comparators and acquisition method together before any protected search. Source
and development searches may price the experiment; protected targets may not.
If screening cannot supply that split, report the obstacle and return to
strategy. No alternate-domain or alternate-shape search is allocated.

**Methods and bounded build.** Reuse the reviewed code on `research/main`
(latest completed study `e29219b`): `tree_gp_search.py`, `tree_library.py`,
the source/prior runners and reports, and the bank/seed/provenance checks.
These experiment runners are absent from the current `main` checkout. Inspection
confirmed that tree search already supports ADD, GT and IF_GT, stores subtree
spans and returns solver trees. No Rust or decoder engine work is required by
this candidate; that is an interface observation, not a measured build price.

Keep source search under ordinary R-tree and the existing extraction rule:
proper 3–9-node subtrees containing an indexed input, recurring across at least
two source cells, deterministic ranking, at most 16 entries. Preserve its
literal orientation convention, ordinary fallback for empty libraries and
half-library mutation-donor mix. Keep initialization, selection, crossover,
primitive accounting and the eight-attempt restart schedule unchanged. New
source rosters change total acquisition cost: do not silently preserve the old
four-cell total while calling attempts per cell unchanged. Price and freeze the
source allocation explicitly; charge unsuccessful sources and empty builds.

Carry four procedures into pricing:

1. Ordinary R-tree.
2. R-sum: the unchanged source-free constructor from 1019, a transport reference.
3. R-order: a supplied repertoire of all six pairwise lo and all six pairwise hi
   helpers, uniform over the twelve expanded expressions, used as half the
   mutation donors. Freeze one orientation convention before search. No selected
   source pairs, learned frequencies or target-specific donors enter this prior.
4. R-learned: independently acquired libraries from the new sources.

R-order deliberately supplies domain knowledge and is the strong practical
comparator. It is not task-blind. Its helper expressions fit the same primitive
cap, and it receives no complete destination programs. It prevents a mismatch
between an old sum prior and a new ordering family from masquerading as a
necessary learned advantage. Differences in repertoire size, frequencies and
insertion rejection remain bundled; this is a procedure comparison. No donor
ablation matrix, rate tuning, variable abstraction or new generator is included.

**First stage: a bounded development probe.** Use fixed seeds and at most
60 minutes of summed queue timeouts. Validate the bank and methods, collect a
small fixed set of independent pilot acquisitions, and inspect source yield,
library content, fresh-development search costs under all four procedures,
between-build variability and actual throughput. These are descriptive
observations, without an outcome table. Preserve failures; do not repeatedly
collect until the desired helper appears. Do not choose winning builds or
change extraction to recognize min/max explicitly.

The deliverable must price a substantive protected comparison, including new
independent acquisitions, all four scoring arms, failures, reporting and agent
work. Use sustained batches and measured worker utilization. A probe that only
demonstrates the compiler runs does not answer its assigned question. Return to
strategy before confirmation; do not promote pilot performance into a digest
belief. Absence of an entry in a small pilot is not proof that it cannot be learned.

**Conditional answer.** A later fixed-size comparison would ask whether acquired
libraries lower capped search cost beyond the supplied R-order prior on protected
combinations, while preserving solve reliability. Keep R-tree and R-sum visible:
they distinguish useful new acquisition from merely damaging one comparator.
Use independent acquisition builds as the learning units, paired fresh searches,
one primary cost effect with a 95% interval, and a meaningful practical increment
chosen before protected scoring. A 20% cost saving is a sizing scenario, not a
registered threshold. Report cells and overlap strata, acquisition-plus-search
curves in arithmetic evaluations and worker seconds, and a failure-charge
sensitivity. Do not infer an uncapped time-to-solution from censored searches.

A worthwhile learned increment with credible repayment would justify investing
in acquisition beyond supplied small helpers. Competitive recovery of R-order
while beating R-sum/R-tree would demonstrate automatic acquisition of useful
new content, but would not establish a practical advantage over domain knowledge
or automatically earn richer machinery. A bounded loss to R-order, ineffective
new acquisition, or helpful supplied donors with unproductive source collection
would locate a limit of this recipe. Broad uncertainty calls for a precision/cost
calculation, not a verdict of equality. No result establishes inherited map
learning, transfer to new primitives, or superiority to every supplied prior.

**Full cost and exit.** Allocate one probe slot, **4–6 h total**, including at
most 120 minutes preparation, at most one queue hour, proposal, review, analysis
and contingency. The complete candidate, including a conditional independent
confirmation, has a provisional **10–16 h total** allowance; the later **6–10 h**
is unallocated, with at most four queue hours if approved. These replace the
older 5–8 h unfamiliar-content sketch, which did not price new acquisition and
a strong new-family prior. The latest 1019 scoring took 31 minutes for 5,184
jobs, but its easy sum donors do not price ordering sources or larger donors.
The 0833 acquisition was 0.245 M evaluations per build; DG was 2.88 M. Neither
is a forecast for the larger source roster here.

Exit after the probe or a measured semantic/build/cost obstacle. At review,
feasibility alone is insufficient: require a consequential learned-versus-prior
question, credible precision and full costs that fit before
**2026-10-12T14:19:15 Europe/Stockholm**, including analysis. If source collection
is too costly, both strong procedures are uninformatively capped, or the pilot
leaves no worthwhile acquisition question, stop this candidate rather than
launching a variant sweep. An unresolved small pilot can still justify a sized
confirmation; it need not win a significance test to earn one.

The nearest precedent found during this review is [Keijzer, Ryan and Cattolico,
*Run Transferable Libraries* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf),
which transfers learned functions across runs. Our literal donors expand into
ordinary trees. A different candidate, [Ellis et al., *DreamCoder* (PLDI
2021)](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf), learns
abstractions and a search policy. This plan tests whether there is valuable new
content for the existing extractor before paying for an abstraction mechanism.
