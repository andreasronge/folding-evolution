# Does retaining the observed recurrent repertoire make acquisition useful?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 1228](../runs/2026-10-11-1228/strategy.md). The steward
supplies the proposal, fixed sample size and primary decision rule. This is a
direction for one development experiment, not an experiment registration.

The [1129 probe](../runs/2026-10-11-1129/analysis.md) supplies a specific reason
to change the procedure. Semantic pooling found 49 recurrent, admissible
helper–build cases; the 16-entry cap discarded 44. Source collection was cheap.
What remains unknown is whether retaining that available repertoire improves
search, once the extra irrelevant entries and their dilution are also paid for.
More helper entries alone would not answer the question.

**One intervention.** Keep R-S's semantic key, minimum observed representative,
two-source-cell recurrence requirement, proper-subtree/input restrictions and
3–9-node emission range. Remove only its top-16 truncation: emit every eligible
class, with one representative per class and uniform draws over the resulting
library. Retain the existing half-library donor mix, empty-library fallback,
32-token program cap and restart schedule. Call this R-all. Keep constants and
comparators that satisfy the existing rule. Do not add helper recognition,
minimum-size filters, source reweighting, simplification, donor weighting or
insertion-rate tuning. This is a changed extraction procedure, not a repair to
the earlier result or a claim that larger libraries generally help.

Reuse `order_library.py`, `order_run.py`, `order_bank.py` and the tree engine at
`db30b15` on the research history; these files are absent from this `main`
checkout. Code inspection found the semantic cap at `ranked[:16]` and uniform
library-entry draws already supported. Preserve the old path for reconstruction
and replay. Validate that R-all contains the exact R-S prefix and all remaining
eligible classes, each representative came from its source corpus, and no
helper census or destination identity enters extraction. The finite source
corpus already bounds the pool; a resource failure should stop preparation,
not silently select a favourable smaller pool.

**First experiment.** Acquire independent new source corpora using the frozen
1129 roster and source effort. Construct capped R-S and R-all from each same
corpus. Compare fresh searches on the six existing development destinations,
keeping R-tree and the supplied R-order prior as references. The literal arm
and sum prior need no further precision in this cycle. Preserve all builds,
including source failures and empty libraries; acquisition builds are the
learning units, with paired scoring seeds and per-cell results. The eight pilot
builds can support reconstruction and cost sizing, not confirmation or selection.

The primary question is useful R-all search cost relative to R-tree. The paired
R-all/R-S contrast checks whether removing truncation improves the current
procedure; improvement over a harmful R-S alone is insufficient. Keep R-order
visible in the decision: the experiment asks whether useful content can be
acquired automatically, not whether acquisition beats supplied domain knowledge.
Choose one worthwhile saving and a fixed size with a 95% interval before scoring;
the 1129 log-gap criterion remains a failed pilot continuation rule, not a rule
to relabel after the fact. Record donor availability, realized insertion and
rejection, and source-derived helper coverage as diagnostics. Changes in size,
content and sampling mass accompany cap removal, so a gain would not isolate
the causal value of order helpers themselves.

Use capped arithmetic evaluations for the primary cost and for acquisition-plus-
search accounting; report solve counts and worker seconds alongside it. Pilot
geometric ratios cannot price arithmetic repayment. Show the strong-prior gap
and any finite break-even against R-tree; if R-order remains cheaper, state that
there is no demonstrated repayment against that prior. Semantic equivalence
means exact equality on D625, not equality on arbitrary inputs.

Keep all 24 protected destinations unsearched. Preserve the recorded admission
rule: exact short aliases excluded, the twelve 84%-agreement source near-aliases
retained and labelled. This explicitly follows the executed 1129 bank, whose
bounded-screen rule differs from the earlier concept plan's wording; do not
change the roster to improve recurrence. Any later protected proposal must
freeze that scope and the whole revised method before scoring, and retain both
overlapping and disjoint destination strata.

**Cost and exit.** One full experiment, expected **4–6 h total**: roughly 1–2 h
preparation/validation, 0.5–1.5 h queue, and 2–2.5 h for proposal, reviews,
analysis and contingency, with **6 h as the total ceiling**. Preparation remains
at most 120 minutes; summed queue timeouts at most 2 h, subordinate to that
total. The measured anchor is 1129: 384 source jobs plus extraction/screening
in 118 s wall, and 480 five-arm destination jobs in 332 s wall. A sizing scenario
of 24 builds × 6 cells × 8 repeats × 4 arms is 4,608 scoring jobs, about 53 min
at the old aggregate rate; this is not a sample-size justification or a measured
R-all rate. Time the new pool and account for tails and changed arithmetic
variance before admission. Do not run a small efficacy pilot and then select
the winning variant. A complete decision-sized comparison is the purchase.

Return to strategy after the result or an earlier validity, precision, build or
cost obstacle. A material saving over R-tree, replicated across acquisitions,
would justify considering a **separately allocated 6–8 h protected comparison**;
the complete candidate therefore costs **10–14 h**, including this first stage.
Usefulness substantially below R-order can answer an acquisition question but
does not automatically justify that second stage. Tight small effects or harm
end this uncapped recurrence-only procedure. Broad uncertainty needs a priced
resolution; it is not equality. Do not automatically try cap 32, a new ranking,
larger representatives or a new source allocation.

The closest precedent is [Keijzer, Ryan and Cattolico, *Run Transferable Libraries*
(2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
A different mechanism is [Bowers et al., *Top-Down Synthesis for Library Learning*
(POPL 2023)](https://arxiv.org/abs/2211.16605): Stitch learns parameterized
abstractions by corpus-guided synthesis for compression. That could pool across
input bindings, but compression is not a search-speed guarantee and syntactic
abstraction does not automatically remove the observed semantic bloat. This
bounded test asks whether the already observed repertoire suffices before
buying that different representation. Neither procedure is per-individual
inheritance of a decoder.
