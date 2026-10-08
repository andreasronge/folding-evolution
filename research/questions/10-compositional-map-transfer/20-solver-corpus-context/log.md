# Log — 20 solver-corpus context

- 2026-10-07 (1707): opened from strategy 1707 (root 10's thirteenth slot; no budget raised).
  Steward probe in a scratch copy of `research/main` (read-only; script in the run folder):
  one corpus per family from 48 G4 searches per training cell (seeds 17 070 000+), fitted T
  (G4 × 24 global multipliers, maximum likelihood), C (G4-shrunk previous-token table, α 50
  pseudo-transitions per row), C400 and K (G4 × multipliers matched to C's exact emitted
  marginals, max error < 0.0001); 12 fresh seeds per cell (17 170 000+). Yield 91% (BE), 98%
  (PA); collection 64 s and 50 s; evaluation 600 searches in 70 s. Mean log2 evaluations G4 /
  T / C / C400 / K: BE 13.99 / 12.33 / 11.55 / 12.87 / 12.95; PA 14.16 / 12.83 / 12.55 / 12.53 /
  12.84. Paired per-search sd of C − T 2.2 (BE) and 1.8 (PA) log2. α 50 frozen from this probe.
  Proposal: run 2026-10-07-1707 (16 independent corpora per family; T, C, K on fresh training
  seeds; all frozen fits on the three holdouts).

- 2026-10-07 (1707, commit `627336d`, [analysis](../../../runs/2026-10-07-1707/analysis.md)): 16
  independent corpora per family (48 G4 collection searches per own training cell; 7 408/7 680
  solved, every cell ≥ 40/48), each fitted to T, C (α 50) and K; 32 fresh seeds per cell and arm,
  shared within corpus; all frozen fits then on the three holdouts. 35 240 searches, 80.6 min;
  replay bit-identical, all tape/table checks passed, K valid on 32/32 (max error 3.3e−5), no
  exclusions. Training cells, pooled over families (t, 15 df): **C/T 1.365× [1.288, 1.446]**
  (BE 1.46×, PA 1.28×, both resolved; 31/32 corpora), **C/K 1.654× [1.568, 1.744]**, but K/T
  0.825× [0.776, 0.878], so the emitted-marginal control is slower than the token fit and C/T,
  not C/K, sizes the contextual increment. T/G4 2.42×, C/G4 3.31× (unpaired); T versus the 20
  saved 1723 maps unresolved (BE 0.95× [0.81, 1.11], PA 1.02× [0.81, 1.28]). 1 × cap
  sensitivity unchanged. Holdouts (32 corpora, 31 df): C/T 1.293× [1.213, 1.378] (30/32), C/K
  1.537×, C/G4 2.75×. Family: matched over mismatched C 1.02× [0.91, 1.15] (BE holdout), 0.75×
  [0.63, 0.89] and 0.99× [0.89, 1.10] (PA holdouts): no family-specific gain resolved; on PA `(F?S:M)+m`
  the BE-fitted tables are faster (shared by T). Corpora carry about 0.45 bits per transition of
  order information above a within-tape shuffle; C's start row is flatter than G4's. Break-even
  against G4: 120–593 future searches for C (evaluations). Outcome **row 1**.
  Decision: close 20 as answered and send root 10 (13 of 13 slots used) to strategy because the
  pre-stated row-1 rule is met with margin and replicated over 32 corpora: a previous-token
  table fitted to exact solver tapes speeds fresh search about 1.37× beyond a token-only fit to
  the same tapes, transfers about 1.29× to the withheld cells, and shows no resolved family advantage; the
  open next step (can evolution or a search-cost learner reach this table) is a new allocation,
  not more of this question.

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is section "Solver-corpus context fit", moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

## Solver-corpus context fit (root 10, run 2026-10-07-1707)

One run, commit `627336d`, complete data (35 240 searches, 81 min; 0315 replay bit-identical,
7 447 solver re-verifications and all table checks passed, no exclusions). Same bank, 1723 split,
D1331, G4, P 256 and 524k cap as 1723–1137. A different learning signal: no search-cost
selection. Per corpus, 48 G4 searches per own training cell (16 corpora per family on disjoint
seeds; 7 408/7 680 solved, every cell ≥ 40/48); the first exact solver's 32-token tape is kept and
transition counts are equalized per cell. Three tables per corpus: **T**, 24 token multipliers on
G4 fitted by maximum likelihood; **C**, the previous-token counts shrunk toward G4's rows (α 50,
frozen from a steward probe on other seeds); **K**, G4 × multipliers matched to C's pooled emitted
token marginal (max error 3.3e−5). Each scored on 32 fresh seeds per cell, shared within corpus;
then all frozen tables on the three withheld cells. Per-corpus contrasts, families weighted
equally, t intervals. Pre-registered rows (row 1); reviewed analysis. Fairly sure of the
numbers; narrow in scope (one bank and split, full-tape fitting, one α, external fitting).
([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md),
[analysis](runs/2026-10-07-1707/analysis.md))

- **A previous-token table fitted to solver tapes speeds fresh search beyond a token-only fit to
  the same tapes.** C/T 1.365× [1.288, 1.446] on training cells; BE 1.46× [1.32, 1.61], PA 1.28×
  [1.20, 1.35]; C faster in 31/32 corpora and 129/160 corpus × cell pairs; unchanged with
  unsolved runs charged 1 × instead of 2 × cap (1.360×). Per-corpus sd 0.27 (BE) and 0.16 (PA)
  log2. T here is the likelihood-best token fit, not the search-fastest token map; T was not
  resolved from the 20 search-selected 1723 maps, and these intervals allow appreciable
  differences (BE 0.95× [0.81, 1.11], PA 1.02× [0.81, 1.28], unpaired).
- **The gain transfers to the withheld cells.** C/T 1.293× [1.213, 1.378] over 32 corpora (30/32
  faster); C/G4 2.75×, T/G4 2.13× (unpaired). So this procedure supplies held-out gain beyond a
  token-frequency bias on this bank.
- **Matching C's pooled emitted token frequencies does not reproduce the gain, but that control
  is not neutral.** C/K 1.654× [1.568, 1.744] (32/32 corpora); K is itself slower than T, 0.825×
  [0.776, 0.878] (training) and 0.841× (withheld). C/T, not C/K, is the better size of the
  contextual increment. Position-specific and in-population frequencies were not matched.
- **No matched-family advantage was resolved on any withheld cell.** C fitted on the matched family over C fitted on the other: 1.02×
  [0.91, 1.15] on the single BE withheld cell, 0.75× [0.63, 0.89] and 0.99× [0.89, 1.10] on the PA
  ones; on `(F?S:M)+m` the BE-fitted tables (both T and C) are faster. C's gains extend to both
  families; the carrying structure and modest family preferences remain unresolved, and one BE
  cell cannot refute a BE preference.
- **The tapes carry order information and the fit is cheap.** About 0.45 bits per transition of
  previous-token dependence above a within-tape shuffle, consistently across all 32 corpora. C has
  lower start-row top-token concentration than G4 (0.52–0.63 against 0.69, though also lower
  start-row entropy); the start row's contribution to the speed gain is unmeasured. One corpus costs
  about 12 M evaluations (500 worker-s); C pays it back against G4 in about 120–590 training-cell
  searches (descriptive, at this cap).
- **Not shown:** that evolution or any search-cost learner can reach C (four selection-based
  context procedures gave no resolved gain, 13–19); which structure carries it (specific bigrams,
  executed versus inert tokens, position); how it depends on α (the probe's α 400 was weaker on
  BE). (Whether one refit from C's own solvers helps further: see the next section.)

