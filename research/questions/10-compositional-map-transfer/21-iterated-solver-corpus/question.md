---
status: closed
tags: [compositional-transfer, decoder, external-fitting, solver-corpus, iterated-fitting, feedback, fresh-start]
budget: {experiments: 1, used: 0}
---
# Does refitting a solver-corpus decoder to solvers found under it give a further, transferable speed-up?

Current summary: **closed after run 2026-10-07-1924 (row 1, 1 of 1 slot; commit `5565d54`).
One feedback refit helped further and the gain transferred. Each of the 32 saved 1707 tables C
collected exact training solvers under itself; refitting them with the unchanged 1707 rule gave C2.
On fresh training seeds C2 beat its parent 1.404× [1.347, 1.464] (32/32 lineages; BE 1.56×, PA
1.27×) and beat a one-shot refit to a fresh G4 corpus (C') 1.408× [1.342, 1.478]. On the three
withheld cells C2/C was 1.289× [1.204, 1.381] (28/32) and C2/C' 1.330× [1.263, 1.401] (31/32). The
fresh one-shot refit replicated its parent within the interval: C'/C 0.997× [0.940, 1.058]
(training), 0.969× [0.908, 1.035] (withheld); differences of about 6–9% are not excluded. So the
increment comes from collecting under C rather than G4, as a procedure: that bundles higher
yield (99.3% against 96.1%), slightly more distinct tapes, and whatever differs in which tapes C
finds; the design does not separate them. C2 is sharper than C in every lineage (body-row entropy
3.91 → 3.80 bits, previous-token MI 0.41 → 0.48), and at this one step that came with a holdout
gain, not a loss. Per paired seed C2 wins about 58% of the time; the whole cost
distribution shifts (training median 4 352 → 3 328 evaluations), most in the upper tail
(unsolved searches 39 → 14 of 5 120). Not shown: a second step,
why C2 is faster (no token-only T2, no start-row ablation, no active-token analysis), how much C2
re-emits its own corpus, family specificity, or a compounded C2-over-G4 number (not run).**

Steward probe before the run (4 lineages, 16 seeds per cell): C2 was faster than C in all four,
by 0.29–0.83 log2; the run used new corpora and new seeds.

Competing explanations:
- A: Solvers found under C carry more useful assembly information than G4 solvers. C2 beats both
  C and C', and the gain holds on the withheld cells.
- B: One round already captures what the corpus can give. C2 ≈ C (within 10%).
- C: Feedback amplifies C's own biases (sharper rows, inherited inert material). C2 is no better on
  training, or better on training only, or worse.
- D: Any C2 gain over C is resampling luck, or a difference between the old fit and a fresh one,
  not the change of source. C' differs from C as much as C2 does.

After run 1924: A is supported at this scope, with "solvers found under C" read as the whole
collection procedure (yield, diversity and content not separated). B is rejected for this step:
C2/C 1.40×, lower bound 1.35. C is not supported for one step: sharpening is present, but the
withheld cells gain 1.29×; whether it compounds over further steps is untested. D is rejected:
C'/C 0.997× [0.940, 1.058] while C2/C' is 1.41×.

Scope: the frozen 1603 four-reducer bank and the 1723 split (BE trains on 4 cells, PA on 6, three
reused holdouts), D1331, `v2_rmin_first`, G4, P 256, length 32, cap 524 288, the 1707 fitting rule
(full tapes, equal cell weight 1 600, shrinkage toward G4 at α 50). Lineages are the 32 saved 1707
corpora. This is repeated external fitting on a reused screened bank. It is not map evolution, it
does not show family specificity, and it does not show that improvement continues indefinitely.

Related: [root 10](../question.md), [20 solver-corpus context](../20-solver-corpus-context/question.md),
[concept plan](../../../plans/iterated-solver-corpus.md),
[strategy 1924](../../../runs/2026-10-07-1924/strategy.md),
[run 1707 analysis](../../../runs/2026-10-07-1707/analysis.md),
[run 1924 analysis](../../../runs/2026-10-07-1924/analysis.md),
[run 1924 decision](../../../runs/2026-10-07-1924/decision.md).

Reopen if (once closed/parked): a second feedback step (C3 from C2) or a token-only refit T2 from
the C-collected corpora gets its own allocation, a fitting rule over executable (active) tokens
becomes available, a new bank with several covered holdouts per family is built, or a later run
finds C2's withheld-cell gain fails on fresh holdouts.
