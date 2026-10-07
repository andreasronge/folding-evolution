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
