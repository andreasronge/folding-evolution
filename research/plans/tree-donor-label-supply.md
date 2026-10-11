# Does learned label supply add value once donor shapes are retained?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 0652](../runs/2026-10-11-0652/strategy.md). This is a direction,
not an experiment registration. The steward supplies the fixed comparison, size
and decision rule.

**Question and decision value.** On gate-sum's predicate-unmatched B/C splits,
does replacing the learned label law with a uniform compatible-label law lose a
useful amount of performance? Keep the acquired arity skeletons, node widths,
entry sizes and library multiplicities. The answer determines whether the next
statistical acquisition candidate needs label information as well as shapes.
It does not answer whether acquisition is needed at all.

[0524](../runs/2026-10-11-0524/analysis.md) found R-perm/R-lib cost
1.031 [0.854, 1.225] on B/C, while R-perm/R-tree was 0.360 [0.299, 0.429].
The permutation preserved learned label counts, removed most learned predicates,
and increased useful B/C pair supply. Therefore neither a token-only mechanism
nor absence of useful learned information follows. The old R-size control also
changed input supply and shape; it cannot answer this replacement question.

**Bounded build.** Extend the reviewed `research/main` implementation at
`7c0e5df`: `tree_permutation.py`, `tree_permutation_run.py`, `tree_gp_search.py`
and the saved 0150 acquisitions. These modules are not in the current `main`
checkout. Reuse the tree parser, compiler, provenance, frozen bank, seed audits,
restart wrapper and reporting. No new source search, execution engine or learner
is needed in this block.

Construct a fixed uniform-label donor library from each acquired library's
ordered arity skeletons and per-node compiled widths. Define compatible labels
from the **whole existing tree grammar**, not the labels that happened to occur
in that source library. In the reviewed grammar, binary nodes admit ADD and GT;
two-token terminals include X0–X3 **and ANY**; one-token terminals are constants;
IF_GT is the sole ternary label. Uniformity within these classes does not mean
uniformity over all programs, or equal input supply to the learned library.
Retaining widths also retains substantial information about terminal kinds.

A simple candidate is independent uniform relabelling within each compatible
class, frozen into a small number of independent realizations per acquisition.
The steward must specify the construction law before scoring. If this law is
compared with 0524's without-replacement permutations, their finite-library
dependencies differ as well as their counts: call it a **replacement of label
supply**, not a pure causal effect of primitive frequencies. A matched finite-pool
construction is an alternative only if its law and scope remain simple. Do not
condition on absence/presence of target motifs, deduplicate, or reject constant
behaviours to make the new control look useful. Preserve multiplicities and
ordinary-donor fallback. Do not silently exclude ANY to preserve indexed inputs;
that would be an additional supplied prior requiring its own justification.

Validate parsing, exact skeleton/width/size invariants and independent
interpreter/compiler/Rust agreement on D625. Audit emitted label counts,
input-bearing entries, behaviours, pair sums and predicates by split; these
are descriptions, not criteria for selecting constructions. Keep construction
randomness separate from search randomness and preserve ordinary-path replay.
Several realizations estimate construction uncertainty; they do not create
additional independent acquisitions.

**First experiment.** Use all twelve B/C cells, equally weighted, as development
data. Compare uniform-label donors with the count-preserving R-perm procedure;
retain ordinary R-tree for absolute usefulness and intact R-lib as the
acquisition reference. Contemporaneous references are preferable; reuse old
rows only with justified pairing and exact replay. Price the complete comparison
before choosing between them. Split A's arrangement-specific advantage has
already been established and need not buy another full scoring matrix.

Hold the initializer, population, lexicase, verifier, primitive capacity, donor
draw probability, ordinary mutation route and eight-attempt restart schedule
fixed. Report realized insertion and rejection rates instead of matching them
after populations diverge. No size, insertion-rate, restart or cap sweep.

Use one primary arithmetic capped-cost replacement contrast with a 95% interval,
an explicit worthwhile loss/retention margin and fixed size. Preserve acquisition
and construction uncertainty, solve fractions, per-split results and worker
seconds. A nonsignificant difference is not retention. A retained ratio between
two ineffective procedures is not useful retention; keep the R-tree comparison
visible. Before scoring, decide how the intact reference constrains a claim that
the simpler procedure retains the acquired benefit.

**What counts as an answer.** Useful retention would make empirical label counts
unnecessary for this replacement at this resolution, conditional on learned
shapes and widths. Next price a source-independent structural generator as a
competitive baseline, or acquisition of shape distributions on different source
content. Do not claim that a no-acquisition method has been demonstrated.
A worthwhile loss would justify carrying the learned label law into a statistical
donor candidate or a different-source acquisition comparison. It would not prove
that the exact empirical frequencies are optimal, that literal expressions are
necessary, or that another simple prior cannot work. Wide intervals require a
decision-relevant resolution price; failed construction or missing baseline gain
returns to strategy without a mechanism verdict.

Charge the original 0150 source searches, failures and extraction to every
deployment that retains their shapes, including the uniform-label replacement.
The approximately 2.88M evaluations per acquired library are not removed by
relabeling. Report acquisition-plus-search cost in evaluations and worker time
separately. This block can choose what information to retain; it cannot itself
demonstrate cheaper acquisition.

**Full cost and exit.** One experiment, expected **4–6 hours total**, including
proposal, build/validation, calibration, scoring, review, analysis and contingency.
Preparation at most 120 minutes; summed queue timeouts at most three hours.
0524 scored 7,776 jobs in 45.6 minutes at about ten effective workers; its B/C
means were 6.84 worker-seconds for R-tree, 2.25 for R-lib and 2.34 for R-perm.
These price references only: uniform donors may be slower. Measure their tails
and sustained rate, plus a fixed size capable of deciding a material replacement,
before queue admission. Leave time for analysis before
2026-10-12T14:19:15 Europe/Stockholm.

Return to strategy after this result or a measured validity, build, precision or
complete-cost obstruction. No automatic second relabeling, input-only arm,
source-size sweep or generator build follows. The next review should prioritize
portability of acquisition or a genuinely source-independent comparator over
another local ingredient test. If only a standalone probe is justified, it uses
this slot, stays within 60 minutes of queue timeouts and returns before confirmation.

The alternative learning mechanism is [Salustowicz and Schmidhuber, *Probabilistic
Incremental Program Evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/),
found in this strategy review's literature search. PIPE updates a program-generating
probability distribution from selected programs. This fixed replacement test is
neither a PIPE implementation nor inherited map evolution; it asks which
information a later statistical learner would need.
