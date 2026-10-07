Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), selected
by [strategy 2129](../runs/2026-10-07-2129/strategy.md). This is a question and implementation
direction; the steward supplies the experiment design, size and decision rules.

Does collecting solvers under a fitted decoder increase the value of fitting context,
or does token-only fitting obtain the same additional improvement? The first corpus study
showed C1 beating T1; the feedback study showed C2 beating C1. Those two results do not
answer this question together because T2 was not evaluated.

**What to reuse.** All four tables already exist for each of 32 paired lineages:

- Original G4-collected corpus: `tables.T` and `tables.C` in
  `experiments/output/2026-10-07/2026-10-07-1707-solver-corpus-context/corpora.json`.
- Feedback corpus collected under C1: `C2.tables.T` and `C2.tables.C` in
  `experiments/output/2026-10-07/2026-10-07-1924-solver-feedback/corpora.json`.

Strategy checked presence for all 32 lineages and exact equality of saved parent C1 tables.
The reviewed fitter and runners are in commit `5565d54` (`solver_corpus_fit.py`,
`solver_corpus_run.py`, `solver_feedback_run.py`); they are absent from this checkout's
experiment directory, so inspect that commit or the research branch. Reuse the frozen bank,
split, exact verifier and search harness. Validate imported tables, provenance and replay
before scoring. No new solver collection, fitting rule or smoothing parameter is needed.

**Comparison.** Evaluate T1, C1, T2 and C2 on shared fresh seeds, with fresh latent populations
and only tables transferred. Keep lineage pairing and both training families. Compare the
context advantage C2/T2 with C1/T1 on log search cost; equivalently compare feedback's
speed-up C2/C1 with T2/T1. Estimate that interaction directly within lineage, rather than
multiplying published ratios from different seed blocks. Include training and the three
reused withheld cells. T is a restricted likelihood fit on G4, not the best possible
token-only search map; the contrast compares these fitting procedures.

**Feasibility first.** Probe throughput for the saved T2 tables and precision of the paired
contrast, then freeze a size that can change the decision before the actual deadline.
Retain independent lineages in preference to many seeds under a few parents. Price fitting
validation and report generation too. The roughly 29-minute three-arm evaluation in 1924
is an anchor, not a four-arm projection. If only a probe fits, preserve its timing and
precision estimates for a later run; do not use a tiny unresolved contrast as a null.

**What would count as an answer.** An increased contextual advantage that transfers supports
feedback improving these contextual fits more than the restricted token fits. An unchanged
advantage with both fits improving supports useful feedback without a demonstrated increase
in context's value. A decreased advantage means token fitting benefits relatively more;
context may still be valuable in C2. Training-only improvement limits transfer. Distinguish
a bounded small interaction from unresolved uncertainty; the steward sets non-overlapping
rules and a worthwhile effect before confirmation.

This comparison does not isolate particular bigrams, active tokens, yield or diversity.
It also does not test a self-updating token-only lineage: both second-round fits use
corpora collected under C1. It concerns one feedback step, external fitting and the reused
screened bank. One root-10 slot is allocated; a third contextual fit C3, token-only feedback
loop, or broader bank requires another strategy decision.
