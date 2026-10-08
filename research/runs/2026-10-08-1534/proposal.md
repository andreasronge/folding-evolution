---
node: questions/10-compositional-map-transfer/25-comparison-gate-transfer
title: Frozen comparison-gate corpus fits (C vs T) on the eight protected holdouts — stage 2
bank: comparison-gate-v1
---

**Question and mechanism.** On the comparison-gate bank's training cells the corpus context
fit C beat the token-only fit T to the same solver tapes 3.11× [2.78, 3.48] over 16 corpora
([1246 analysis](../2026-10-08-1246/analysis.md)). Each cell was its fit's own source, so that
is a fitting result, not transfer. Does the advantage hold on the eight holdout compositions
that no search has touched? Four are BE and four PA, one per repeated reducer. It is the
tree's first transfer test with several protected compositions per family (strategy 1246's
named gap). Sub-question [25](../../questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md).

**Closest technique.** A transition model learned from good programs:
[N-gram GP](https://repository.essex.ac.uk/9722/1/ces-479.pdf)
and [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/). Reusing a solution distribution learned
on source problems resembles [Ardeh et al. 2020](https://gpbib.cs.ucl.ac.uk/gp-html/Ardeh_2020_CEC.html).
The map adapts by external fitting (fitted once, frozen; populations start fresh). This run is a **transfer/boundary test** of a known procedure, not a new method.

**Design (frozen in 1246, unchanged).** Everything below was fixed in run 1246's `freeze.json`
and runner metadata before any holdout search (method hash `abd2ba10…`, split `b0cc4ae0…`,
schedule `f8ebc628…`).
- *Tables.* All 32 fitted tables (C and T for 16 corpora), loaded from
  `experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training/corpora.json`.
  The runner refuses any table whose hash differs from `freeze.json`. No refit. K stays
  unscored.
- *Arms and unit.* Every corpus's C and T run on all 8 holdouts × 16 seeds (phase-2 seeds,
  paired between C and T within a corpus, distinct across corpora). That is 4 096 searches.
  G4 gets 32 seeds per holdout (phase-5 seeds, 256 searches), descriptive only. Cap 524 288,
  P 256, exact D1331 check. The unit is the corpus (n = 16, 8 per family).
- *Implementation.* Add a stage-2 entry to `comparison_gate_run.py` that runs exactly the
  frozen roster, plus a holdout section in the report. The smoke run uses training cells and a
  separate seed base only. **No holdout search before the queue.** Keep 1246's fixed balanced
  prefix rule: BE1/PA1 … BE8/PA8 pair blocks in order, ≥ 6 complete pairs required, no fallback
  after an error.

**Feasibility and cost.** 1246's report prices stage 2 at **3 940 s of queue at training
difficulty** (C 5.5 s and T 11.2 s worker time per training search, about 9.6 effective
workers). Holdouts may be harder; if every search hit the cap (about 25 s each) it would take 3.1 h. **Timeout: 3 h**, so the ≥ 6-pair prefix completes even
at 2× training cost. Agent time is about 2.5 h: a small runner extension (tables and scoring
code exist), review, analysis and decision. Total about 4–5 h. A fresh corpus costs about 423 s
if the result needs more corpora.

**Primary comparison.** Holdout C/T = exp(mean over corpora of [mean over 8 holdouts × 16
paired seeds of log cost_T − log cost_C]). Unsolved runs count as 2 × cap, families are weighted
equally, and the interval is a 95% t over 16 corpora (frozen endpoint).
- **Lower bound > 1.0:** context's advantage over token fitting transfers to the protected new
  compositions, at this bank and procedure's scope.
- **Upper bound < 1.10:** a holdout gain is bounded below 10% despite the 3.1× training gain.
  The training advantage is then mostly specific to the source cells (explanation B). This does
  not show absence.
- **Otherwise unresolved.** Report how many fresh corpora would resolve the observed estimate,
  priced at 423 s each plus holdout scoring, and return to strategy.

Pre-stated secondary results (intervals only, no decision rule). Per-holdout C/T for all 8
cells and the count with C/T > 1. A leave-one-holdout-out range, so one cell cannot carry the
pooled result. Matched minus mismatched training family on log C/T, with a 95% interval over
corpora (explanation F). The holdout/training shrinkage of log C/T. The 1 × cap sensitivity.
C/G4 and T/G4 solve rates and costs (G4 unpaired, descriptive). The corpus interval does
not capture task-to-task spread over only 8 holdouts; the per-holdout table reports it.

**Precision.** Training per-corpus sd was 0.21 log (half-width ×1.12 at n = 16); at sd 0.30 it
is ×1.17, so a true 1.3× resolves and a true 1.0× comes out unresolved, not bounded.

**Expectation.** I expect holdout C/T of about 1.5–2.5×: smaller than training, as on the old
bank (1.37× → 1.29×), but resolved. Mismatched-family holdouts should show smaller gains than
matched ones. Surprises: C/T below 1.10 (the fit overfits its source compositions), or C/T on
holdouts about equal to training (no shrinkage at all).

**Next action.** Root 10 has used 16 of 16 slots: this needs a one-slot allocation (strategy
1246 required review before funding transfer; the price is now measured). If granted, a researcher adds the stage-2 entry on the run branch, smokes it on training cells
and queues the frozen roster. Then analysis, and a decision on whether root 10's transfer
question is answered at this scope.
