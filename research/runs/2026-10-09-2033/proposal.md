---
node: questions/10-compositional-map-transfer/36-sparse-source-feedback
title: One feedback batch under C4+F4 versus four more G4 attempts
bank: then-addition-v1
---
**Question and mechanism.** Per [strategy 2033](strategy.md) and the [plan](../../plans/sparse-source-feedback.md). Can the cheap C4+F4 bias collect its own
next small source batch so that the rebuilt decoder and library beat spending the same
attempts under G4? Biased collection may raise yield and fill empty cells (35's losses tracked
them, post hoc), or reinforce syntax it already has.

**Closest known technique.** Iterated model-building search: [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/)
updates a program distribution from search results, and [DreamCoder](https://arxiv.org/abs/2006.08381)
([PLDI 2021](https://pldi21.sigplan.org/details/pldi-2021-papers/55/DreamCoder-Bootstrapping-Inductive-Program-Synthesis-with-Wake-Sleep-Library-Learning))
alternates search with library learning from solved programs. Here the map adapts by
**external fitting** in one batched step, then is frozen and reused on excluded compositions.
Not new in kind ([21](../../questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md)
found exact feedback 1.33× on a large corpus); this is a **boundary test**: does feedback
survive a sparse, hole-ridden first batch, against a static control of equal attempts?

**Arms.** Each of 35's 64 builds (16 corpora × 4 source blocks) shares its first batch
(1246 attempts 4b+1…4b+4 per training cell, failures kept).
- **A8 (adaptive):** 4 new attempts per training cell under that build's frozen C4+F4
  (operator and fallback unchanged), new collection seeds; 1 024 searches.
- **S8 (static):** 1246 G4 attempts 16+4b+1…16+4b+4 per cell: disjoint from every
  seed block, chosen by schedule order, original cost charged. No new collection.
- Both pool 8 attempts per cell and rebuild C and F with 35's code unchanged. Fitting mass is
  already fixed at 1 600 per non-empty cell, so more tapes do not weaken the α 50 prior;
  empty cells still get G4's expected transitions.
- References: retained C4+F4 rows from 1743 and full F/C rows from 1036, on the same roster,
  seeds and cases. Replayed by sample, not rescored.

**Experimental unit.** Corpus (16; t on 15 df). Four nested builds per corpus, equal weight. Scoring uses 1743's roster: 16 then-addition cells × 16 seeds per
build-block, 2 arms, 8 192 searches.

**Feasibility (measured tonight, read-only, 652fde5 worktree).** The probe ran C4+F4 for
blocks 0 and 2 on training cells, one attempt per cell, new seeds: **117/128 solved** (G4:
~60% in these first batches, 9.6 solvers per 16 attempts). In cells that were empty in the
source, 4/6 solved. Mean **≈100k evaluations and 4.5 worker-s per search**, against 310k for
a G4 attempt. G4 sanity check: 11/16. Adaptive collection costs about 8 min of
wall time, and its batch costs about a third of a G4 batch in evaluations. Scoring at 1743's
rate (8 192 searches in 104 min) takes ~105 min. `small_source_run.py` already saves and
verifies solvers.

**Full cost.** Preparation ≤ 120 min (researcher). Queue: prepare (collection, fits, hash and
replay gates) timeout 45 min, score 3 h, so 3.75 h summed, expected ~2.2 h. Critic,
review, analysis and decision ~2 h. Total ≈ 6–7 h, done before 08:12. Admission: 16 seeds if projected scoring fits 3 h, else 12.

**Primary comparison and decision rule.** σ = cost(S8)/cost(A8), using 1743's estimator
(log capped cost, unsolved = 2 × cap, cells and seeds averaged, blocks equally weighted,
then corpora; 95% t interval). Worthwhile increment: 1.10×, as for F4/W4.
- Lower bound > 1.10: **feedback works.** Continue to the economics.
- Upper bound < 1.10: **feedback is not worth it.** End the sparse-feedback policy.
- Otherwise **unresolved**: report a resolution price and return to strategy.

Reported, no rule: sensitivities (1 × cap, both-solved, BE/PA, each block);
A8 and S8 against retained C4+F4 (does more data help at all) and against full F (ρ);
solver counts, empty cells and library sizes per arm; A + N·S curves in evaluations for A8,
S8, C4+F4, full F and G4. These charge the shared first batch, every failed attempt and the
intermediate build. The usefulness question beyond
keeping the seed is answered by the A8/C4+F4 interval and its break-even N, not by σ.

**Expectations.** From the probe, A8 pools ~24 solvers per build against S8's ~19, has
fewer empty cells, and its second batch costs about a third of S8's evaluations. I expect σ ≈ 1.15 [1.05, 1.26], with both enlarged arms beating C4+F4
and neither reaching full F (ρ ≈ 0.75–0.85). That risks an unresolved result. If σ is unresolved but A8 matches S8 at a third of the extra cost, adaptive
collection is still the cheaper way to buy data. **Surprises:** σ < 1 (lock-in: biased
solvers narrow C or F), or A8 ≥ full F.

**Scope.** Development sources and bank, external fitting, one update. Decoder, library,
yield and content are not separated; not transfer or inherited map evolution.

**Next action.** Researcher extends `small_source_run.py` (on 652fde5) with the A8 collection
and S8 selection. Gates: the S8 and first-batch attempt keys are disjoint and hashed; the
1743 C4+F4 builds re-fit bit-exactly from their 4 attempts; 1743 rows replay. Then: queue,
analyse, and return to strategy whatever the outcome.
