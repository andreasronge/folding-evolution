---
node: questions/10-compositional-map-transfer/30-position-matched-replacement
title: Position-matched replacements Q and P for the frozen context tables C (1548 row F seeds)
bank: then-addition-v1
---
**Question and mechanism.** In run 0125, the frozen context tables C beat K, which is G4 reweighted
to C's *pooled* frequencies, by 2.48× [2.17, 2.83] on then-addition. K differs from C in its
conditional rows and in where tokens sit on the tape. I follow [strategy 0239](strategy.md) and its
[plan](../../plans/position-matched-context.md), and score two frozen projections of each C:
- **Q** (primary): G4's rows × 24 multipliers per position, matched to C's emitted marginal at each
  of the 32 positions. It keeps G4's previous-token dependence.
- **P** (interpretation): each position is drawn independently from C's marginal at that position.

**Steward probe** (read-only, saved 1246 tables). Q fits exactly in floating point, and quantised P
errors are ≤ 2.7e-5. A crude quantiser left Q errors ≤ 8.7e-4, so the fit must run `normalize`
inside its loop. Two caveats:
1. C's rows are as far from Q's as from K's (KL 0.11–0.14 bits per transition for both, against
   0.44–0.47 bits of dependence in C). Position matching mainly changes the start of the tape
   (position-0 total variation 0.07–0.21).
2. One allele resample changes about 2.9 decoded tokens under C, 1.7 under Q and 0.9 under P.
   C ≫ Q would therefore implicate C's conditional rows, as supply, as variation neighbourhood or
   both, without separating the two.

**Closest known technique.** Position-specific EDA program models, adapted by external fitting.
- P is univariate-positional, like PBIL
  ([Baluja 1994](https://www.ri.cmu.edu/pub_files/pub1/baluja_shumeet_1994_2/baluja_shumeet_1994_2.pdf))
  and PIPE's per-node distributions ([Salustowicz & Schmidhuber 1997](https://pubmed.ncbi.nlm.nih.gov/10021756/)).
- Q is positional-conditional on a fixed template. EDP instead learns parent–child dependencies at
  tree positions ([Yanai & Iba 2003](https://gpbib.cs.ucl.ac.uk/gp-html/Yanai_2003_EodpboBn.html)).
- C is a position-free bigram, like N-gram GP ([Poli & McPhee 2008](https://repository.essex.ac.uk/9722/)).

A **mechanism test** of a known family: it adds order-versus-position controls for maps used inside
evolutionary search.

**Arms, unit, seeds.** Q and P are built from the 16 frozen 1246 C tables (8 BE-, 8 PA-fitted).
They run on 1548 row F's 16 cells with the same 8 paired seeds and 64-case draws as C, T and K:
4 096 new searches. C, T and G4 rows are reused from 1548 and K rows from 0125. P 256, cap 524 288,
the exact D1331 check and the variation operators are unchanged. The unit is the corpus
(n = 16, all that exist).

The fit uses `normalize` (floor 250), propagates the quantised Q marginal from one position to the
next, and needs max error ≤ 1e-3 at every position. Gates before the queue:
- table hashes and per-position errors;
- Q's position-0 row equals C's start row;
- the positional decoder fed 32 copies of K replays 16 rows from 0125 bit-exactly;
- 32 C/T rows replay bit-exactly.

On any gate failure, write `infeasible.md` with a price.

**Feasibility.** K ran at about 12.2 worker-seconds per search (2 048 searches in 41.5 min on 10
workers). Q and P use numpy lookups of about 19 MB. Expected queue time is about 84–92 min, and
about 2.8 h if every search caps. Preparation times 32 searches. Queue timeouts are 0.5 h + 3 h,
within strategy's 4 h. At the corpus sd of log C/K (0.25), the 95% half-width is about ×1.14.

**Full cost.** About 2 h to build, validate and review, about 1.5 h of queue (3.5 h worst case),
and about 1.5 h for analysis and decision: **5–7 h**, using root 10's slot 21. No new corpora,
fits or bank.

**Primary comparison and decision rule.** C/Q = exp(mean over corpora of the mean over 16 cells × 8
seeds of log cost_Q − log cost_C). Unsolved runs count as 2 × cap, with a t interval on 15 df.
- **Lower bound ≥ 1.20 → positional supply on G4's grammar is insufficient.** The acquisition target
  must carry conditional structure. Strategy then weighs fragments against a contextual acquisition
  mechanism, and positional-vector learners are deprioritised.
- **Upper bound ≤ 1.20 → sufficient within 20%.** Strategy prices acquiring a positional map. C/P is
  then read against the same bands to see whether G4's grammar is needed.
- **Otherwise unresolved.** Report the interval and the price of resolving it: about 30 corpora for
  ±10%, which needs new collection.

Reported without a rule:
- paired Q/K;
- C/P and Q/P;
- the share log(C/Q)/log(C/K);
- 1 × cap and both-solved sensitivities;
- solves, per-cell and BE/PA results;
- tokens changed per mutation and per crossover for each arm.

No top-up.

**Expectations.** I expect C/Q of 1.7–2.4×, Q/K of 1.0–1.4×, and P slower than Q. Two results
would surprise me: C/Q upper bound ≤ 1.20 (the start of the tape carries the advantage), or P ≥ Q.

**Scope.** Development bank (mechanism evidence, not transfer); external projections, not
acquisition; uniform-prior marginals.

**Next action.** Researcher: extend the 0125 harness (`frequency_matched_run.py`, `research/main`
`8e62831`), pass the gates, then queue. After analysis, return with `next: strategy`.
