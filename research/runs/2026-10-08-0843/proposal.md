---
node: questions/23-heritable-variation-bias
title: Inherited token frequencies at equal exposure — frozen vector vs uniform, with broken-ancestry and scaffold controls (slot 1, corrected)
bank: tag-threshold-v1   # sum/max > 1, 5 on length-4 lists over 0..9; threshold 2 untouched (development bank)
---
**Question.** This follows [strategy 0843](strategy.md) and its [addendum](../../plans/heritable-bias-equal-exposure.md). Each program carries a token-frequency vector that its offspring inherit. With equal exposure, does selection make that vector useful once it is frozen and the programs are discarded? Usefulness is measured against **uniform**. Ancestry-broken and hand-scaffold arms test linkage and practical value.

**Closest technique.** This is self-adaptation by per-individual inheritance. [Stephens et al. 1997/98](https://pubmed.ncbi.nlm.nih.gov/9847423/) and [Angeline 1996](https://gpbib.cs.ucl.ac.uk/gp-html/angeline_1996_aigp2.html) study inherited variation parameters that are never rewarded directly. [Glickman & Sycara 2000](https://ri.cmu.edu/?p=8077) show such parameters can be selected to protect resident fitness rather than to aid search. That is explanation D, and continuing episodes after a solve adds exactly this maintenance pressure. New here: a token distribution, tested frozen on fresh populations; a mechanism test, not a new technique.

**Design.**
- **Code.** `inherited_bias.py` at `25f929e`, unchanged except for fixed-duration episodes. Every episode runs exactly 128 generations, so each run has 6,144 in both arms. The first solve is recorded and does not end the episode. Verification stops after the first witness; evaluation and reproduction continue.
- **Arms and seeds.** Inherited and broken, for sum and max. A new master seed; no 2243 acquisitions are reused.
- **Unit.** One acquisition run: **20 per family × arm**, 80 in total.
- **Frozen scoring.** Each learned vector gets 16 shared seeds per training target (32 searches), with a cap of 262,144. Uniform, scaffold and the 1558 fit get the same 16 seeds plus 48 more per target.
- **Validation.** Immediate/last-generation/no solves, equal scheduled counts, σ = 0 replay.
- **Queue entries.** Acquisition, sum scoring and max scoring run separately, so a timeout keeps completed work.

**Feasibility** (2243 [stage 0](../2026-10-07-2243/infeasible.md)).
- An acquisition run should take about 260 s: about 27 ms per generation excluding the verifier (≈ 170 s for 6,144), plus up to 90 s of verification before the first solves.
- A censored frozen search costs ≈ 10 s and a solved sum search 1–3 s. The max1 uniform tail is 170 s, for a mean of ≈ 55 s.

**Cost** on 10 workers:

| Part | Time |
|---|---|
| Acquisition | ≈ 35 min |
| Learned scoring (2,560 searches) | ≈ 30 min |
| Reference scoring (768 searches) | ≈ 9 min |
| **Total at measured means** | **≈ 74 min** |
| Timeouts (2× allowance + 15 min checks) | ≈ 2.7 h |
| Agent work | ≈ 3 h |
| **Full cost** | **≈ 6 h** |

During preparation the researcher re-times one acquisition per family × arm, without looking at frozen performance. If the projection exceeds 3 h, extra reference seeds are cut from 48 to 16; acquisition runs are never cut.

**Primary comparison** (per family, never pooled): **R_u = uniform ÷ inherited**.
- **Score.** Geometric-mean evaluations to exact over both training targets. Censored searches count at the cap, and solve counts are reported.
- **Interval.** 95% crossed bootstrap over acquisition runs within family and seed indices within target.
- **Precision.** Assuming a between-run SD of 0.5–0.8 log, the interval is ×/÷1.33–1.48. The per-search SD of ≈ 1 log was measured; the between-run SD is an assumption, and this run will measure it.

| Outcome | Rule |
|---|---|
| **Acquired** | lower bound > 1 and point ≥ 1.5× |
| **Bounded** | upper bound < 1.5× |
| **Unresolved** | otherwise |

**Interpretation controls** (stated now, not gates):
- **Linkage.** L = broken ÷ inherited, shown beside broken ÷ uniform so that beating a degraded control is visible.
- **Practical value.** Scaffold ÷ inherited.
- **Descriptive.** Episode solves, lineage depth, Price covariances, distance from uniform, and θ trajectories. The trajectories watch CONST_2 and "safe" tokens such as SEP_A and slots, which would signal maintenance selection.

**Next action:**
- **Acquired in a family, L lower bound > 1, and scaffold advantage lower bound < 2×:** propose slot 2, frozen matched/mismatched transfer to threshold 2.
- **Acquired, but linkage unresolved or scaffold clearly better:** record the acquisition, stop expanding this procedure, go to strategy.
- **Bounded in both families:** park 23 with a bound on this procedure (B/E), not on self-adaptation; go to strategy.
- **Unresolved:** go to strategy with the measured between-run SD and the price of an extension.

**Expectation.**
- **Sum:** acquired ≈ 45%, unresolved 30%, bounded 25%.
- **Max:** bounded ≈ 55%. Selection runs mostly on partial lexicase fitness, since only about 7 of 48 episodes solve.
- **Most likely overall:** a modest sum acquisition that the scaffold beats clearly (≈ 5× in stage 0), which ends this expansion.

**Surprises:** broken ≈ inherited with both beating uniform (floor or drift giving generic supply); max inherited beating uniform; inherited within 2× of the scaffold.

**Scope.** One rule, σ and schedule, including maintenance after solving. Development bank, training targets only, fixed token meanings.
