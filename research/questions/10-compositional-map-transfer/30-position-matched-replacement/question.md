---
status: closed
tags: [compositional-transfer, then-addition, external-fitting, solver-corpus, context, position, frequency-control, eda]
budget: {experiments: 1, used: 0}
---
# Do C's per-position token frequencies, on G4's grammar or alone, reproduce its search advantage?

Current summary: **closed — neither frozen positional replacement reproduces C's advantage on
then-addition.** Run 2026-10-09-0306 scored Q (G4's rows × per-position multipliers matched to C's
emitted marginal at all 32 positions, C's start row at position 0) and P (independent draws from C's
positional marginals) on 1548 row F's 16 cells with C/T/K's paired seeds: C/Q 2.41× [2.11, 2.75]
(1 × cap 2.21×, both-solved 1.95×) and C/P 5.47× [4.79, 6.25], all 16 corpora and cells above 1.20,
so both replacements are insufficient under the pre-stated band. Q is not resolved from the
pooled-frequency K (Q/K 1.03× [0.93, 1.13]): adding C's per-position marginals to G4 gave no resolved
gain, and a gain above about 1.13× is excluded at this scope. P, with no previous-token dependence, solves 50.5% against C's 86.5% and is 2.27× slower
than Q. Background: question 29 showed that matching C's pooled emitted frequencies on G4's template
(K) leaves C 2.48× [2.17, 2.83] faster; K and C also differ in per-position marginals (position-0
total variation 0.07–0.21, mean over positions 0.009–0.017), and this question found no resolved
effect of that difference.

Competing explanations:
- A: this G4-based positional replacement is insufficient: C/Q resolves above 1.20. Whether
  independent positional supply suffices depends on C/P. (Rejecting Q alone would not show that C's
  learned rows are necessary.) **Supported** for Q, and P is insufficient too (both lower bounds
  ≥ 2.11×).
- B: per-position supply on G4's grammar suffices; C/Q upper bound ≤ 1.20. **Not supported** (upper
  bound 2.75×).
- B′: per-position supply alone suffices; C/P upper bound ≤ 1.20 as well. **Not supported** (upper
  bound 6.25×).

What remains open: whether C's conditional rows themselves, or the wider mutation neighbourhood
they create (about 3 tokens changed per allele resample against 1.7 for Q and K, 0.9 for P), carry
the advantage; and whether any acquired (rather than externally projected) positional or contextual
map reaches C.

Read-only probe (steward, 0239, on the saved tables; descriptive): Q fits C's per-position marginals
exactly in floating point; C's conditional rows are about as far from Q's as from K's (KL 0.11–0.14
bits per transition for both, against 0.44–0.47 bits of adjacent-token dependence in C). One uniform
allele resample changes about 2.8–3.1 decoded tokens under C, 1.7 under Q, 0.9 under P, so Q and P also
differ from C in variation neighbourhood.

Scope limits: then-addition-v1 is a development bank; external projections of C, not acquisition;
marginals are under the uniform latent prior, not the populations selection visits; one operator
set; the result rejects these two frozen replacements, not every positional learner.

Related: [root 10](../question.md), [29](../29-frequency-matched-transfer/question.md),
[26](../26-then-addition-fresh-bank/question.md), [plan](../../../plans/position-matched-context.md),
[strategy 0239](../../../runs/2026-10-09-0239/strategy.md),
[proposal 0239](../../../runs/2026-10-09-0239/proposal.md),
[infeasible 0239](../../../runs/2026-10-09-0239/infeasible.md),
[decision 0239](../../../runs/2026-10-09-0239/decision.md),
[proposal 0306](../../../runs/2026-10-09-0306/proposal.md),
[analysis 0306](../../../runs/2026-10-09-0306/analysis.md),
[decision 0306](../../../runs/2026-10-09-0306/decision.md),
[fragment plan](../../../plans/learned-executable-fragments.md).

Reopen if: a positional learner acquired by selection or feedback (not an external projection)
reaches C within 1.2× on a bank, which would contradict the frozen-projection result; or a
variation-matched control (C's rows with a mutation neighbourhood matched to Q/K, or Q with C's)
shows the C − Q gap is mostly a neighbourhood effect, making the positional reading worth revisiting
with matched variation; or a fresh bank shows C/Q ≤ 1.2.
