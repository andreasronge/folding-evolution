---
node: questions/10-compositional-map-transfer/24-comparison-gate-bank
title: Comparison-gated bank, frozen 4+4 holdout split, and corpus context vs token fit on its training cells
bank: comparison-gate-v1
---

**Question and mechanism.** Per [strategy 1246](strategy.md) and the
[plan](../../plans/comparison-gated-transfer.md): does the solver-corpus context fit (C), which beat
a token-only fit (T) 1.37× on the old bank, keep that advantage on new, longer compositions? The new bank uses BE `A>B ? C : D+E` and PA
`(A>B ? C : D)+E`, with A–E drawn from SUM/MAX/MIN/FIRST (one reducer repeated) and
13 tokens per program. This stage freezes the bank, split and tables and measures C/T on training cells only;
holdouts stay unsearched for stage 2. Sub-question [24](../../questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md)
uses root 10's sixteenth slot.

**Closest technique.** The fit learns an instruction-transition model from good programs and
samples from it. External fitting, as in
[N-gram GP (Poli & McPhee 2008)](https://experts.umn.edu/en/publications/a-linear-estimation-of-distribution-gp-system/)
(3-gram EDA for linear GP) and [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/). Transferring a
source-learned solution distribution resembles
[Ardeh et al. 2020](https://gpbib.cs.ucl.ac.uk/gp-html/Ardeh_2020_CEC.html) (probabilistic
prototype tree). This adds a **replication and boundary test** on fresh GT-gated compositions,
and the tree's first split with several protected holdouts per family.

**Steward probe** (read-only, `research/main` a804f4f; [files](steward_probe/)):
- The roster has 2×240 programs. 162+162 have non-constant gates, giving 220 distinct
  behaviours: none shared across families and none equal to a 1603 cell.
- The exact ≤9-token screen (frozen 1603 rule, 104 s) keeps **37 BE and 56 PA** behaviours. The
  old bank kept 5 and 8. Most gates compare FIRST with another reducer.
- G4 ran 8 seeds on 6+6 sampled retained cells at cap 524k: **57/96 solved** (2/8–7/8 per cell).
  Medians run from 48k evaluations to above the cap. Harder than the old bank
  (45–50/50) but tractable; 1.48 s wall per search on 10 workers. These 12 cells are now development/training only.
- Each of the 15 four-cell training subsets of the probed cells covers at least 4 untouched,
  role-covered holdout candidates per family.

**Design.**
- *Bank.* Re-run roster and screen in-repo, validate canonicals Rust vs Python, save the D1331
  manifest and hashes (≤9 tokens cannot certify 13-token minimality).
- *Training cells.* BE `F>S?F:M+m`, `F>m?S:F+M`, `S>F?M:F+m`, `S>F?m:M+S`.
  PA `(F>S?F:m)+M`, `(F>S?m:M)+F`, `(M>F?m:S)+S`, `(S>F?M:m)+m` (probed 4-subset covering most holdout candidates).
- *Holdouts.* Four per family, one for each repeated reducer, so both families have identical
  token totals. Each is the unprobed role-covered candidate with lowest
  sha256(id+"1246"), performance-blind; the rest stays untouched.
- *Fitting:* the frozen 1707 rule (first exact solver's tape, 1600 transitions per cell, T = 24
  multipliers on G4, C shrunk α 50 toward G4); K fitted, not scored; G4 unchanged.
- *Arms and unit.* 8 corpora per family, each from 48 G4 collection searches per own training
  cell (3 072 searches). C and T run on 16 fresh seeds per corpus × own training cell, with
  seeds shared between C and T (2 048 searches). G4 gets 32 fresh seeds per training cell
  (256, descriptive headroom). The unit is the corpus (n 16).
- *Freeze for stage 2* (before any holdout search): holdout ids, table hashes, seeds, scoring:
  C and T of every corpus on all 8 holdouts × 16 seeds, G4 32 per holdout (4 352 searches).

**Feasibility and cost.** At the probe's 1.48 s per search, collection takes about 76 min,
C/T scoring about 35–50 min (fitted maps solved 2.4–3.3× sooner than G4 on the old bank)
and G4 about 6 min, so roughly **2.0–2.2 h of queue**. I set the timeout at **3 h**.
Interleaved scoring leaves whole corpora on timeout (analysis needs ≥ 12). With agents, about 5 h. Stage 2
would add about 1.5 h of queue and 2.5 h of agent time, so **about 9–10 h overall**, under the
12–18 h envelope. Probe yield on the chosen cells: 40/64 (one BE cell 2/8, about 12 tapes per corpus).

**Primary comparison.** C/T is the geometric-mean ratio of evaluations to an exact solve,
with unsolved searches counted as 2× cap. It is computed per corpus over its 4 own cells × 16
seeds, and summarized as a 95% t-interval over corpora, with both families weighted equally.
Sensitivity checks use 1× cap and each family separately.
- Lower bound > 1.0 and collection yield ≥ 40%: recommend stage 2 (frozen holdout C/T)
  to the strategist.
- Upper bound < 1.10: the context advantage does not reproduce on this bank's training
  cells, and stage 2 is not worth its cost for C/T. The bank stays available.
- Otherwise the result is unresolved. Report the number of extra corpora needed and return
  to strategy.

**Expectation.** I expect C/T of about 1.2–1.4×. The gate's token order is something context
can express and counts cannot. Surprises: C/T ≤ 1 (the gain belonged to the old shapes) or
yield < 40% (collection is the obstacle).

**Next action.** If approved, a researcher implements this on `research/main` (bank module,
split, corpus runner pointed at the new bank), with a smoke run and no holdout search. After
the queue: analysis, then a strategy review deciding stage 2.
