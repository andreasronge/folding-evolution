---
node: questions/10-compositional-map-transfer/31-distribution-preserving-recoding
title: Recoded Q — wider mutation ripple at an exactly fixed random-program distribution
bank: then-addition-v1
---
**Question and mechanism.** Per [strategy 0537](strategy.md) and its [plan](../../plans/distribution-preserving-variation.md): C beats Q by 2.41× [2.11, 2.75]
([0306](../2026-10-09-0306/analysis.md)), and C's mutations change more tokens. Q decodes by
cumulative thresholds: an allele maps to the same quantile in every context, so downstream tokens
mostly survive an upstream change. The proposal permutes allele entries within each body row
(positions 1–31, previous tokens 0–23), with a different permutation per context. Every row keeps
its token counts, so every complete tape keeps its uniform-prior probability. But a changed token
now re-draws downstream tokens more often. Does that wider neighbourhood alone, at exactly fixed
supply, recover part of C's advantage?

**Closest known technique.** This is grammatical evolution's *ripple effect*. Ripple crossover is
argued to explore better in [O'Neill et al., GPEM 2003](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2003_GPEM.html).
Low locality hurts mutation-based search in [Rothlauf & Oetzel, EuroGP 2006](https://madoc.bib.uni-mannheim.de/1255).
[Stephens (1999)](https://arxiv.org/abs/nlin/0006051) studies operator effects among equivalent
genotypes. What this adds: the ripple strength is a dial, with the random-program distribution
fixed exactly and against a fitted reference (C). The map is frozen and built externally; there is
no selection or inheritance. A mechanism test, not an acquisition method.

**Arms.** All are built per corpus from the 16 Q tables of 0306.
- **R30**: a random 30% of each body row's 23 000 allele entries, permuted among themselves.
- **R100**: a full random permutation of each body row (dose arm).
- **Q** and **C**: reused rows from 0306 and 1548.

Position 0 unchanged. A permutation shared across contexts would only relabel alleles; under
these operators that equals Q in law, so it is not run. Construction seeds `[537, corpus, dose, k]`
are fixed now. Each corpus and dose gets two realizations k, each on 4 of the 8 seeds per cell, so
realizations are nested in corpora. All new arms reuse Q's 2 048 (corpus, cell, seed) triples,
case draws and streams. Q's generation-0 alleles are mapped through the inverse permutation, once,
so the initial token tapes are identical. The unit is the corpus, n = 16.

**Feasibility.** I ran a read-only probe in this run (12 s): uniform tapes, n 4 096, seed
202610090537, means over 16 corpora. f = 0.3 was chosen from this table before any scoring and is
now frozen:

| | tokens changed / resample | downstream | P(≥ 4) | Bernoulli 0.03 |
|---|---|---|---|---|
| C | 3.10 | 2.24 | 0.32 | 2.77 |
| Q | 1.77 | 0.88 | 0.10 | 1.65 |
| R30 | 3.10 | 2.21 | 0.32 | 2.78 |
| R100 | 7.60 | 6.72 | 0.63 | 6.19 |

R30 matches C's footprint, within 0.2 on every corpus. Gates:
- exact row counts;
- generation-0 token hashes equal Q's on all 4 096 rows;
- under an identity recoding, the new code replays 16 Q rows (0306) and 16 C rows (1548) bit-exactly.

Descriptive audit: change-count and span histograms (single resample, full offspring operator) on
uniform tapes and on 1246 C solver tapes.

**Cost.** The lookup shape is unchanged, so decoding costs the same. Q took 11.7 worker-s per
search in 0306 (6.8 solved, 25.7 capped) on 10 workers. The 4 096 new searches should take about
80 min, at most about 176 min if all are capped. Timeouts: preparation 1 800 s and scoring
12 000 s, 3.8 h in total. Implementation extends the 0306 runner at `2bab2c2` (a permuted
`PositionalDecoder` lookup, an inverse encoder, vendored Q rows): about 90–120 min. Total about
5–7 h including agents.

**Primary comparison.** Q/R30 = exp(mean over corpora of mean over cells and seeds of
[log cost_Q − log cost_R30]), with unsolved runs costed at 2 × cap and a 95% t interval on 15 df.
- Lower bound ≥ 1.20: **useful gain at fixed supply**.
- Upper bound ≤ 1.20: **no useful gain**.
- Otherwise: **unresolved** (with a resolution price).

The expected half-width is about ×1.10–1.15, as for Q/K. Also reported, without a rule:
- C/R30 (an upper bound ≤ 1.5 counts as "approaches C");
- gap share log(Q/R30)/log(Q/C);
- Q/R100;
- solves, 1 × cap and both-solved results, and spread across cells and realizations.

**Expectation.** Q/R30 0.85–1.10 and R100 slower than Q (0.6–0.9×): unstructured ripple re-draws
from G4-shaped rows and costs locality. That would point to C's conditional content, not its width.
**Surprise:** Q/R30 with a lower bound ≥ 1.2, or R100 ≥ R30. Either makes undirected coupling a lever.

**Next action.**
- Useful gain and approaches C: acquire variation coupling before building
  [fragments](../../plans/learned-executable-fragments.md).
- Useful gain with a gap remaining: keep both candidates for the strategist.
- No useful gain at either dose: end the recoding line. This favours dependency-carrying targets
  but does not prove C's rows are necessary.

All branches return to strategy. Scope: one development bank, frozen maps, one operator set.
