---
status: open
tags: [compositional-transfer, then-addition, external-fitting, solver-corpus, context, position, frequency-control, eda]
budget: {experiments: 1, used: 0}
---
# Do C's per-position token frequencies, on G4's grammar or alone, reproduce its search advantage?

Current summary: **not yet scored.** Run 2026-10-09-0239 built Q and P and passed every
intervention and replay gate (marginal errors ≤ 3.8e-5, positional TV ≤ 1.6e-4, bit-exact legacy
replays) but stopped at its runtime admission gate, 70 s over the 3 h scoring timeout; re-proposed
unchanged with a 3 h 15 min timeout in run 2026-10-09-0306. A 32-search preparation sample (Q 9/16,
P 6/16 solved, unpaired, rotating cells) is an observation, not an efficacy estimate. Question 29 showed that matching
C's pooled emitted frequencies on G4's template (K) leaves C 2.48× [2.17, 2.83] faster on
then-addition. K differs from C in both its conditional rows and its per-position marginals
(position-0 total variation 0.07–0.21, mean over positions 0.009–0.017). This question scores two
frozen projections of C: Q (G4's rows × per-position multipliers, matched to C's marginal at every
position; keeps G4's previous-token dependence) and P (independent draws from C's per-position
marginals; no dependence).

Competing explanations:
- A: C's advantage needs its learned conditional rows (or the variation neighbourhood they create);
  C/Q resolves above 1.20.
- B: per-position supply on G4's grammar suffices; C/Q upper bound ≤ 1.20.
- B′: per-position supply alone suffices; C/P upper bound ≤ 1.20 as well.

Read-only probe (steward, 0239, on the saved tables; descriptive): Q fits C's per-position marginals
exactly in floating point; C's conditional rows are about as far from Q's as from K's (KL 0.11–0.14
bits per transition for both, against 0.44–0.47 bits of adjacent-token dependence in C). One uniform
allele resample changes about 2.8–3.1 decoded tokens under C, 1.7 under Q, 0.9 under P, so Q and P also
differ from C in variation neighbourhood.

Scope limits: then-addition-v1 is a development bank; external projections of C, not acquisition;
marginals are under the uniform latent prior.

Related: [root 10](../question.md), [29](../29-frequency-matched-transfer/question.md),
[26](../26-then-addition-fresh-bank/question.md), [plan](../../../plans/position-matched-context.md),
[strategy 0239](../../../runs/2026-10-09-0239/strategy.md),
[proposal 0239](../../../runs/2026-10-09-0239/proposal.md),
[infeasible 0239](../../../runs/2026-10-09-0239/infeasible.md),
[decision 0239](../../../runs/2026-10-09-0239/decision.md),
[proposal 0306](../../../runs/2026-10-09-0306/proposal.md).

Reopen if: (set when closed or parked). If parked for runtime, reopen when a scoring timeout of at
least 11 700 s fits the remaining queue allowance, or the decoder runs ≥ 10% faster on the same gates.
