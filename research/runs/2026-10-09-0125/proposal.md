---
node: questions/10-compositional-map-transfer/29-frequency-matched-transfer
title: Frozen frequency-matched K tables on then-addition (C/K on 1548 row F seeds)
bank: then-addition-v1
---
**Question and mechanism.** Run 1548 found that the frozen comparison-gate context tables C beat
token-only fits T to the same G4 solver tapes by 2.12× [1.86, 2.41] on the then-addition bank.
C and T emit different token frequencies, so that result does not say whether C needs its
context or whether its pooled frequencies would be enough. The frozen K tables answer this
directly. K is G4 × 24 token multipliers tuned so its pooled emitted marginals match C's (max
error 2.9e-5, recomputed by strategy 0125). They exist for all 16 corpora and have never been
scored. If K ≈ C, the next learner can target a 24-number frequency map. If C ≫ K, the
useful content is structure beyond pooled frequency, which justifies the
[fragment plan](../../plans/learned-executable-fragments.md) or another contextual learner.
I follow [strategy 0125](strategy.md) as written.

**Closest known technique.** EDA program models of different order. C is a bigram
(previous-token) model and K a reweighted univariate model on a fixed template. The nearest
precedent is N-gram GP, which learns a 3-gram distribution over linear-GP instructions
([Poli & McPhee, EuroGP 2008](https://repository.essex.ac.uk/9722/)). PIPE is its univariate ancestor ([Salustowicz & Schmidhuber 1997](https://pubmed.ncbi.nlm.nih.gov/10021756/)). Both
adapt by external fitting, as here. This is a **mechanism/boundary test**, not a new technique.
It adds a frequency-matched order control on a cross-shape transfer bank. The tree's one prior
instance is on a different bank: C/K 1.65×, with K slower than T (0.83×) on four-reducer
training cells ([20](../../questions/10-compositional-map-transfer/20-solver-corpus-context/question.md)).

**Arms, unit, seeds.** One new arm: K, using the 16 frozen 1246 tables (8 BE-fitted, 8
PA-fitted). It runs on 1548 row F's 16 cells with the **same 8 paired seeds and 64-case draws**
per corpus × cell as C and T. That is 2 048 searches. C, T and G4 rows are reused from 1548,
with P 256, cap 524 288 and the exact D1331 check unchanged. The unit is the corpus (n = 16).
Before scoring, preparation must verify K table hashes against `freeze.json`, the bank SHA and the
marginal match. It must also replay 32 C/T rows bit-exactly at `45b2bdb`; on failure, stop with a priced correction.

**Feasibility.** In 1548 row F, 4 352 searches took 70 min. Mean worker time was C 7.1 s, T
11.2 s and G4 13.5 s per search, at about 9.8 workers effective. K at T's rate takes about 39 min;
at G4's rate about 47 min. If every search caps, about 1.7 h. Preparation times 16 K searches
before admission. The queue timeout is 2.5 h, within strategy's 3 h. Precision: the per-corpus
sd of log C/T on row F was 0.243, so with n = 16 the 95% half-width is about ×1.14.

**Full cost.** Preparation, review and replay about 1.5 h; queue about 1 h; analysis and decision about 1.5 h: **4–4.5 h**. This uses root 10's last slot (19/20 used). No new acquisition,
fit, bank or G4 rows.

**Primary comparison and decision rule.** Primary: C/K = exp(mean over corpora of the mean over
cells × paired seeds of log cost_K − log cost_C). Unsolved runs count as 2 × cap, with a t
interval on 15 df. Bands:
- **C/K lower bound ≥ 1.20 → pooled frequencies insufficient.** C carries a worthwhile
  advantage beyond its pooled emitted frequencies. Report it to strategy as the target for a
  structural learner (fragments or context) at its full price.
- **C/K upper bound ≤ 1.20 → K adequate within 20%.** Next, prioritize acquiring frequencies with
  the simpler map, by selection or inheritance, before building richer representations.
- **Otherwise unresolved.** Return to strategy with the C/K interval and the price of resolving
  it. Equality is not claimed.

Reported without a rule: K/T, the descriptive share log(K/T)/log(C/T) (not "the fraction caused by order"), 1 × cap and
both-solved sensitivities (the latter is selection-conditioned), solve counts, per-cell C/K,
BE- vs PA-fitted C/K and K/G4. No top-up after K is seen.

**Expectations.** From question 20 I expect C/K about 1.5–2.5×, LB well above 1.20, with K near
or below T (K/T 0.8–1.1). Two results would surprise me: C/K UB ≤ 1.20 (pooled frequencies suffice here though they failed in question 20) or K/T clearly above 1.3 (C's marginals beat the token fit's own ML marginals, so T misses a frequency target).

**Scope.** A mechanism follow-up on a development bank, not fresh transfer evidence. K matches pooled, not positional, frequencies, keeps G4's context template, and does not match solver supply or mutation neighbourhoods. A large C/K does not
show that fragments will help. A small C/K does not show that context is useless elsewhere.

**Next action.** Researcher: build the K arm on the 1548 harness, run validation and replay, time
16 searches, then queue. After analysis, return to strategy (`next: strategy`) with the band
outcome and the fragment plan's price.
