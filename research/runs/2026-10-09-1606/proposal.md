---
node: questions/10-compositional-map-transfer/34-chain-block-suffix-preservation
title: Chain blocks with versus without suffix preservation (W vs R on then-addition)
bank: then-addition-v1
---
Per [strategy 1606](strategy.md) and its [plan](../../plans/chain-block-suffix-preservation.md); root 10 slot 26; sub-question [34](../../questions/10-compositional-map-transfer/34-chain-block-suffix-preservation/question.md).

**Question.** W (C-chain blocks added to C's unchanged search) beats C 1.23× [1.15, 1.31] on then-addition ([1036](../2026-10-09-1036/analysis.md)). W re-encodes the allele after each block so that allele keeps its old token. Is this containment part of W's gain, or do the coordinated chain proposals do the work alone? The answer decides whether boundary repair belongs in the baseline of the next acquired-decoder test.

**Closest known technique.** This is the locality, or "ripple", problem of context-dependent maps in grammatical evolution:
- [Rothlauf & Oetzel](https://madoc.bib.uni-mannheim.de/1255/1/ww_11_2005.pdf): low locality hurts mutation.
- [Castle & Johnson 2010](https://gpbib.cs.ucl.ac.uk/gp-html/Castle_2010_EuroGP.html): a change can alter the meaning of all following genes.
- [O'Neill et al. 2003](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2003_GPEM.html): argue that ripple *helps* crossover.
- [Lourenço et al. 2016](https://gpbib.cs.ucl.ac.uk/gp-html/Lourenco_2016_GPEM.html): SGE removes ripple by design.

They disagree on the sign. This is a mechanism test of a known question in a new decoder (externally fitted previous-token table; nothing inherited or outer-selected), adding a matched contrast that differs only in the ripple.

**Probe** ([script](steward_probe/suffix_probe.py), read-only, 16 C tables). Without the repair, 65–67% of block edits change the decoded suffix. When they do, about 3 tokens change: about 2 extra per edit beside 2.9 inside the block. Frequent but local. This also corrects 32's reading that C's point mutation "re-decodes the whole suffix".

**Arms.** C tables, search (P 256, lexicase, 524 288 cap), length and start laws, rate 0.2 and RNG streams are as in 1036. The code base is `e9a04f8`.
- **W:** the historical 1036 rows.
- **R:** same draws and same block tokens as W. At the boundary, R reads the token the unchanged allele decodes to after the new final token, then draws uniformly within that token's interval. Its decoded output therefore equals the unrepaired output, and it uses the same number of RNG draws as W. Nothing beyond the boundary changes.
- **C:** the historical 1036 rows, as the practical reference.

**Unit.** The source corpus (n = 16). R runs 16 then-addition cells × 16 seeds per corpus, 4 096 searches in all. Each is paired with 1036's W and C rows by (corpus, cell, seed). A reference set runs the 8 comparison-gate holdouts × 8 seeds (1 024 searches), descriptive only.

**Prepare gates.**
- Replay one W and one C row per corpus bit-exactly. 1350 did this at `e9a04f8` (48/48).
- Run a 10k forced-edit audit: R equals W in the block and prefix; R's decode equals the unrepaired decode; the boundary allele lies in its interval; no allele beyond it changes. Record the realized ripple histogram.
- Run a 32-search timing smoke.

If the replay fails, run fresh W and R on new seeds (8 192 searches, no holdouts), and drop paired use of C.

**Feasibility and cost.** In 1036, W took 6.20 worker-s per search on then-addition and 3.37 on holdouts. At 10 workers that projects to about 48 min, or 55 min with a 15% margin; the fallback is about 99 min. Queue timeouts are 30 + 110 = **140 min**. Agents take about 3 h, for a total of about **4–5 h**, well within the 15.9 h left.

**Precision.** 1036's W/C half-width was ×1.069, so I project about ×1.07 here. Doubling seeds would reach only ×1.06.

**Primary comparison.** W/R = exp(mean over corpora of the paired log cost_R − log cost_W). Unsolved searches count as 2 × cap, and the interval is a 95% t on 15 df. The worthwhile size is **1.10×**, about half of W/C's log gain (√1.227 ≈ 1.108). Rules, in order:
1. **Ripple helps:** upper bound < 1. Drop the repair.
2. **Preservation needed:** lower bound > 1 and point ≥ 1.10. Keep the repair in later acquisition baselines.
3. **Not needed at this resolution:** upper bound < 1.10. If R/C's lower bound is > 1, chain proposals help without containment (not shown to be the sole cause).
4. **Unresolved:** otherwise. Report a ×1.05 price; no top-up.

**Descriptive.** R/C, holdout contrasts, BE/PA split, per-cell results, 1 × cap, both-solved pairs, solves, mean evaluations and worker-s, and realized tokens changed inside and beyond each block.

**Scope.** This is a development bank. C remains an external fit, and W's length law came from F. The run does not explain C/T, modules or acquisition.

**Expectation.** Ripple adds about 2 tokens to edits of about 3 tokens. That is a moderate widening, and 31 found that undirected width hurts. My guess is W/R of 1.03–1.10 (rule 3 or 4), with R/C above 1. W/R ≥ 1.15 or < 0.95 would surprise me.

**Next action.** Every rule returns to strategy, and nothing further is funded automatically.
