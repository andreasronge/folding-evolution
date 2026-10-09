---
status: closed
tags: [compositional-transfer, then-addition, external-fitting, solver-corpus, context, token-control, frequency-control, eda]
budget: {experiments: 1, used: 0}
---
# Does a G4 token map matched to the context fit's emitted frequencies reproduce its transferred advantage on then-addition?

Current summary: **closed after run 0125 (answered at this scope; root 10's 20th and last
slot). No: on the then-addition bank the frozen context tables C beat the frequency-matched
control K 2.48× [2.17, 2.83]** (16 corpora, 2 × cap; 1 × cap 2.25× [1.98, 2.54]; both-solved
pairs 1.92× [1.68, 2.21], selection-conditioned). K is G4 × 24 token multipliers matched to C's
pooled emitted marginals (max error 2.9e-5). Every corpus (1.44–3.67×) and every cell (1.42–3.67×)
favours C; BE-fitted 2.77×, PA-fitted 2.21×. K is also slower than the token-only fit T to the same
solver tapes, K/T 0.86× [0.77, 0.96], so moving T's 24 multipliers to C's pooled marginals costs
speed. K beats G4 descriptively (1.57×, unpaired G4 rows), about a third of C's log advantage
over G4. Solves: C 86.5%, T 75.5%, K 72.5%, G4 63.3%. Pre-stated rule: lower bound ≥ 1.20 → this
G4-based pooled-frequency replacement is insufficient within 20% on these cells. Direction and
K/T replicate question 20 on the four-reducer bank (C/K 1.65×, K/T 0.83×).
[Analysis](../../../runs/2026-10-09-0125/analysis.md), commit `8e62831`.

Not shown: which structure carries C's advantage. K keeps G4's previous-token context and matches
only pooled, not positional, marginals, so context dependencies and positional frequencies are
bundled in C − K. Nothing here says a fragment learner or any other structural learner would help.
then-addition-v1 is now a development bank; this is a mechanism result, not new transfer evidence.

Competing explanations:
- A: C's advantage needs more than pooled frequencies (context, position or neighbourhood); C/K
  resolves above a worthwhile margin.
- B: C's advantage is carried by its pooled emitted frequencies on G4's template; K comes close to C.
- C: partial: K recovers part of C/T but leaves a resolved gap.

Where they stand after run 0125: A supported at this scope (C/K lower bound 2.17);
B not supported (K recovers less than T does); C not supported as stated, since K recovers some of
G4's gap (descriptive) but none of C/T (K/T < 1).

Scope limits: then-addition-v1 is now a development bank; K matches pooled, not positional,
frequencies and keeps G4's context template; external fitting, not evolutionary acquisition.

Related: [root 10](../question.md), [26](../26-then-addition-fresh-bank/question.md),
[20](../20-solver-corpus-context/question.md), [24](../24-comparison-gate-bank/question.md),
[plan](../../../plans/transferred-context-frequency-control.md),
[proposal 0125](../../../runs/2026-10-09-0125/proposal.md),
[analysis 0125](../../../runs/2026-10-09-0125/analysis.md),
[decision 0125](../../../runs/2026-10-09-0125/decision.md),
[fragment plan](../../../plans/learned-executable-fragments.md).

Reopen if: a learner proposes to acquire a frequency-only target and needs to know whether
positional (32-position) rather than pooled matching closes the gap, in which case a
position-matched K on these frozen corpora and 1548 row F seeds is the cheap test (harness
`experiments.chem_tape.frequency_matched_run`); or a fresh bank, frozen with a structural learner,
needs the same control. Narrowing C/K by replication is not a reason.
