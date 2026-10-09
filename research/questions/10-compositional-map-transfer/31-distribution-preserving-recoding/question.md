---
status: closed
tags: [compositional-transfer, then-addition, variation-neighbourhood, locality, recoding, fixed-supply, ripple]
budget: {experiments: 1, used: 0}
---
# Does widening Q's mutation neighbourhood, with its random-program distribution held exactly fixed, speed search toward C?

Current summary: **closed. The tested recodings were harmful; no useful gain at either dose.**
C (the frozen 1246 context table) is 2.41× [2.11, 2.75] faster than Q (G4 matched to C's
per-position marginals) on then-addition (30). C changes about 3 tokens per allele resample, Q
about 1.7. Run 2026-10-09-0537 recoded each of the 16 Q tables with context-dependent allele
permutations inside every body row. Row token counts were exact, so the uniform-prior distribution
of complete tapes was Q's, and initial token tapes were identical. R30 (30% of each row permuted)
matched C's mutation width: 3.00 tokens per resample against C 2.95 and Q 1.71, and similar on
C-solver tapes. R100 (full permutation) reached 7.7.

Cost ratio cost_Q/cost_R30 was 0.855 [0.801, 0.914], over 16 corpora with unsolved runs at
2 × cap. So R30 was 1.17× [1.09, 1.25] *slower* than Q. The result was the same at 1 × cap, on
both-solved pairs, in both construction realizations and in both fitting families; 14/16 corpora
were below 1. R100 was 2.4× slower than Q (0.409 [0.386, 0.434]) and solved 52% of searches
against Q's 74%. R30 stays 2.82× [2.49, 3.19] slower than C. The pre-stated label is "no useful
gain at either dose".

At Q's exact random-program distribution, adding undirected coupling of C's size cost speed, and
more of it cost more. Scope:
- one development bank, frozen external maps, one operator set and two random within-row recodings;
- the recoding also changes allele–token correlations and crossover's effect, so mutation width is
  not isolated;
- a structured, locality-preserving recoding is untested;
- this does not show that C's conditional rows are necessary.

Competing explanations:
- A. C's advantage is partly its wider, ripple-like neighbourhood: a C-matched recoding of Q speeds
  search at fixed supply. **Not supported for these recodings:** the C-width recoding was resolved
  slower than Q.
- B. Width is incidental; what helps is C's conditional content (what the ripple re-draws toward).
  Unstructured ripple is neutral or harmful (low locality, Rothlauf & Oetzel 2006).
  **Consistent:** unstructured ripple was harmful, with a monotone dose. C's content, or ripple
  structured the way C's rows structure it, remains the candidate. Which of these it is was not
  tested.

Related: [30](../30-position-matched-replacement/question.md),
[29](../29-frequency-matched-transfer/question.md),
[26](../26-then-addition-fresh-bank/question.md), [fragment plan](../../../plans/learned-executable-fragments.md),
[recoding plan](../../../plans/distribution-preserving-variation.md),
[run 0537 analysis](../../../runs/2026-10-09-0537/analysis.md),
[run 0537 decision](../../../runs/2026-10-09-0537/decision.md).

Reopen if: a structured recoding (one that keeps local token neighbourhoods, or one derived from
C's rows) is proposed with a measured reason to expect it to differ from random permutation; or
a later learner's gain is credited to its mutation neighbourhood rather than its content, and a
fixed-supply control is needed to check that.
